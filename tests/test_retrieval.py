from services.memory.phase1b.retrieval import RetrievalService

class Embedding:
    def embed(self, query): return [0.1, 0.2]
class Qdrant:
    collection_alias = "memory_chunks_v1"
    def __init__(self): self.owners = None
    def search(self, vector, owners, limit, **filters):
        self.owners = owners
        return [{"score": .9, "payload": {"memory_id": "m1", "chunk_id": "c1", "owner": "A", "tags": ["policy"], "source": "handbook", "created_at": "2026-01-01T00:00:00Z"}}]

def test_retrieval_returns_citations_and_forces_server_owner_scope():
    qdrant = Qdrant(); service = RetrievalService(Embedding(), qdrant, "p1", lambda m, c: "approved content")
    response = service.vector_search("where", 5, ("A",), tags_any=("policy",))
    assert qdrant.owners == ("A",) and response["results"][0]["citation"]["chunk_id"] == "c1"
    assert response["results"][0]["content"] == "approved content"

def test_embedding_failure_is_safe_503_contract():
    class Broken: 
        def embed(self, query): raise TimeoutError()
    try: RetrievalService(Broken(), Qdrant(), "p1").vector_search("q", 1, ("A",))
    except RuntimeError as error: assert str(error) == "embedding_unavailable"
    else: assert False
