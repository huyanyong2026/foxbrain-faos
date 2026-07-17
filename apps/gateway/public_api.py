"""Same-origin public proxy for the Gateway's approved Core datasets."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from foxbrain_os.enterprise_data_service import EnterpriseDataClient
from foxbrain_os.platform_governance import runtime_payload, version_payload


IDENTITY_ROLES = {
    "ceo": {"roles": ["founder", "ceo", "leader"], "route": "https://huyan.vafox.com", "permissions": ["enterprise:read", "decision:approve", "memory:read"]},
    "admin": {"roles": ["administrator", "employee"], "route": "https://core.vafox.com", "permissions": ["identity:read", "permission:validate", "audit:read"]},
    "employee": {"roles": ["employee"], "route": "https://ai.vafox.com", "permissions": ["mission:read", "workflow:write", "memory:contribute"]},
}

PUBLIC_ROUTES = {
    "/api/public/stores": "api/v1/public/stores",
    "/api/public/brands": "api/v1/public/brands",
    "/api/public/status": "api/v1/public/status",
}


class GatewayPublicHandler(BaseHTTPRequestHandler):
    server_version = "VAFOXGatewayData/1.0"

    def log_message(self, fmt, *args):
        return

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _session_secret(self):
        return os.environ.get("GATEWAY_SESSION_SECRET", "dev-gateway-session-secret-change-me").encode("utf-8")

    def _vid_for(self, credential_type, credential_value):
        digest = hmac.new(self._session_secret(), f"{credential_type}:{credential_value}".encode("utf-8"), hashlib.sha256).hexdigest()[:20].upper()
        return f"VID-VAFOX-{digest}"

    def _signed_token(self, vid, role_key):
        issued_at = int(time.time())
        nonce = secrets.token_urlsafe(8)
        message = f"{vid}.{role_key}.{issued_at}.{nonce}"
        sig = hmac.new(self._session_secret(), message.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{message}.{sig}"

    def _verify_token(self):
        auth = self.headers.get("Authorization", "")
        token = auth.removeprefix("Bearer ").strip() if auth.startswith("Bearer ") else self.headers.get("X-VAFOX-Session", "")
        parts = token.split(".")
        if len(parts) != 5:
            return None
        vid, role_key, issued_at, nonce, sig = parts
        message = f"{vid}.{role_key}.{issued_at}.{nonce}"
        expected = hmac.new(self._session_secret(), message.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        if int(time.time()) - int(issued_at) > 3600:
            return None
        return {"vid": vid, "role_key": role_key, "issued_at": int(issued_at), "session_id": nonce}

    def _identity_context(self, session):
        role_key = session.get("role_key", "employee")
        profile = IDENTITY_ROLES.get(role_key, IDENTITY_ROLES["employee"])
        return {"vid": session["vid"], "roles": profile["roles"], "relationships": ["vafox-outdoor-life"], "growth_stage": "home-entry", "permissions": profile["permissions"], "mission_context": "Welcome Home", "route": profile["route"]}

    def _reply(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "public, max-age=300")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if self.path in ("/", "/version"):
            return self._reply(200, {**version_payload("gateway"), "display": "VAFOX Gateway Genesis"})
        if self.path == "/health/version":
            return self._reply(200, version_payload("gateway"))
        if self.path == "/health/runtime":
            return self._reply(200, runtime_payload("gateway"))
        if self.path in ("/identity/me", "/identity/context", "/identity/roles", "/routing/resolve"):
            session = self._verify_token()
            if not session:
                return self._reply(401, {"error": "invalid_or_expired_session"})
            context = self._identity_context(session)
            if self.path == "/identity/me":
                return self._reply(200, {"vid": context["vid"], "roles": context["roles"]})
            if self.path == "/identity/roles":
                return self._reply(200, {"roles": context["roles"], "permissions": context["permissions"]})
            if self.path == "/routing/resolve":
                return self._reply(200, {"route": context["route"], "manual_system_selection": False})
            return self._reply(200, context)
        if self.path == "/healthz":
            if self.client_address[0] not in {"127.0.0.1", "::1"}:
                return self._reply(404, {"error": "not_found"})
            return self._reply(200, {"status": "ok"})
        core_path = PUBLIC_ROUTES.get(self.path)
        if not core_path:
            return self._reply(404, {"error": "not_found"})
        result = self.server.client.get(core_path)
        if not result.get("ok"):
            return self._reply(503, {"error": "public_data_temporarily_unavailable"})
        return self._reply(200, result["data"])

    def do_POST(self):
        if self.path != "/identity/login":
            return self._reply(405, {"error": "read_only_api"})
        payload = self._read_json()
        credential_type = payload.get("credential_type", "mobile_phone")
        credential_value = str(payload.get("credential_value", "")).strip()
        role_hint = str(payload.get("role_hint", "employee")).lower()
        if credential_type not in {"mobile_phone", "wechat", "enterprise_wechat", "erp_employee_id", "membership_id", "supplier_id", "brand_id"}:
            return self._reply(400, {"error": "unsupported_credential"})
        if not credential_value:
            return self._reply(400, {"error": "credential_required"})
        profile = IDENTITY_ROLES.get(role_hint, IDENTITY_ROLES["employee"])
        vid = self._vid_for(credential_type, credential_value)
        token = self._signed_token(vid, role_hint if role_hint in IDENTITY_ROLES else "employee")
        return self._reply(200, {"vid": vid, "session_token": token, "roles": profile["roles"], "route": profile["route"], "manual_system_selection": False})

    def _read_only(self):
        self._reply(405, {"error": "read_only_api"})
    do_PUT = _read_only
    do_PATCH = _read_only
    do_DELETE = _read_only


def create_server(host=None, port=None, client=None):
    server = ThreadingHTTPServer(
        (host or os.environ.get("GATEWAY_DATA_HOST", "127.0.0.1"), int(port or os.environ.get("GATEWAY_DATA_PORT", "8091"))),
        GatewayPublicHandler,
    )
    server.client = client or EnterpriseDataClient(
        os.environ.get("CORE_BASE_URL", "https://core.vafox.com"),
        os.environ.get("CORE_PUBLIC_API_TOKEN", ""),
        cache_seconds=int(os.environ.get("CORE_PUBLIC_CACHE_SECONDS", "300")),
    )
    return server


if __name__ == "__main__":
    create_server().serve_forever()
