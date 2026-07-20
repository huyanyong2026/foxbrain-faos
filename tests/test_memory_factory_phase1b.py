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


def test_qdrant_collection_alias_point_lifecycle_and_health():
    calls = []
    def transport(method, path, payload):
        calls.append((method, path, payload))
        if path == "/collections": return {"result": {"collections": [{"name": "memory_chunks_v1__default"}]}}
        if path == "/healthz": return {"result": {"title": "qdrant"}}
        if path.endswith("/points/search"): return {"result": [{"id": "p1", "score": .9, "payload": {"owner": "finance"}}]}
        return {"result": True}
    adapter = QdrantAdapter("http://qdrant.test", request=transport)
    initialized = adapter.initialize(3)
    assert initialized["collection"] == "memory_chunks_v1__default"
    assert initialized["alias"] == "memory_chunks_v1"
    assert ("POST", "/aliases", {"actions": [{"create_alias": {"collection_name": "memory_chunks_v1__default", "alias_name": "memory_chunks_v1"}}]}) in calls
    adapter.switch_alias("memory_chunks_v2__default")
    assert ("POST", "/aliases", {"actions": [{"delete_alias": {"alias_name": "memory_chunks_v1"}}, {"create_alias": {"collection_name": "memory_chunks_v2__default", "alias_name": "memory_chunks_v1"}}]}) in calls
    payload = {"memory_id": "m1", "chunk_id": "c1", "owner": "finance", "tags": ["plan"], "source": "manual", "created_at": "2026-07-20T00:00:00Z", "content_hash": "a" * 64, "embedding_profile": "bge-m3@v1"}
    adapter.upsert([{"id": adapter.point_id("c1", "bge-m3@v1"), "vector": [.1, .2, .3], "payload": payload}])
    adapter.search([.1, .2, .3], ["finance"], 1)
    adapter.delete(memory_id="m1")
    assert adapter.collections()[0]["name"] == "memory_chunks_v1__default"
    assert adapter.health()["status"] == "ok"
    assert any(method == "PUT" and "/points?wait=true" in path for method, path, _ in calls)
    assert any(method == "POST" and path.endswith("/points/delete?wait=true") for method, path, _ in calls)


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


class FakeQdrant:
    collection_alias = "memory_chunks_v1"
    def health(self): return {"status": "ok", "qdrant": {"title": "qdrant"}}
    def collections(self): return [{"name": "memory_chunks_v1__default"}]
    def initialize(self, dimension, collection, distance): return {"collection": collection or "memory_chunks_v1__default", "alias": self.collection_alias, "dimension": dimension, "distance": distance}


def test_vector_foundation_api_is_explicitly_injected():
    app = create_app(FakeMemory(), qdrant_client=FakeQdrant())
    assert request(app, "GET", "/health/vector")[0] == 200
    status, body = request(app, "GET", "/collections")
    assert status == 200 and body["alias"] == "memory_chunks_v1"
    status, body = request(app, "POST", "/collections/init", json.dumps({"dimension": 1024}).encode())
    assert status == 201 and body["dimension"] == 1024
    assert request(create_app(FakeMemory()), "GET", "/health/vector")[0] == 503
