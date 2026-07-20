-- V1 canonical PostgreSQL schema. Migration is intentionally not executed by this scaffold.
CREATE TYPE lifecycle_status AS ENUM ('pending', 'active', 'disabled', 'retired');
CREATE TYPE health_status AS ENUM ('unknown', 'healthy', 'degraded', 'unhealthy');
CREATE TYPE orchestrator_executor AS ENUM ('codex', 'workbuddy', 'marvis');
CREATE TYPE task_result_type AS ENUM ('codex_pr', 'deployment_report', 'status_report');
CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE test_result AS ENUM ('not_run', 'passed', 'failed', 'partial');
CREATE TYPE review_status AS ENUM ('pending_review', 'approved');

CREATE TABLE servers (
  id UUID PRIMARY KEY, hostname TEXT NOT NULL UNIQUE, ip INET NOT NULL,
  provider TEXT NOT NULL, role TEXT NOT NULL,
  status lifecycle_status NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE services (
  id UUID PRIMARY KEY, server_id UUID NOT NULL REFERENCES servers(id), service_name TEXT NOT NULL,
  version TEXT NOT NULL, health_status health_status NOT NULL DEFAULT 'unknown',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(), UNIQUE(server_id, service_name)
);
CREATE TABLE deployments (
  id UUID PRIMARY KEY, version TEXT NOT NULL, deploy_time TIMESTAMPTZ NOT NULL,
  operator TEXT NOT NULL, rollback_version TEXT
);
CREATE TABLE health_checks (
  id UUID PRIMARY KEY, resource_kind TEXT NOT NULL CHECK (resource_kind IN ('server', 'service')),
  resource_id UUID NOT NULL, status health_status NOT NULL, latency_ms INTEGER,
  detail TEXT, checked_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX health_checks_resource_checked_idx ON health_checks(resource_kind, resource_id, checked_at DESC);

-- Result reporting and review metadata only. No executor connection is modeled here.
CREATE TABLE task_results (
  id UUID PRIMARY KEY, task_id TEXT NOT NULL, executor orchestrator_executor NOT NULL,
  result_type task_result_type NOT NULL, summary TEXT NOT NULL,
  artifact_url TEXT, log_url TEXT, test_result test_result NOT NULL DEFAULT 'not_run',
  risk_level risk_level NOT NULL DEFAULT 'medium', created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX task_results_task_created_idx ON task_results(task_id, created_at DESC);
CREATE TABLE reviews (
  id UUID PRIMARY KEY REFERENCES task_results(id), status review_status NOT NULL DEFAULT 'pending_review',
  approved_at TIMESTAMPTZ
);
