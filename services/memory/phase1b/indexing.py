"""Asynchronous, idempotent Phase 1B document indexing pipeline.

The HTTP API only creates jobs.  A separately composed worker calls ``run``;
there is deliberately no embedding work on the upload request path.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

from .chunking import chunk_text, normalize_text
from .qdrant import QdrantAdapter


class IndexingError(RuntimeError): pass

def extract_text(raw: bytes, media_type: str, name: str) -> tuple[str, list[dict]]:
    """Return text and optional source locations; binary parsers stay optional."""
    suffix = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if media_type.startswith("text/") or suffix in {"txt", "md", "markdown"}:
        return raw.decode("utf-8"), []
    if suffix in {"pdf", "docx"}:
        raise IndexingError("extract_failed")
    if suffix in {"xls", "xlsx"}:
        raise IndexingError("unsupported_file_type")
    raise IndexingError("unsupported_file_type")


@dataclass
class IndexJob:
    id: str; memory_id: str; owner: str; status: str; embedding_profile: str; chunk_profile: str
    source_version: str; attempt_count: int = 0; error_code: str | None = None; error_message: str | None = None
    chunk_count: int = 0; created_at: str = ""; updated_at: str = ""


class InMemoryIndexJobs:
    """Small queue contract used by tests and local workers; replaceable by Redis/Postgres."""
    def __init__(self): self.jobs = {}; self.keys = {}; self.queue = []
    def create(self, memory_id, owner, embedding_profile, chunk_profile, source_version, force=False):
        key = (memory_id, source_version, embedding_profile, chunk_profile)
        if key in self.keys and not force: return self.jobs[self.keys[key]], False
        import uuid
        now = datetime.now(timezone.utc).isoformat(); job = IndexJob(str(uuid.uuid4()), memory_id, owner, "pending", embedding_profile, chunk_profile, source_version, created_at=now, updated_at=now)
        self.jobs[job.id] = job; self.keys[key] = job.id; self.queue.append(job.id); return job, True
    def get(self, job_id): return self.jobs.get(job_id)


class IndexWorker:
    def __init__(self, memory_service, jobs, embedding_provider, qdrant, profile_id, chunk_size=512, overlap=64, batch_size=32, max_chunks=10000):
        self.memory_service, self.jobs, self.embedding_provider, self.qdrant = memory_service, jobs, embedding_provider, qdrant
        self.profile_id, self.chunk_size, self.overlap, self.batch_size, self.max_chunks = profile_id, chunk_size, overlap, batch_size, max_chunks
    def run(self, job_id):
        job = self.jobs.get(job_id)
        if not job: raise KeyError(job_id)
        job.status = "processing"; job.attempt_count += 1; job.updated_at = datetime.now(timezone.utc).isoformat()
        try:
            item, raw = self.memory_service.content(job.memory_id) or (None, None)
            if not item: raise IndexingError("memory_not_found")
            text, _ = extract_text(raw, item["type"], item["name"]); text = normalize_text(text)
            if not text.strip(): raise IndexingError("empty_document")
            chunks = chunk_text(job.memory_id, job.source_version, text, self.chunk_size, self.overlap)
            if len(chunks) > self.max_chunks: raise IndexingError("document_too_large")
            now = datetime.now(timezone.utc).isoformat(); points = []
            for start in range(0, len(chunks), self.batch_size):
                batch = chunks[start:start + self.batch_size]; vectors = self.embedding_provider.embed_batch([c.text for c in batch])
                if len(vectors) != len(batch): raise IndexingError("embedding_failed")
                for chunk, vector in zip(batch, vectors):
                    if not isinstance(vector, list) or not vector: raise IndexingError("dimension_mismatch")
                    payload = {"memory_id": job.memory_id, "chunk_id": chunk.id, "owner": job.owner, "tags": item["tags"], "source": item["source"], "created_at": now, "content_hash": chunk.content_sha256, "embedding_profile": job.embedding_profile}
                    points.append({"id": QdrantAdapter.point_id(chunk.id, job.embedding_profile), "vector": vector, "payload": payload})
                self.qdrant.upsert(points); points = []
            job.status, job.chunk_count, job.error_code = "completed", len(chunks), None
        except IndexingError as error: job.status, job.error_code = "failed", str(error)
        except Exception: job.status, job.error_code = "failed", "index_failed"
        job.updated_at = datetime.now(timezone.utc).isoformat(); return job
