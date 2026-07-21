"""M4 HTTP, authentication, citation, ACL, and privilege-escalation coverage."""
import io
import json
import os
from datetime import datetime, timezone

from services.embedding.app import create_app as embedding_app
from services.knowledge.app import create_app as knowledge_app
from packages.vafox_foundation.auth import issue_token


def request(app, method, path, body=None, headers=None):
    status = []
    environ = {"REQUEST_METHOD": method, "PATH_INFO": path.split("?", 1)[0], "QUERY_STRING": path.partition("?")[2],
               "wsgi.input": io.BytesIO(body or b""), "CONTENT_LENGTH": str(len(body or b""))}
    environ.update(headers or {})
    response = b"".join(app(environ, lambda value, _: status.append(value))).decode()
    return int(status[0].split()[0]), json.loads(response)


class Embedding:
    def capabilities(self):
        return type("C", (), {"dimension": 3, "model_id": "semantic_v2", "model_version": "v2"})()
    def embed_batch(self, texts): return [[float(index), 2, 3] for index, _ in enumerate(texts)]
    def health_check(self): return {"status": "ok"}


def test_embedding_http_health_single_and_batch_contract():
    app = embedding_app(Embedding())
    assert request(app, "GET", "/health")[0] == 200
    status, payload = request(app, "POST", "/embed", b'{"text":"hello"}')
    assert status == 200 and payload["vector"] == [0.0, 2, 3] and payload["dimension"] == 3
    status, payload = request(app, "POST", "/embed_batch", b'{"texts":["a","b"]}')
    assert status == 200 and len(payload["vectors"]) == 2 and payload["version"] == "v2"


class Memory:
    def __init__(self):
        now = datetime.now(timezone.utc).isoformat()
        self.records = {"11111111-1111-1111-1111-111111111111": {"id": "11111111-1111-1111-1111-111111111111", "name": "SOP", "source": "manual.pdf", "owner_id": "alice", "organization_id": "org-a", "department_id": "ops", "visibility": "private", "status": "active", "tags": ["opening", "required"], "metadata": {"knowledge": {"domain": "sop", "title": "Opening SOP", "brand": "fox"}}, "created_at": now, "updated_at": now}}
    def get(self, identifier): return self.records.get(identifier)
    def content(self, identifier):
        record = self.get(identifier)
        return (record, b"secret operating procedure") if record else None


class Retrieval:
    def vector_search(self, **_):
        return {"results": [{"memory_id": "11111111-1111-1111-1111-111111111111", "content": "opening procedure", "source": "manual.pdf", "score": .9, "citation": {"chunk_id": "c1", "page": 1}}]}


def headers(user="alice", org="org-a", department="ops"):
    return {"HTTP_X_VAFOX_USER_ID": user, "HTTP_X_VAFOX_ORGANIZATION_ID": org, "HTTP_X_VAFOX_DEPARTMENT_ID": department}


def test_knowledge_search_citation_detail_acl_and_owner_override_is_ignored():
    app = knowledge_app(Memory(), Retrieval())
    status, payload = request(app, "GET", "/api/knowledge/search?query=open&tags=opening,required&owner=alice", headers=headers())
    assert status == 200 and payload["items"][0]["citation"]["chunk_id"] == "c1"
    status, payload = request(app, "GET", "/api/knowledge/11111111-1111-1111-1111-111111111111", headers=headers())
    assert status == 200 and payload["content"] == "secret operating procedure"
    # A client supplied owner cannot turn Bob into Alice or cross the private ACL.
    status, payload = request(app, "GET", "/api/knowledge/search?query=open&owner=alice", headers=headers("bob"))
    assert status == 200 and payload["items"] == []
    status, payload = request(app, "GET", "/api/knowledge/11111111-1111-1111-1111-111111111111", headers=headers("bob"))
    assert status == 403 and payload["error"] == "forbidden"


def test_knowledge_requires_trusted_authentication():
    app = knowledge_app(Memory(), Retrieval())
    assert request(app, "GET", "/api/knowledge/search?query=open")[0] == 401


def test_knowledge_accepts_verified_jwt_auth_context(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    token = issue_token("alice", ["department"])
    # JWT claims are the direct-service equivalent of gateway identity headers.
    token = token.split(".")
    import base64
    claims = json.loads(base64.urlsafe_b64decode(token[1] + "=" * (-len(token[1]) % 4)))
    claims.update({"organization_id": "org-a", "department_id": "ops"})
    encoded = base64.urlsafe_b64encode(json.dumps(claims, separators=(",", ":")).encode()).rstrip(b"=").decode()
    from hashlib import sha256
    import hmac
    signature = base64.urlsafe_b64encode(hmac.new(b"test-secret", f"{token[0]}.{encoded}".encode(), sha256).digest()).rstrip(b"=").decode()
    app = knowledge_app(Memory(), Retrieval())
    status, payload = request(app, "GET", "/api/knowledge/search?query=open", headers={"HTTP_AUTHORIZATION": f"Bearer {token[0]}.{encoded}.{signature}"})
    assert status == 200 and payload["items"][0]["knowledge_id"]
