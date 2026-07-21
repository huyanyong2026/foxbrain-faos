import io
import json
from wsgiref.util import setup_testing_defaults

from services.memory.app import create_app
from services.memory.acl import AuthContext, can_access


def request(app, method, path, payload=b"", headers=None):
    environ = {}
    setup_testing_defaults(environ)
    environ.update({"REQUEST_METHOD": method, "PATH_INFO": path, "CONTENT_TYPE": "application/json", "CONTENT_LENGTH": str(len(payload)), "wsgi.input": io.BytesIO(payload)})
    environ.update(headers or {})
    captured = {}
    body = b"".join(app(environ, lambda status, response_headers: captured.update(status=status)))
    return int(captured["status"][:3]), json.loads(body or b"{}")


def headers(user, department="ops", scope=""):
    return {"HTTP_X_VAFOX_ORGANIZATION_ID": "org-1", "HTTP_X_VAFOX_DEPARTMENT_ID": department,
            "HTTP_X_VAFOX_USER_ID": user, "HTTP_X_VAFOX_ROLE_SCOPE": scope}


class Memory:
    def __init__(self): self.created = None; self.records = {}
    def create(self, name, content, content_type, source, acl, metadata, tags):
        self.created = acl
        return {"memory_id": "created"}
    def get(self, memory_id): return self.records.get(memory_id)
    def delete(self, memory_id): return False


def record(owner, department="ops", visibility="private"):
    return {"id": owner, "organization_id": "org-1", "department_id": department, "owner_id": owner,
            "role_scope": visibility, "visibility": visibility}


def test_upload_binds_acl_from_auth_context_not_client_owner_or_visibility():
    memory = Memory()
    app = create_app(memory)
    status, _ = request(app, "POST", "/api/v1/memory/receive", json.dumps({"name": "a.txt", "source": "upload", "content": "secret", "owner": "other", "visibility": "organization"}).encode(), headers("user-a"))
    assert status == 201
    assert memory.created.owner_id == "user-a" and memory.created.upload_visibility == "private"


def test_user_a_and_b_are_mutually_isolated_for_get_and_admin_is_authorized():
    memory = Memory(); memory.records["b"] = record("user-b", "finance")
    app = create_app(memory)
    assert request(app, "GET", "/api/v1/memory/items/b", headers=headers("user-a", "ops"))[0] == 403
    assert request(app, "GET", "/api/v1/memory/items/b", headers=headers("user-b", "finance"))[0] == 200
    assert request(app, "GET", "/api/v1/memory/items/b", headers=headers("admin", "ops", "admin"))[0] == 200


def test_acl_scope_rules_cover_private_department_organization_and_cross_org():
    user_a = AuthContext("org-1", "ops", "user-a", frozenset())
    assert not can_access(user_a, record("user-b", "finance"))
    assert can_access(user_a, record("user-b", "ops", "department"))
    assert can_access(user_a, record("user-b", "finance", "organization"))
    assert not can_access(user_a, {**record("user-b"), "organization_id": "org-2"})
