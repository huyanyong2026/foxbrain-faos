-- Sprint 1 PostgreSQL persistence contract.  The application remains read-only
-- with respect to SAP B1; audit events are append-only.
create table if not exists foxbrain_users (
  id text primary key, username text unique not null, password_hash text not null,
  identity_type text not null check (identity_type in ('human', 'ai_employee', 'system')),
  created_at timestamptz not null default now()
);
create table if not exists foxbrain_user_roles (
  user_id text not null references foxbrain_users(id), role_key text not null,
  primary key (user_id, role_key)
);
create table if not exists foxbrain_data_scopes (
  user_id text not null references foxbrain_users(id), scope_type text not null,
  scope_value text not null, primary key (user_id, scope_type, scope_value)
);
create table if not exists foxbrain_audit_events (
  id text primary key, event_type text not null, actor_id text, details jsonb not null,
  created_at timestamptz not null default now()
);
