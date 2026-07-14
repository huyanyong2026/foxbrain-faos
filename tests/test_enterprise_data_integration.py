import json
import hashlib
import hmac
import threading
import unittest
import urllib.error
import urllib.request
from unittest import mock

from apps.gateway.public_api import create_server as create_gateway_server
from foxbrain_os.enterprise_data_service import EnterpriseDataClient


class FakeResponse:
    status = 200

    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class FakeCoreClient:
    def __init__(self):
        self.paths = []

    def get(self, path, params=None):
        self.paths.append(path)
        return {"ok": True, "status": 200, "data": {"items": [{"id": "NS", "name": "南山店"}]}}


class EnterpriseDataClientTests(unittest.TestCase):
    def test_only_approved_https_host_is_allowed(self):
        EnterpriseDataClient("https://core.vafox.com", "token")
        with self.assertRaises(ValueError):
            EnterpriseDataClient("http://core.vafox.com", "token")
        with self.assertRaises(ValueError):
            EnterpriseDataClient("https://core.vafox.com.evil.example", "token")

    @mock.patch("foxbrain_os.enterprise_data_service.urlopen")
    def test_client_uses_get_bearer_token_and_cache(self, mocked_urlopen):
        mocked_urlopen.return_value = FakeResponse({"object_type": "brands", "items": []})
        client = EnterpriseDataClient("https://core.vafox.com", "secret", cache_seconds=60)
        first = client.objects("brands")
        second = client.objects("brands")
        self.assertTrue(first["ok"] and second["ok"])
        self.assertEqual(mocked_urlopen.call_count, 1)
        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")

    @mock.patch("foxbrain_os.enterprise_data_service.urlopen")
    def test_explorer_match_sends_phone_hmac_not_plain_phone(self, mocked_urlopen):
        mocked_urlopen.return_value = FakeResponse({"matched": False, "items": []})
        client = EnterpriseDataClient("https://core.vafox.com", "explorer-token", cache_seconds=0)
        result = client.explorer_customer_match("13800138000")
        self.assertTrue(result["ok"])
        request = mocked_urlopen.call_args.args[0]
        expected = hmac.new(b"explorer-token", b"13800138000", hashlib.sha256).hexdigest()
        self.assertIn(expected, request.full_url)
        self.assertNotIn("13800138000", request.full_url)


class GatewayPublicProxyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = FakeCoreClient()
        cls.server = create_gateway_server("127.0.0.1", 0, cls.client)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:{}".format(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def request(self, path, method="GET"):
        request = urllib.request.Request(self.base + path, method=method)
        try:
            with urllib.request.urlopen(request) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as exc:
            return exc.code, json.load(exc)

    def test_only_public_routes_are_proxied(self):
        status, payload = self.request("/api/public/stores")
        self.assertEqual(status, 200)
        self.assertEqual(payload["items"][0]["name"], "南山店")
        self.assertEqual(self.client.paths[-1], "api/v1/public/stores")
        self.assertEqual(self.request("/api/public/customers")[0], 404)

    def test_gateway_proxy_is_read_only(self):
        self.assertEqual(self.request("/api/public/stores", "POST")[0], 405)


if __name__ == "__main__":
    unittest.main()
