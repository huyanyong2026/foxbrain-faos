import io
import json
import os
from wsgiref.util import setup_testing_defaults

os.environ.setdefault("DATABASE_URL", "postgresql://unused")
os.environ.setdefault("MINIO_ENDPOINT", "http://minio:9000")
os.environ.setdefault("MINIO_ROOT_USER", "test")
os.environ.setdefault("MINIO_ROOT_PASSWORD", "test")

from services.memory.app import create_app
from services.memory.phase1b.chunking import chunk_text, normalize_text
from services.memory.phase1b.config import Phase1BSettings
from services.memory.phase1b.qdrant import QdrantAdapter


def request(app, method, path, payload=b"", headers=None):
    environ = {}; setup_testing_defaults(environ); environ.update({"REQUEST_METHOD": method, "PATH_INFO": path.split("?", 1)[0], "QUERY_STRING": path.partition("?")[2], "CONTENT_TYPE": "application/json", "CONTENT_LENGTH": str(len(payload)), "wsgi.input": io.BytesIO(payload)})
    environ.update(headers or {}); captured = {}
    body = b"".join(app(environ, lambda status, response_headers: captured.update(status=status, headers=response_headers)))
    return int(captured["status"][:3]), json.loads(body or b"{}")


def test_phase1b_config_and_deterministic_chunk_pipeline():
    settings = Phase1BSettings.from_env({"EMBEDDING_PROFILE_REGISTRY": json.dumps({"bge-m3@v1": {"provider": "bge-m3", "model_id": "bge-m3", "model_version": "v1", "dimension": 1024, "max_input_tokens": 8192}})})
    assert settings.profiles["bge-m3@v1"].dimension == 1024
    assert normalize_text("A\r\nB\x00") == "A\nB"
    assert chunk_text("memory-1", 1, "one two three four", 2, 1) == chunk_text("memory-1", 1, "one two three four", 2, 1)


def test_qdrant_filter_always_enforces_authorized_owner():
    payload = QdrantAdapter.filter_for(["finance"], ["plan"], "manual", "2026-01-01T00:00:00Z", "current")
    assert payload["must"][0] == {"key": "owner", "match": {"any": ["finance"]}}
    assert payload["must_not"][0]["key"] == "memory_id"
    try: QdrantAdapter.filter_for([])
    except PermissionError: pass
    else: assert False, "owner filtering must never be optional"


class FakeMemory: pass
class FakeRetrieval:
    def vector_search(self, **kwargs):
        return {"query_id": "query-1", "embedding_profile": "bge-m3@v1", "results": [{"memory_id": "m2", "score": .9}], "owners_seen": list(kwargs["owners"])}
    def related(self, **kwargs): return {"memory_id": kwargs["memory_id"], "results": []}


def test_vector_api_uses_trusted_owner_claim_and_related_skeleton():
    app = create_app(FakeMemory(), FakeRetrieval())
    payload = json.dumps({"query": "plan", "filters": {"owners": ["finance"]}}).encode()
    status, body = request(app, "POST", "/api/v1/search/vector", payload, {"HTTP_X_VAFOX_AUTHORIZED_OWNERS": "finance,hr"})
    assert status == 200 and body["owners_seen"] == ["finance"]
    denied = json.dumps({"query": "plan", "filters": {"owners": ["engineering"]}}).encode()
    assert request(app, "POST", "/api/v1/search/vector", denied, {"HTTP_X_VAFOX_AUTHORIZED_OWNERS": "finance"})[0] == 403
    assert request(app, "POST", "/api/v1/search/vector", payload)[0] == 401
    assert request(app, "GET", "/api/v1/memory/m1/related?top_k=5", headers={"HTTP_X_VAFOX_AUTHORIZED_OWNERS": "finance"})[0] == 200
