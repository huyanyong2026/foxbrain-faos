"""Read-only Dify adapter; it owns no Qdrant client or write capability."""
from __future__ import annotations
import hmac

class DifyAdapter:
    def __init__(self, retrieval, credentials: dict[str, tuple[str, ...]]):
        self.retrieval, self.credentials = retrieval, credentials
    def retrieve(self, token, query, top_k=5, filters=None):
        owners = next((scope for credential, scope in self.credentials.items() if hmac.compare_digest(token or "", credential)), None)
        if owners is None: raise PermissionError("invalid_service_credential")
        filters = filters or {}
        result = self.retrieval.vector_search(query=query, top_k=top_k, owners=owners, tags_any=tuple(filters.get("tags", ())), source=filters.get("source"), include_text=True)
        records = [{"content": row["content"], "score": row["score"], "title": row["document_title"], "source": row["source"], "metadata": {"memory_id": row["memory_id"], "chunk_id": row["chunk_id"], "page": row["page"], "section": row["section"], "tags": row["tags"]}, "citation": row["citation"]} for row in result["results"]]
        return {"records": records, "query": query, "elapsed_ms": result["elapsed_ms"]}
