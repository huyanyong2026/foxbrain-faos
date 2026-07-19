import json
import os
from wsgiref.simple_server import make_server
from packages.vafox_foundation.auth import issue_token
from packages.vafox_foundation.http import json_response, service_app


def login(environ, start_response):
    if environ.get("CONTENT_TYPE", "").split(";")[0] != "application/json":
        return json_response(start_response, 415, {"error": "json_content_type_required"}), 415
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
        body = json.loads(environ["wsgi.input"].read(length) or b"{}")
    except (ValueError, json.JSONDecodeError):
        return json_response(start_response, 400, {"error": "invalid_json"}), 400
    if not hmac_compare(body.get("username"), os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin")) or not hmac_compare(body.get("password"), os.getenv("BOOTSTRAP_ADMIN_PASSWORD")):
        return json_response(start_response, 401, {"error": "invalid_credentials"}), 401
    return json_response(start_response, 200, {"access_token": issue_token(body["username"], ["platform:admin"]), "token_type": "Bearer"}), 200


def hmac_compare(left, right):
    import hmac
    return isinstance(left, str) and isinstance(right, str) and hmac.compare_digest(left, right)

app = service_app("auth", {("POST", "/api/v1/auth/login"): login})
if __name__ == "__main__":
    make_server("0.0.0.0", 8080, app).serve_forever()
