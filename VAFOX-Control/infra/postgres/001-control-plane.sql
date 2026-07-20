-- V1 canonical PostgreSQL schema. Migration is intentionally not executed by this scaffold.
CREATE TYPE lifecycle_status AS ENUM ('pending', 'active', 'disabled', 'retired');
CREATE TYPE health_status AS ENUM ('unknown', 'healthy', 'degraded', 'unhealthy');

CREATE TABLE servers (
  id UUID PRIMARY KEY, name TEXT NOT NULL UNIQUE, environment TEXT NOT NULL,
  region TEXT NOT NULL, endpoint TEXT NOT NULL, labels JSONB NOT NULL DEFAULT '{}',
  status lifecycle_status NOT NULL DEFAULT 'pending', health_status health_status NOT NULL DEFAULT 'unknown',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE services (
  id UUID PRIMARY KEY, server_id UUID NOT NULL REFERENCES servers(id), name TEXT NOT NULL,
  version TEXT NOT NULL, endpoint TEXT NOT NULL, capabilities JSONB NOT NULL DEFAULT '[]',
  status lifecycle_status NOT NULL DEFAULT 'pending', health_status health_status NOT NULL DEFAULT 'unknown',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(), UNIQUE(server_id, name)
);
CREATE TABLE deployments (
  id UUID PRIMARY KEY, service_id UUID NOT NULL REFERENCES services(id), version TEXT NOT NULL,
  artifact_digest TEXT NOT NULL, environment TEXT NOT NULL, change_reference TEXT NOT NULL,
  status lifecycle_status NOT NULL DEFAULT 'pending', created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE health_checks (
  id UUID PRIMARY KEY, resource_kind TEXT NOT NULL CHECK (resource_kind IN ('server', 'service')),
  resource_id UUID NOT NULL, status health_status NOT NULL, latency_ms INTEGER,
  detail TEXT, checked_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX health_checks_resource_checked_idx ON health_checks(resource_kind, resource_id, checked_at DESC);
