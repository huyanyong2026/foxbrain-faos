"""Read-only SAP Mirror projections for the FoxBrain Core data contract.

The adapter is deliberately given read functions rather than a database
connection. This keeps SAP_MIRROR as the only data source and prevents this
boundary from acquiring any write capability.
"""
from __future__ import annotations


class SAPMirrorAdapter:
    """Project SAP_MIRROR Product, Sales, Inventory, Customer and Supplier facts."""

    SOURCE = "sap_mirror"
    VERSION = "sap-mirror-core-v1"
    CONFIDENCE = 0.95

    def __init__(self, query, objects, timestamp, sales_reader):
        self.query, self.objects = query, objects
        self.timestamp, self.sales_reader = timestamp, sales_reader

    def _envelope(self, data):
        return {"data": data, "source": self.SOURCE, "timestamp": self.timestamp(),
                "version": self.VERSION, "confidence": self.CONFIDENCE, "mode": "read_only"}

    def read(self, domain, store_ids=(), limit=100):
        limit = max(1, min(int(limit), 200))
        domain = {"products": "product", "customers": "customer", "suppliers": "supplier"}.get(domain, domain)
        stores = {str(value) for value in store_ids}
        if domain == "sales":
            return self._envelope(self.sales_reader(stores, limit)["data"])
        if domain == "product":
            rows = self.objects("products", limit, 0)["items"]
            return self._envelope([{"product_id": row.get("id"), "sku": row.get("sku", row.get("id")), "name": row.get("name"), "brand": row.get("brand"), "category": row.get("category"), "cost": row.get("avg_cost", row.get("stock_amount")), "price": row.get("price"), "status": row.get("status", "active"), "lifecycle": row.get("lifecycle", "active")} for row in rows])
        if domain == "stores":
            rows = self.objects("stores", limit, 0, "", stores)["items"]
            return self._envelope([{"store_id": row.get("id"), "name": row.get("name"), "region": row.get("region"), "sales": row.get("sales_90d"), "target": row.get("target")} for row in rows])
        if domain == "customer":
            rows = self.objects("customers", limit, 0)["items"]
            return self._envelope([{"customer_id": row.get("id"), "name": row.get("name"), "member_level": row.get("member_level", "unclassified"), "purchase_history": row.get("purchase_history", {"documents_365d": row.get("purchase_documents_365d"), "amount_365d": row.get("purchase_amount_365d")}), "equipment_profile": row.get("equipment_profile"), "activity_interest": row.get("activity_interest")} for row in rows])
        if domain == "supplier":
            rows = self.objects("suppliers", limit, 0)["items"]
            return self._envelope([{"supplier_id": row.get("id"), "name": row.get("name"), "status": row.get("cooperation_status", "active"), "purchase_documents_365d": row.get("purchase_documents_365d"), "purchase_amount_365d": row.get("purchase_amount_365d"), "last_purchase_date": row.get("last_purchase_date")} for row in rows])
        if domain == "inventory":
            rows = self.query("""select top %s w.ItemCode sku,w.WhsCode store_id,w.OnHand quantity,
                cast(null as int) age,cast(null as decimal(19,6)) turnover,
                case when w.OnHand<0 then 'negative_stock' when w.OnHand=0 then 'out_of_stock' else 'normal' end risk
                from dbo.OITW w order by w.OnHand desc""", (limit,))
            return self._envelope([row for row in rows if not stores or str(row.get("store_id")) in stores])
        raise ValueError("unknown_domain")
