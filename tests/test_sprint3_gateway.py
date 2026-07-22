import io
import json

from services.gateway.app import app


def call(path, authorization=None):
    status = []
    environ = {
        "REQUEST_METHOD": "GET", "PATH_INFO": path, "QUERY_STRING": "",
        "wsgi.input": io.BytesIO(), "CONTENT_LENGTH": "0", "CONTENT_TYPE": "application/json",
    }
    if authorization:
        environ["HTTP_AUTHORIZATION"] = authorization
    response = b"".join(app(environ, lambda value, _: status.append(value)))
    return int(status[0].split()[0]), json.loads(response)


def test_sprint3_gateway_rejects_unauthenticated_and_non_api_prefix_paths():
    status, payload = call("/api/customer/profile/C1")
    assert status == 401 and payload["error"] == "unauthorized"
    status, payload = call("/api/customer-support")
    assert status == 404 and payload["error"] == "route_not_found"
