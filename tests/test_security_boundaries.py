import importlib.util
import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path


TEST_APP_DIR = tempfile.mkdtemp(prefix="foxbrain-security-")
os.environ["APP_DIR"] = TEST_APP_DIR
SPEC = importlib.util.spec_from_file_location(
    "foxbrain_portal_security_test",
    Path(__file__).resolve().parents[1] / "portal_v2.py",
)
portal = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(portal)


class HeaderMap(dict):
    def get(self, key, default=None):
        return super().get(key, default)


class SecurityBoundaryTests(unittest.TestCase):
    def test_session_round_trip_and_expiry(self):
        issued_at = int(time.time())
        token = portal.issue_session(42, issued_at)
        self.assertEqual(portal.session_user_id(token, issued_at + 60), "42")
        self.assertIsNone(
            portal.session_user_id(token, issued_at + portal.SESSION_TTL_SECONDS + 1)
        )

    def test_legacy_session_is_rejected(self):
        self.assertIsNone(portal.session_user_id(portal.sign("42")))

    def test_tampered_session_is_rejected(self):
        token = portal.issue_session(42, int(time.time()))
        self.assertIsNone(portal.session_user_id(token + "x"))

    def test_same_origin_request_is_accepted(self):
        request = object.__new__(portal.App)
        request.headers = HeaderMap(
            {
                "Host": "huyan.vafox.com",
                "X-Forwarded-Proto": "https",
                "Origin": "https://huyan.vafox.com",
            }
        )
        self.assertTrue(request.write_request_is_same_origin())

    def test_cross_origin_and_missing_origin_are_rejected(self):
        request = object.__new__(portal.App)
        request.headers = HeaderMap(
            {"Host": "huyan.vafox.com", "Origin": "https://example.invalid"}
        )
        self.assertFalse(request.write_request_is_same_origin())
        request.headers = HeaderMap({"Host": "huyan.vafox.com"})
        self.assertFalse(request.write_request_is_same_origin())


def tearDownModule():
    shutil.rmtree(TEST_APP_DIR, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
