-- VAFOX Orchestrator V1 local bootstrap schema.
-- This script initializes only the local Compose PostgreSQL volume. It creates
-- registry metadata tables and does not configure any external integration.

DO $$
BEGIN
  CREATE TYPE lifecycle_status AS ENUM ('pending', 'active', 'disabled', 'retired');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
  CREATE TYPE health_status AS ENUM ('unknown', 'healthy', 'degraded', 'unhealthy');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS servers (
  id UUID PRIMARY KEY,
  hostname TEXT NOT NULL UNIQUE,
  ip INET NOT NULL,
  provider TEXT NOT NULL,
  role TEXT NOT NULL,
  status lifecycle_status NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS services (
  id UUID PRIMARY KEY,
  server_id UUID NOT NULL REFERENCES servers(id),
  service_name TEXT NOT NULL,
  version TEXT NOT NULL,
  health_status health_status NOT NULL DEFAULT 'unknown',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(server_id, service_name)
);

CREATE TABLE IF NOT EXISTS deployments (
  id UUID PRIMARY KEY,
  version TEXT NOT NULL,
  deploy_time TIMESTAMPTZ NOT NULL,
  operator TEXT NOT NULL,
  rollback_version TEXT
);

CREATE TABLE IF NOT EXISTS health_checks (
  id UUID PRIMARY KEY,
  resource_kind TEXT NOT NULL CHECK (resource_kind IN ('server', 'service')),
  resource_id UUID NOT NULL,
  status health_status NOT NULL,
  latency_ms INTEGER,
  detail TEXT,
  checked_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS health_checks_resource_checked_idx
  ON health_checks(resource_kind, resource_id, checked_at DESC);
