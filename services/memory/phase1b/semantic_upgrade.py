"""Side-by-side semantic_v2 reindexing with a guarded Qdrant alias cutover."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .indexing import InMemoryIndexJobs, IndexWorker


SEMANTIC_V2_PROFILE = "semantic_v2"
SEMANTIC_V2_COLLECTION = "memory_chunks_v2"


@dataclass(frozen=True)
class ReindexResult:
    collection: str
    profile: str
    memories: int
    chunks: int
    verified: bool
    switched: bool
    completed_at: str


class SemanticV2Reindexer:
    """Rebuild a new collection and only then atomically move the live alias.

    The source alias/collection is never written to or deleted.  Any failure
    before ``switch_alias`` leaves production retrieval on the old index.
    """
    def __init__(self, memory_service, embedding_provider, qdrant, profile, *, collection=SEMANTIC_V2_COLLECTION,
                 chunk_size=384, overlap=64, batch_size=32):
        if profile.id != SEMANTIC_V2_PROFILE:
            raise ValueError("semantic_v2 embedding profile is required")
        if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
            raise ValueError("invalid semantic_v2 chunk limits")
        self.memory_service, self.embedding_provider, self.qdrant = memory_service, embedding_provider, qdrant
        self.profile, self.collection = profile, collection
        self.chunk_size, self.overlap, self.batch_size = chunk_size, overlap, batch_size

    def run(self, *, switch_alias=False) -> ReindexResult:
        existing = {item.get("name") for item in self.qdrant.collections()}
        if self.collection in existing:
            raise ValueError("semantic_v2 collection already exists; refuse to overwrite")
        self.qdrant.create_collection(self.collection, self.profile.dimension, self.profile.distance)
        jobs = InMemoryIndexJobs(); memories = chunks = 0
        worker = IndexWorker(self.memory_service, jobs, self.embedding_provider, self.qdrant, self.profile.id,
                             chunk_size=self.chunk_size, overlap=self.overlap, batch_size=self.batch_size,
                             target_collection=self.collection)
        for item in self.memory_service.iter_active():
            job, _ = jobs.create(item["id"], item["owner_id"], self.profile.id, "semantic-v2-recursive-whitespace", item["updated_at"])
            job = worker.run(job.id)
            if job.status != "completed":
                raise RuntimeError(f"reindex_failed:{item['id']}:{job.error_code}")
            memories += 1; chunks += job.chunk_count
        verified = self.qdrant.count(self.collection) == chunks
        if not verified:
            raise RuntimeError("semantic_v2_verification_failed")
        if switch_alias:
            self.qdrant.switch_alias(self.collection)
        return ReindexResult(self.collection, self.profile.id, memories, chunks, verified, switch_alias,
                             datetime.now(timezone.utc).isoformat())
