"""Unified HTTP entry point: route-only proxy with JWT authorization at the edge."""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from wsgiref.simple_server import make_server

from packages.vafox_foundation.auth import verify_token
from packages.vafox_foundation.http import json_response, service_app

UPSTREAMS = {
    "/api/v1/auth": "http://auth:8080",
    "/api/v1/core": "http://core-data:8080",
    "/api/v1/ai": "http://ai:8080",
    "/api/v1/memory": "http://memory:8080",
    "/api/knowledge": "http://knowledge:8080",
    "/api/workspace": "http://business:8080",
    "/api/ceo": "http://business:8080",
    "/api/kailas": "http://business:8080",
    "/api/wechat": "http://business:8080",
    "/api/wecom": "http://wecom-integration:8080",
    "/api/wework": "http://wecom-integration:8080",
    "/api/customer": "http://business:8080",
    "/api/retail": "http://business:8080",
    "/api/store": "http://business:8080",
}


def proxy(environ, start_response):
    path = environ["PATH_INFO"]
    upstream = next((value for prefix, value in UPSTREAMS.items() if path == prefix or path.startswith(prefix + "/")), None)
    if not upstream:
        return json_response(start_response, 404, {"error": "route_not_found"}), 404
    claims = None
    # WeCom signs its callback itself; it cannot provide a FoxBrain bearer token.
    if not (path.startswith("/api/v1/auth") or path in {"/api/wecom/message", "/api/wework/callback"}):
        authorization = environ.get("HTTP_AUTHORIZATION", "")
        try:
            claims = verify_token(authorization.removeprefix("Bearer ")) if authorization.startswith("Bearer ") else (_ for _ in ()).throw(PermissionError())
        except PermissionError:
            return json_response(start_response, 401, {"error": "unauthorized"}), 401
    body = environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0))
    headers = {"Content-Type": environ.get("CONTENT_TYPE", "application/json")}
    if claims:
        # Only the verified gateway claim set is forwarded to internal services.
        headers.update({"X-VAFOX-Organization-ID": str(claims.get("organization_id", claims.get("org_id", ""))),
                        "X-VAFOX-User-ID": str(claims.get("sub", "")),
                        "X-VAFOX-Department-ID": str(claims.get("department_id", "")),
                        "X-VAFOX-Role-Scope": ",".join(str(role) for role in claims.get("role_scopes", claims.get("roles", [])))})
    request = Request(upstream + path, data=body if body else None, method=environ["REQUEST_METHOD"], headers=headers)
    try:
        with urlopen(request, timeout=float(os.getenv("UPSTREAM_TIMEOUT_SECONDS", "5"))) as response:
            payload, status = response.read(), response.status
    except HTTPError as error:
        payload, status = error.read(), error.code
    except (URLError, TimeoutError):
        return json_response(start_response, 503, {"error": "upstream_unavailable"}), 503
    start_response(f"{status} OK", [("Content-Type", "application/json"), ("Content-Length", str(len(payload)))])
    return [payload], status


def app(environ, start_response):
    if environ["PATH_INFO"] in {"/health", "/healthz", "/api/v1/health"}:
        return service_app("gateway")(environ, start_response)
    response, _ = proxy(environ, start_response)
    return response

if __name__ == "__main__":
    make_server("0.0.0.0", 8080, app).serve_forever()
