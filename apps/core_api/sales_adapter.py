"""Read-only adapter from the SAP sync sales projection to the Core contract."""
from __future__ import annotations

from datetime import datetime, timezone


REQUIRED_EVIDENCE_FIELDS = frozenset(("source", "timestamp", "version", "confidence"))


class SalesDomainAdapter:
    """Expose line-level sales facts stored by the SAP mirror sync.

    The adapter owns no connection and performs no mutations.  Keeping this
    projection separate from the SAP B1 document tables makes the source
    boundary explicit: SAP B1 -> SAP Mirror/sap_sync -> Core Sales Domain.
    """

    VERSION = "sales-domain-v1"
    SOURCE = "sap_sync.sap_sales_orders"

    def __init__(self, query, timestamp):
        self.query = query
        self.timestamp = timestamp

    def read(self, store_ids=(), limit=100):
        limit = max(1, min(int(limit), 200))
        allowed_stores = {str(store) for store in store_ids}
        rows = self.query(
            """select top %s cast(o.order_id as varchar(64)) order_id,o.store,
            l.sku,cast(l.quantity as decimal(19,4)) quantity,
            cast(l.amount as decimal(19,4)) amount,cast(l.margin as decimal(19,4)) margin,
            o.order_date date
            from dbo.sap_sales_orders o
            join dbo.sap_sales_order_lines l on l.order_id=o.order_id
            where coalesce(o.is_cancelled,0)=0
            order by o.order_date desc,o.order_id desc,l.line_number asc""",
            (limit,),
        )
        data = [
            {key: row.get(key) for key in ("order_id", "store", "sku", "quantity", "amount", "margin", "date")}
            for row in rows if not allowed_stores or str(row.get("store")) in allowed_stores
        ]
        return {
            "data": data,
            "source": self.SOURCE,
            "timestamp": self.timestamp() or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "version": self.VERSION,
            "confidence": 0.95,
            "mode": "read_only",
        }
