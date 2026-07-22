import json
import hashlib
import hmac
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from apps.core_api.app import CoreService, TokenPolicy, create_server, quote_identifier


class FakeService:
    def status(self):
        return {"service": "core", "mode": "read_only", "checked_at": "now", "mirror": {"status": "completed"}}

    def tables(self):
        return [{"table": "dbo.OITM", "status": "completed"}]

    def rows(self, schema, table, limit, offset):
        return {"table": schema + "." + table, "rows": [{"ItemCode": "A1"}]}

    def operation_snapshot(self, store, as_of):
        return {"as_of": as_of, "warehouse": {"WhsCode": "NS", "WhsName": store}, "products": [], "sales": []}

    def replenishment_input(self):
        return {"batch_id": "core-1", "business_date": "2026-07-13", "items": [{"sku_code": "A1"}]}

    def business_objects(self, object_type, limit=50, offset=0, object_id="", allowed_store_ids=None):
        items = {
            "stores": [
                {"id": "NS", "name": "南山店", "sales_90d": 100, "stock_amount": 50},
                {"id": "ZX", "name": "振兴店", "sales_90d": 200, "stock_amount": 70},
            ],
            "products": [{"id": "A1", "name": "冲锋衣"}],
            "brands": [{"id": "1", "name": "KAILAS", "sales_amount_90d": 300}],
            "suppliers": [{"id": "S1", "name": "供应商"}],
            "customers": [{"id": "C1", "name": "顾客", "phone": "13800138000", "mobile": ""}],
        }[object_type]
        if object_id:
            items = [item for item in items if item["id"] == object_id]
        if object_type == "stores" and allowed_store_ids:
            items = [item for item in items if item["id"] in allowed_store_ids]
        return {"object_type": object_type, "items": items, "returned": len(items)}

    def customer_purchases(self, customer_id, limit=200):
        return {
            "customer_id": customer_id,
            "returned": 1,
            "data_as_of": "2026-07-14T00:00:00+00:00",
            "source": {"system": "core.vafox.com", "mode": "read_only"},
            "items": [{
                "purchase_key": "OINV:1:0", "sku": "A1", "product_name": "冲锋衣",
                "brand_name": "KAILAS", "purchase_date": "2026-07-01",
                "quantity": 1, "amount": 999, "source_document": "invoice",
            }],
        }

    def explorer_customer_match(self, phone_hash, hmac_secret, limit=500):
        expected = hmac.new(hmac_secret.encode(), b"13800138000", hashlib.sha256).hexdigest()
        return {
            "matched": hmac.compare_digest(phone_hash, expected),
            "customer": {"id": "C1", "name": "顾客"} if phone_hash == expected else None,
            "items": self.customer_purchases("C1", limit)["items"] if phone_hash == expected else [],
            "source": {"system": "core.vafox.com", "mode": "read_only"},
        }

    def public_objects(self, object_type):
        values = self.business_objects(object_type)["items"]
        return {"object_type": object_type, "items": [{"id": item["id"], "name": item["name"]} for item in values]}

    def business_summary(self):
        return {"sales_amount": 1000, "gross_profit": 300, "source": {"mode": "read_only"}}

    def data_health(self):
        return {"status": "healthy", "object_counts": {"stores": 2}, "problems": []}

    def domain(self, name, store_ids=None, limit=100):
        samples = {
            "products": {"product_id": "A1", "sku": "A1", "brand": "KAILAS", "category": "outer", "cost": 1, "price": 2, "status": "active", "lifecycle": "active"},
            "sales": {"order_id": "1", "store_id": "NS", "sku": "A1", "amount": 2, "margin": 1, "date": "2026-07-14"},
            "inventory": {"sku": "A1", "store_id": "NS", "quantity": 1, "age": 3, "turnover": 2, "risk": "normal"},
            "customers": {"customer_id": "C1", "member_level": "gold", "purchase_history": [], "equipment_profile": None, "activity_interest": None},
            "stores": {"store_id": "NS", "name": "南山店", "region": "深圳", "sales": 2, "target": 3},
        }
        data = [samples[name]]
        if store_ids and name in {"sales", "inventory", "stores"}:
            data = [row for row in data if row.get("store_id") in store_ids]
        return {"data": data, "source": "core." + name, "timestamp": "2026-07-14T00:00:00+00:00", "version": "v1", "confidence": .95, "mode": "read_only"}


class CoreApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        policy = TokenPolicy(json.dumps({
            "huyan": {"token": "facts-token", "role": "ceo", "scopes": ["facts:read", "objects:read", "customers:read", "health:read"]},
            "store": {"token": "store-token", "role": "store_manager", "store_ids": ["NS"], "scopes": ["objects:read", "store:read"]},
            "ai": {"token": "ai-token", "role": "purchasing", "scopes": ["objects:read", "health:read"]},
            "operator": {"token": "raw-token", "role": "core_operator", "scopes": ["raw:read"]},
            "gateway": {"token": "public-token", "scopes": ["public:read"]},
            "explorer": {"token": "explorer-token", "role": "explorer_service", "scopes": ["explorer:match"]},
            "domains": {"token": "domain-token", "role": "buyer", "scopes": ["product:read", "inventory:read", "sales:read", "customer:assigned", "store:read"]},
        }))
        cls.server = create_server("127.0.0.1", 0, FakeService(), policy)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:{}".format(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def request(self, path, token=None, method="GET"):
        headers = {"Authorization": "Bearer " + token} if token else {}
        request = urllib.request.Request(self.base + path, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as exc:
            return exc.code, json.load(exc)

    def test_facts_token_reads_health_and_rows(self):
        self.assertEqual(self.request("/api/health", "facts-token")[0], 200)
        self.assertEqual(self.request("/api/v1/tables/dbo/OITM/rows", "facts-token")[0], 401)
        self.assertEqual(self.request("/api/v1/tables/dbo/OITM/rows", "raw-token")[0], 200)
        status, snapshot = self.request("/api/v1/operation/snapshot?store=%E5%8D%97%E5%B1%B1%E5%BA%97&as_of=2026-07-13", "facts-token")
        self.assertEqual(status, 200)
        self.assertEqual(snapshot["warehouse"]["WhsCode"], "NS")
        status, payload = self.request("/api/v1/replenishment/input", "facts-token")
        self.assertEqual(status, 200)
        self.assertEqual(payload["batch_id"], "core-1")

    def test_gateway_token_cannot_read_enterprise_tables(self):
        self.assertEqual(self.request("/api/v1/public/status", "public-token")[0], 200)
        status, payload = self.request("/api/v1/public/stores", "public-token")
        self.assertEqual(status, 200)
        self.assertNotIn("sales_90d", payload["items"][0])
        self.assertEqual(self.request("/api/v1/tables", "public-token")[0], 401)
        self.assertEqual(self.request("/api/v1/objects/stores", "public-token")[0], 401)

    def test_business_objects_health_and_summary(self):
        self.assertEqual(self.request("/api/v1/objects/products", "ai-token")[0], 200)
        self.assertEqual(self.request("/api/v1/data-health", "ai-token")[0], 200)
        status, payload = self.request("/api/v1/business/summary", "facts-token")
        self.assertEqual(status, 200)
        self.assertEqual(payload["source"]["mode"], "read_only")

    def test_store_manager_is_limited_to_assigned_store(self):
        status, payload = self.request("/api/v1/objects/stores", "store-token")
        self.assertEqual(status, 200)
        self.assertEqual([item["id"] for item in payload["items"]], ["NS"])
        self.assertEqual(self.request("/api/v1/objects/products", "store-token")[0], 403)

    def test_customer_objects_require_sensitive_scope(self):
        self.assertEqual(self.request("/api/v1/objects/customers", "ai-token")[0], 401)
        self.assertEqual(self.request("/api/v1/objects/customers", "facts-token")[0], 200)

    def test_customer_purchases_require_sensitive_scope(self):
        path = "/api/v1/objects/customers/C1/purchases"
        self.assertEqual(self.request(path, "public-token")[0], 401)
        self.assertEqual(self.request(path, "ai-token")[0], 401)
        status, payload = self.request(path, "facts-token")
        self.assertEqual(status, 200)
        self.assertEqual(payload["items"][0]["brand_name"], "KAILAS")

    def test_explorer_match_is_hash_only_and_uses_dedicated_scope(self):
        phone_hash = hmac.new(b"explorer-token", b"13800138000", hashlib.sha256).hexdigest()
        path = "/api/v1/explorer/customer-match?phone_hash=" + phone_hash
        self.assertEqual(self.request(path, "public-token")[0], 401)
        self.assertEqual(self.request(path, "facts-token")[0], 401)
        status, payload = self.request(path, "explorer-token")
        self.assertEqual(status, 200)
        self.assertTrue(payload["matched"])
        self.assertNotIn("phone", payload["customer"])

    def test_missing_token_and_writes_are_rejected(self):
        self.assertEqual(self.request("/api/health")[0], 401)
        self.assertEqual(self.request("/api/v1/status", "facts-token", "POST")[0], 405)

    def test_identifier_validation(self):
        self.assertEqual(quote_identifier("OITM"), "[OITM]")
        with self.assertRaises(ValueError):
            quote_identifier("OITM; drop table x")

    def test_operation_snapshot_filters_inactive_catalog_rows(self):
        source = (Path(__file__).resolve().parents[1] / "apps" / "core_api" / "app.py").read_text(encoding="utf-8")
        self.assertIn("coalesce(w.OnHand,0)<>0", source)
        self.assertIn("or s.ItemCode is not null", source)

    def test_state_status_is_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.db"
            import sqlite3
            db = sqlite3.connect(path)
            try:
                db.execute("create table mirror_runs(source_tables integer, completed_tables integer, failed_tables integer, started_at integer, finished_at integer, error text)")
                db.execute("insert into mirror_runs values(2120,2120,0,1,2,null)")
                db.commit()
            finally:
                db.close()
            status = CoreService(path, "dbo.OITM", connector=lambda: None).status()
            self.assertEqual(status["mirror"]["status"], "completed")
            self.assertEqual(status["mirror"]["completed_tables"], 2120)

    def test_business_data_core_domains_have_evidence_envelopes(self):
        required = {
            "products": "product_id", "sales": "order_id", "inventory": "quantity",
            "customers": "customer_id", "stores": "store_id",
        }
        for domain, field in required.items():
            status, payload = self.request("/api/v1/" + domain, "domain-token")
            self.assertEqual(status, 200)
            self.assertIn(field, payload["data"][0])
            self.assertEqual({"source", "timestamp", "version", "confidence"}, set(payload) & {"source", "timestamp", "version", "confidence"})

    def test_domain_rbac_is_default_deny_and_store_scope_is_enforced(self):
        self.assertEqual(self.request("/api/v1/inventory", "store-token")[0], 401)
        status, payload = self.request("/api/v1/stores", "store-token")
        self.assertEqual(status, 200)
        self.assertEqual(payload["data"][0]["store_id"], "NS")


if __name__ == "__main__":
    unittest.main()
