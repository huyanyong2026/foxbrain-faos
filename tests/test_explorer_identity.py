import hashlib
import hmac
import http.client
import json
import sqlite3
import tempfile
import threading
import time
import unittest
import urllib.parse
from contextlib import closing
from pathlib import Path

from apps.gateway.explorer_identity import (
    CorePurchaseMatcher,
    ExplorerStore,
    SignedPhoneVerifier,
    WeChatOAuth,
    create_server,
    normalize_phone,
)


class FakeOAuth:
    configured = True

    def authorization_url(self, state):
        return "https://wechat.example/authorize?state=" + urllib.parse.quote(state)

    def exchange(self, code):
        if code != "valid-code":
            raise ValueError("微信授权无效")
        return {"openid": "raw-openid-001", "display_name": "山野同行者", "city": "深圳"}


class FakePhoneVerifier:
    def verify(self, phone, token):
        if token != "verified-token":
            raise ValueError("手机号未验证")
        return normalize_phone(phone)


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
            "brand_name": "KAILAS", "purchase_date": "2026-07-01", "quantity": 1, "amount": 1680,
        }]}}


class ExplorerIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / "explorer.db"
        self.store = ExplorerStore(self.db_path, "identity-secret-for-tests-1234567890")
        self.matcher = FakeMatcher()
        self.server = create_server(
            "127.0.0.1", 0, store=self.store, oauth=FakeOAuth(),
            phone_verifier=FakePhoneVerifier(), matcher=self.matcher,
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
        encoded = urllib.parse.urlencode(body or {}) if body is not None else None
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

    def create_login(self):
        status, headers, _ = self.request("POST", "/explorer/auth/wechat/start", {
            "consent": "1", "interest": "徒步",
        })
        self.assertEqual(status, 302)
        state = urllib.parse.parse_qs(urllib.parse.urlparse(headers["Location"]).query)["state"][0]
        status, headers, _ = self.request(
            "GET", "/explorer/auth/wechat/callback?code=valid-code&state=" + urllib.parse.quote(state)
        )
        self.assertEqual(status, 302)
        cookie = headers["Set-Cookie"].split(";", 1)[0]
        self.assertIn("Path=/", headers["Set-Cookie"])
        return state, cookie

    def test_wechat_identity_purchase_match_and_self_only_access(self):
        state, cookie = self.create_login()
        status, _, payload = self.request("GET", "/api/explorer/me", cookie=cookie)
        self.assertEqual(status, 200)
        profile = json.loads(payload)["profile"]
        self.assertEqual(profile["city"], "深圳")
        self.assertIn("徒步", profile["interests"])

        status, _, payload = self.request("POST", "/api/explorer/phone/verify", {
            "phone": "13800138000", "verification_token": "verified-token",
        }, cookie)
        self.assertEqual(status, 200)
        self.assertTrue(json.loads(payload)["matched"])
        self.assertEqual(self.matcher.phones, ["13800138000"])

        status, _, payload = self.request("GET", "/api/explorer/equipment", cookie=cookie)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(payload)["items"][0]["brand_name"], "KAILAS")

        second_id, _ = self.store.create_or_get("other-openid", "另一位探索者", "广州", "v1", [])
        second_cookie = "explorer_session=" + self.store.create_session(second_id)
        status, _, payload = self.request("GET", "/api/explorer/equipment", cookie=second_cookie)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(payload)["items"], [])

        status, _, _ = self.request(
            "GET", "/explorer/auth/wechat/callback?code=valid-code&state=" + urllib.parse.quote(state)
        )
        self.assertEqual(status, 400)

    def test_raw_openid_and_phone_are_not_stored(self):
        _, cookie = self.create_login()
        self.request("POST", "/api/explorer/phone/verify", {
            "phone": "13800138000", "verification_token": "verified-token",
        }, cookie)
        with closing(sqlite3.connect(self.db_path)) as connection:
            openid_hash, phone_hash, last4 = connection.execute(
                "select openid_hash,mobile_hash,mobile_last4 from explorer_identities"
            ).fetchone()
        self.assertNotEqual(openid_hash, "raw-openid-001")
        self.assertNotEqual(phone_hash, "13800138000")
        self.assertEqual(last4, "8000")
        self.assertNotIn(b"raw-openid-001", self.db_path.read_bytes())
        self.assertNotIn(b"13800138000", self.db_path.read_bytes())

    def test_csrf_unauthenticated_and_write_method_guards(self):
        self.assertEqual(self.request("GET", "/api/explorer/me")[0], 401)
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=4)
        body = urllib.parse.urlencode({"consent": "1"})
        connection.request("POST", "/explorer/auth/wechat/start", body, {
            "Host": self.host, "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(body)), "Origin": "https://evil.example",
        })
        self.assertEqual(connection.getresponse().status, 403)
        connection.close()
        self.assertEqual(self.request("DELETE", "/api/explorer/me")[0], 405)

    def test_core_matcher_uses_read_only_core_client(self):
        client = FakeCoreClient()
        customer, items, source = CorePurchaseMatcher(client).match("13800138000")
        self.assertEqual(customer["id"], "C100")
        self.assertEqual(items[0]["sku"], "K001")
        self.assertEqual(source["system"], "core.vafox.com")
        self.assertEqual(client.last_match_call, ("13800138000", 500))

    def test_signed_phone_verifier_and_unconfigured_wechat(self):
        secret = b"phone-verification-secret-1234567890"
        expires = str(int(time.time()) + 60)
        signature = hmac.new(secret, ("13800138000:" + expires).encode(), hashlib.sha256).hexdigest()
        verifier = SignedPhoneVerifier(secret.decode())
        self.assertEqual(verifier.verify("+86 13800138000", expires + "." + signature), "13800138000")
        oauth = WeChatOAuth("", "", "https://gateway.vafox.com/explorer/auth/wechat/callback")
        self.assertFalse(oauth.configured)
        with self.assertRaises(ValueError):
            oauth.authorization_url("state")


if __name__ == "__main__":
    unittest.main()
