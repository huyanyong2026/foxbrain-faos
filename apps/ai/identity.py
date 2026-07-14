"""FireFox Identity Center domain model and permission rules."""

from __future__ import annotations

import json


ROLE_DEFINITIONS = {
    "ceo": {
        "name": "CEO",
        "permissions": ["*"],
        "scope": "company",
    },
    "management": {
        "name": "管理层",
        "permissions": [
            "ai.use", "ai.business", "ai.inventory", "ai.brand", "ai.enterprise",
            "business.read", "brand.read", "store.read", "inventory.read",
            "knowledge.read", "knowledge.write", "tasks.read", "tasks.create",
            "approvals.manage", "identity.view",
        ],
        "scope": "company",
    },
    "store_manager": {
        "name": "店长",
        "permissions": [
            "ai.use", "ai.business", "ai.inventory", "business.read", "store.read",
            "inventory.read", "replenishment.read", "employee_growth.read",
            "product.read", "knowledge.read", "tasks.read", "tasks.create",
        ],
        "scope": "store",
    },
    "purchaser": {
        "name": "采购员",
        "permissions": [
            "ai.use", "ai.inventory", "inventory.read", "purchase.read",
            "product.read", "brand.read", "business.trend.read", "knowledge.read",
            "tasks.read", "tasks.create",
        ],
        "scope": "company",
    },
    "employee": {
        "name": "普通员工",
        "permissions": [
            "ai.use", "ai.content", "product.read", "brand.knowledge.read",
            "knowledge.read", "guide.read", "training.read", "tasks.read",
        ],
        "scope": "self",
    },
    "identity_admin": {
        "name": "身份管理员",
        "permissions": ["identity.view", "identity.manage", "identity.audit"],
        "scope": "company",
    },
}

AGENT_PERMISSIONS = {
    "business": "ai.business",
    "inventory": "ai.inventory",
    "brand": "ai.brand",
    "content": "ai.content",
    "enterprise": "ai.enterprise",
}

IDENTITY_SCHEMA_STATEMENTS = (
    """create table if not exists identity_org_units(
    id bigserial primary key,unit_id varchar(80) unique not null,name varchar(160) not null,
    unit_type varchar(30) not null check(unit_type in ('company','department','store')),
    parent_id bigint references identity_org_units(id),core_object_id varchar(120),
    status varchar(20) not null default 'active',created_at timestamptz not null default now(),
    updated_at timestamptz not null default now())""",
    """create table if not exists identity_positions(
    id bigserial primary key,position_id varchar(80) unique not null,name varchar(120) not null,
    department_id bigint references identity_org_units(id),default_role varchar(40) not null,
    status varchar(20) not null default 'active',created_at timestamptz not null default now(),
    updated_at timestamptz not null default now())""",
    """create table if not exists identity_profiles(
    id bigserial primary key,user_id bigint unique not null references auth_users(id) on delete cascade,
    life_type varchar(30) not null default 'people',real_name varchar(120) not null,
    employee_no varchar(80) unique,mobile varchar(40) unique,wecom_userid varchar(120) unique,
    department_id bigint references identity_org_units(id),store_id bigint references identity_org_units(id),
    position_id bigint references identity_positions(id),status varchar(20) not null default 'active',
    verification_status varchar(20) not null default 'verified',must_change_password boolean not null default true,
    created_at timestamptz not null default now(),updated_at timestamptz not null default now())""",
    """create table if not exists identity_roles(
    id bigserial primary key,role_key varchar(40) unique not null,name varchar(100) not null,
    description text not null default '',default_scope varchar(30) not null,
    system_role boolean not null default true,created_at timestamptz not null default now())""",
    """create table if not exists identity_permissions(
    id bigserial primary key,permission_key varchar(100) unique not null,name varchar(160) not null,
    category varchar(60) not null,created_at timestamptz not null default now())""",
    """create table if not exists identity_role_permissions(
    role_id bigint not null references identity_roles(id) on delete cascade,
    permission_id bigint not null references identity_permissions(id) on delete cascade,
    primary key(role_id,permission_id))""",
    """create table if not exists identity_user_roles(
    user_id bigint not null references auth_users(id) on delete cascade,
    role_id bigint not null references identity_roles(id) on delete cascade,
    assigned_by bigint references auth_users(id),assigned_at timestamptz not null default now(),
    primary key(user_id,role_id))""",
    """create table if not exists identity_data_scopes(
    id bigserial primary key,user_id bigint not null references auth_users(id) on delete cascade,
    scope_type varchar(30) not null check(scope_type in ('company','department','store','self')),
    scope_value varchar(120) not null default '*',source varchar(40) not null default 'role',
    created_at timestamptz not null default now(),unique(user_id,scope_type,scope_value))""",
    """create table if not exists identity_login_audit(
    id bigserial primary key,user_id bigint references auth_users(id),login_identifier varchar(160) not null,
    result varchar(30) not null,auth_method varchar(30) not null default 'password',ip_address varchar(80),
    user_agent text,occurred_at timestamptz not null default now())""",
    """create table if not exists identity_permission_audit(
    id bigserial primary key,user_id bigint references auth_users(id),permission_key varchar(100) not null,
    resource_type varchar(80),resource_id varchar(160),decision varchar(20) not null,
    reason varchar(240),ip_address varchar(80),occurred_at timestamptz not null default now())""",
    """create table if not exists identity_wecom_sso_states(
    id bigserial primary key,state_hash varchar(128) unique not null,redirect_path varchar(240) not null default '/dashboard',
    status varchar(20) not null default 'pending',created_at timestamptz not null default now(),
    consumed_at timestamptz,expires_at timestamptz not null)""",
    "create index if not exists idx_identity_profile_org on identity_profiles(department_id,store_id,position_id,status)",
    "create index if not exists idx_identity_login_audit on identity_login_audit(user_id,occurred_at desc)",
    "create index if not exists idx_identity_permission_audit on identity_permission_audit(user_id,occurred_at desc)",
)


def permission_catalog():
    permissions = set()
    for definition in ROLE_DEFINITIONS.values():
        permissions.update(item for item in definition["permissions"] if item != "*")
    permissions.update(("identity.manage", "identity.audit", "vault.read", "enterprise.all"))
    return sorted(permissions)


def seed_identity(cur):
    for role_key, definition in ROLE_DEFINITIONS.items():
        cur.execute(
            """insert into identity_roles(role_key,name,description,default_scope)
            values(%s,%s,%s,%s) on conflict(role_key) do update set name=excluded.name,
            description=excluded.description,default_scope=excluded.default_scope""",
            (role_key, definition["name"], "FireFox Identity Center 系统角色", definition["scope"]),
        )
    for permission in permission_catalog():
        category = permission.split(".", 1)[0]
        cur.execute(
            """insert into identity_permissions(permission_key,name,category) values(%s,%s,%s)
            on conflict(permission_key) do update set name=excluded.name,category=excluded.category""",
            (permission, permission, category),
        )
    for role_key, definition in ROLE_DEFINITIONS.items():
        permissions = permission_catalog() if "*" in definition["permissions"] else definition["permissions"]
        for permission in permissions:
            cur.execute(
                """insert into identity_role_permissions(role_id,permission_id)
                select r.id,p.id from identity_roles r,identity_permissions p
                where r.role_key=%s and p.permission_key=%s on conflict do nothing""",
                (role_key, permission),
            )


def permissions_for_roles(role_keys):
    result = set()
    for role_key in role_keys:
        definition = ROLE_DEFINITIONS.get(role_key, {})
        if "*" in definition.get("permissions", []):
            return {"*"}
        result.update(definition.get("permissions", []))
    return result


def allows(permissions, permission):
    return "*" in permissions or permission in permissions


def build_identity_context(user_id, real_name, employee_no, role_keys, store_id=None, department_id=None):
    role_keys = list(dict.fromkeys(role_keys or ["employee"]))
    permissions = permissions_for_roles(role_keys)
    scopes = []
    if any(ROLE_DEFINITIONS.get(role, {}).get("scope") == "company" for role in role_keys):
        scopes.append({"type": "company", "value": "*"})
    elif any(ROLE_DEFINITIONS.get(role, {}).get("scope") == "store" for role in role_keys) and store_id:
        scopes.append({"type": "store", "value": str(store_id)})
    else:
        scopes.append({"type": "self", "value": str(user_id)})
    return {
        "user_id": int(user_id), "real_name": str(real_name), "employee_no": str(employee_no or ""),
        "roles": role_keys, "permissions": sorted(permissions), "data_scopes": scopes,
        "store_id": store_id, "department_id": department_id,
    }


def authorize_ai_context(identity, agent_type, requested_store_id=None):
    required = AGENT_PERMISSIONS.get(agent_type)
    if not required or not allows(set(identity.get("permissions", [])), required):
        raise PermissionError("当前岗位没有使用该 AI 助手的权限")
    store_scopes = [item["value"] for item in identity.get("data_scopes", []) if item["type"] == "store"]
    if store_scopes:
        if requested_store_id and str(requested_store_id) not in store_scopes:
            raise PermissionError("只能分析本人负责的门店")
        requested_store_id = store_scopes[0]
    return {
        "identity": {
            "user_id": identity["user_id"], "employee_no": identity.get("employee_no", ""),
            "roles": identity.get("roles", []), "data_scopes": identity.get("data_scopes", []),
        },
        "effective_store_id": requested_store_id,
        "core_access": "read_only",
    }


def identity_snapshot_json(identity):
    return json.dumps(identity, ensure_ascii=False, sort_keys=True)
