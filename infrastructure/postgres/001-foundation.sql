-- Foundation-only schema. Business tables intentionally do not belong here.
CREATE TABLE IF NOT EXISTS service_bootstrap (
  service_name TEXT PRIMARY KEY,
  initialized_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
