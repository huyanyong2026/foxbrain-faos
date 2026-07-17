import http.client
import json
import threading
import time
import unittest

from apps.gateway.public_api import GatewayIdentityCenter, create_server


class FakeClient:
    def get(self, path):
        return {"ok": True, "data": {"path": path, "items": []}}


class GatewayIdentityCenterTests(unittest.TestCase):
    def test_vid_resolution_is_stable_and_private(self):
        center = GatewayIdentityCenter("gateway-identity-secret-for-tests-1234567890")
        first = center.resolve_vid("erp_employee_id", "E001")
        second = center.resolve_vid("erp_employee_id", "E001")
        other = center.resolve_vid("erp_employee_id", "E002")
        self.assertEqual(first, second)
        self.assertNotEqual(first, other)
        self.assertTrue(first.startswith("VID-VAFOX-"))
        self.assertNotIn("E001", first)

    def test_role_recognition_routes_only_ceo_employee_and_admin(self):
        center = GatewayIdentityCenter("gateway-identity-secret-for-tests-1234567890")
        cases = {
            "ceo": "https://huyan.vafox.com",
            "employee": "https://ai.vafox.com",
            "store-manager": "https://ai.vafox.com",
            "admin": "https://core.vafox.com",
            "supplier": "https://ai.vafox.com",
            "customer": "https://ai.vafox.com",
        }
        for hint, route in cases.items():
            result = center.login({"credential_type": "mobile_phone", "credential_value": "13800138000", "role_hint": hint})
            self.assertEqual(result["route"], route)
            self.assertFalse(result["manual_system_selection"])
            self.assertTrue(result["one_identity"])

    def test_session_expiry_and_logout(self):
        center = GatewayIdentityCenter("gateway-identity-secret-for-tests-1234567890", ttl_seconds=1)
        token = center.login({"credential_type": "wechat", "credential_value": "open-1", "role_hint": "admin"})["session_token"]
        self.assertEqual(center.verify_session(token)["role_key"], "admin")
        center.revoke_session(token)
        self.assertIsNone(center.verify_session(token))
        token = center.login({"credential_type": "wechat", "credential_value": "open-2", "role_hint": "employee"})["session_token"]
        time.sleep(1.1)
        self.assertIsNone(center.verify_session(token))


class GatewayIdentityHttpTests(unittest.TestCase):
    def setUp(self):
        self.server = create_server(
            "127.0.0.1", 0, client=FakeClient(),
            identity=GatewayIdentityCenter("gateway-identity-secret-for-tests-1234567890"),
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=4)
        payload = json.dumps(body).encode() if body is not None else None
        req_headers = {"Host": "gateway.vafox.com"}
        if payload is not None:
            req_headers.update({"Content-Type": "application/json", "Content-Length": str(len(payload))})
        req_headers.update(headers or {})
        conn.request(method, path, body=payload, headers=req_headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        return res.status, dict(res.getheaders()), json.loads(data)

    def test_one_login_cookie_context_and_routing(self):
        status, headers, payload = self.request("POST", "/identity/login", {
            "credential_type": "erp_employee_id", "credential_value": "E-CEO", "role_hint": "ceo",
        })
        self.assertEqual(status, 200)
        self.assertEqual(payload["route"], "https://huyan.vafox.com")
        self.assertIn("vafox_gateway_session=", headers["Set-Cookie"])
        self.assertIn("HttpOnly", headers["Set-Cookie"])
        cookie = headers["Set-Cookie"].split(";", 1)[0]

        status, _, context = self.request("GET", "/identity/context", headers={"Cookie": cookie})
        self.assertEqual(status, 200)
        self.assertEqual(context["vid"], payload["vid"])
        self.assertEqual(context["primary_role"], "ceo")

        status, _, route = self.request("GET", "/routing/resolve", headers={"Cookie": cookie})
        self.assertEqual(status, 200)
        self.assertEqual(route, {"route": "https://huyan.vafox.com", "manual_system_selection": False})

    def test_unsupported_supplier_and_brand_credentials_are_not_built(self):
        for credential_type in ("supplier_id", "brand_id"):
            status, _, payload = self.request("POST", "/identity/login", {
                "credential_type": credential_type, "credential_value": "X1", "role_hint": "admin",
            })
            self.assertEqual(status, 400)
            self.assertEqual(payload["error"], "unsupported_credential")


if __name__ == "__main__":
    unittest.main()
