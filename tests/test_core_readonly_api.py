import json
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

    def replenishment_input(self):
        return {"batch_id": "core-1", "business_date": "2026-07-13", "items": [{"sku_code": "A1"}]}


class CoreApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        policy = TokenPolicy(json.dumps({
            "huyan": {"token": "facts-token", "scopes": ["facts:read"]},
            "gateway": {"token": "public-token", "scopes": ["public:read"]},
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
        self.assertEqual(self.request("/api/v1/tables/dbo/OITM/rows", "facts-token")[0], 200)
        status, payload = self.request("/api/v1/replenishment/input", "facts-token")
        self.assertEqual(status, 200)
        self.assertEqual(payload["batch_id"], "core-1")

    def test_gateway_token_cannot_read_enterprise_tables(self):
        self.assertEqual(self.request("/api/v1/public/status", "public-token")[0], 200)
        self.assertEqual(self.request("/api/v1/tables", "public-token")[0], 401)

    def test_missing_token_and_writes_are_rejected(self):
        self.assertEqual(self.request("/api/health")[0], 401)
        self.assertEqual(self.request("/api/v1/status", "facts-token", "POST")[0], 405)

    def test_identifier_validation(self):
        self.assertEqual(quote_identifier("OITM"), "[OITM]")
        with self.assertRaises(ValueError):
            quote_identifier("OITM; drop table x")

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


if __name__ == "__main__":
    unittest.main()
