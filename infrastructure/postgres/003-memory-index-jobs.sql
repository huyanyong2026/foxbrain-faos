-- Phase 1B async index-job ledger.  It does not alter Phase 1A tables.
CREATE TABLE IF NOT EXISTS memory_index_jobs (
 id UUID PRIMARY KEY, memory_id UUID NOT NULL REFERENCES memory_items(id), owner TEXT NOT NULL,
 status TEXT NOT NULL CHECK (status IN ('pending','processing','completed','failed','cancelled')),
 embedding_profile TEXT NOT NULL, chunk_profile TEXT NOT NULL, source_version TEXT NOT NULL,
 attempt_count INTEGER NOT NULL DEFAULT 0, error_code TEXT, error_message TEXT, chunk_count INTEGER NOT NULL DEFAULT 0,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(), started_at TIMESTAMPTZ, completed_at TIMESTAMPTZ, updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 UNIQUE(memory_id, source_version, embedding_profile, chunk_profile)
);
CREATE INDEX IF NOT EXISTS memory_index_jobs_memory_idx ON memory_index_jobs(memory_id, updated_at DESC);
