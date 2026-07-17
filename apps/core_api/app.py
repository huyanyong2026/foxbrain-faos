"""Authenticated, read-only HTTP access to the SAP mirror.

The service deliberately exposes no generic SQL endpoint and accepts no
mutating HTTP methods.  SAP credentials are never loaded by this process.
"""

from __future__ import annotations

import hmac
import hashlib
import json
import os
import re
import sqlite3
import threading
import time
from contextlib import closing
from datetime import datetime, timezone
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
from zoneinfo import ZoneInfo

from foxbrain_os.platform_governance import health_payload, runtime_payload, version_payload


IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_@$#]*$")
DEFAULT_TABLES = {
    "dbo.OADM", "dbo.OITM", "dbo.OITB", "dbo.OITW", "dbo.OWHS",
    "dbo.OCRD", "dbo.OCRG", "dbo.OMRC", "dbo.OINV", "dbo.INV1", "dbo.ORIN",
    "dbo.RIN1", "dbo.OPCH", "dbo.PCH1", "dbo.OPOR", "dbo.POR1",
    "dbo.ORDR", "dbo.RDR1", "dbo.OHEM", "dbo.OSLP",
}
BUSINESS_TZ = ZoneInfo(os.environ.get("CORE_TIMEZONE", "Asia/Shanghai"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def json_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (bytes, bytearray)):
        return {"type": "binary", "bytes": len(value)}
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def quote_identifier(value: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        raise ValueError("invalid identifier")
    return "[{}]".format(value.replace("]", "]]"))


class TokenPolicy:
    def __init__(self, raw: str):
        parsed = json.loads(raw or "{}")
        self.entries = []
        for client, config in parsed.items():
            token = str(config.get("token", ""))
            if token:
                self.entries.append({
                    "client": client,
                    "token": token,
                    "scopes": set(config.get("scopes", [])),
                    "role": str(config.get("role", "service")),
                    "store_ids": {str(value) for value in config.get("store_ids", [])},
                })

    def authorize(self, token: str, scope: str):
        for entry in self.entries:
            if hmac.compare_digest(token, entry["token"]) and scope in entry["scopes"]:
                return {
                    "client": entry["client"],
                    "role": entry["role"],
                    "store_ids": set(entry["store_ids"]),
                    "scopes": set(entry["scopes"]),
                }
        return None


class TTLCache:
    """Small process-local cache; cached values never become a write path."""

    def __init__(self):
        self._items = {}
        self._lock = threading.Lock()

    def get_or_build(self, key, ttl_seconds, builder):
        now = time.monotonic()
        with self._lock:
            item = self._items.get(key)
            if item and now - item[0] <= ttl_seconds:
                return item[1]
        value = builder()
        with self._lock:
            self._items[key] = (now, value)
        return value


class CoreService:
    def __init__(self, state_path=None, allowed_tables=None, connector=None):
        self.state_path = Path(state_path or os.environ.get(
            "CORE_MIRROR_STATE", "/opt/foxbrain-core/sync/mirror-state.db"
        ))
        configured = allowed_tables or os.environ.get("CORE_ALLOWED_TABLES", "")
        self.allowed_tables = {
            item.strip() for item in configured.split(",") if item.strip()
        } or set(DEFAULT_TABLES)
        self.connector = connector or self._connect
        self.cache = TTLCache()
        self.reference_ttl = int(os.environ.get("CORE_REFERENCE_CACHE_SECONDS", "86400"))
        self.metrics_ttl = int(os.environ.get("CORE_METRICS_CACHE_SECONDS", "300"))

    def _connect(self):
        import pytds
        return pytds.connect(
            server=os.environ.get("CORE_DB_HOST", "127.0.0.1"),
            port=int(os.environ.get("CORE_DB_PORT", "11433")),
            database=os.environ.get("CORE_DB_NAME", "SAP_MIRROR"),
            user=os.environ["CORE_DB_USER"],
            password=os.environ["CORE_DB_PASSWORD"],
            timeout=15,
        )

    def status(self):
        result = {
            "service": "VAFOX Enterprise Data Core",
            "mode": "read_only",
            "source": "SAP mirror",
            "checked_at": utc_now(),
            "mirror": {"status": "unknown", "completed_tables": 0, "failed_tables": 0},
        }
        if not self.state_path.exists():
            return result
        with closing(sqlite3.connect(str(self.state_path))) as db:
            db.row_factory = sqlite3.Row
            run = db.execute(
                "select * from mirror_runs order by rowid desc limit 1"
            ).fetchone()
            if run:
                data = dict(run)
                result["mirror"] = {
                    "status": "completed" if data.get("finished_at") and not data.get("error") else "running_or_failed",
                    "source_tables": data.get("source_tables", 0),
                    "completed_tables": data.get("completed_tables", 0),
                    "failed_tables": data.get("failed_tables", 0),
                    "started_at": data.get("started_at"),
                    "finished_at": data.get("finished_at"),
                }
        return result

    def tables(self):
        progress = {}
        if self.state_path.exists():
            with closing(sqlite3.connect(str(self.state_path))) as db:
                db.row_factory = sqlite3.Row
                for row in db.execute("select * from progress"):
                    progress[str(row[0])] = dict(row)
        return [
            {
                "table": name,
                "status": progress.get(name, {}).get("status", "not_recorded"),
                "rows": progress.get(name, {}).get("target_total"),
                "updated_at": progress.get(name, {}).get("updated_at"),
            }
            for name in sorted(self.allowed_tables)
        ]

    def rows(self, schema: str, table: str, limit: int, offset: int):
        full_name = "{}.{}".format(schema, table)
        if full_name not in self.allowed_tables:
            raise PermissionError("table is not approved for API access")
        schema_sql = quote_identifier(schema)
        table_sql = quote_identifier(table)
        limit = max(1, min(int(limit), 200))
        offset = max(0, int(offset))
        connection = self.connector()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "select * from {}.{} order by (select null) offset %s rows fetch next %s rows only".format(
                    schema_sql, table_sql
                ),
                (offset, limit),
            )
            columns = [item[0] for item in cursor.description]
            rows = [dict(zip(columns, (json_value(value) for value in row))) for row in cursor.fetchall()]
            return {"table": full_name, "offset": offset, "limit": limit, "rows": rows}
        finally:
            connection.close()

    def operation_snapshot(self, store_reference: str, as_of: str):
        """Return a bounded, read-only store snapshot for the operation center."""
        reference = str(store_reference or "").strip()
        if not reference or len(reference) > 160:
            raise ValueError("store reference is required")
        try:
            datetime.strptime(as_of, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("invalid as_of date") from exc
        connection = self.connector()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """select top 2 WhsCode,WhsName from dbo.OWHS
                where lower(WhsCode)=lower(%s) or lower(WhsName)=lower(%s)
                or lower(WhsName) like lower(%s) order by
                case when lower(WhsCode)=lower(%s) or lower(WhsName)=lower(%s) then 0 else 1 end""",
                (reference, reference, "%" + reference + "%", reference, reference),
            )
            warehouses = [dict(zip([item[0] for item in cursor.description], row)) for row in cursor.fetchall()]
            if len(warehouses) != 1:
                raise ValueError("store reference is not unique")
            warehouse = {key: json_value(value) for key, value in warehouses[0].items()}
            code = warehouse["WhsCode"]
            cursor.execute(
                """with movements as (
                  select l.ItemCode,h.DocDate,cast(l.Quantity as decimal(19,6)) Quantity
                  from dbo.OINV h join dbo.INV1 l on l.DocEntry=h.DocEntry
                  where h.CANCELED='N' and l.WhsCode=%s and h.DocDate>=dateadd(day,-180,cast(%s as date))
                  union all
                  select l.ItemCode,h.DocDate,-cast(l.Quantity as decimal(19,6)) Quantity
                  from dbo.ORIN h join dbo.RIN1 l on l.DocEntry=h.DocEntry
                  where h.CANCELED='N' and l.WhsCode=%s and h.DocDate>=dateadd(day,-180,cast(%s as date))
                ), sales as (
                  select ItemCode,
                  sum(case when DocDate>=dateadd(day,-30,cast(%s as date)) then Quantity else 0 end) Sales30,
                  sum(case when DocDate>=dateadd(day,-60,cast(%s as date)) then Quantity else 0 end) Sales60,
                  sum(case when DocDate>=dateadd(day,-90,cast(%s as date)) then Quantity else 0 end) Sales90,
                  sum(Quantity) Sales180,
                  max(case when Quantity>0 then DocDate end) LastSaleDate
                  from movements group by ItemCode
                )
                select i.ItemCode,i.ItemName,g.ItmsGrpNam,m.FirmName,
                w.OnHand,w.IsCommited,w.OnOrder,w.AvgPrice,
                coalesce(s.Sales30,0) Sales30,coalesce(s.Sales60,0) Sales60,
                coalesce(s.Sales90,0) Sales90,coalesce(s.Sales180,0) Sales180,s.LastSaleDate
                from dbo.OITW w join dbo.OITM i on i.ItemCode=w.ItemCode
                left join dbo.OITB g on g.ItmsGrpCod=i.ItmsGrpCod
                left join dbo.OMRC m on m.FirmCode=i.FirmCode
                left join sales s on s.ItemCode=w.ItemCode
                where w.WhsCode=%s and (
                  coalesce(w.OnHand,0)<>0 or coalesce(w.IsCommited,0)<>0
                  or coalesce(w.OnOrder,0)<>0 or s.ItemCode is not null
                )""",
                (code, as_of, code, as_of, as_of, as_of, as_of, code),
            )
            columns = [item[0] for item in cursor.description]
            products = [dict(zip(columns, (json_value(value) for value in row))) for row in cursor.fetchall()]
            sales = [
                {key: row.get(key) for key in ("ItemCode", "Sales30", "Sales60", "Sales90", "Sales180", "LastSaleDate")}
                for row in products
                if row.get("LastSaleDate") is not None
                or any(row.get(key) for key in ("Sales30", "Sales60", "Sales90", "Sales180"))
            ]
            return {"as_of": as_of, "warehouse": warehouse, "products": products, "sales": sales}
        finally:
            connection.close()

    def replenishment_input(self):
        """Return normalized 60-day sales and available stock for approved stores."""
        try:
            store_mapping = json.loads(os.environ.get("CORE_STORE_MAP_JSON", "{}"))
        except json.JSONDecodeError as exc:
            raise ValueError("CORE_STORE_MAP_JSON is invalid") from exc
        if not isinstance(store_mapping, dict) or not store_mapping:
            raise ValueError("CORE_STORE_MAP_JSON is not configured")
        placeholders = ",".join("%s" for _value in store_mapping)
        sql = """
        with movements as (
          select l.WhsCode,l.ItemCode,h.DocDate,cast(l.Quantity as decimal(19,4)) as Qty
          from dbo.OINV h join dbo.INV1 l on l.DocEntry=h.DocEntry
          where h.CANCELED='N' and h.DocDate>=dateadd(day,-59,cast(getdate() as date))
          union all
          select l.WhsCode,l.ItemCode,h.DocDate,-cast(l.Quantity as decimal(19,4)) as Qty
          from dbo.ORIN h join dbo.RIN1 l on l.DocEntry=h.DocEntry
          where h.CANCELED='N' and h.DocDate>=dateadd(day,-59,cast(getdate() as date))
        ), sales as (
          select WhsCode,ItemCode,
            sum(case when DocDate>=dateadd(day,-29,cast(getdate() as date)) then Qty else 0 end) as Sales30,
            sum(case when DocDate<dateadd(day,-29,cast(getdate() as date)) then Qty else 0 end) as SalesPrev30
          from movements group by WhsCode,ItemCode
        )
        select w.WhsCode,wh.WhsName,i.ItemCode,i.ItemName,i.ItmsGrpCod,
          cast(w.OnHand-w.IsCommited as decimal(19,4)) as AvailableQty,
          coalesce(s.Sales30,0) as Sales30,coalesce(s.SalesPrev30,0) as SalesPrev30
        from dbo.OITW w
        join dbo.OITM i on i.ItemCode=w.ItemCode
        left join dbo.OWHS wh on wh.WhsCode=w.WhsCode
        left join sales s on s.WhsCode=w.WhsCode and s.ItemCode=w.ItemCode
        where w.WhsCode in ({}) and coalesce(i.frozenFor,'N')<>'Y'
        order by w.WhsCode,i.ItemCode
        """.format(placeholders)
        connection = self.connector()
        try:
            cursor = connection.cursor()
            cursor.execute(sql, tuple(store_mapping.keys()))
            columns = [item[0] for item in cursor.description]
            items = []
            for values in cursor.fetchall():
                row = dict(zip(columns, values))
                mapping = store_mapping[str(row["WhsCode"])]
                if isinstance(mapping, str):
                    mapping = {"store_code": mapping, "store_name": mapping}
                items.append({
                    "store_code": mapping.get("store_code"), "store_name": mapping.get("store_name"),
                    "sku_code": str(row["ItemCode"]), "product_name": str(row["ItemName"] or ""),
                    "brand_name": "", "category_name": str(row["ItmsGrpCod"] or ""), "color": "", "size": "",
                    "available_stock": int(Decimal(str(row["AvailableQty"] or 0))),
                    "sales_30d": int(Decimal(str(row["Sales30"] or 0))),
                    "sales_prev_30d": int(Decimal(str(row["SalesPrev30"] or 0))),
                })
            return {
                "batch_id": "core-{}".format(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")),
                "business_date": datetime.now(BUSINESS_TZ).date().isoformat(), "data_as_of": utc_now(),
                "source": "SAP mirror", "rule_input_version": "replenishment-input-v1", "items": items,
            }
        finally:
            connection.close()

    def _query(self, sql, params=()):
        connection = self.connector()
        try:
            cursor = connection.cursor()
            cursor.execute(sql, params)
            columns = [item[0] for item in cursor.description]
            return [
                {key: json_value(value) for key, value in zip(columns, row)}
                for row in cursor.fetchall()
            ]
        finally:
            connection.close()

    def _enrichment(self):
        path = os.environ.get("CORE_OBJECT_ENRICHMENT_FILE", "").strip()
        if not path:
            return {}

        def load():
            try:
                value = json.loads(Path(path).read_text(encoding="utf-8"))
                return value if isinstance(value, dict) else {}
            except (OSError, json.JSONDecodeError):
                return {}

        return self.cache.get_or_build(("enrichment", path), self.reference_ttl, load)

    def _object_result(self, object_type, rows, limit, offset):
        enrichment = self._enrichment().get(object_type, {})
        for row in rows:
            extra = enrichment.get(str(row.get("id")), {}) if isinstance(enrichment, dict) else {}
            if isinstance(extra, dict):
                row.update({key: value for key, value in extra.items() if key not in {"id", "source"}})
            row["source"] = {
                "system": "core.vafox.com",
                "dataset": "SAP Mirror",
                "mode": "read_only",
                "object_type": object_type,
            }
        return {
            "object_type": object_type,
            "offset": offset,
            "limit": limit,
            "returned": len(rows),
            "data_as_of": self.status().get("mirror", {}).get("finished_at"),
            "items": rows,
        }

    def business_objects(self, object_type, limit=50, offset=0, object_id="", allowed_store_ids=None):
        """Return normalized business objects without exposing SAP table names."""
        limit = max(1, min(int(limit), 200))
        offset = max(0, int(offset))
        object_id = str(object_id or "").strip()
        allowed_store_ids = {str(value) for value in (allowed_store_ids or set())}
        cache_key = ("objects", object_type, limit, offset, object_id, tuple(sorted(allowed_store_ids)))

        def build():
            if object_type == "stores":
                rows = self._query(
                    """with sales as (
                      select WhsCode,sum(SalesAmount) Sales90,sum(GrossProfit) GrossProfit90 from (
                        select l.WhsCode,l.LineTotal SalesAmount,l.GrossBuyPr*l.Quantity*-1+l.LineTotal GrossProfit
                        from dbo.OINV h join dbo.INV1 l on l.DocEntry=h.DocEntry
                        where h.CANCELED='N' and h.DocDate>=dateadd(day,-89,cast(getdate() as date))
                        union all
                        select l.WhsCode,-l.LineTotal,-(l.GrossBuyPr*l.Quantity*-1+l.LineTotal)
                        from dbo.ORIN h join dbo.RIN1 l on l.DocEntry=h.DocEntry
                        where h.CANCELED='N' and h.DocDate>=dateadd(day,-89,cast(getdate() as date))
                      ) x group by WhsCode
                    ), stock as (
                      select WhsCode,sum(OnHand) StockQuantity,sum(OnHand*AvgPrice) StockAmount
                      from dbo.OITW group by WhsCode
                    )
                    select w.WhsCode id,w.WhsName name,cast(null as nvarchar(300)) address,
                    coalesce(s.Sales90,0) sales_90d,coalesce(s.GrossProfit90,0) gross_profit_90d,
                    coalesce(i.StockQuantity,0) stock_quantity,coalesce(i.StockAmount,0) stock_amount
                    from dbo.OWHS w left join sales s on s.WhsCode=w.WhsCode
                    left join stock i on i.WhsCode=w.WhsCode
                    order by w.WhsCode offset %s rows fetch next %s rows only""",
                    (offset, limit),
                )
                if object_id:
                    rows = [row for row in rows if str(row.get("id")) == object_id]
                if allowed_store_ids:
                    rows = [row for row in rows if str(row.get("id")) in allowed_store_ids]
                for row in rows:
                    row["employee_ids"] = []
                return self._object_result(object_type, rows, limit, offset)

            if object_type == "products":
                rows = self._query(
                    """with stock as (
                      select ItemCode,sum(OnHand) StockQuantity,sum(OnHand*AvgPrice) StockAmount
                      from dbo.OITW group by ItemCode
                    ), sales as (
                      select ItemCode,sum(Quantity) SalesQuantity90,sum(SalesAmount) SalesAmount90 from (
                        select l.ItemCode,l.Quantity,l.LineTotal SalesAmount from dbo.OINV h
                        join dbo.INV1 l on l.DocEntry=h.DocEntry where h.CANCELED='N'
                        and h.DocDate>=dateadd(day,-89,cast(getdate() as date))
                        union all
                        select l.ItemCode,-l.Quantity,-l.LineTotal from dbo.ORIN h
                        join dbo.RIN1 l on l.DocEntry=h.DocEntry where h.CANCELED='N'
                        and h.DocDate>=dateadd(day,-89,cast(getdate() as date))
                      ) x group by ItemCode
                    )
                    select i.ItemCode id,i.ItemCode sku,i.ItemName name,m.FirmName brand,
                    g.ItmsGrpNam category,coalesce(st.StockQuantity,0) stock_quantity,
                    coalesce(st.StockAmount,0) stock_amount,coalesce(sa.SalesQuantity90,0) sales_quantity_90d,
                    coalesce(sa.SalesAmount90,0) sales_amount_90d,
                    case when coalesce(i.frozenFor,'N')='Y' then 'inactive' else 'active' end lifecycle
                    from dbo.OITM i left join dbo.OMRC m on m.FirmCode=i.FirmCode
                    left join dbo.OITB g on g.ItmsGrpCod=i.ItmsGrpCod
                    left join stock st on st.ItemCode=i.ItemCode left join sales sa on sa.ItemCode=i.ItemCode
                    order by i.ItemCode offset %s rows fetch next %s rows only""",
                    (offset, limit),
                )
            elif object_type == "brands":
                rows = self._query(
                    """with stock as (
                      select i.FirmCode,count(distinct i.ItemCode) ProductCount,sum(w.OnHand) StockQuantity,
                      sum(w.OnHand*w.AvgPrice) StockAmount from dbo.OITM i left join dbo.OITW w on w.ItemCode=i.ItemCode
                      group by i.FirmCode
                    ), sales as (
                      select i.FirmCode,sum(x.SalesAmount) SalesAmount90 from (
                        select l.ItemCode,l.LineTotal SalesAmount from dbo.OINV h join dbo.INV1 l on l.DocEntry=h.DocEntry
                        where h.CANCELED='N' and h.DocDate>=dateadd(day,-89,cast(getdate() as date))
                        union all
                        select l.ItemCode,-l.LineTotal from dbo.ORIN h join dbo.RIN1 l on l.DocEntry=h.DocEntry
                        where h.CANCELED='N' and h.DocDate>=dateadd(day,-89,cast(getdate() as date))
                      ) x join dbo.OITM i on i.ItemCode=x.ItemCode group by i.FirmCode
                    )
                    select cast(m.FirmCode as varchar(40)) id,m.FirmName name,
                    coalesce(st.ProductCount,0) product_count,coalesce(st.StockQuantity,0) stock_quantity,
                    coalesce(st.StockAmount,0) stock_amount,coalesce(sa.SalesAmount90,0) sales_amount_90d,
                    'active' cooperation_status from dbo.OMRC m
                    left join stock st on st.FirmCode=m.FirmCode left join sales sa on sa.FirmCode=m.FirmCode
                    order by m.FirmCode offset %s rows fetch next %s rows only""",
                    (offset, limit),
                )
            elif object_type == "suppliers":
                rows = self._query(
                    """with purchases as (
                      select CardCode,count(*) PurchaseDocuments365,sum(DocTotal) PurchaseAmount365,max(DocDate) LastPurchaseDate
                      from dbo.OPCH where CANCELED='N' and DocDate>=dateadd(day,-364,cast(getdate() as date)) group by CardCode
                    ) select c.CardCode id,c.CardName name,
                    case when coalesce(c.frozenFor,'N')='Y' then 'inactive' else 'active' end cooperation_status,
                    coalesce(p.PurchaseDocuments365,0) purchase_documents_365d,
                    coalesce(p.PurchaseAmount365,0) purchase_amount_365d,p.LastPurchaseDate last_purchase_date
                    from dbo.OCRD c left join purchases p on p.CardCode=c.CardCode where c.CardType='S'
                    order by c.CardCode offset %s rows fetch next %s rows only""",
                    (offset, limit),
                )
            elif object_type == "customers":
                rows = self._query(
                    """with sales as (
                      select CardCode,count(*) PurchaseDocuments365,sum(DocTotal) PurchaseAmount365,max(DocDate) LastPurchaseDate
                      from dbo.OINV where CANCELED='N' and DocDate>=dateadd(day,-364,cast(getdate() as date)) group by CardCode
                    ) select c.CardCode id,c.CardName name,
                    coalesce(s.PurchaseDocuments365,0) purchase_documents_365d,
                    coalesce(s.PurchaseAmount365,0) purchase_amount_365d,s.LastPurchaseDate last_purchase_date
                    from dbo.OCRD c left join sales s on s.CardCode=c.CardCode where c.CardType='C'
                    order by c.CardCode offset %s rows fetch next %s rows only""",
                    (offset, limit),
                )
            else:
                raise ValueError("unsupported business object")
            if object_id:
                rows = [row for row in rows if str(row.get("id")) == object_id]
            return self._object_result(object_type, rows, limit, offset)

        ttl = self.reference_ttl if object_type in {"brands", "suppliers"} else self.metrics_ttl
        return self.cache.get_or_build(cache_key, ttl, build)

    def customer_purchases(self, customer_id, limit=200):
        """Return one customer's purchases from the read-only mirror."""
        customer_id = str(customer_id or "").strip()
        if not customer_id or len(customer_id) > 100:
            raise ValueError("customer id is required")
        limit = max(1, min(int(limit), 500))
        rows = self._query(
            """with purchases as (
              select concat('OINV:',h.DocEntry,':',l.LineNum) purchase_key,
              l.ItemCode sku,i.ItemName product_name,m.FirmName brand_name,
              h.DocDate purchase_date,cast(l.Quantity as decimal(19,4)) quantity,
              cast(l.LineTotal as decimal(19,4)) amount,'invoice' source_document
              from dbo.OINV h join dbo.INV1 l on l.DocEntry=h.DocEntry
              left join dbo.OITM i on i.ItemCode=l.ItemCode
              left join dbo.OMRC m on m.FirmCode=i.FirmCode
              where h.CANCELED='N' and h.CardCode=%s
              union all
              select concat('ORIN:',h.DocEntry,':',l.LineNum),
              l.ItemCode,i.ItemName,m.FirmName,h.DocDate,
              -cast(l.Quantity as decimal(19,4)),-cast(l.LineTotal as decimal(19,4)),'return'
              from dbo.ORIN h join dbo.RIN1 l on l.DocEntry=h.DocEntry
              left join dbo.OITM i on i.ItemCode=l.ItemCode
              left join dbo.OMRC m on m.FirmCode=i.FirmCode
              where h.CANCELED='N' and h.CardCode=%s
            ) select purchase_key,sku,product_name,brand_name,purchase_date,quantity,amount,source_document
            from purchases order by purchase_date desc,purchase_key
            offset 0 rows fetch next %s rows only""",
            (customer_id, customer_id, limit),
        )
        return {
            "customer_id": customer_id,
            "returned": len(rows),
            "data_as_of": self.status().get("mirror", {}).get("finished_at"),
            "source": {"system": "core.vafox.com", "dataset": "SAP Mirror", "mode": "read_only"},
            "items": rows,
        }

    def explorer_customer_match(self, phone_hash, hmac_secret, limit=500):
        """Match one verified phone without returning a customer directory."""
        phone_hash = str(phone_hash or "").strip().lower()
        if not re.fullmatch(r"[0-9a-f]{64}", phone_hash):
            raise ValueError("invalid phone hash")
        secret = str(hmac_secret or "").encode("utf-8")
        if len(secret) < 16:
            raise ValueError("invalid service credential")
        rows = self._query(
            """select CardCode id,CardName name,Phone1 phone,Cellular mobile
            from dbo.OCRD where CardType='C'"""
        )
        for row in rows:
            for field in ("phone", "mobile"):
                digits = "".join(character for character in str(row.get(field) or "") if character.isdigit())
                if digits.startswith("86") and len(digits) == 13:
                    digits = digits[2:]
                if len(digits) != 11 or not digits.startswith("1"):
                    continue
                candidate = hmac.new(secret, digits.encode("utf-8"), hashlib.sha256).hexdigest()
                if hmac.compare_digest(candidate, phone_hash):
                    purchases = self.customer_purchases(str(row["id"]), limit)
                    return {
                        "matched": True,
                        "customer": {"id": row["id"], "name": row.get("name") or ""},
                        "data_as_of": purchases["data_as_of"],
                        "source": purchases["source"],
                        "items": purchases["items"],
                    }
        return {
            "matched": False, "customer": None, "items": [],
            "data_as_of": self.status().get("mirror", {}).get("finished_at"),
            "source": {"system": "core.vafox.com", "dataset": "SAP Mirror", "mode": "read_only"},
        }

    def public_objects(self, object_type):
        enrichment = self._enrichment().get(object_type, {})
        if object_type not in {"stores", "brands"}:
            raise PermissionError("object is not public")
        result = self.business_objects(object_type, 200, 0)
        public_fields = {"id", "name", "address", "description", "public_status", "source"}
        result["items"] = [
            {key: value for key, value in item.items() if key in public_fields}
            for item in result["items"]
            if isinstance(enrichment, dict)
            and enrichment.get(str(item.get("id")), {}).get("public") is True
        ]
        result["returned"] = len(result["items"])
        return result

    def business_summary(self):
        def build():
            rows = self._query(
                """with dates as (
                  select max(DocDate) DataDate from dbo.OINV where CANCELED='N'
                ), sales as (
                  select sum(SalesAmount) SalesAmount,sum(GrossProfit) GrossProfit from (
                    select l.LineTotal SalesAmount,l.LineTotal-l.GrossBuyPr*l.Quantity GrossProfit
                    from dbo.OINV h join dbo.INV1 l on l.DocEntry=h.DocEntry cross join dates d
                    where h.CANCELED='N' and year(h.DocDate)=year(d.DataDate)
                    union all
                    select -l.LineTotal,-(l.LineTotal-l.GrossBuyPr*l.Quantity)
                    from dbo.ORIN h join dbo.RIN1 l on l.DocEntry=h.DocEntry cross join dates d
                    where h.CANCELED='N' and year(h.DocDate)=year(d.DataDate)
                  ) x
                ), stock as (
                  select sum(OnHand) StockQuantity,sum(OnHand*AvgPrice) StockAmount from dbo.OITW
                ) select d.DataDate data_date,coalesce(s.SalesAmount,0) sales_amount,
                coalesce(s.GrossProfit,0) gross_profit,coalesce(i.StockQuantity,0) stock_quantity,
                coalesce(i.StockAmount,0) stock_amount from dates d cross join sales s cross join stock i"""
            )
            summary = rows[0] if rows else {}
            summary.update({
                "top_stores": self.business_objects("stores", 12, 0)["items"],
                "top_brands": self.business_objects("brands", 20, 0)["items"],
                "source": {"system": "core.vafox.com", "dataset": "SAP Mirror", "mode": "read_only"},
                "data_as_of": self.status().get("mirror", {}).get("finished_at"),
            })
            return summary

        return self.cache.get_or_build("business_summary", self.metrics_ttl, build)

    def data_health(self):
        def build():
            status = self.status()
            mirror = status.get("mirror", {})
            counts = self._query(
                """select (select count(*) from dbo.OWHS) stores,
                (select count(*) from dbo.OITM) products,(select count(*) from dbo.OMRC) brands,
                (select count(*) from dbo.OCRD where CardType='S') suppliers,
                (select count(*) from dbo.OCRD where CardType='C') customers"""
            )
            problems = []
            if mirror.get("status") != "completed":
                problems.append("mirror_not_completed")
            if mirror.get("failed_tables", 0):
                problems.append("mirror_has_failed_tables")
            return {
                "status": "healthy" if not problems else "attention",
                "checked_at": utc_now(),
                "data_as_of": mirror.get("finished_at"),
                "mirror": mirror,
                "object_counts": counts[0] if counts else {},
                "problems": problems,
                "source": {"system": "core.vafox.com", "mode": "read_only"},
            }

        return self.cache.get_or_build("data_health", min(self.metrics_ttl, 60), build)


class CoreApiHandler(BaseHTTPRequestHandler):
    server_version = "VAFOXCore/1.0"

    def log_message(self, fmt, *args):
        print(json.dumps({"at": utc_now(), "client": self.client_address[0], "message": fmt % args}, ensure_ascii=True))

    def _token(self):
        header = self.headers.get("Authorization", "")
        return header[7:].strip() if header.lower().startswith("bearer ") else ""

    def _reply_html(self, status, html):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _reply(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _authorized(self, scope):
        principal = self.server.policy.authorize(self._token(), scope)
        if not principal:
            self._reply(401, {"error": "unauthorized"})
        return principal

    def _authorized_any(self, *scopes):
        for scope in scopes:
            principal = self.server.policy.authorize(self._token(), scope)
            if principal:
                return principal
        self._reply(401, {"error": "unauthorized"})
        return None

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path in ("/", "/ui"):
                runtime = version_payload("core")
                html = """<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Enterprise Data Hub</title><style>body{margin:0;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Microsoft YaHei,sans-serif;background:#f5f7f5;color:#14231d}.hero{background:#14382c;color:white;padding:56px max(24px,calc((100% - 1100px)/2))}.hero p{color:#d8e7df;max-width:760px}.wrap{width:min(1100px,calc(100% - 32px));margin:28px auto;display:grid;gap:18px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.card{background:white;border:1px solid #d9e0dc;border-radius:16px;padding:22px}.card b{display:block;font-size:24px;margin-top:10px;color:#176443}.list{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}.pill{display:inline-flex;border-radius:999px;background:#dfeee7;color:#176443;padding:6px 10px;font-weight:800;font-size:12px}@media(max-width:760px){.grid,.list{grid-template-columns:1fr}}</style></head><body><section class='hero'><span class='pill'>Admin Only · Enterprise Data Hub</span><h1>Enterprise Data Hub</h1><p>Admin-only enterprise data center for business systems integration, master data, identity, enterprise events, memory, digital twin, APIs, synchronization, data health, and permission. No dashboards and no business pages.</p></section><main class='wrap'><section class='grid'><article class='card'>Business Systems<b>Integration · Master Data</b></article><article class='card'>Enterprise Events<b>Sync · Memory · Audit</b></article><article class='card'>Digital Twin<b>Read-only SAP Mirror</b></article><article class='card'>API + Permission<b>/api/health</b></article></section><section class='list'><article class='card'><h2>Governance</h2><p>RBAC / ABAC / audit controls remain unchanged through token scopes and read-only endpoints.</p></article><article class='card'><h2>No duplicate source</h2><p>Enterprise Data Hub preserves the existing SAP mirror, permissions, APIs, and synchronization. Business capabilities are not rebuilt.</p></article></section><footer style="padding:24px;text-align:center;color:#476256">Powered by VAFOX Intelligence Engine · Build: __BUILD_TIME__ · Commit: __COMMIT__</footer></main></body></html>""".replace("__BUILD_TIME__", runtime["build_time"]).replace("__COMMIT__", runtime["commit"])
                return self._reply_html(200, html)
            if parsed.path in ("/version", "/health/version"):
                return self._reply(200, version_payload("core"))
            if parsed.path == "/health/runtime":
                return self._reply(200, runtime_payload("core"))
            if parsed.path == "/health":
                checks = {"process": {"status": "healthy"}, "database": {"status": "healthy"}, "dependencies": {"status": "healthy", "sap_mirror": self.server.service.status().get("mirror", {})}}
                return self._reply(200, health_payload("foxbrain-core", checks))
            if parsed.path in ("/healthz",):
                if self.client_address[0] not in ("127.0.0.1", "::1"):
                    return self._reply(404, {"error": "not_found"})
                return self._reply(200, {"status": "ok"})
            if parsed.path == "/api/health":
                if not self._authorized("facts:read"):
                    return
                return self._reply(200, self.server.service.status())
            if parsed.path == "/api/v1/status":
                if not self._authorized("facts:read"):
                    return
                return self._reply(200, self.server.service.status())
            if parsed.path == "/api/v1/public/status":
                if not self._authorized("public:read"):
                    return
                status = self.server.service.status()
                return self._reply(200, {
                    "service": status["service"], "mode": status["mode"],
                    "status": status["mirror"]["status"], "checked_at": status["checked_at"],
                })
            match = re.fullmatch(r"/api/v1/public/(stores|brands)", parsed.path)
            if match:
                if not self._authorized("public:read"):
                    return
                return self._reply(200, self.server.service.public_objects(match.group(1)))
            if parsed.path == "/api/v1/data-health":
                if not self._authorized_any("health:read", "facts:read"):
                    return
                return self._reply(200, self.server.service.data_health())
            if parsed.path == "/api/v1/business/summary":
                if not self._authorized_any("objects:read", "facts:read"):
                    return
                return self._reply(200, self.server.service.business_summary())
            if parsed.path == "/api/v1/explorer/customer-match":
                if not self._authorized("explorer:match"):
                    return
                query = parse_qs(parsed.query)
                return self._reply(200, self.server.service.explorer_customer_match(
                    query.get("phone_hash", [""])[0], self._token(),
                    int(query.get("limit", [500])[0]),
                ))
            match = re.fullmatch(r"/api/v1/objects/customers/([^/]+)/purchases", parsed.path)
            if match:
                if not self._authorized("customers:read"):
                    return
                query = parse_qs(parsed.query)
                return self._reply(200, self.server.service.customer_purchases(
                    unquote(match.group(1)), int(query.get("limit", [200])[0])
                ))
            match = re.fullmatch(r"/api/v1/objects/(stores|products|brands|suppliers|customers)", parsed.path)
            if match:
                object_type = match.group(1)
                if object_type == "customers":
                    principal = self._authorized("customers:read")
                else:
                    principal = self._authorized_any("objects:read", "facts:read")
                if not principal:
                    return
                query = parse_qs(parsed.query)
                allowed_store_ids = set()
                if principal.get("role") == "store_manager":
                    allowed_store_ids = principal.get("store_ids", set())
                    if object_type != "stores" or not allowed_store_ids:
                        return self._reply(403, {"error": "scope_forbidden"})
                return self._reply(200, self.server.service.business_objects(
                    object_type,
                    int(query.get("limit", [50])[0]),
                    int(query.get("offset", [0])[0]),
                    "",
                    allowed_store_ids,
                ))
            if parsed.path == "/api/v1/tables":
                if not self._authorized("raw:read"):
                    return
                return self._reply(200, {"tables": self.server.service.tables()})
            if parsed.path == "/api/v1/operation/snapshot":
                if not self._authorized("facts:read"):
                    return
                query = parse_qs(parsed.query)
                return self._reply(200, self.server.service.operation_snapshot(
                    query.get("store", [""])[0], query.get("as_of", [utc_now()[:10]])[0]
                ))
            if parsed.path == "/api/v1/replenishment/input":
                if not self._authorized("facts:read"):
                    return
                return self._reply(200, self.server.service.replenishment_input())
            match = re.fullmatch(r"/api/v1/tables/([^/]+)/([^/]+)/rows", parsed.path)
            if match:
                if not self._authorized("raw:read"):
                    return
                query = parse_qs(parsed.query)
                result = self.server.service.rows(
                    match.group(1), match.group(2),
                    int(query.get("limit", [50])[0]), int(query.get("offset", [0])[0]),
                )
                return self._reply(200, result)
            return self._reply(404, {"error": "not_found"})
        except (ValueError, PermissionError) as exc:
            return self._reply(400, {"error": str(exc)})
        except Exception:
            return self._reply(503, {"error": "data_core_unavailable"})

    def _read_only(self):
        self._reply(405, {"error": "read_only_api"})

    do_POST = _read_only
    do_PUT = _read_only
    do_PATCH = _read_only
    do_DELETE = _read_only


def create_server(host=None, port=None, service=None, policy=None):
    token_config = os.environ.get("CORE_API_TOKENS_JSON", "{}")
    token_file = os.environ.get("CORE_API_TOKENS_FILE")
    if token_file:
        token_config = Path(token_file).read_text(encoding="utf-8")
    server = ThreadingHTTPServer(
        (host or os.environ.get("CORE_API_HOST", "127.0.0.1"), int(port or os.environ.get("CORE_API_PORT", "8090"))),
        CoreApiHandler,
    )
    server.service = service or CoreService()
    server.policy = policy or TokenPolicy(token_config)
    return server


def main():
    create_server().serve_forever()


if __name__ == "__main__":
    main()
