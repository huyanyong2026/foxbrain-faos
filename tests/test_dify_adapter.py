from services.memory.phase1b.dify_adapter import DifyAdapter

class Retrieval:
    def vector_search(self, **kwargs):
        assert kwargs["owners"] == ("org-a",)
        return {"elapsed_ms": 1, "results": [{"content": "policy", "score": .8, "document_title": "Handbook", "source": "manual", "memory_id": "m", "chunk_id": "c", "page": 1, "section": "leave", "tags": [], "citation": {"memory_id": "m", "chunk_id": "c"}}]}

def test_adapter_is_read_only_and_preserves_dify_citations():
    response = DifyAdapter(Retrieval(), {"rotatable-secret": ("org-a",)}).retrieve("rotatable-secret", "leave")
    assert response["records"][0]["metadata"]["chunk_id"] == "c"
    try: DifyAdapter(Retrieval(), {"x": ("org-a",)}).retrieve("bad", "leave")
    except PermissionError: pass
    else: assert False
