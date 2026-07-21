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
from services.memory.phase1b.indexing import InMemoryIndexJobs, IndexWorker
from services.memory.phase1b.retrieval import RetrievalService
from services.memory.acl import AuthContext


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


def test_qdrant_filter_always_enforces_enterprise_permission_scope():
    context = AuthContext("org-1", "finance", "finance-user", frozenset())
    payload = QdrantAdapter.filter_for(context, ["plan"], "manual", "2026-01-01T00:00:00Z", "current")
    assert payload["must"][0] == {"key": "organization_id", "match": {"value": "org-1"}}
    assert payload["must_not"][0]["key"] == "memory_id"
    try: QdrantAdapter.filter_for(None)
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
    adapter.search([.1, .2, .3], AuthContext("org-1", "finance", "finance", frozenset()), 1)
    adapter.delete(memory_id="m1")
    assert adapter.collections()[0]["name"] == "memory_chunks_v1__default"
    assert adapter.health()["status"] == "ok"
    assert any(method == "PUT" and "/points?wait=true" in path for method, path, _ in calls)
    assert any(method == "POST" and path.endswith("/points/delete?wait=true") for method, path, _ in calls)


class FakeMemory: pass
class FakeRetrieval:
    def vector_search(self, **kwargs):
        return {"query_id": "query-1", "embedding_profile": "bge-m3@v1", "results": [{"memory_id": "m2", "score": .9}], "context_owner": kwargs["context"].owner_id}
    def related(self, **kwargs): return {"memory_id": kwargs["memory_id"], "results": []}


def test_vector_api_uses_trusted_auth_context_and_ignores_client_owner_filter():
    app = create_app(FakeMemory(), FakeRetrieval())
    payload = json.dumps({"query": "plan", "filters": {"owners": ["finance"]}}).encode()
    headers = {"HTTP_X_VAFOX_ORGANIZATION_ID": "org-1", "HTTP_X_VAFOX_DEPARTMENT_ID": "finance", "HTTP_X_VAFOX_USER_ID": "finance-user"}
    status, body = request(app, "POST", "/api/v1/search/vector", payload, headers)
    assert status == 200 and body["context_owner"] == "finance-user"
    denied = json.dumps({"query": "plan", "filters": {"owners": ["engineering"]}}).encode()
    assert request(app, "POST", "/api/v1/search/vector", denied, headers)[0] == 200
    assert request(app, "POST", "/api/v1/search/vector", payload)[0] == 401


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


class PipelineMemory:
    def content(self, memory_id):
        return ({"name": "strategy.md", "type": "text/markdown", "source": "upload", "tags": ["plan"], "organization_id": "org-1", "department_id": "strategy", "owner_id": "alice", "role_scope": "private", "visibility": "private"}, b"# Strategy\nRevenue plan is approved.\n")


class PipelineEmbedding:
    def embed(self, text): return [float(len(text)), 1.0]
    def embed_batch(self, texts): return [self.embed(text) for text in texts]


class PipelineQdrant:
    collection_alias = "memory_chunks_v1"
    def __init__(self): self.points = []; self.initialized = []
    def ensure_initialized(self, dimension): self.initialized.append(dimension)
    def upsert(self, points): self.points.extend(points)
    def search(self, vector, context, limit, **filters):
        return [{"score": .99, "payload": point["payload"]} for point in self.points if point["payload"]["owner_id"] == context.owner_id][:limit]


def test_real_worker_indexes_chunks_and_returns_complete_citation():
    jobs, store, embedding = InMemoryIndexJobs(), PipelineQdrant(), PipelineEmbedding()
    job, _ = jobs.create("m-strategy", "alice", "openai@v1", "recursive-whitespace-v2", "rev-1")
    completed = IndexWorker(PipelineMemory(), jobs, embedding, store, "openai@v1", chunk_size=3, overlap=1).run(job.id)
    assert completed.status == "completed" and completed.chunk_count > 0 and store.initialized == [2]
    payload = store.points[0]["payload"]
    assert {"chunk_id", "memory_id", "content", "offset", "token_count", "content_hash", "page", "section", "owner", "tags"} <= set(payload)
    result = RetrievalService(embedding, store, "openai@v1").vector_search("Revenue", 1, AuthContext("org-1", "strategy", "alice", frozenset()))
    assert result["results"][0]["citation"] == {"document_name": "strategy.md", "page": None, "section": "Strategy", "chunk_id": payload["chunk_id"], "source": "upload"}
    assert RetrievalService(embedding, store, "openai@v1").vector_search("Revenue", 1, AuthContext("org-1", "strategy", "bob", frozenset()))["results"] == []
