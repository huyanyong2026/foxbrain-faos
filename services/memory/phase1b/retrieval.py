"""Narrow retrieval facade that keeps Qdrant authorization filtering server-side."""
from __future__ import annotations

from .embedding import EmbedInput, EmbedRequest


class RetrievalService:
    def __init__(self, embedding_provider, qdrant, profile_id: str):
        self.embedding_provider = embedding_provider
        self.qdrant = qdrant
        self.profile_id = profile_id

    def vector_search(self, query, top_k, owners, tags_any=(), source=None, created_at_gte=None,
                      include_text=False, embedding_profile=None):
        if embedding_profile and embedding_profile != self.profile_id:
            raise RuntimeError("embedding_profile_not_available")
        response = self.embedding_provider.embed(EmbedRequest(self.profile_id, (EmbedInput("query", query),), "query", "query"))
        vector = response.vectors.get("query")
        if not vector:
            raise RuntimeError("query_embedding_failed")
        points = self.qdrant.search(vector, owners, top_k, tags_any=tags_any, source=source, created_at_gte=created_at_gte)
        results = [{"memory_id": row["payload"]["memory_id"], "chunk_id": row["payload"]["chunk_id"],
                    "score": row["score"], "metadata": row["payload"]} for row in points]
        return {"embedding_profile": self.profile_id, "results": results}
