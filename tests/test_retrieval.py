from services.memory.phase1b.retrieval import RetrievalService
from services.memory.acl import AuthContext

class Embedding:
    def embed(self, query): return [0.1, 0.2]
class Qdrant:
    collection_alias = "memory_chunks_v1"
    def __init__(self): self.context = None
    def search(self, vector, context, limit, **filters):
        self.context = context
        return [{"score": .9, "payload": {"memory_id": "m1", "chunk_id": "c1", "owner": "A", "tags": ["policy"], "source": "handbook", "created_at": "2026-01-01T00:00:00Z"}}]

def test_retrieval_returns_citations_and_forces_server_permission_scope():
    qdrant = Qdrant(); service = RetrievalService(Embedding(), qdrant, "p1", lambda m, c: "approved content")
    context = AuthContext("org-1", "finance", "A", frozenset())
    response = service.vector_search("where", 5, context, tags_any=("policy",))
    assert qdrant.context == context and response["results"][0]["citation"]["chunk_id"] == "c1"
    assert response["results"][0]["content"] == "approved content"

def test_embedding_failure_is_safe_503_contract():
    class Broken: 
        def embed(self, query): raise TimeoutError()
    try: RetrievalService(Broken(), Qdrant(), "p1").vector_search("q", 1, AuthContext("org-1", None, "A", frozenset()))
    except RuntimeError as error: assert str(error) == "embedding_unavailable"
    else: assert False
