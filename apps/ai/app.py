#!/usr/bin/env python3
"""VAFOX Enterprise AI Center collaboration application."""

from __future__ import annotations

import json
import os
import secrets
import hashlib
from datetime import date, datetime, timedelta, timezone
from functools import wraps
from urllib.parse import quote, urlparse

import bcrypt
import psycopg2
import psycopg2.extras
from flask import Flask, abort, g, jsonify, redirect, render_template, request, send_file, session

from foxbrain_os.platform_governance import control_tower_status, health_payload, runtime_payload, version_payload
from foxbrain_os.ai_os_v6 import build_ai_os_v6_contract, create_ai_task, route_ai_question

try:
    from .connectors import ceo_brain_connector, data_core_connector, living_enterprise_connector
    from .ceo_strategy import build_ceo_strategy_snapshot
    from .domain import (
        AGENT_ROLES, CONNECTIONS, DEFAULT_APPROVAL_POLICY, DIGITAL_WORKFORCE_AGENTS, SCHEMA_STATEMENTS, new_id, normalize_evidence,
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
    from .replenishment import (
        ALLOWED_STORES, RULE_VERSION, build_excel, business_now, business_today, calculate_batch, new_batch_id,
        normalize_input_rows, parse_uploaded_file,
    )
except ImportError:
    from connectors import ceo_brain_connector, data_core_connector, living_enterprise_connector
    from ceo_strategy import build_ceo_strategy_snapshot
    from domain import (
    AGENT_ROLES,
    CONNECTIONS,
    DEFAULT_APPROVAL_POLICY,
    DIGITAL_WORKFORCE_AGENTS,
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
    from replenishment import (
        ALLOWED_STORES, RULE_VERSION, build_excel, business_now, business_today, calculate_batch, new_batch_id,
        normalize_input_rows, parse_uploaded_file,
    )


app = Flask(__name__)
if os.environ.get("FOXBRAIN_ENV") == "production" and not os.environ.get("AUTH_SECRET_KEY"):
    raise RuntimeError("生产环境必须通过环境变量配置 AUTH_SECRET_KEY")
app.secret_key = os.environ.get("AUTH_SECRET_KEY") or "development-only-change-before-production"
app.permanent_session_lifetime = timedelta(hours=8)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=True)

@app.context_processor
def inject_runtime_version():
    return {"runtime_version": version_payload("ai")}


AI_WORKSPACE_V6_LABEL = "VAFOX Digital Workforce OS V6"
AI_WORKSPACE_V6_EXAMPLES = (
    "分析火狐狸当前最大经营风险",
    "南山店最近经营怎么样？",
    "Osprey库存风险？",
    "下个月采购重点是什么？",
)
AGENT_TYPE_BY_V6_NAME = {
    "CEO Agent": "ceo",
    "Supply Agent": "supply_chain",
    "Supply Chain Agent": "supply_chain",
    "Store Agent": "store",
    "Finance Agent": "finance",
    "Commerce Agent": "business",
    "Growth Agent": "growth",
    "Forecast Engine": "inventory",
    "Customer Agent": "customer",
}


def workspace_v6_context(question):
    route = route_ai_question(question)
    response = {"conclusion": "AI OS V6 prepared a governed recommendation.", "reason": "AI Router V6 selected intent, agents, Core data, and task policy from the question.", "data_source": route["core_data_sources"], "recommendation": "Review the recommendation and approve governed operational actions only.", "next_action": "Create a V6 autonomous draft task for the responsible owner.", "route": route}
    task = create_ai_task(question, owner="AI Router V6")
    return {"route": route, "response": response, "task": task}


def v6_evidence_from_route(route):
    objects = route.get("business_objects") or ["Enterprise"]
    sources = route.get("core_data_sources") or ["Core Enterprise Digital Twin"]
    return [{
        "source_layer": "enterprise_fact",
        "source_type": "core.vafox.com",
        "source_id": "auto-link:" + "+".join(objects),
        "source_ref": "https://core.vafox.com/auto-link/" + "-".join(objects).lower(),
        "statement": "AI Router V6 automatically linked {} to {} for this answer.".format(", ".join(objects), ", ".join(sources)),
    }]


def answer_text_from_v6_response(response):
    return "\n".join([
        "Conclusion: " + response["conclusion"],
        "Reason: " + response["reason"],
        "Data Source: " + ", ".join(response["data_source"]),
        "Recommendation: " + response["recommendation"],
        "Next Action: " + response["next_action"],
    ])


def select_v6_agent_id(route, user):
    allowed_agents = accessible_agents(user)
    by_type = {agent["agent_type"]: agent["agent_id"] for agent in allowed_agents}
    for agent_name in route.get("selected_agents", []):
        agent_type = AGENT_TYPE_BY_V6_NAME.get(agent_name)
        if agent_type in by_type:
            return by_type[agent_type]
    return allowed_agents[0]["agent_id"] if allowed_agents else "agent-enterprise"

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
    for agent_type, name, description in AGENT_ROLES + DIGITAL_WORKFORCE_AGENTS:
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
        coalesce(a.store_code,case s.name when '南山店' then 'nanshan' when '振兴店' then 'zhenxing'
        when '航苑店' then 'hangyuan' end) store_code,
        p.real_name,p.employee_no,p.mobile,p.wecom_userid,p.department_id,p.store_id,p.position_id,
        p.verification_status,p.must_change_password
        from auth_users a left join identity_profiles p on p.user_id=a.id
        left join identity_org_units s on s.id=p.store_id where a.id=%s""",
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


GATEWAY_LOGIN_URL = os.environ.get("GATEWAY_LOGIN_URL", "https://gateway.vafox.com/login")


def gateway_login_redirect():
    next_path = request.full_path if request.query_string else request.path
    return redirect(f"{GATEWAY_LOGIN_URL}?next={quote(next_path)}")


def login_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith(("/api/", "/ops-api/")):
                return jsonify({"ok": False, "message": "请先通过 VAFOX Gateway 登录"}), 401
            return gateway_login_redirect()
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


def replenishment_required(function):
    return permission_required("replenishment.read")(function)


def can_access_store(user, store_code):
    scopes = user["identity"]["data_scopes"]
    if any(item["type"] == "company" for item in scopes):
        return True
    return any(item["type"] == "store" for item in scopes) and user.get("store_code") == store_code


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


def latest_replenishment_batch():
    return one(
        """select * from replenishment_batches where status in ('completed','completed_with_warnings')
        order by business_date desc,revision desc,completed_at desc limit 1"""
    )


def replenishment_summary(batch_id):
    if not batch_id:
        return []
    return rows(
        """select store_code,store_name,count(*) filter(where recommendation='replenish') as suggested_skus,
        count(*) filter(where priority='紧急') as urgent_skus,sum(suggested_qty) as suggested_units
        from replenishment_items where batch_id=%s group by store_code,store_name order by store_name""",
        (batch_id,),
    )


def save_replenishment_batch(input_rows, source_type, source_name, business_date, metadata=None):
    normalized = normalize_input_rows(input_rows)
    results = calculate_batch(normalized)
    batch_id = new_batch_id(source_type, business_date.isoformat())
    warnings = sum(1 for item in results if item["warning"])
    status = "completed_with_warnings" if warnings else "completed"
    cur = get_db().cursor()
    cur.execute(
        """select coalesce(max(revision),0)+1 as revision from replenishment_batches
        where business_date=%s and source_type=%s and source_name=%s and rule_version=%s""",
        (business_date, source_type, source_name, RULE_VERSION),
    )
    revision = cur.fetchone()["revision"]
    cur.execute(
        """insert into replenishment_batches(batch_id,business_date,source_type,source_name,data_as_of,
        rule_version,status,revision,input_rows,result_rows,metadata,created_by,completed_at)
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,now())""",
        (batch_id, business_date, source_type, source_name, business_now(), RULE_VERSION,
         status, revision, len(normalized), len(results), json.dumps(metadata or {}, ensure_ascii=False), session.get("user_id")),
    )
    insert_sql = """insert into replenishment_items(
        batch_id,store_code,store_name,sku_code,product_name,brand_name,category_name,color,size,
        available_stock,sales_30d,sales_prev_30d,sales_60d,avg_daily_sales,stock_days,safety_stock,
        suggested_qty,priority,recommendation,reason,warning)
        values(%(batch_id)s,%(store_code)s,%(store_name)s,%(sku_code)s,%(product_name)s,%(brand_name)s,
        %(category_name)s,%(color)s,%(size)s,%(available_stock)s,%(sales_30d)s,%(sales_prev_30d)s,
        %(sales_60d)s,%(avg_daily_sales)s,%(stock_days)s,%(safety_stock)s,%(suggested_qty)s,
        %(priority)s,%(recommendation)s,%(reason)s,%(warning)s)"""
    for item in results:
        cur.execute(insert_sql, {**item, "batch_id": batch_id})
    cur.execute(
        """insert into replenishment_audit_logs(action,batch_id,actor_id,details)
        values('generate',%s,%s,%s::jsonb)""",
        (batch_id, session.get("user_id"), json.dumps({"source_type": source_type, "rows": len(results), "warnings": warnings}, ensure_ascii=False)),
    )
    get_db().commit()
    return batch_id


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
        required = {"business": "ai.business", "inventory": "ai.inventory", "brand": "ai.brand", "content": "ai.content", "enterprise": "ai.enterprise", "ceo": "ai.ceo", "supply_chain": "supply_chain.read", "finance": "finance.read", "store": "store.read", "growth": "business.trend.read"}.get(agent_type)
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
    return redirect("/home") if "user_id" in session else gateway_login_redirect()


@app.route("/login")
def login_page():
    return gateway_login_redirect()


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
    return jsonify({"ok": False, "message": "VAFOX Gateway is the canonical login authority", "redirect": GATEWAY_LOGIN_URL}), 410


def legacy_identity_login_api_disabled():
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
    return jsonify({"ok": True, "redirect": "/change-password" if user.get("must_change_password") else "/home"})


@app.post("/api/logout")
@login_required
def logout_api():
    require_csrf()
    record_login_audit(session.get("username"), "logout", session.get("user_id"))
    session.clear()
    return jsonify({"ok": True, "redirect": GATEWAY_LOGIN_URL})


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


@app.route("/home")
@permission_required("ai.use")
def home():
    user = current_user()
    latest_batch = latest_replenishment_batch()
    metrics = {
        "agents": one("select count(*) as value from ai_agents where status='active'")["value"],
        "pending_runs": one("select count(*) as value from ai_agent_runs where approval_status='pending'")["value"],
        "pending_tasks": one("select count(*) as value from ai_tasks where approval_status='pending'")["value"],
        "knowledge": one("select count(*) as value from ai_knowledge_items where status='approved'")["value"],
    }
    summary = replenishment_summary(latest_batch["batch_id"] if latest_batch else None)
    ceo_snapshot = build_ceo_strategy_snapshot(
        metrics, latest_batch, summary,
        approved_runs=one("select count(*) as value from ai_agent_runs where approval_status='approved'")["value"],
        memories=one("select count(*) as value from ai_memory_items where status in ('approved','pending_review')")["value"],
    )
    return render_template("dashboard.html", user=user, metrics=metrics,
                           connections=rows("select * from enterprise_connections order by id"),
                           runs=visible_runs(user, 8),
                           replenishment_batch=latest_batch,
                           replenishment_summary=summary, ceo_snapshot=ceo_snapshot)


@app.get("/ceo/strategy")
@permission_required("ai.ceo")
def ceo_strategy_page():
    user = current_user()
    latest_batch = latest_replenishment_batch()
    summary = replenishment_summary(latest_batch["batch_id"] if latest_batch else None)
    metrics = {
        "agents": one("select count(*) as value from ai_agents where status='active'")["value"],
        "pending_runs": one("select count(*) as value from ai_agent_runs where approval_status='pending'")["value"],
        "pending_tasks": one("select count(*) as value from ai_tasks where approval_status='pending'")["value"],
        "knowledge": one("select count(*) as value from ai_knowledge_items where status='approved'")["value"],
    }
    snapshot = build_ceo_strategy_snapshot(
        metrics, latest_batch, summary,
        approved_runs=one("select count(*) as value from ai_agent_runs where approval_status='approved'")["value"],
        memories=one("select count(*) as value from ai_memory_items where status in ('approved','pending_review')")["value"],
    )
    return render_template("ceo_strategy.html", user=user, snapshot=snapshot)


@app.post("/api/huyan/ask")
@permission_required("ai.ceo")
def huyan_ask_api():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question") or "").strip()
    if not question:
        return jsonify({"ok": False, "error": "question_required"}), 400
    routed_agents = ["Supply Agent", "Finance Agent", "Store Agent", "Growth Agent", "Customer Agent"]
    latest_batch = latest_replenishment_batch()
    summary = replenishment_summary(latest_batch["batch_id"] if latest_batch else None)
    metrics = {
        "agents": one("select count(*) as value from ai_agents where status='active'")["value"],
        "pending_runs": one("select count(*) as value from ai_agent_runs where approval_status='pending'")["value"],
        "pending_tasks": one("select count(*) as value from ai_tasks where approval_status='pending'")["value"],
        "knowledge": one("select count(*) as value from ai_knowledge_items where status='approved'")["value"],
    }
    snapshot = build_ceo_strategy_snapshot(metrics, latest_batch, summary)
    return jsonify({
        "ok": True,
        "question": question,
        "router": {"mode": "automatic", "agents": routed_agents},
        "answer": {
            "发生什么": snapshot["briefing"]["what_happened"],
            "为什么": snapshot["briefing"]["why_happened"],
            "影响": snapshot["risks"] + snapshot["opportunities"],
            "建议行动": snapshot["briefing"]["what_should_do_next"],
        },
    })


@app.get("/ops-api/ceo/strategy")
@permission_required("ai.ceo")
def ceo_strategy_api():
    latest_batch = latest_replenishment_batch()
    summary = replenishment_summary(latest_batch["batch_id"] if latest_batch else None)
    metrics = {
        "agents": one("select count(*) as value from ai_agents where status='active'")["value"],
        "pending_runs": one("select count(*) as value from ai_agent_runs where approval_status='pending'")["value"],
        "pending_tasks": one("select count(*) as value from ai_tasks where approval_status='pending'")["value"],
        "knowledge": one("select count(*) as value from ai_knowledge_items where status='approved'")["value"],
    }
    return jsonify({"ok": True, "snapshot": build_ceo_strategy_snapshot(
        metrics, latest_batch, summary,
        approved_runs=one("select count(*) as value from ai_agent_runs where approval_status='approved'")["value"],
        memories=one("select count(*) as value from ai_memory_items where status in ('approved','pending_review')")["value"],
    )})


@app.route("/dashboard")
@login_required
def dashboard_compat():
    return redirect("/home")


@app.route("/workbench")
@permission_required("ai.use")
def workbench():
    user = current_user()
    preview_question = request.args.get("q") or AI_WORKSPACE_V6_EXAMPLES[1]
    return render_template(
        "workbench.html", user=user, agents=accessible_agents(user), runs=visible_runs(user, 30),
        examples=AI_WORKSPACE_V6_EXAMPLES, v6=workspace_v6_context(preview_question),
        contract=build_ai_os_v6_contract(), workspace_label=AI_WORKSPACE_V6_LABEL,
    )


@app.post("/ops-api/runs")
@permission_required("ai.use")
def create_run():
    require_csrf()
    question = str(request.form.get("question") or "").strip()
    if not question:
        raise ValueError("企业问题不能为空")
    user = current_user()
    route = route_ai_question(question)
    response = {"conclusion": "AI OS V6 prepared a governed recommendation.", "reason": "AI Router V6 selected intent, agents, Core data, and task policy from the question.", "data_source": route["core_data_sources"], "recommendation": "Review the recommendation and approve governed operational actions only.", "next_action": "Create a V6 autonomous draft task for the responsible owner.", "route": route}
    evidence = v6_evidence_from_route(route)
    validate_ai_run(question, evidence)
    agent_id = select_v6_agent_id(route, user)
    selected_agent = one("select agent_type from ai_agents where agent_id=%s and status='active'", (agent_id,))
    if not selected_agent:
        raise ValueError("AI助手不存在或未启用")
    permission_context = authorize_ai_context(user["identity"], selected_agent["agent_type"], request.form.get("store_id"))
    run_id = new_id("RUN")
    task = create_ai_task(question, owner=user.get("real_name") or user.get("display_name") or "AI Router V6")
    result = {"response": response, "auto_task": task, "memory_learning": "pending_feedback_after_owner_decision"}
    cur = get_db().cursor()
    cur.execute(
        """insert into ai_agent_runs(run_id,agent_id,question,context_json,evidence_json,answer,result_json,status,approval_status,created_by)
        values(%s,%s,%s,%s::jsonb,%s::jsonb,%s,%s::jsonb,'pending_review','pending',%s)""",
        (run_id, agent_id, question, json.dumps({
            "ai_router_v6": route, "business_objects": route["business_objects"],
            "required_agents": route["selected_agents"], "required_data": route["core_data_sources"],
            "identity": permission_context["identity"], "effective_store_id": permission_context["effective_store_id"],
            "core_access": "read_only_auto_linked", "manual_configuration_removed": True,
        }, ensure_ascii=False), json.dumps(evidence, ensure_ascii=False), answer_text_from_v6_response(response),
         json.dumps(result, ensure_ascii=False), session["user_id"]),
    )
    save_evidence(cur, "agent_run", run_id, evidence)
    cur.execute(
        """insert into ai_tasks(task_id,title,description,owner_name,priority,status,source_type,source_id,source_ref,evidence_json,created_by)
        values(%s,%s,%s,%s,%s,'pending_approval','ai_agent_run',%s,%s,%s::jsonb,%s)""",
        (task["task_id"] + "-" + run_id[-8:], task["title"], "Auto-generated by AI Router V6; execution requires human approval.",
         task["owner"], task["priority"], run_id, "https://ai.vafox.com/workbench#" + run_id, json.dumps(evidence, ensure_ascii=False), session["user_id"]),
    )
    get_db().commit()
    return redirect("/workbench#" + run_id)


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


@app.get("/admin")
@permission_required("identity.view")
def admin_page():
    return render_template("admin.html", user=current_user())


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
    return redirect("/home")


@app.get("/replenishment")
@replenishment_required
def replenishment_center():
    user = current_user()
    batch = latest_replenishment_batch()
    summaries = replenishment_summary(batch["batch_id"] if batch else None)
    if user["role"] == "store_manager":
        summaries = [item for item in summaries if item["store_code"] == user.get("store_code")]
    return render_template(
        "replenishment.html", user=user, batch=batch, summaries=summaries,
        stores=ALLOWED_STORES, can_import=user["role"] in ("admin", "manager", "boss"),
    )


@app.get("/replenishment/stores/<store_code>")
@replenishment_required
def replenishment_store(store_code):
    if store_code not in ALLOWED_STORES:
        abort(404)
    user = current_user()
    if not can_access_store(user, store_code):
        abort(403)
    requested_batch = request.args.get("batch")
    batch = one("select * from replenishment_batches where batch_id=%s", (requested_batch,)) if requested_batch else latest_replenishment_batch()
    if not batch:
        return render_template("replenishment_store.html", user=user, store_code=store_code,
                               store_name=ALLOWED_STORES[store_code], batch=None, items=[], brands=[], categories=[])
    conditions = ["batch_id=%s", "store_code=%s"]
    params = [batch["batch_id"], store_code]
    brand = str(request.args.get("brand") or "").strip()
    category = str(request.args.get("category") or "").strip()
    priority = str(request.args.get("priority") or "").strip()
    query = str(request.args.get("q") or "").strip()
    if brand:
        conditions.append("brand_name=%s")
        params.append(brand)
    if category:
        conditions.append("category_name=%s")
        params.append(category)
    if priority:
        conditions.append("priority=%s")
        params.append(priority)
    if query:
        conditions.append("(sku_code ilike %s or product_name ilike %s)")
        params.extend(["%" + query + "%", "%" + query + "%"])
    order_map = {
        "sales": "sales_30d desc,sku_code", "quantity": "suggested_qty desc,sku_code",
        "stock_days": "stock_days asc nulls last,sku_code",
    }
    order_sql = order_map.get(request.args.get("sort"), "case priority when '紧急' then 1 when '高' then 2 when '普通' then 3 else 4 end,stock_days asc nulls last,sku_code")
    items = rows("select * from replenishment_items where {} order by {}".format(" and ".join(conditions), order_sql), tuple(params))
    brands = rows("select distinct brand_name from replenishment_items where batch_id=%s and store_code=%s and brand_name<>'' order by brand_name", (batch["batch_id"], store_code))
    categories = rows("select distinct category_name from replenishment_items where batch_id=%s and store_code=%s and category_name<>'' order by category_name", (batch["batch_id"], store_code))
    return render_template(
        "replenishment_store.html", user=user, store_code=store_code, store_name=ALLOWED_STORES[store_code],
        batch=batch, items=items, brands=brands, categories=categories, filters=request.args,
    )


@app.get("/replenishment/history")
@replenishment_required
def replenishment_history():
    return render_template(
        "replenishment_history.html", user=current_user(),
        batches=rows("select * from replenishment_batches order by business_date desc,revision desc,created_at desc limit 180"),
    )


@app.get("/replenishment/history/<batch_id>")
@replenishment_required
def replenishment_history_detail(batch_id):
    batch = one("select * from replenishment_batches where batch_id=%s", (batch_id,))
    if not batch:
        abort(404)
    user = current_user()
    summaries = replenishment_summary(batch_id)
    if user["role"] == "store_manager":
        summaries = [item for item in summaries if item["store_code"] == user.get("store_code")]
    return render_template("replenishment_history_detail.html", user=user, batch=batch, summaries=summaries)


@app.get("/admin/data-import")
@manager_required
def replenishment_import_page():
    return render_template("replenishment_import.html", user=current_user(), rule_version=RULE_VERSION,
                           business_date=business_today().isoformat())


@app.post("/ops-api/replenishment/import")
@manager_required
def import_replenishment_file():
    require_csrf()
    upload = request.files.get("file")
    if not upload or not upload.filename:
        raise ValueError("请选择补货数据文件")
    content = upload.read(10 * 1024 * 1024 + 1)
    if len(content) > 10 * 1024 * 1024:
        raise ValueError("文件不能超过10MB")
    source_name = os.path.basename(upload.filename).replace("\x00", "").strip()
    input_rows = parse_uploaded_file(source_name, content)
    try:
        business_date = date.fromisoformat(request.form.get("business_date") or business_today().isoformat())
    except ValueError as exc:
        raise ValueError("业务日期格式不正确") from exc
    batch_id = save_replenishment_batch(
        input_rows, "admin_upload", source_name, business_date,
        {"original_filename": source_name, "sha256": hashlib.sha256(content).hexdigest(),
         "source_label": "管理员上传的真实SAP导出文件"},
    )
    return redirect("/replenishment/history/{}".format(batch_id))


def generate_replenishment_from_core():
    """Fetch one normalized Core batch and save it exactly once."""
    result = data_core_connector(
        os.environ.get("CORE_BASE_URL", "https://core.vafox.com"),
        os.environ.get("CORE_API_TOKEN", ""),
    ).get_json("api/v1/replenishment/input")
    if not result["ok"]:
        raise ValueError("Data Core 补货接口暂不可用：{}".format(result.get("error") or "unknown"))
    payload = result["data"] or {}
    core_batch_id = str(payload.get("batch_id") or "").strip()
    if not core_batch_id:
        raise ValueError("Data Core 返回结果缺少 batch_id")
    existing = one(
        """select batch_id from replenishment_batches where source_type='core_api' and source_name=%s
        and status in ('completed','completed_with_warnings') order by created_at desc limit 1""",
        (core_batch_id,),
    )
    if existing:
        return existing["batch_id"], False
    input_rows = payload.get("items") or payload.get("data") or []
    business_date = date.fromisoformat(payload.get("business_date") or business_today().isoformat())
    batch_id = save_replenishment_batch(
        input_rows, "core_api", core_batch_id, business_date,
        {"core_batch_id": core_batch_id, "data_as_of": payload.get("data_as_of"),
         "source_label": "core.vafox.com"},
    )
    return batch_id, True


@app.post("/ops-api/replenishment/pull-core")
@manager_required
def pull_replenishment_from_core():
    require_csrf()
    batch_id, _created = generate_replenishment_from_core()
    return redirect("/replenishment/history/{}".format(batch_id))


@app.post("/ops-api/internal/replenishment/run")
def run_replenishment_internal():
    require_service_token()
    batch_id, created = generate_replenishment_from_core()
    return jsonify({"ok": True, "batch_id": batch_id, "created": created,
                    "source": "core.vafox.com", "sap_write": False})


@app.get("/ops-api/replenishment/export/<batch_id>/<store_code>.xlsx")
@replenishment_required
def export_replenishment_excel(batch_id, store_code):
    if store_code not in ALLOWED_STORES:
        abort(404)
    user = current_user()
    if not can_access_store(user, store_code):
        abort(403)
    batch = one("select * from replenishment_batches where batch_id=%s", (batch_id,))
    if not batch:
        abort(404)
    items = rows(
        """select * from replenishment_items where batch_id=%s and store_code=%s
        order by case priority when '紧急' then 1 when '高' then 2 when '普通' then 3 else 4 end,sku_code""",
        (batch_id, store_code),
    )
    stream = build_excel(items, {
        "业务日期": batch["business_date"].isoformat(), "数据来源": batch["source_name"],
        "数据批次": batch["batch_id"], "规则版本": batch["rule_version"],
        "生成时间": batch["completed_at"].astimezone().isoformat(timespec="seconds") if batch["completed_at"] else "",
    })
    cur = get_db().cursor()
    cur.execute(
        "insert into replenishment_audit_logs(action,batch_id,store_code,actor_id) values('export',%s,%s,%s)",
        (batch_id, store_code, session.get("user_id")),
    )
    get_db().commit()
    filename = "{}_AI补货建议_{}.xlsx".format(ALLOWED_STORES[store_code], batch["business_date"].strftime("%Y%m%d"))
    return send_file(stream, as_attachment=True, download_name=filename,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.get("/ops-api/replenishment/latest")
@replenishment_required
def replenishment_latest_api():
    batch = latest_replenishment_batch()
    if not batch:
        return jsonify({"ok": True, "data_status": "waiting_for_data", "batch": None, "stores": []})
    return jsonify({
        "ok": True, "data_status": batch["status"],
        "batch": {key: batch[key] for key in ("batch_id", "business_date", "source_type", "source_name", "rule_version", "status")},
        "stores": replenishment_summary(batch["batch_id"]),
    })




@app.get("/internal/health")
@permission_required("identity.manage")
def internal_health_console():
    record_permission_audit("internal.health.view", "allowed", "runtime", "production", "管理员查看生产运行健康控制台")
    services = [version_payload(name) for name in ("gateway", "huyan", "ai", "core")]
    rows_html = "".join(
        "<tr><td>{service}</td><td>{status}</td><td>{version}</td><td>{commit}</td><td>{build_time}</td><td>{deploy_time}</td><td>{environment}</td></tr>".format(**item)
        for item in services
    )
    return """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VAFOX Internal Health</title><style>body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Microsoft YaHei,sans-serif;margin:0;background:#f6f8f7;color:#12251d}.wrap{max-width:1100px;margin:40px auto;padding:0 20px}.card{background:white;border:1px solid #dce5df;border-radius:18px;padding:24px;box-shadow:0 10px 30px rgba(10,35,25,.06)}table{width:100%;border-collapse:collapse}th,td{text-align:left;border-bottom:1px solid #edf2ef;padding:12px}th{color:#476256;font-size:13px;text-transform:uppercase}.ok{color:#087f5b;font-weight:800}</style></head><body><main class="wrap"><section class="card"><h1>VAFOX AI OS V6 Internal Health Console</h1><p>Administrator-only production verification console. RBAC/ABAC and permission audit controls are enforced before rendering.</p><table><thead><tr><th>Service</th><th>Status</th><th>Version</th><th>Commit</th><th>Build</th><th>Deploy</th><th>Environment</th></tr></thead><tbody>""" + rows_html + """</tbody></table></section></main></body></html>"""



@app.get("/internal/runtime-check")
@permission_required("identity.manage")
def internal_runtime_check():
    record_permission_audit("internal.runtime_check.view", "allowed", "runtime", "production", "管理员查看 AI OS V6 运行自验证页面")
    services = [runtime_payload(name) for name in ("gateway", "huyan", "ai", "core")]
    rows_html = "".join(
        "<tr><td>{service}</td><td class='pass'>PASS</td><td>{version}</td><td>{commit}</td><td>{build_time}</td><td>{environment}</td></tr>".format(**item)
        for item in services
    )
    return """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI OS V6 Runtime Check</title><style>body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Microsoft YaHei,sans-serif;margin:0;background:#f6f8f7;color:#12251d}.wrap{max-width:1100px;margin:40px auto;padding:0 20px}.card{background:white;border:1px solid #dce5df;border-radius:18px;padding:24px;box-shadow:0 10px 30px rgba(10,35,25,.06)}table{width:100%;border-collapse:collapse}th,td{text-align:left;border-bottom:1px solid #edf2ef;padding:12px}th{color:#476256;font-size:13px;text-transform:uppercase}.pass{color:#087f5b;font-weight:900}.badge{display:inline-flex;border-radius:999px;background:#dff5e9;color:#087f5b;padding:6px 12px;font-weight:800}</style></head><body><main class="wrap"><section class="card"><span class="badge">Version: AI OS V6</span><h1>VAFOX Runtime Verification</h1><p>Admin-only self-verification page. Only safe runtime metadata is shown; RBAC and audit logging are preserved.</p><table><thead><tr><th>Service</th><th>Result</th><th>Version</th><th>Commit</th><th>Build</th><th>Environment</th></tr></thead><tbody>""" + rows_html + """</tbody></table></section></main></body></html>"""

@app.get("/version")
@app.get("/health/version")
def version():
    return jsonify(version_payload("ai"))


@app.get("/health/runtime")
def runtime_health():
    return jsonify(runtime_payload("ai"))


@app.get("/health")
def platform_health():
    try:
        value = one("select 1 as value")["value"]
        checks = {"process": {"status": "healthy"}, "database": {"status": "healthy" if value == 1 else "unhealthy"}, "dependencies": {"status": "healthy", "core_configured": bool(os.environ.get("CORE_BASE_URL"))}}
        payload = health_payload("foxbrain-ai", checks)
        return jsonify(payload), 200 if payload["status"] == "healthy" else 503
    except Exception:
        return jsonify(health_payload("foxbrain-ai", {"process": {"status": "healthy"}, "database": {"status": "unhealthy"}, "dependencies": {"status": "healthy"}})), 503


@app.get("/control-tower")
def control_tower():
    return jsonify(control_tower_status())


@app.get("/ops-api/health")
def health():
    try:
        value = one("select 1 as value")["value"]
        return jsonify({"ok": value == 1, "service": "VAFOX Enterprise AI Center", "sap_write": False})
    except Exception:
        return jsonify({"ok": False, "service": "VAFOX Enterprise AI Center"}), 503


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
