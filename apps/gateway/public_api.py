"""Same-origin public proxy and Identity Center for gateway.vafox.com."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from foxbrain_os.enterprise_data_service import EnterpriseDataClient
from foxbrain_os.platform_governance import runtime_payload, version_payload


SESSION_TTL_SECONDS = 8 * 60 * 60
SESSION_COOKIE = "vafox_gateway_session"
GATEWAY_HOST = "gateway.vafox.com"

IDENTITY_ROLES = {
    "ceo": {
        "label": "CEO",
        "aliases": {"ceo", "founder", "boss", "owner", "chairman", "leader"},
        "roles": ["ceo", "founder", "leader"],
        "route": "https://huyan.vafox.com",
        "permissions": ["enterprise:read", "decision:approve", "memory:read"],
    },
    "employee": {
        "label": "Employee",
        "aliases": {"employee", "staff", "worker", "store_manager", "purchaser", "management"},
        "roles": ["employee"],
        "route": "https://ai.vafox.com",
        "permissions": ["mission:read", "workflow:write", "memory:contribute"],
    },
    "admin": {
        "label": "Admin",
        "aliases": {"admin", "administrator", "identity_admin", "data_admin", "system_admin"},
        "roles": ["admin", "identity_admin"],
        "route": "https://core.vafox.com",
        "permissions": ["identity:read", "permission:validate", "audit:read"],
    },
}

SUPPORTED_CREDENTIALS = {"mobile_phone", "wechat", "enterprise_wechat", "erp_employee_id", "membership_id"}
PUBLIC_ROUTES = {
    "/api/public/stores": "api/v1/public/stores",
    "/api/public/brands": "api/v1/public/brands",
    "/api/public/status": "api/v1/public/status",
}


def _canonical(value):
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")


class GatewayIdentityCenter:
    """Gateway-only identity resolver with VID, role, session, and route contracts."""

    def __init__(self, secret=None, ttl_seconds=SESSION_TTL_SECONDS):
        self.secret = (secret or os.environ.get("GATEWAY_SESSION_SECRET") or "dev-gateway-session-secret-change-me-32chars").encode("utf-8")
        if len(self.secret) < 32:
            raise ValueError("GATEWAY_SESSION_SECRET must contain at least 32 characters")
        self.ttl_seconds = int(ttl_seconds)
        self.revoked_session_hashes = set()

    def digest(self, purpose, value):
        return hmac.new(self.secret, f"{purpose}:{value}".encode("utf-8"), hashlib.sha256).hexdigest()

    def resolve_vid(self, credential_type, credential_value):
        credential_type = _canonical(credential_type)
        normalized_value = str(credential_value or "").strip()
        if credential_type not in SUPPORTED_CREDENTIALS:
            raise ValueError("unsupported_credential")
        if not normalized_value:
            raise ValueError("credential_required")
        digest = self.digest("gateway-vid", f"{credential_type}:{normalized_value}")[:20].upper()
        return f"VID-VAFOX-{digest}"

    def recognize_role(self, *signals):
        values = {_canonical(signal) for signal in signals if str(signal or "").strip()}
        for role_key, definition in IDENTITY_ROLES.items():
            if values & definition["aliases"]:
                return role_key
        return "employee"

    def issue_session(self, vid, role_key):
        role_key = role_key if role_key in IDENTITY_ROLES else "employee"
        issued_at = int(time.time())
        expires_at = issued_at + self.ttl_seconds
        nonce = secrets.token_urlsafe(12)
        message = f"{vid}.{role_key}.{issued_at}.{expires_at}.{nonce}"
        sig = hmac.new(self.secret, message.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{message}.{sig}"

    def verify_session(self, token):
        parts = str(token or "").split(".")
        if len(parts) != 6:
            return None
        vid, role_key, issued_at, expires_at, nonce, sig = parts
        message = f"{vid}.{role_key}.{issued_at}.{expires_at}.{nonce}"
        expected = hmac.new(self.secret, message.encode("utf-8"), hashlib.sha256).hexdigest()
        token_hash = self.digest("gateway-session", token)
        try:
            expired = int(time.time()) >= int(expires_at)
        except ValueError:
            return None
        if token_hash in self.revoked_session_hashes or expired or not hmac.compare_digest(sig, expected):
            return None
        return {"vid": vid, "role_key": role_key, "issued_at": int(issued_at), "expires_at": int(expires_at), "session_id": nonce}

    def revoke_session(self, token):
        if token:
            self.revoked_session_hashes.add(self.digest("gateway-session", token))

    def identity_context(self, session):
        role_key = session.get("role_key") if session else "employee"
        profile = IDENTITY_ROLES.get(role_key, IDENTITY_ROLES["employee"])
        return {
            "vid": session["vid"],
            "identity_home": GATEWAY_HOST,
            "one_identity": True,
            "roles": profile["roles"],
            "primary_role": role_key,
            "role_label": profile["label"],
            "relationships": ["vafox-outdoor-life"],
            "permissions": profile["permissions"],
            "route": profile["route"],
            "manual_system_selection": False,
            "session": {"issued_at": session["issued_at"], "expires_at": session["expires_at"]},
        }

    def login(self, payload):
        vid = self.resolve_vid(payload.get("credential_type", "mobile_phone"), payload.get("credential_value", ""))
        role_key = self.recognize_role(payload.get("role_hint"), payload.get("role"), payload.get("position"))
        token = self.issue_session(vid, role_key)
        session = self.verify_session(token)
        context = self.identity_context(session)
        return {**context, "session_token": token}


class GatewayPublicHandler(BaseHTTPRequestHandler):
    server_version = "VAFOXGatewayIdentity/1.0"

    def log_message(self, fmt, *args):
        return

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _session_token(self):
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth.removeprefix("Bearer ").strip()
        if self.headers.get("X-VAFOX-Session"):
            return self.headers.get("X-VAFOX-Session", "").strip()
        jar = cookies.SimpleCookie(self.headers.get("Cookie", ""))
        return jar[SESSION_COOKIE].value if SESSION_COOKIE in jar else ""

    def _verify_token(self):
        return self.server.identity.verify_session(self._session_token())

    def _reply(self, status, payload, headers=None, cache_control="no-store"):
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", cache_control)
        self.send_header("X-Content-Type-Options", "nosniff")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/version"):
            return self._reply(200, {**version_payload("gateway"), "display": "VAFOX Gateway Identity Center"}, cache_control="public, max-age=300")
        if path == "/health/version":
            return self._reply(200, version_payload("gateway"), cache_control="public, max-age=300")
        if path == "/health/runtime":
            return self._reply(200, runtime_payload("gateway"), cache_control="public, max-age=300")
        if path in ("/identity/me", "/identity/context", "/identity/roles", "/routing/resolve", "/session"):
            session = self._verify_token()
            if not session:
                return self._reply(401, {"error": "invalid_or_expired_session"})
            context = self.server.identity.identity_context(session)
            if path == "/identity/me":
                return self._reply(200, {"vid": context["vid"], "roles": context["roles"], "primary_role": context["primary_role"]})
            if path == "/identity/roles":
                return self._reply(200, {"roles": context["roles"], "permissions": context["permissions"], "primary_role": context["primary_role"]})
            if path == "/routing/resolve":
                return self._reply(200, {"route": context["route"], "manual_system_selection": False})
            if path == "/session":
                return self._reply(200, {"active": True, "session": context["session"]})
            return self._reply(200, context)
        if path == "/healthz":
            if self.client_address[0] not in {"127.0.0.1", "::1"}:
                return self._reply(404, {"error": "not_found"})
            return self._reply(200, {"status": "ok"}, cache_control="public, max-age=30")
        core_path = PUBLIC_ROUTES.get(path)
        if not core_path:
            return self._reply(404, {"error": "not_found"})
        result = self.server.client.get(core_path)
        if not result.get("ok"):
            return self._reply(503, {"error": "public_data_temporarily_unavailable"})
        return self._reply(200, result["data"], cache_control="public, max-age=300")

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/identity/login":
            try:
                result = self.server.identity.login(self._read_json())
            except ValueError as error:
                return self._reply(400, {"error": str(error)})
            cookie = cookies.SimpleCookie()
            cookie[SESSION_COOKIE] = result["session_token"]
            cookie[SESSION_COOKIE]["path"] = "/"
            cookie[SESSION_COOKIE]["httponly"] = True
            cookie[SESSION_COOKIE]["secure"] = True
            cookie[SESSION_COOKIE]["samesite"] = "Lax"
            cookie[SESSION_COOKIE]["max-age"] = str(self.server.identity.ttl_seconds)
            return self._reply(200, result, headers={"Set-Cookie": cookie.output(header="").strip()})
        if path == "/identity/logout":
            token = self._session_token()
            self.server.identity.revoke_session(token)
            return self._reply(200, {"ok": True})
        return self._reply(405, {"error": "identity_center_only"})

    def _read_only(self):
        self._reply(405, {"error": "read_only_api"})
    do_PUT = _read_only
    do_PATCH = _read_only
    do_DELETE = _read_only


def create_server(host=None, port=None, client=None, identity=None):
    bind_host = host if host is not None else os.environ.get("GATEWAY_DATA_HOST", "127.0.0.1")
    bind_port = int(port if port is not None else os.environ.get("GATEWAY_DATA_PORT", "8091"))
    server = ThreadingHTTPServer(
        (bind_host, bind_port),
        GatewayPublicHandler,
    )
    server.identity = identity or GatewayIdentityCenter()
    server.client = client or EnterpriseDataClient(
        os.environ.get("CORE_BASE_URL", "https://core.vafox.com"),
        os.environ.get("CORE_PUBLIC_API_TOKEN", ""),
        cache_seconds=int(os.environ.get("CORE_PUBLIC_CACHE_SECONDS", "300")),
    )
    return server


if __name__ == "__main__":
    create_server().serve_forever()
