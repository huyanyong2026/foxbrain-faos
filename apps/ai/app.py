#!/usr/bin/env python3
"""FoxBrain Enterprise AI collaboration application."""

from __future__ import annotations

import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from urllib.parse import urlparse

import bcrypt
import psycopg2
import psycopg2.extras
from flask import Flask, abort, g, jsonify, redirect, render_template, request, send_file, session

try:
    from .connectors import ceo_brain_connector, data_core_connector, living_enterprise_connector
    from .domain import (
        AGENT_ROLES, CONNECTIONS, DEFAULT_APPROVAL_POLICY, SCHEMA_STATEMENTS, new_id, normalize_evidence,
        require_human_approval, validate_ai_run, validate_feedback, validate_task,
    )
    from .identity import (
        IDENTITY_SCHEMA_STATEMENTS, ROLE_DEFINITIONS, allows, authorize_ai_context,
        build_identity_context, seed_identity,
    )
    from .operation import (
        OPERATION_SCHEMA_STATEMENTS, CoreSnapshotClient, export_inventory_health,
        export_replenishment, export_root, inventory_health_analysis, replenishment_analysis,
    )
except ImportError:
    from connectors import ceo_brain_connector, data_core_connector, living_enterprise_connector
    from domain import (
    AGENT_ROLES,
    CONNECTIONS,
    DEFAULT_APPROVAL_POLICY,
    SCHEMA_STATEMENTS,
    new_id,
    normalize_evidence,
    require_human_approval,
    validate_ai_run,
    validate_feedback,
    validate_task,
)
    from identity import (
        IDENTITY_SCHEMA_STATEMENTS, ROLE_DEFINITIONS, allows, authorize_ai_context,
        build_identity_context, seed_identity,
    )
    from operation import (
        OPERATION_SCHEMA_STATEMENTS, CoreSnapshotClient, export_inventory_health,
        export_replenishment, export_root, inventory_health_analysis, replenishment_analysis,
    )


app = Flask(__name__)
if os.environ.get("FOXBRAIN_ENV") == "production" and not os.environ.get("AUTH_SECRET_KEY"):
    raise RuntimeError("生产环境必须通过环境变量配置 AUTH_SECRET_KEY")
app.secret_key = os.environ.get("AUTH_SECRET_KEY") or "development-only-change-before-production"
app.permanent_session_lifetime = timedelta(hours=8)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=True)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "postgres"),
    "port": os.environ.get("DB_PORT", "5432"),
    "dbname": os.environ.get("DB_NAME", "vafox_platform"),
    "user": os.environ.get("DB_USER", "vafox_admin"),
    "password": os.environ.get("DB_PASS", ""),
}


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(cursor_factory=psycopg2.extras.RealDictCursor, **DB_CONFIG)
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    conn = psycopg2.connect(cursor_factory=psycopg2.extras.RealDictCursor, **DB_CONFIG)
    cur = conn.cursor()
    cur.execute(
        """create table if not exists auth_users(
        id bigserial primary key,username varchar(64) unique not null,password_hash varchar(255) not null,
        display_name varchar(128) not null,email varchar(255),role varchar(20) default 'user',
        status varchar(20) default 'pending',created_at timestamptz default now(),approved_by varchar(64),
        approved_at timestamptz,last_login timestamptz)"""
    )
    for statement in IDENTITY_SCHEMA_STATEMENTS:
        cur.execute(statement)
    seed_identity(cur)
    cur.execute(
        """insert into identity_org_units(unit_id,name,unit_type)
        values('company-firefox','火狐狸公司','company') on conflict(unit_id) do nothing"""
    )
    cur.execute(
        """insert into identity_org_units(unit_id,name,unit_type,parent_id)
        select 'department-shenzhen-retail','深圳门店','department',id from identity_org_units
        where unit_id='company-firefox' on conflict(unit_id) do nothing"""
    )
    for unit_id, name in (("store-nanshan", "南山店"), ("store-zhenxing", "振兴店"), ("store-hangyuan", "航苑店")):
        cur.execute(
            """insert into identity_org_units(unit_id,name,unit_type,parent_id,core_object_id)
            select %s,%s,'store',id,%s from identity_org_units where unit_id='department-shenzhen-retail'
            on conflict(unit_id) do update set name=excluded.name,core_object_id=excluded.core_object_id""",
            (unit_id, name, name),
        )
    for role_key, definition in ROLE_DEFINITIONS.items():
        cur.execute(
            """insert into identity_positions(position_id,name,default_role)
            values(%s,%s,%s) on conflict(position_id) do update set name=excluded.name,
            default_role=excluded.default_role""",
            ("position-" + role_key, definition["name"], role_key),
        )
    legacy_roles = {"boss": ("ceo",), "admin": ("management", "identity_admin"), "manager": ("management",), "user": ("employee",)}
    cur.execute(
        """insert into identity_profiles(user_id,real_name,status,verification_status,must_change_password)
        select id,display_name,'active','pending',false from auth_users
        on conflict(user_id) do nothing"""
    )
    cur.execute("select id,role from auth_users")
    for legacy in cur.fetchall():
        for role_key in legacy_roles.get(legacy["role"], ("employee",)):
            cur.execute(
                """insert into identity_user_roles(user_id,role_id)
                select %s,id from identity_roles where role_key=%s on conflict do nothing""",
                (legacy["id"], role_key),
            )
            scope_type = ROLE_DEFINITIONS[role_key]["scope"]
            scope_value = "*" if scope_type == "company" else str(legacy["id"])
            cur.execute(
                """insert into identity_data_scopes(user_id,scope_type,scope_value,source)
                values(%s,%s,%s,'legacy_role') on conflict do nothing""",
                (legacy["id"], scope_type if scope_type != "store" else "self", scope_value),
            )
    for statement in SCHEMA_STATEMENTS:
        cur.execute(statement)
    for statement in OPERATION_SCHEMA_STATEMENTS:
        cur.execute(statement)
    for agent_type, name, description in AGENT_ROLES:
        cur.execute(
            """insert into ai_agents(agent_id,agent_type,name,description,permission_scope,tool_scope,approval_policy)
            values(%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb) on conflict(agent_id) do nothing""",
            (
                "agent-" + agent_type,
                agent_type,
                name,
                description,
                json.dumps({"data": "read_only", "objects": ["brand", "store", "product", "document"]}, ensure_ascii=False),
                json.dumps(["enterprise_context", "knowledge_search", "task_draft"], ensure_ascii=False),
                json.dumps(DEFAULT_APPROVAL_POLICY, ensure_ascii=False),
            ),
        )
    for connection_type, name, base_url, access_mode in CONNECTIONS:
        cur.execute(
            """insert into enterprise_connections(connection_id,connection_type,name,base_url,access_mode)
            values(%s,%s,%s,%s,%s) on conflict(connection_id) do update set name=excluded.name,
            base_url=excluded.base_url,access_mode=excluded.access_mode,updated_at=now()""",
            ("connection-" + connection_type, connection_type, name, base_url, access_mode),
        )
    cur.execute(
        """insert into wecom_connections(connection_id,name) values('wecom-main','火狐狸企业微信')
        on conflict(connection_id) do nothing"""
    )
    conn.commit()
    cur.close()
    conn.close()


def current_user():
    if "user_id" not in session:
        return None
    cur = get_db().cursor()
    cur.execute(
        """select a.id,a.username,a.display_name,a.email,a.role,a.status,a.last_login,
        p.real_name,p.employee_no,p.mobile,p.wecom_userid,p.department_id,p.store_id,p.position_id,
        p.verification_status,p.must_change_password
        from auth_users a left join identity_profiles p on p.user_id=a.id where a.id=%s""",
        (session["user_id"],),
    )
    row = cur.fetchone()
    if not row:
        return None
    user = dict(row)
    cur.execute(
        """select r.role_key from identity_user_roles ur join identity_roles r on r.id=ur.role_id
        where ur.user_id=%s order by r.id""",
        (user["id"],),
    )
    role_keys = [item["role_key"] for item in cur.fetchall()] or ["employee"]
    user["identity"] = build_identity_context(
        user["id"], user.get("real_name") or user["display_name"], user.get("employee_no"),
        role_keys, user.get("store_id"), user.get("department_id"),
    )
    return user


def permission_allowed(permission):
    user = current_user()
    return bool(user and allows(set(user["identity"]["permissions"]), permission))


def record_permission_audit(permission, decision, resource_type="", resource_id="", reason=""):
    cur = get_db().cursor()
    cur.execute(
        """insert into identity_permission_audit(
        user_id,permission_key,resource_type,resource_id,decision,reason,ip_address)
        values(%s,%s,%s,%s,%s,%s,%s)""",
        (session.get("user_id"), permission, resource_type or None, resource_id or None,
         decision, reason[:240], request.headers.get("X-Forwarded-For", request.remote_addr)),
    )
    get_db().commit()


def login_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith(("/api/", "/ops-api/")):
                return jsonify({"ok": False, "message": "请先登录"}), 401
            return redirect("/auth/login")
        return function(*args, **kwargs)
    return decorated


def manager_required(function):
    @wraps(function)
    @login_required
    def decorated(*args, **kwargs):
        if not permission_allowed("approvals.manage"):
            record_permission_audit("approvals.manage", "denied", reason="审批权限不足")
            abort(403)
        return function(*args, **kwargs)
    return decorated


def permission_required(permission):
    def decorator(function):
        @wraps(function)
        @login_required
        def decorated(*args, **kwargs):
            if not permission_allowed(permission):
                record_permission_audit(permission, "denied", resource_type=request.endpoint or "route")
                abort(403)
            return function(*args, **kwargs)
        return decorated
    return decorator


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(24)
    return session["csrf_token"]


def require_csrf():
    supplied = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token") or (request.get_json(silent=True) or {}).get("csrf_token")
    if not supplied or not secrets.compare_digest(str(supplied), str(session.get("csrf_token") or "")):
        abort(403)


def require_service_token():
    expected = os.environ.get("INTERNAL_SERVICE_TOKEN") or ""
    supplied = request.headers.get("X-FoxBrain-Service-Token") or ""
    if not expected or not secrets.compare_digest(expected, supplied):
        abort(403)


app.jinja_env.globals["csrf_token"] = csrf_token


@app.after_request
def security_headers(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:"
    return response


def rows(query, params=()):
    cur = get_db().cursor()
    cur.execute(query, params)
    return cur.fetchall()


def one(query, params=()):
    result = rows(query, params)
    return result[0] if result else None


def evidence_from_form(form):
    return normalize_evidence([{
        "source_layer": form.get("source_layer") or "enterprise_fact",
        "source_type": form.get("source_type"),
        "source_id": form.get("source_id"),
        "source_ref": form.get("source_ref"),
        "statement": form.get("statement"),
    }])


def save_evidence(cur, target_type, target_id, evidence):
    for item in normalize_evidence(evidence):
        cur.execute(
            """insert into ai_evidence_links(target_type,target_id,source_layer,source_type,source_id,source_ref,statement)
            values(%s,%s,%s,%s,%s,%s,%s) on conflict do nothing""",
            (target_type, target_id, item["source_layer"], item["source_type"], item["source_id"], item["source_ref"], item["statement"]),
        )


def accessible_agents(user):
    permissions = set(user["identity"]["permissions"])
    allowed = []
    for agent in rows("select * from ai_agents where status='active' order by id"):
        agent_type = str(agent["agent_type"])
        required = {"business": "ai.business", "inventory": "ai.inventory", "brand": "ai.brand", "content": "ai.content", "enterprise": "ai.enterprise"}.get(agent_type)
        if required and allows(permissions, required):
            allowed.append(agent)
    return allowed


def visible_runs(user, limit=30):
    scopes = user["identity"]["data_scopes"]
    if any(item["type"] == "company" for item in scopes):
        return rows("select * from ai_agent_runs order by updated_at desc limit %s", (limit,))
    return rows(
        """select * from ai_agent_runs where created_by=%s
        or context_json->'identity'->>'user_id'=%s order by updated_at desc limit %s""",
        (user["id"], str(user["id"]), limit),
    )


@app.route("/")
def index():
    return redirect("/dashboard" if "user_id" in session else "/auth/login")


@app.route("/login")
def login_page():
    return render_template("login.html", wecom_enabled=bool(os.environ.get("WECOM_CORP_ID") and os.environ.get("WECOM_AGENT_ID")))


def record_login_audit(identifier, result, user_id=None, method="password"):
    cur = get_db().cursor()
    cur.execute(
        """insert into identity_login_audit(user_id,login_identifier,result,auth_method,ip_address,user_agent)
        values(%s,%s,%s,%s,%s,%s)""",
        (user_id, str(identifier or "")[:160], result, method,
         request.headers.get("X-Forwarded-For", request.remote_addr), request.headers.get("User-Agent", "")[:1000]),
    )
    get_db().commit()


@app.post("/api/login")
def identity_login_api():
    data = request.get_json(silent=True) or request.form
    identifier = (data.get("username") or "").strip()
    user = one(
        """select a.*,p.real_name,p.employee_no,p.mobile,p.wecom_userid,p.status profile_status,
        p.must_change_password from auth_users a left join identity_profiles p on p.user_id=a.id
        where lower(a.username)=lower(%s) or p.employee_no=%s or p.mobile=%s or p.wecom_userid=%s
        or (p.real_name=%s and (select count(*) from identity_profiles where real_name=%s and status='active')=1)
        order by case when lower(a.username)=lower(%s) then 0 else 1 end limit 1""",
        (identifier, identifier, identifier, identifier, identifier, identifier, identifier),
    )
    password = data.get("password") or ""
    if not user or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        record_login_audit(identifier, "failed", user["id"] if user else None)
        return jsonify({"ok": False, "message": "姓名、员工编号、手机号或密码不正确"}), 401
    if user["status"] != "approved" or user.get("profile_status") not in (None, "active"):
        record_login_audit(identifier, "disabled", user["id"])
        return jsonify({"ok": False, "message": "账号或员工身份已停用，请联系管理员"}), 403
    session.clear()
    session.permanent = True
    session.update(user_id=user["id"], username=user["username"], display_name=user["display_name"], role=user["role"])
    csrf_token()
    cur = get_db().cursor()
    cur.execute("update auth_users set last_login=now() where id=%s", (user["id"],))
    get_db().commit()
    record_login_audit(identifier, "success", user["id"])
    return jsonify({"ok": True, "redirect": "/change-password" if user.get("must_change_password") else "/dashboard"})


@app.post("/api/logout")
@login_required
def logout_api():
    require_csrf()
    record_login_audit(session.get("username"), "logout", session.get("user_id"))
    session.clear()
    return jsonify({"ok": True, "redirect": "/auth/login"})


@app.route("/change-password")
@login_required
def change_password_page():
    return render_template("change_password.html", user=current_user())


@app.post("/ops-api/change-password")
@login_required
def change_password():
    require_csrf()
    current = request.form.get("current_password") or ""
    new_password = request.form.get("new_password") or ""
    confirm = request.form.get("confirm_password") or ""
    user = one("select password_hash from auth_users where id=%s", (session["user_id"],))
    if not user or not bcrypt.checkpw(current.encode(), user["password_hash"].encode()):
        raise ValueError("当前密码不正确")
    if len(new_password) < 12 or not any(c.isupper() for c in new_password) or not any(c.islower() for c in new_password) or not any(c.isdigit() for c in new_password):
        raise ValueError("新密码至少12位，并包含大写字母、小写字母和数字")
    if new_password != confirm:
        raise ValueError("两次输入的新密码不一致")
    password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(rounds=12)).decode()
    cur = get_db().cursor()
    cur.execute("update auth_users set password_hash=%s where id=%s", (password_hash, session["user_id"]))
    cur.execute("update identity_profiles set must_change_password=false,updated_at=now() where user_id=%s", (session["user_id"],))
    get_db().commit()
    session.clear()
    return render_template("message.html", title="密码已更新", message="请使用新密码重新登录。")


@app.get("/auth/wecom/status")
def wecom_sso_status():
    configured = bool(os.environ.get("WECOM_CORP_ID") and os.environ.get("WECOM_AGENT_ID"))
    return jsonify({"ok": True, "configured": configured, "mode": "sso_placeholder"})


@app.get("/auth/wecom/start")
def wecom_sso_start():
    if not os.environ.get("WECOM_CORP_ID") or not os.environ.get("WECOM_AGENT_ID"):
        return render_template("message.html", title="企业微信登录尚未启用", message="接口已经预留，待管理员配置企业微信应用后启用。"), 503
    state = secrets.token_urlsafe(32)
    session["wecom_sso_state"] = state
    return jsonify({"ok": True, "state_created": True, "next": "wecom_oauth_authorization"})


@app.get("/auth/wecom/callback")
def wecom_sso_callback():
    if not os.environ.get("WECOM_CORP_ID") or not os.environ.get("WECOM_AGENT_ID"):
        return jsonify({"ok": False, "message": "企业微信登录尚未配置"}), 503
    supplied = request.args.get("state") or ""
    expected = session.pop("wecom_sso_state", "")
    if not supplied or not expected or not secrets.compare_digest(supplied, expected):
        abort(403)
    return jsonify({"ok": False, "message": "企业微信身份交换将在配置应用凭据后启用"}), 501


@app.route("/identity")
@permission_required("identity.view")
def identity_center_page():
    users = rows(
        """select a.id,a.username,a.status,a.last_login,p.real_name,p.employee_no,p.mobile,
        p.wecom_userid,p.verification_status,p.must_change_password,s.name store_name,
        coalesce(string_agg(distinct r.name,'、'),'未分配') role_names
        from auth_users a left join identity_profiles p on p.user_id=a.id
        left join identity_org_units s on s.id=p.store_id
        left join identity_user_roles ur on ur.user_id=a.id left join identity_roles r on r.id=ur.role_id
        group by a.id,p.id,s.name order by p.real_name nulls last,a.id"""
    )
    return render_template(
        "identity.html", user=current_user(), users=users,
        roles=rows("select role_key,name from identity_roles order by id"),
        stores=rows("select id,name from identity_org_units where unit_type='store' and status='active' order by id"),
        login_audit=rows("select * from identity_login_audit order by occurred_at desc limit 50"),
        permission_audit=rows("select * from identity_permission_audit order by occurred_at desc limit 50"),
        can_manage=permission_allowed("identity.manage"),
    )


@app.post("/ops-api/identity/users")
@permission_required("identity.manage")
def create_identity_user():
    require_csrf()
    form = request.form
    real_name = str(form.get("real_name") or "").strip()
    employee_no = str(form.get("employee_no") or "").strip()
    mobile = str(form.get("mobile") or "").strip()
    role_key = str(form.get("role_key") or "employee").strip()
    password = str(form.get("temporary_password") or "")
    store_id = form.get("store_id") or None
    if not real_name or not employee_no:
        raise ValueError("真实姓名和员工编号必须填写")
    if role_key not in ROLE_DEFINITIONS:
        raise ValueError("岗位角色无效")
    if role_key == "store_manager" and not store_id:
        raise ValueError("店长必须绑定负责门店")
    if len(password) < 12 or not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password):
        raise ValueError("临时密码至少12位，并包含大写字母、小写字母和数字")
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
    cur = get_db().cursor()
    cur.execute(
        """insert into auth_users(username,password_hash,display_name,role,status,approved_by,approved_at)
        values(%s,%s,%s,'user','approved',%s,now()) returning id""",
        (employee_no, password_hash, real_name, session.get("username")),
    )
    user_id = cur.fetchone()["id"]
    cur.execute(
        """insert into identity_profiles(user_id,real_name,employee_no,mobile,store_id,status,verification_status,must_change_password)
        values(%s,%s,%s,%s,%s,'active','verified',true)""",
        (user_id, real_name, employee_no, mobile or None, store_id),
    )
    cur.execute(
        """update identity_profiles set position_id=(select id from identity_positions where default_role=%s order by id limit 1)
        where user_id=%s""",
        (role_key, user_id),
    )
    cur.execute(
        """insert into identity_user_roles(user_id,role_id,assigned_by)
        select %s,id,%s from identity_roles where role_key=%s""",
        (user_id, session["user_id"], role_key),
    )
    scope_type = ROLE_DEFINITIONS[role_key]["scope"]
    scope_value = "*" if scope_type == "company" else str(store_id if scope_type == "store" else user_id)
    cur.execute(
        """insert into identity_data_scopes(user_id,scope_type,scope_value,source)
        values(%s,%s,%s,'role')""",
        (user_id, scope_type, scope_value),
    )
    get_db().commit()
    record_permission_audit("identity.manage", "allowed", "identity_user", str(user_id), "创建真实员工身份")
    return redirect("/identity")


@app.post("/ops-api/identity/users/<int:user_id>/role")
@permission_required("identity.manage")
def assign_identity_role(user_id):
    require_csrf()
    role_key = str(request.form.get("role_key") or "").strip()
    if role_key not in ROLE_DEFINITIONS:
        raise ValueError("岗位角色无效")
    if user_id == session["user_id"] and role_key not in ("ceo", "identity_admin"):
        raise ValueError("不能移除自己当前的身份管理权限")
    cur = get_db().cursor()
    cur.execute("delete from identity_user_roles where user_id=%s", (user_id,))
    cur.execute("delete from identity_data_scopes where user_id=%s", (user_id,))
    cur.execute(
        """insert into identity_user_roles(user_id,role_id,assigned_by)
        select %s,id,%s from identity_roles where role_key=%s""",
        (user_id, session["user_id"], role_key),
    )
    profile = one("select store_id from identity_profiles where user_id=%s", (user_id,))
    scope_type = ROLE_DEFINITIONS[role_key]["scope"]
    if scope_type == "store" and not (profile and profile.get("store_id")):
        raise ValueError("店长角色必须先绑定负责门店")
    scope_value = "*" if scope_type == "company" else str(profile["store_id"] if scope_type == "store" else user_id)
    cur.execute(
        """insert into identity_data_scopes(user_id,scope_type,scope_value,source)
        values(%s,%s,%s,'role')""",
        (user_id, scope_type, scope_value),
    )
    cur.execute(
        """update identity_profiles set position_id=(select id from identity_positions where default_role=%s order by id limit 1),
        updated_at=now() where user_id=%s""",
        (role_key, user_id),
    )
    get_db().commit()
    record_permission_audit("identity.manage", "allowed", "identity_user", str(user_id), "调整岗位角色")
    return redirect("/identity")


@app.post("/ops-api/identity/users/<int:user_id>/status")
@permission_required("identity.manage")
def update_identity_status(user_id):
    require_csrf()
    status = request.form.get("status")
    if status not in ("active", "disabled"):
        raise ValueError("身份状态无效")
    if user_id == session["user_id"] and status == "disabled":
        raise ValueError("不能停用当前登录账号")
    cur = get_db().cursor()
    cur.execute("update identity_profiles set status=%s,updated_at=now() where user_id=%s", (status, user_id))
    cur.execute("update auth_users set status=%s where id=%s", ("approved" if status == "active" else "disabled", user_id))
    get_db().commit()
    record_permission_audit("identity.manage", "allowed", "identity_user", str(user_id), "更新账号状态")
    return redirect("/identity")


@app.get("/ops-api/identity/me")
@login_required
def identity_me_api():
    user = current_user()
    return jsonify({"ok": True, "identity": user["identity"], "real_name": user.get("real_name") or user["display_name"]})


@app.route("/dashboard")
@permission_required("ai.use")
def dashboard():
    user = current_user()
    metrics = {
        "agents": one("select count(*) as value from ai_agents where status='active'")["value"],
        "pending_runs": one("select count(*) as value from ai_agent_runs where approval_status='pending'")["value"],
        "pending_tasks": one("select count(*) as value from ai_tasks where approval_status='pending'")["value"],
        "knowledge": one("select count(*) as value from ai_knowledge_items where status='approved'")["value"],
    }
    return render_template("dashboard.html", user=user, metrics=metrics,
                           connections=rows("select * from enterprise_connections order by id"),
                           runs=visible_runs(user, 8))


@app.route("/workbench")
@permission_required("ai.use")
def workbench():
    user = current_user()
    return render_template("workbench.html", user=user, agents=accessible_agents(user), runs=visible_runs(user, 30))


@app.post("/ops-api/runs")
@permission_required("ai.use")
def create_run():
    require_csrf()
    form = request.form
    evidence = evidence_from_form(form)
    validate_ai_run(form.get("question"), evidence)
    user = current_user()
    agent = one("select agent_type from ai_agents where agent_id=%s and status='active'", (form.get("agent_id"),))
    if not agent:
        raise ValueError("AI助手不存在或未启用")
    permission_context = authorize_ai_context(user["identity"], agent["agent_type"], form.get("store_id"))
    run_id = new_id("RUN")
    cur = get_db().cursor()
    cur.execute(
        """insert into ai_agent_runs(run_id,agent_id,question,context_json,evidence_json,created_by)
        values(%s,%s,%s,%s::jsonb,%s::jsonb,%s)""",
        (run_id, form.get("agent_id"), form.get("question").strip(), json.dumps({
            "object_type": form.get("object_type"), "object_id": form.get("object_id"),
            "identity": permission_context["identity"], "effective_store_id": permission_context["effective_store_id"],
            "core_access": "read_only",
        }, ensure_ascii=False), json.dumps(evidence, ensure_ascii=False), session["user_id"]),
    )
    save_evidence(cur, "agent_run", run_id, evidence)
    get_db().commit()
    return redirect("/workbench")


@app.post("/ops-api/internal/runs/<run_id>/result")
def attach_run_result(run_id):
    require_service_token()
    data = request.get_json(silent=True) or {}
    evidence = normalize_evidence(data.get("evidence"))
    ai_source_ref = str(data.get("ai_source_ref") or "").strip()
    host = (urlparse(ai_source_ref).hostname or "").lower()
    if host != "ai.vafox.com" and not host.endswith(".ai.vafox.com"):
        return jsonify({"ok": False, "message": "AI结果必须保留 ai.vafox.com 来源"}), 400
    evidence.append({
        "source_layer": "ai_analysis", "source_type": "ai.vafox.com", "source_id": run_id,
        "source_ref": ai_source_ref, "statement": "AI分析候选，等待人工确认",
    })
    cur = get_db().cursor()
    cur.execute(
        """update ai_agent_runs set answer=%s,result_json=%s::jsonb,evidence_json=%s::jsonb,
        status='pending_review',approval_status='pending',updated_at=now() where run_id=%s""",
        (data.get("answer") or "", json.dumps(data.get("result") or {}, ensure_ascii=False), json.dumps(evidence, ensure_ascii=False), run_id),
    )
    if cur.rowcount != 1:
        abort(404)
    save_evidence(cur, "agent_run", run_id, evidence)
    get_db().commit()
    return jsonify({"ok": True, "status": "pending_review"})


@app.post("/ops-api/runs/<run_id>/review")
@manager_required
def review_run(run_id):
    require_csrf()
    row = one("select approval_status from ai_agent_runs where run_id=%s", (run_id,))
    if not row:
        abort(404)
    status = require_human_approval(row["approval_status"], request.form.get("action"))
    cur = get_db().cursor()
    cur.execute("update ai_agent_runs set approval_status=%s,reviewed_by=%s,reviewed_at=now(),updated_at=now() where run_id=%s", (status, session["user_id"], run_id))
    get_db().commit()
    return redirect("/workbench")


@app.route("/agents")
@permission_required("ai.use")
def agents_page():
    return render_template("agents.html", user=current_user(), agents=rows("select * from ai_agents order by id"))


@app.route("/wecom")
@permission_required("identity.view")
def wecom_page():
    return render_template("wecom.html", user=current_user(), connections=rows("select * from wecom_connections order by id"))


@app.route("/knowledge")
@permission_required("knowledge.read")
def knowledge_page():
    return render_template("knowledge.html", user=current_user(), items=rows("select * from ai_knowledge_items order by updated_at desc limit 100"))


@app.post("/ops-api/knowledge")
@permission_required("knowledge.write")
def create_knowledge():
    require_csrf()
    form = request.form
    evidence = evidence_from_form(form)
    if not str(form.get("title") or "").strip():
        raise ValueError("知识标题不能为空")
    knowledge_id = new_id("KN")
    cur = get_db().cursor()
    cur.execute(
        """insert into ai_knowledge_items(knowledge_id,title,summary,content,object_type,object_id,
        source_type,source_id,source_ref,evidence_json,created_by) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s)""",
        (knowledge_id, form.get("title"), form.get("summary") or "", form.get("content") or "", form.get("object_type") or None, form.get("object_id") or None, form.get("source_type"), form.get("source_id"), form.get("source_ref"), json.dumps(evidence, ensure_ascii=False), session["user_id"]),
    )
    save_evidence(cur, "knowledge", knowledge_id, evidence)
    get_db().commit()
    return redirect("/knowledge")


@app.post("/ops-api/knowledge/<knowledge_id>/review")
@manager_required
def review_knowledge(knowledge_id):
    require_csrf()
    action = request.form.get("action")
    status = "approved" if action == "approve" else "rejected" if action == "reject" else None
    if not status:
        abort(400)
    cur = get_db().cursor()
    cur.execute(
        """update ai_knowledge_items set status=%s,approved_by=%s,approved_at=now(),updated_at=now()
        where knowledge_id=%s and status='draft'""",
        (status, session["user_id"], knowledge_id),
    )
    if cur.rowcount != 1:
        abort(400)
    get_db().commit()
    return redirect("/knowledge")


@app.route("/tasks")
@permission_required("tasks.read")
def tasks_page():
    return render_template("tasks.html", user=current_user(), tasks=rows("select * from ai_tasks order by updated_at desc limit 100"),
                           approved_runs=rows("select run_id,question,evidence_json from ai_agent_runs where approval_status='approved' order by reviewed_at desc limit 50"))


@app.post("/ops-api/tasks")
@permission_required("tasks.create")
def create_task():
    require_csrf()
    form = request.form
    source_id = form.get("source_id")
    source_type = "ai_agent_run"
    source_ref = "https://ai.vafox.com/workbench#{}".format(source_id)
    source_run = one("select approval_status,evidence_json from ai_agent_runs where run_id=%s", (source_id,))
    if not source_run or source_run["approval_status"] != "approved":
        raise ValueError("只有人工批准的 AI 分析才能生成任务")
    evidence = normalize_evidence(source_run["evidence_json"])
    validate_task(form.get("title"), source_type, source_id, source_ref, evidence)
    task_id = new_id("TASK")
    cur = get_db().cursor()
    cur.execute(
        """insert into ai_tasks(task_id,title,description,owner_name,priority,source_type,source_id,
        source_ref,evidence_json,created_by) values(%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s)""",
        (task_id, form.get("title"), form.get("description") or "", form.get("owner_name") or "", form.get("priority") or "normal", source_type, source_id, source_ref, json.dumps(evidence, ensure_ascii=False), session["user_id"]),
    )
    save_evidence(cur, "task", task_id, evidence)
    get_db().commit()
    return redirect("/tasks")


@app.post("/ops-api/tasks/<task_id>/review")
@manager_required
def review_task(task_id):
    require_csrf()
    row = one("select approval_status from ai_tasks where task_id=%s", (task_id,))
    if not row:
        abort(404)
    status = require_human_approval(row["approval_status"], request.form.get("action"))
    task_status = "todo" if status == "approved" else "rejected"
    cur = get_db().cursor()
    cur.execute("update ai_tasks set approval_status=%s,status=%s,approved_by=%s,approved_at=now(),updated_at=now() where task_id=%s", (status, task_status, session["user_id"], task_id))
    get_db().commit()
    return redirect("/tasks")


@app.route("/feedback")
@permission_required("ai.use")
def feedback_page():
    return render_template("feedback.html", user=current_user(), feedback=rows("select f.*,r.question from ai_feedback f join ai_agent_runs r on r.run_id=f.run_id order by f.created_at desc limit 100"),
                           runs=rows("select run_id,question from ai_agent_runs where approval_status in ('approved','rejected') order by reviewed_at desc limit 50"))


@app.post("/ops-api/feedback")
@permission_required("ai.use")
def create_feedback():
    require_csrf()
    form = request.form
    score = validate_feedback(form.get("feedback_type"), form.get("effect_score"))
    feedback_id = new_id("FB")
    cur = get_db().cursor()
    cur.execute("insert into ai_feedback(feedback_id,run_id,feedback_type,comment,effect_score,created_by) values(%s,%s,%s,%s,%s,%s)",
                (feedback_id, form.get("run_id"), form.get("feedback_type"), form.get("comment") or "", score, session["user_id"]))
    get_db().commit()
    return redirect("/feedback")


@app.post("/ops-api/feedback/<feedback_id>/review")
@manager_required
def review_feedback(feedback_id):
    require_csrf()
    action = request.form.get("action")
    status = "approved" if action == "approve" else "rejected" if action == "reject" else None
    if not status:
        abort(400)
    cur = get_db().cursor()
    cur.execute("update ai_feedback set learning_status=%s,reviewed_by=%s,reviewed_at=now() where feedback_id=%s and learning_status='pending_review'", (status, session["user_id"], feedback_id))
    if cur.rowcount != 1:
        abort(400)
    get_db().commit()
    return redirect("/feedback")


@app.post("/ops-api/connections/check")
@manager_required
def check_connections():
    require_csrf()
    definitions = {
        "data_core": (data_core_connector, os.environ.get("CORE_BASE_URL", "https://core.vafox.com"), os.environ.get("CORE_API_TOKEN", ""), "api/health"),
        "ceo_brain": (ceo_brain_connector, os.environ.get("CEO_BRAIN_BASE_URL", "https://huyan.vafox.com"), os.environ.get("CEO_BRAIN_API_TOKEN", ""), "api/health"),
        "living_enterprise": (living_enterprise_connector, os.environ.get("CEO_BRAIN_BASE_URL", "https://huyan.vafox.com"), os.environ.get("CEO_BRAIN_API_TOKEN", ""), "api/living-enterprise"),
    }
    cur = get_db().cursor()
    for connection_type, (factory, base_url, token, path) in definitions.items():
        result = factory(base_url, token).get_json(path)
        cur.execute(
            """update enterprise_connections set status=%s,last_checked_at=now(),
            last_success_at=case when %s then now() else last_success_at end,last_error=%s,updated_at=now()
            where connection_type=%s""",
            ("connected" if result["ok"] else "unavailable", result["ok"], None if result["ok"] else result["error"][:500], connection_type),
        )
    get_db().commit()
    return redirect("/dashboard")


@app.get("/ops-api/health")
def health():
    try:
        value = one("select 1 as value")["value"]
        return jsonify({"ok": value == 1, "service": "FoxBrain Enterprise AI", "sap_write": False})
    except Exception:
        return jsonify({"ok": False, "service": "FoxBrain Enterprise AI"}), 503


@app.get("/ops-api/workbench")
@login_required
def workbench_api():
    return jsonify({"ok": True, "agents": rows("select agent_id,name,status from ai_agents order by id"),
                    "connections": rows("select connection_type,name,status,last_success_at from enterprise_connections order by id")})


def operation_stores(user):
    scopes = user["identity"]["data_scopes"]
    if any(item["type"] == "company" for item in scopes):
        return rows(
            """select id,name,core_object_id from identity_org_units
            where unit_type='store' and status='active' order by id"""
        )
    store_ids = [int(item["value"]) for item in scopes if item["type"] == "store" and str(item["value"]).isdigit()]
    if not store_ids:
        return []
    return rows(
        """select id,name,core_object_id from identity_org_units
        where unit_type='store' and status='active' and id=any(%s) order by id""",
        (store_ids,),
    )


def operation_store(user, store_id):
    if not str(store_id or "").isdigit():
        raise ValueError("请选择有效门店")
    for store in operation_stores(user):
        if int(store["id"]) == int(store_id):
            return store
    record_permission_audit("store.read", "denied", "store", str(store_id), "门店超出当前身份数据范围")
    raise PermissionError("只能分析当前岗位有权查看的门店")


def visible_operation_runs(user, analysis_type, limit=30):
    allowed_ids = [int(store["id"]) for store in operation_stores(user)]
    if not allowed_ids:
        return []
    return rows(
        """select run_id,analysis_type,store_id,store_name,source_updated_at,summary_json,
        excel_path,status,created_at from operation_analysis_runs
        where analysis_type=%s and store_id=any(%s) order by created_at desc limit %s""",
        (analysis_type, allowed_ids, limit),
    )


def selected_operation_run(user, analysis_type):
    run_id = str(request.args.get("run") or "").strip()
    if not run_id:
        return None
    result = one("select * from operation_analysis_runs where run_id=%s and analysis_type=%s", (run_id, analysis_type))
    if not result:
        abort(404)
    operation_store(user, result["store_id"])
    return result


def operation_connector():
    return data_core_connector(
        os.environ.get("CORE_BASE_URL", "https://core.vafox.com"),
        os.environ.get("CORE_API_TOKEN", ""),
    )


def create_operation_run(analysis_type):
    require_csrf()
    user = current_user()
    store = operation_store(user, request.form.get("store_id"))
    core_reference = store.get("core_object_id") or store["name"]
    client = CoreSnapshotClient(operation_connector())
    source_status = client.source_status()
    snapshot = client.operation_snapshot(core_reference)
    if analysis_type == "replenishment":
        result = replenishment_analysis(snapshot, core_reference)
        summary = {
            "商品数量": len(result["items"]),
            "建议补货商品": sum(1 for item in result["items"] if item["suggested_quantity"] > 0),
            "建议补货总量": sum(item["suggested_quantity"] for item in result["items"]),
        }
    else:
        result = inventory_health_analysis(snapshot, core_reference)
        summary = {
            "商品数量": len(result["items"]),
            "库存金额": result["inventory_amount"],
            "风险商品": sum(value for key, value in result["levels"].items() if key != "健康"),
            "风险等级": result["levels"],
        }
    run_id = new_id("OP")
    day_text = result["as_of"].replace("-", "")
    safe_store_name = "".join(character for character in store["name"] if character.isalnum() or character in "-_ ").strip() or "门店"
    filename = "{}_{}_{}_{}.xlsx".format(
        safe_store_name,
        "智能补货建议" if analysis_type == "replenishment" else "积压库存分析",
        day_text,
        run_id,
    )
    path = export_root() / filename
    if analysis_type == "replenishment":
        export_replenishment(result, path)
    else:
        export_inventory_health(result, path)
    mirror = source_status.get("mirror") or {}
    source_updated_at = mirror.get("finished_at") or source_status.get("checked_at")
    source_ref = json.dumps({
        "service": "core.vafox.com", "mode": source_status.get("mode", "read_only"),
        "mirror_status": mirror.get("status"), "tables": result["source_tables"],
    }, ensure_ascii=False)
    cur = get_db().cursor()
    cur.execute(
        """insert into operation_analysis_runs(
        run_id,analysis_type,store_id,store_name,source_ref,source_updated_at,result_json,
        summary_json,excel_path,status,created_by)
        values(%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s,'pending_review',%s)""",
        (run_id, analysis_type, store["id"], store["name"], source_ref, source_updated_at,
         json.dumps(result, ensure_ascii=False), json.dumps(summary, ensure_ascii=False), str(path), user["id"]),
    )
    cur.execute(
        "insert into operation_analysis_audit(run_id,action,user_id,note) values(%s,'created',%s,%s)",
        (run_id, user["id"], "通过core.vafox.com只读数据生成，等待人工确认"),
    )
    get_db().commit()
    return run_id


@app.get("/operation")
@login_required
def operation_home():
    if not (permission_allowed("replenishment.read") or permission_allowed("inventory.read")):
        abort(403)
    return render_template("operation_home.html", user=current_user())


@app.get("/operation/replenishment")
@permission_required("replenishment.read")
def operation_replenishment_page():
    user = current_user()
    return render_template(
        "operation_replenishment.html", user=user, stores=operation_stores(user),
        runs=visible_operation_runs(user, "replenishment"),
        selected=selected_operation_run(user, "replenishment"),
        can_approve=permission_allowed("approvals.manage"),
    )


@app.post("/ops-api/operation/replenishment/run")
@permission_required("replenishment.read")
def operation_replenishment_run():
    return redirect("/operation/replenishment?run=" + create_operation_run("replenishment"))


@app.get("/operation/inventory-health")
@permission_required("inventory.read")
def operation_inventory_health_page():
    user = current_user()
    return render_template(
        "operation_inventory_health.html", user=user, stores=operation_stores(user),
        runs=visible_operation_runs(user, "inventory_health"),
        selected=selected_operation_run(user, "inventory_health"),
        can_approve=permission_allowed("approvals.manage"),
    )


@app.post("/ops-api/operation/inventory-health/run")
@permission_required("inventory.read")
def operation_inventory_health_run():
    return redirect("/operation/inventory-health?run=" + create_operation_run("inventory_health"))


@app.get("/ops-api/operation/exports/<run_id>")
@login_required
def operation_export(run_id):
    run = one("select * from operation_analysis_runs where run_id=%s", (run_id,))
    if not run:
        abort(404)
    required = "replenishment.read" if run["analysis_type"] == "replenishment" else "inventory.read"
    if not permission_allowed(required):
        abort(403)
    operation_store(current_user(), run["store_id"])
    root = export_root().resolve()
    path = os.path.realpath(run["excel_path"] or "")
    if os.path.commonpath((str(root), path)) != str(root) or not os.path.isfile(path):
        abort(404)
    return send_file(path, as_attachment=True, download_name=os.path.basename(path))


@app.post("/ops-api/operation/runs/<run_id>/review")
@manager_required
def operation_review(run_id):
    require_csrf()
    action = request.form.get("action")
    status = "approved" if action == "approve" else "rejected" if action == "reject" else None
    if not status:
        raise ValueError("请选择确认或拒绝")
    run = one("select store_id,analysis_type from operation_analysis_runs where run_id=%s", (run_id,))
    if not run:
        abort(404)
    operation_store(current_user(), run["store_id"])
    cur = get_db().cursor()
    cur.execute(
        """update operation_analysis_runs set status=%s,approved_by=%s,approved_at=now()
        where run_id=%s and status='pending_review'""",
        (status, session["user_id"], run_id),
    )
    if cur.rowcount != 1:
        raise ValueError("该分析已经完成审核")
    cur.execute(
        "insert into operation_analysis_audit(run_id,action,user_id,note) values(%s,%s,%s,%s)",
        (run_id, status, session["user_id"], "人工审核经营建议；系统未执行采购或库存变更"),
    )
    get_db().commit()
    target = "/operation/replenishment" if run["analysis_type"] == "replenishment" else "/operation/inventory-health"
    return redirect(target + "?run=" + run_id)


@app.get("/ops-api/exchange/approved-runs")
def approved_runs_exchange():
    """Machine-readable, human-approved AI results for CEO Brain pull sync."""
    require_service_token()
    approved = rows(
        """select run_id,agent_id,question,answer,result_json,evidence_json,reviewed_at
        from ai_agent_runs where approval_status='approved' and status='pending_review'
        order by reviewed_at desc limit 100"""
    )
    return jsonify({"ok": True, "source": "ai.vafox.com", "human_approved": True, "items": approved})


@app.errorhandler(403)
def forbidden(_exc):
    return render_template("message.html", title="没有操作权限", message="该操作需要负责人或管理员权限。"), 403


@app.errorhandler(ValueError)
def invalid_business_input(exc):
    return render_template("message.html", title="暂时不能这样操作", message=str(exc)), 400


@app.errorhandler(500)
def internal_error(_exc):
    return render_template("message.html", title="暂时无法完成", message="服务暂时不可用，请稍后重试。"), 500


@app.errorhandler(PermissionError)
def identity_permission_error(exc):
    return render_template("message.html", title="没有访问权限", message=str(exc)), 403


@app.errorhandler(403)
def identity_forbidden(_exc):
    return render_template("message.html", title="没有访问权限", message="当前岗位或数据范围不允许执行此操作。"), 403


@app.errorhandler(ValueError)
def identity_invalid_input(exc):
    return render_template("message.html", title="请检查填写内容", message=str(exc)), 400


if __name__ == "__main__":
    init_db()
    app.run(host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", "5010")), debug=False)
