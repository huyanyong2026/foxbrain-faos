"""Enterprise retrieval facade: authorization is always delegated to Qdrant filters."""
from __future__ import annotations
import hashlib
import time

class RetrievalService:
    def __init__(self, embedding_provider, qdrant, profile_id, content_resolver=None):
        self.embedding_provider, self.qdrant, self.profile_id = embedding_provider, qdrant, profile_id
        self.content_resolver = content_resolver or (lambda memory_id, chunk_id: "")

    def vector_search(self, query, top_k, context, tags_any=(), source=None, created_at_gte=None,
                      created_at_lte=None, exclude_memory_id=None, memory_id=None, include_text=True, embedding_profile=None):
        if embedding_profile and embedding_profile != self.profile_id: raise RuntimeError("embedding_unavailable")
        if not isinstance(tags_any, (list, tuple)) or not all(isinstance(v, str) for v in tags_any): raise ValueError("invalid_filter")
        started = time.monotonic()
        try: vector = self.embedding_provider.embed(query)
        except Exception as error: raise RuntimeError("embedding_unavailable") from error
        try: points = self.qdrant.search(vector, context, top_k, tags_any=tags_any, source=source, created_at_gte=created_at_gte, created_at_lte=created_at_lte, exclude_memory_id=exclude_memory_id, memory_id=memory_id)
        except Exception as error: raise RuntimeError("vector_store_unavailable") from error
        results = []
        for row in points:
            p = row["payload"]; mid, cid = p["memory_id"], p["chunk_id"]
            content = (self.content_resolver(mid, cid) or p.get("content", "")) if include_text else ""
            citation = {"document_name": p.get("document_name", ""), "page": p.get("page"),
                        "section": p.get("section"), "chunk_id": cid, "source": p["source"]}
            results.append({"memory_id": mid, "chunk_id": cid, "content": content, "score": row["score"], "source": p["source"], "document_name": p.get("document_name", ""), "page": p.get("page"), "section": p.get("section"), "tags": p["tags"], "created_at": p["created_at"], "citation": citation})
        return {"query": query, "query_hash": hashlib.sha256(query.encode()).hexdigest(), "results": results, "top_k": top_k, "embedding_profile": self.profile_id, "collection_alias": self.qdrant.collection_alias, "elapsed_ms": round((time.monotonic() - started) * 1000, 2)}

    def related(self, memory_id, top_k, context, embedding_profile=None):
        # A resolver may expose the representative source chunk as text in a future composition.
        raise KeyError(memory_id)
