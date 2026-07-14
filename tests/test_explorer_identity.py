import http.client
import json
import sqlite3
import tempfile
import threading
import unittest
import urllib.parse
from contextlib import closing
from pathlib import Path
from unittest import mock

from apps.gateway.explorer_identity import (
    CorePurchaseMatcher,
    ExplorerStore,
    WebhookSmsSender,
    create_server,
    normalize_phone,
)


class FakeSmsSender:
    configured = True

    def __init__(self):
        self.messages = []

    def send(self, phone, code):
        self.messages.append((phone, code))


class FakeMatcher:
    def __init__(self):
        self.phones = []

    def match(self, phone):
        self.phones.append(phone)
        return (
            {"id": "C100", "name": "顾客"},
            [{
                "purchase_key": "OINV:8:0", "sku": "K001", "product_name": "轻量冲锋衣",
                "brand_name": "KAILAS", "purchase_date": "2026-07-01",
                "quantity": 1, "amount": 1680,
            }],
            {"system": "core.vafox.com", "mode": "read_only", "data_as_of": "2026-07-14"},
        )


class FakeCoreClient:
    def explorer_customer_match(self, phone, limit=500):
        self.last_match_call = (phone, limit)
        return {"ok": True, "data": {
            "customer": {"id": "C100", "name": "顾客"},
            "data_as_of": "2026-07-14", "items": [{
                "purchase_key": "OINV:8:0", "sku": "K001", "product_name": "轻量冲锋衣",
                "brand_name": "KAILAS", "purchase_date": "2026-07-01",
                "quantity": 1, "amount": 1680,
            }],
        }}


class ExplorerPhoneLoginTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / "explorer.db"
        self.store = ExplorerStore(self.db_path, "identity-secret-for-tests-1234567890")
        self.sms = FakeSmsSender()
        self.matcher = FakeMatcher()
        self.server = create_server(
            "127.0.0.1", 0, store=self.store, sms_sender=self.sms, matcher=self.matcher,
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.host = "127.0.0.1:{}".format(self.server.server_port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def request(self, method, path, body=None, cookie=""):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=4)
        encoded = urllib.parse.urlencode(body or {}, doseq=True) if body is not None else None
        headers = {"Host": self.host}
        if encoded is not None:
            headers.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": str(len(encoded.encode("utf-8"))),
                "Origin": "http://" + self.host,
            })
        if cookie:
            headers["Cookie"] = cookie
        connection.request(method, path, body=encoded, headers=headers)
        response = connection.getresponse()
        payload = response.read()
        result = response.status, dict(response.getheaders()), payload
        connection.close()
        return result

    def create_login(self, phone="13800138000"):
        status, _, payload = self.request("POST", "/api/explorer/phone/code", {
            "phone": phone, "consent": "1",
        })
        self.assertEqual(status, 200)
        self.assertIn("验证码已发送".encode(), payload)
        self.assertEqual(self.sms.messages[-1][0], phone)
        code = self.sms.messages[-1][1]
        status, headers, _ = self.request("POST", "/explorer/auth/phone", {
            "phone": phone, "code": code, "display_name": "山野同行者", "city": "深圳",
            "interest": ["徒步", "摄影"], "consent": "1",
        })
        self.assertEqual(status, 302)
        cookie = headers["Set-Cookie"].split(";", 1)[0]
        self.assertIn("Path=/", headers["Set-Cookie"])
        return code, cookie

    def test_phone_login_purchase_match_and_self_only_access(self):
        code, cookie = self.create_login()
        status, _, payload = self.request("GET", "/api/explorer/me", cookie=cookie)
        self.assertEqual(status, 200)
        profile = json.loads(payload)["profile"]
        self.assertEqual(profile["city"], "深圳")
        self.assertEqual(profile["mobile_last4"], "8000")
        self.assertIn("徒步", profile["interests"])
        self.assertEqual(self.matcher.phones, ["13800138000"])

        status, _, payload = self.request("GET", "/api/explorer/equipment", cookie=cookie)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(payload)["items"][0]["brand_name"], "KAILAS")

        second_id, _ = self.store.create_or_get_phone(
            "13900139000", "另一位探索者", "广州", "v1", []
        )
        second_cookie = "explorer_session=" + self.store.create_session(second_id)
        status, _, payload = self.request("GET", "/api/explorer/equipment", cookie=second_cookie)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(payload)["items"], [])

        status, _, payload = self.request("POST", "/explorer/auth/phone", {
            "phone": "13800138000", "code": code, "consent": "1",
        })
        self.assertEqual(status, 200)
        self.assertIn("验证码已失效".encode(), payload)

    def test_raw_phone_and_code_are_not_stored(self):
        code, _ = self.create_login()
        with closing(sqlite3.connect(self.db_path)) as connection:
            phone_hash, last4 = connection.execute(
                "select mobile_hash,mobile_last4 from explorer_identities"
            ).fetchone()
            code_hash = connection.execute(
                "select code_hash from explorer_phone_codes order by id desc limit 1"
            ).fetchone()[0]
        self.assertNotEqual(phone_hash, "13800138000")
        self.assertNotEqual(code_hash, code)
        self.assertEqual(last4, "8000")
        contents = self.db_path.read_bytes()
        self.assertNotIn(b"13800138000", contents)
        self.assertNotIn(code.encode(), contents)

    def test_code_rate_limit_attempt_limit_and_expiry(self):
        code_id, phone, code = self.store.issue_phone_code("13800138000", "127.0.0.1")
        self.store.mark_phone_code(code_id, "sent")
        with self.assertRaisesRegex(ValueError, "发送过于频繁"):
            self.store.issue_phone_code(phone, "127.0.0.1")
        for _ in range(4):
            with self.assertRaisesRegex(ValueError, "不正确"):
                self.store.verify_phone_code(phone, "000000" if code != "000000" else "000001")
        with self.assertRaisesRegex(ValueError, "错误次数过多"):
            self.store.verify_phone_code(phone, "000000" if code != "000000" else "000001")

    def test_csrf_unauthenticated_and_legacy_wechat_guards(self):
        self.assertEqual(self.request("GET", "/api/explorer/me")[0], 401)
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=4)
        body = urllib.parse.urlencode({"phone": "13800138000", "consent": "1"})
        connection.request("POST", "/api/explorer/phone/code", body, {
            "Host": self.host, "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(body)), "Origin": "https://evil.example",
        })
        self.assertEqual(connection.getresponse().status, 403)
        connection.close()
        self.assertEqual(self.request("DELETE", "/api/explorer/me")[0], 405)
        status, headers, _ = self.request("GET", "/explorer/auth/wechat/callback")
        self.assertEqual(status, 302)
        self.assertEqual(headers["Location"], "/explorer/register")

    def test_core_matcher_uses_read_only_core_client(self):
        client = FakeCoreClient()
        customer, items, source = CorePurchaseMatcher(client).match("13800138000")
        self.assertEqual(customer["id"], "C100")
        self.assertEqual(items[0]["sku"], "K001")
        self.assertEqual(source["system"], "core.vafox.com")
        self.assertEqual(client.last_match_call, ("13800138000", 500))

    def test_unconfigured_sms_and_webhook_payload(self):
        sender = WebhookSmsSender("", "")
        self.assertFalse(sender.configured)
        with self.assertRaisesRegex(ValueError, "正在配置"):
            sender.send("13800138000", "123456")

        response = mock.MagicMock()
        response.status = 204
        response.__enter__.return_value = response
        configured = WebhookSmsSender("https://sms.example/send", "sms-token-for-tests")
        with mock.patch("apps.gateway.explorer_identity.urllib.request.urlopen", return_value=response) as opened:
            configured.send("13800138000", "123456")
        request = opened.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(payload["phone"], "13800138000")
        self.assertEqual(payload["scene"], "explorer_login")
        self.assertEqual(request.get_header("Authorization"), "Bearer sms-token-for-tests")

    def test_phone_normalization(self):
        self.assertEqual(normalize_phone("+86 138-0013-8000"), "13800138000")
        with self.assertRaises(ValueError):
            normalize_phone("123")


if __name__ == "__main__":
    unittest.main()
