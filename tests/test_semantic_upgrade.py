from services.memory.phase1b.config import EmbeddingProfile
from services.memory.phase1b.semantic_upgrade import SEMANTIC_V2_COLLECTION, SemanticV2Reindexer


class Memory:
    def iter_active(self):
        yield {"id": "one", "owner_id": "alice", "updated_at": "v1"}
    def content(self, memory_id):
        assert memory_id == "one"
        return ({"name": "sales.md", "type": "text/markdown", "source": "crm", "tags": ["sales"], "organization_id": "org-1", "department_id": "sales", "owner_id": "alice", "role_scope": "private", "visibility": "private"}, b"# Sales\nRecommend the premium product bundle.")


class Embeddings:
    def embed_batch(self, texts): return [[0.1, 0.2, 0.3] for _ in texts]


class Qdrant:
    collection_alias = "memory_chunks_v1"
    def __init__(self): self.created = []; self.points = []; self.switched = []
    def collections(self): return [{"name": "memory_chunks_v1__default"}]
    def create_collection(self, collection, dimension, distance): self.created.append((collection, dimension, distance))
    def upsert(self, points, collection=None):
        assert collection == SEMANTIC_V2_COLLECTION
        self.points.extend(points)
    def count(self, collection): return len(self.points) if collection == SEMANTIC_V2_COLLECTION else 0
    def switch_alias(self, collection): self.switched.append(collection)


def test_semantic_v2_reindex_creates_new_collection_verifies_then_switches_alias():
    qdrant = Qdrant()
    profile = EmbeddingProfile("semantic_v2", "bge-m3", "bge-m3", "v2", 3, 8192)
    result = SemanticV2Reindexer(Memory(), Embeddings(), qdrant, profile, chunk_size=100).run(switch_alias=True)
    assert qdrant.created == [("memory_chunks_v2", 3, "Cosine")]
    assert result.verified and result.switched and result.chunks == len(qdrant.points)
    assert qdrant.switched == ["memory_chunks_v2"]


def test_semantic_v2_never_overwrites_an_existing_collection():
    qdrant = Qdrant(); qdrant.collections = lambda: [{"name": "memory_chunks_v2"}]
    profile = EmbeddingProfile("semantic_v2", "hunyuan", "hunyuan-embedding", "v1", 3, 8192)
    try: SemanticV2Reindexer(Memory(), Embeddings(), qdrant, profile).run()
    except ValueError as error: assert "refuse to overwrite" in str(error)
    else: assert False
