-- VAFOX Memory Factory V1 migration. This schema contains no SAP, Core, or business-domain data.
CREATE TABLE IF NOT EXISTS schema_migrations (
  version TEXT PRIMARY KEY,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS memory_items (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  size BIGINT NOT NULL CHECK (size >= 0),
  source TEXT NOT NULL,
  owner TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  storage_path TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'deleted')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS memory_items_name_search_idx ON memory_items USING GIN (to_tsvector('simple', name));
CREATE INDEX IF NOT EXISTS memory_items_metadata_search_idx ON memory_items USING GIN (metadata);
CREATE INDEX IF NOT EXISTS memory_items_owner_idx ON memory_items (owner);

-- Enterprise ACL fields are additive so deployments with Phase 1A data remain valid.
ALTER TABLE memory_items ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'legacy';
ALTER TABLE memory_items ADD COLUMN IF NOT EXISTS department_id TEXT;
ALTER TABLE memory_items ADD COLUMN IF NOT EXISTS owner_id TEXT NOT NULL DEFAULT 'legacy';
ALTER TABLE memory_items ADD COLUMN IF NOT EXISTS role_scope TEXT NOT NULL DEFAULT 'owner';
ALTER TABLE memory_items ADD COLUMN IF NOT EXISTS visibility TEXT NOT NULL DEFAULT 'private'
  CHECK (visibility IN ('private', 'department', 'organization'));
CREATE INDEX IF NOT EXISTS memory_items_acl_idx ON memory_items (organization_id, department_id, owner_id, visibility);

CREATE TABLE IF NOT EXISTS storage_objects (
  id UUID PRIMARY KEY,
  memory_id UUID NOT NULL REFERENCES memory_items(id) ON DELETE CASCADE,
  storage_path TEXT NOT NULL UNIQUE,
  bucket TEXT NOT NULL,
  size BIGINT NOT NULL CHECK (size >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS storage_objects_memory_id_idx ON storage_objects (memory_id);

CREATE TABLE IF NOT EXISTS memory_tags (
  memory_id UUID NOT NULL REFERENCES memory_items(id) ON DELETE CASCADE,
  tag TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (memory_id, tag)
);

INSERT INTO schema_migrations(version) VALUES ('002-memory-factory') ON CONFLICT DO NOTHING;
INSERT INTO schema_migrations(version) VALUES ('004-memory-enterprise-acl') ON CONFLICT DO NOTHING;
