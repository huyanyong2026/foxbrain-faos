"""Same-origin public proxy for the Gateway's approved Core datasets."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from foxbrain_os.enterprise_data_service import EnterpriseDataClient
from foxbrain_os.platform_governance import version_payload


PUBLIC_ROUTES = {
    "/api/public/stores": "api/v1/public/stores",
    "/api/public/brands": "api/v1/public/brands",
    "/api/public/status": "api/v1/public/status",
}


class GatewayPublicHandler(BaseHTTPRequestHandler):
    server_version = "VAFOXGatewayData/1.0"

    def log_message(self, fmt, *args):
        return

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
            return self._reply(200, {**version_payload("gateway"), "display": "FoxBrain Portal V4"})
        if self.path == "/health/version":
            return self._reply(200, version_payload("gateway"))
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

    def _read_only(self):
        self._reply(405, {"error": "read_only_api"})

    do_POST = _read_only
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
