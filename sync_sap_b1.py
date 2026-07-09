import os
import json
import sqlite3
import traceback
import time
from datetime import date
from decimal import Decimal

import psycopg2
import pytds
from dotenv import load_dotenv
from psycopg2.extras import execute_values


BASE = os.getenv("SAP_SYNC_BASE", "/opt/firefox-sap-sync")
SUMMARY_FILE = os.getenv("SAP_SUMMARY_FILE", os.path.join(BASE, "latest_summary.json"))
load_dotenv(os.path.join(BASE, ".env"))

SAP = {k: os.getenv(k) for k in ["SAP_HOST", "SAP_DB", "SAP_USER", "SAP_PASSWORD"]}
SAP_PORT = int(os.getenv("SAP_PORT", "1433"))
PG = {
    "host": os.getenv("PG_HOST") or os.getenv("POSTGRES_HOST") or "postgres",
    "port": int(os.getenv("PG_PORT") or os.getenv("POSTGRES_PORT") or "5432"),
    "dbname": os.getenv("PG_DB") or os.getenv("POSTGRES_DB"),
    "user": os.getenv("PG_USER") or os.getenv("POSTGRES_USER"),
    "password": os.getenv("PG_PASSWORD") or os.getenv("POSTGRES_PASSWORD"),
}
APP_DIR = os.getenv("APP_DIR", "/data/firefox-portal")
PORTAL_DB = os.getenv("PORTAL_DB", os.path.join(APP_DIR, "portal.db"))


def U(s):
    return s.encode("ascii").decode("unicode_escape")


def pg_conn():
    missing = [k for k, v in PG.items() if k != "port" and not v]
    if missing:
        raise RuntimeError("Missing PostgreSQL config: " + ", ".join(missing))
    return psycopg2.connect(**PG)


def write_portal_sync_history(status, started_at, finished_at, counts=None, error=""):
    try:
        os.makedirs(APP_DIR, exist_ok=True)
        conn = sqlite3.connect(PORTAL_DB)
        conn.execute(
            """
create table if not exists sap_sync_history(
 id integer primary key autoincrement,
 sync_id text unique,
 job_name text not null default 'sap_b1_sync',
 trigger_type text,
 status text,
 started_at integer,
 finished_at integer,
 duration_seconds integer,
 records_read integer,
 records_written integer,
 records_updated integer,
 records_failed integer,
 error_message text,
 log_path text,
 created_by integer
)
"""
        )
        total = sum(int(v or 0) for v in (counts or {}).values())
        sync_id = "SAP-" + str(int(started_at))
        conn.execute(
            "insert or replace into sap_sync_history(sync_id,job_name,trigger_type,status,started_at,finished_at,duration_seconds,records_read,records_written,records_updated,records_failed,error_message,log_path,created_by) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (sync_id, "sap_b1_sync", os.getenv("SAP_SYNC_TRIGGER", "scheduled"), status, int(started_at), int(finished_at), int(finished_at - started_at), total, total, 0, 0 if status == "success" else 1, error[:1000], "", None),
        )
        conn.commit()
        conn.close()
    except Exception as exc:
        print("PORTAL_SYNC_HISTORY_FAILED", str(exc)[:300])


def sap_conn():
    return pytds.connect(
        server=SAP["SAP_HOST"],
        port=SAP_PORT,
        user=SAP["SAP_USER"],
        password=SAP["SAP_PASSWORD"],
        database=SAP["SAP_DB"],
        timeout=60,
        login_timeout=15,
        autocommit=True,
        validate_host=False,
    )


def as_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return float(value or 0)


def as_date(value):
    if isinstance(value, date):
        return value.isoformat()
    return str(value or "")


def write_summary(conn):
    cur = conn.cursor()
    cur.execute(
        """
select sales_date, sales_amount, gross_profit
from sap_daily_sales_summary
where sales_date = (select max(sales_date) from sap_daily_sales_summary)
"""
    )
    latest = cur.fetchone()
    data_date = latest[0] if latest else None
    yesterday_sales = as_float(latest[1]) if latest else 0
    yesterday_gross_profit = as_float(latest[2]) if latest else 0
    yesterday_gross_margin = (yesterday_gross_profit / yesterday_sales * 100) if yesterday_sales else 0

    month_sales = 0
    month_gross_profit = 0
    top_stores = []
    if data_date:
        cur.execute(
            """
select coalesce(sum(sales_amount),0), coalesce(sum(gross_profit),0)
from sap_daily_sales_summary
where date_trunc('month', sales_date) = date_trunc('month', %s::date)
""",
            (data_date,),
        )
        month = cur.fetchone()
        month_sales = as_float(month[0])
        month_gross_profit = as_float(month[1])
        cur.execute(
            """
select whs_code, coalesce(sum(sales_amount),0), coalesce(sum(gross_profit),0)
from sap_store_sales_summary
where date_trunc('month', sales_date) = date_trunc('month', %s::date)
group by whs_code
order by coalesce(sum(sales_amount),0) desc
limit 8
""",
            (data_date,),
        )
        top_stores = [
            {"store": row[0] or "未分仓库", "sales": as_float(row[1]), "gross_profit": as_float(row[2])}
            for row in cur.fetchall()
        ]

    cur.execute("select coalesce(sum(on_hand * avg_price),0) from sap_stock_by_whs where on_hand > 0")
    inventory_amount = as_float(cur.fetchone()[0])
    cur.execute("select count(*) from sap_stock_by_whs where on_hand > 20 and coalesce(is_commited,0) = 0")
    risk_count = int(cur.fetchone()[0] or 0)

    month_target = float(os.getenv("MONTH_TARGET", "900000"))
    completion_rate = (month_sales / month_target * 100) if month_target else 0
    suggestions = [
        f"本月销售完成率 {completion_rate:.1f}%，今天先看排名靠前门店的差距和毛利。",
        f"昨日毛利率 {yesterday_gross_margin:.1f}%，低毛利单据要优先复盘折扣和品类结构。",
        "库存风险数量较高时，先按门店、品牌、尺码三层拆解，找出可调拨和可促销商品。",
        "店长晨会建议围绕昨日销售、今日目标、重点会员、库存提醒四件事展开。",
    ]
    todos = [
        "确认昨日各门店销售与毛利异常项。",
        "检查 SAP B1 每晚 22:00 自动同步是否成功。",
        "把今日重点商品和会员跟进任务发给店长。",
    ]
    summary = {
        "data_date": as_date(data_date),
        "yesterday_sales": yesterday_sales,
        "yesterday_gross_profit": yesterday_gross_profit,
        "yesterday_gross_margin": yesterday_gross_margin,
        "month_sales": month_sales,
        "month_gross_profit": month_gross_profit,
        "month_target": month_target,
        "completion_rate": completion_rate,
        "inventory_amount": inventory_amount,
        "risk_count": risk_count,
        "top_stores": top_stores,
        "ai_suggestions": suggestions,
        "todos": todos,
    }
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("SAP_SUMMARY_WRITTEN", SUMMARY_FILE)


def init_pg(conn):
    cur = conn.cursor()
    cur.execute(
        """
CREATE TABLE IF NOT EXISTS sap_sync_runs (
 id bigserial PRIMARY KEY, started_at timestamptz DEFAULT now(), finished_at timestamptz,
 source_host text, source_db text, status text, message text
);
CREATE TABLE IF NOT EXISTS sap_customers (
 card_code text PRIMARY KEY, card_name text, card_type text, group_code int, phone1 text, cellular text,
 balance numeric, credit_line numeric, create_date date, update_date date
);
CREATE TABLE IF NOT EXISTS sap_items (
 item_code text PRIMARY KEY, item_name text, item_group int, code_bars text,
 on_hand numeric, is_commited numeric, on_order numeric, buy_unit text, sale_unit text
);
CREATE TABLE IF NOT EXISTS sap_warehouses (
 whs_code text PRIMARY KEY, whs_name text, location int, inactive text
);
CREATE TABLE IF NOT EXISTS sap_salespersons (
 slp_code int PRIMARY KEY, slp_name text, active text, memo text
);
CREATE TABLE IF NOT EXISTS sap_stock_by_whs (
 item_code text, whs_code text, on_hand numeric, is_commited numeric, on_order numeric, avg_price numeric,
 PRIMARY KEY (item_code, whs_code)
);
CREATE TABLE IF NOT EXISTS sap_sales_invoices (
 doc_entry int PRIMARY KEY, doc_num int, canceled text, doc_status text, doc_date date,
 card_code text, card_name text, doc_total numeric, paid_to_date numeric, gross_profit numeric,
 slp_code int, comments text, create_date date, update_date date
);
CREATE TABLE IF NOT EXISTS sap_sales_invoice_lines (
 doc_entry int, line_num int, item_code text, description text, quantity numeric, price numeric,
 disc_prcnt numeric, line_total numeric, gross_buy_price numeric, gross_profit numeric,
 whs_code text, slp_code int, doc_date date,
 PRIMARY KEY (doc_entry,line_num)
);
CREATE TABLE IF NOT EXISTS sap_purchase_orders (
 doc_entry int PRIMARY KEY, doc_num int, canceled text, doc_status text, doc_date date,
 card_code text, card_name text, doc_total numeric, slp_code int, comments text
);
CREATE TABLE IF NOT EXISTS sap_daily_sales_summary (
 sales_date date PRIMARY KEY, invoice_count int, sales_amount numeric, gross_profit numeric,
 updated_at timestamptz DEFAULT now()
);
CREATE TABLE IF NOT EXISTS sap_store_sales_summary (
 sales_date date, whs_code text, line_count int, quantity numeric, sales_amount numeric, gross_profit numeric,
 PRIMARY KEY (sales_date, whs_code)
);
"""
    )
    conn.commit()


def table_cols(cur, table):
    cur.execute(
        "select lower(COLUMN_NAME) from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME=%s",
        (table,),
    )
    return {row[0] for row in cur.fetchall()}


def col_expr(existing, col, alias):
    if col.lower() in existing:
        return f"[{col}] as [{alias}]"
    return f"NULL as [{alias}]"


def fetch_table(cur, table, cols, where=""):
    existing = table_cols(cur, table)
    select = ", ".join(col_expr(existing, col, alias) for col, alias in cols)
    cur.execute(f"select {select} from dbo.[{table}] {where}")
    return cur.fetchall()


def replace_table(pg, table, columns, rows):
    cur = pg.cursor()
    cur.execute(f"TRUNCATE TABLE {table}")
    if rows:
        template = "(" + ",".join(["%s"] * len(columns)) + ")"
        execute_values(
            cur,
            f"INSERT INTO {table} ({','.join(columns)}) VALUES %s",
            rows,
            template=template,
            page_size=2000,
        )
    pg.commit()
    return len(rows)


def main():
    started_at = time.time()
    pg = pg_conn()
    init_pg(pg)
    pc = pg.cursor()
    pc.execute(
        "insert into sap_sync_runs(source_host, source_db, status) values(%s,%s,'running') returning id",
        (SAP["SAP_HOST"], SAP["SAP_DB"]),
    )
    run_id = pc.fetchone()[0]
    pg.commit()
    counts = {}
    try:
        sap = sap_conn()
        sc = sap.cursor()
        counts["customers"] = replace_table(
            pg,
            "sap_customers",
            [
                "card_code",
                "card_name",
                "card_type",
                "group_code",
                "phone1",
                "cellular",
                "balance",
                "credit_line",
                "create_date",
                "update_date",
            ],
            fetch_table(
                sc,
                "OCRD",
                [
                    ("CardCode", "card_code"),
                    ("CardName", "card_name"),
                    ("CardType", "card_type"),
                    ("GroupCode", "group_code"),
                    ("Phone1", "phone1"),
                    ("Cellular", "cellular"),
                    ("Balance", "balance"),
                    ("CreditLine", "credit_line"),
                    ("CreateDate", "create_date"),
                    ("UpdateDate", "update_date"),
                ],
            ),
        )
        counts["items"] = replace_table(
            pg,
            "sap_items",
            [
                "item_code",
                "item_name",
                "item_group",
                "code_bars",
                "on_hand",
                "is_commited",
                "on_order",
                "buy_unit",
                "sale_unit",
            ],
            fetch_table(
                sc,
                "OITM",
                [
                    ("ItemCode", "item_code"),
                    ("ItemName", "item_name"),
                    ("ItmsGrpCod", "item_group"),
                    ("CodeBars", "code_bars"),
                    ("OnHand", "on_hand"),
                    ("IsCommited", "is_commited"),
                    ("OnOrder", "on_order"),
                    ("BuyUnitMsr", "buy_unit"),
                    ("SalUnitMsr", "sale_unit"),
                ],
            ),
        )
        counts["warehouses"] = replace_table(
            pg,
            "sap_warehouses",
            ["whs_code", "whs_name", "location", "inactive"],
            fetch_table(
                sc,
                "OWHS",
                [
                    ("WhsCode", "whs_code"),
                    ("WhsName", "whs_name"),
                    ("Location", "location"),
                    ("Inactive", "inactive"),
                ],
            ),
        )
        counts["salespersons"] = replace_table(
            pg,
            "sap_salespersons",
            ["slp_code", "slp_name", "active", "memo"],
            fetch_table(
                sc,
                "OSLP",
                [
                    ("SlpCode", "slp_code"),
                    ("SlpName", "slp_name"),
                    ("Active", "active"),
                    ("Memo", "memo"),
                ],
            ),
        )
        counts["stock_by_whs"] = replace_table(
            pg,
            "sap_stock_by_whs",
            ["item_code", "whs_code", "on_hand", "is_commited", "on_order", "avg_price"],
            fetch_table(
                sc,
                "OITW",
                [
                    ("ItemCode", "item_code"),
                    ("WhsCode", "whs_code"),
                    ("OnHand", "on_hand"),
                    ("IsCommited", "is_commited"),
                    ("OnOrder", "on_order"),
                    ("AvgPrice", "avg_price"),
                ],
            ),
        )
        counts["sales_invoices"] = replace_table(
            pg,
            "sap_sales_invoices",
            [
                "doc_entry",
                "doc_num",
                "canceled",
                "doc_status",
                "doc_date",
                "card_code",
                "card_name",
                "doc_total",
                "paid_to_date",
                "gross_profit",
                "slp_code",
                "comments",
                "create_date",
                "update_date",
            ],
            fetch_table(
                sc,
                "OINV",
                [
                    ("DocEntry", "doc_entry"),
                    ("DocNum", "doc_num"),
                    ("CANCELED", "canceled"),
                    ("DocStatus", "doc_status"),
                    ("DocDate", "doc_date"),
                    ("CardCode", "card_code"),
                    ("CardName", "card_name"),
                    ("DocTotal", "doc_total"),
                    ("PaidToDate", "paid_to_date"),
                    ("GrosProfit", "gross_profit"),
                    ("SlpCode", "slp_code"),
                    ("Comments", "comments"),
                    ("CreateDate", "create_date"),
                    ("UpdateDate", "update_date"),
                ],
            ),
        )
        counts["sales_invoice_lines"] = replace_table(
            pg,
            "sap_sales_invoice_lines",
            [
                "doc_entry",
                "line_num",
                "item_code",
                "description",
                "quantity",
                "price",
                "disc_prcnt",
                "line_total",
                "gross_buy_price",
                "gross_profit",
                "whs_code",
                "slp_code",
                "doc_date",
            ],
            fetch_table(
                sc,
                "INV1",
                [
                    ("DocEntry", "doc_entry"),
                    ("LineNum", "line_num"),
                    ("ItemCode", "item_code"),
                    ("Dscription", "description"),
                    ("Quantity", "quantity"),
                    ("Price", "price"),
                    ("DiscPrcnt", "disc_prcnt"),
                    ("LineTotal", "line_total"),
                    ("GrossBuyPr", "gross_buy_price"),
                    ("GrssProfit", "gross_profit"),
                    ("WhsCode", "whs_code"),
                    ("SlpCode", "slp_code"),
                    ("DocDate", "doc_date"),
                ],
            ),
        )
        counts["purchase_orders"] = replace_table(
            pg,
            "sap_purchase_orders",
            [
                "doc_entry",
                "doc_num",
                "canceled",
                "doc_status",
                "doc_date",
                "card_code",
                "card_name",
                "doc_total",
                "slp_code",
                "comments",
            ],
            fetch_table(
                sc,
                "OPOR",
                [
                    ("DocEntry", "doc_entry"),
                    ("DocNum", "doc_num"),
                    ("CANCELED", "canceled"),
                    ("DocStatus", "doc_status"),
                    ("DocDate", "doc_date"),
                    ("CardCode", "card_code"),
                    ("CardName", "card_name"),
                    ("DocTotal", "doc_total"),
                    ("SlpCode", "slp_code"),
                    ("Comments", "comments"),
                ],
            ),
        )
        pc = pg.cursor()
        pc.execute("TRUNCATE TABLE sap_daily_sales_summary")
        pc.execute(
            """
insert into sap_daily_sales_summary(sales_date, invoice_count, sales_amount, gross_profit)
select doc_date, count(*), coalesce(sum(doc_total),0), coalesce(sum(gross_profit),0)
from sap_sales_invoices where coalesce(canceled,'N')='N' group by doc_date
"""
        )
        pc.execute("TRUNCATE TABLE sap_store_sales_summary")
        pc.execute(
            """
insert into sap_store_sales_summary(sales_date, whs_code, line_count, quantity, sales_amount, gross_profit)
select doc_date, coalesce(whs_code,''), count(*), coalesce(sum(quantity),0), coalesce(sum(line_total),0), coalesce(sum(gross_profit),0)
from sap_sales_invoice_lines group by doc_date, coalesce(whs_code,'')
"""
        )
        pc.execute(
            "update sap_sync_runs set finished_at=now(), status='success', message=%s where id=%s",
            (str(counts), run_id),
        )
        write_summary(pg)
        pg.commit()
        write_portal_sync_history("success", started_at, time.time(), counts)
        sap.close()
        print("SAP_SYNC_SUCCESS", counts)
    except Exception:
        pg.rollback()
        msg = traceback.format_exc()
        pc = pg.cursor()
        pc.execute(
            "update sap_sync_runs set finished_at=now(), status='failed', message=%s where id=%s",
            (msg[:3000], run_id),
        )
        pg.commit()
        write_portal_sync_history("failed", started_at, time.time(), counts, msg)
        print("SAP_SYNC_FAILED", msg)
        raise
    finally:
        pg.close()


if __name__ == "__main__":
    main()
