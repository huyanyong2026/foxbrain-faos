#!/usr/bin/env python3
"""FoxBrain Enterprise AI collaboration application."""

from __future__ import annotations

import json
import os
import secrets
from datetime import timedelta
from functools import wraps
from urllib.parse import urlparse

import bcrypt
import psycopg2
import psycopg2.extras
from flask import Flask, abort, g, jsonify, redirect, render_template, request, session

try:
    from .connectors import ceo_brain_connector, data_core_connector, living_enterprise_connector
    from .domain import (
        AGENT_ROLES, CONNECTIONS, DEFAULT_APPROVAL_POLICY, SCHEMA_STATEMENTS, new_id, normalize_evidence,
        require_human_approval, validate_ai_run, validate_feedback, validate_task,
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
    for statement in SCHEMA_STATEMENTS:
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
    cur.execute("select id,username,display_name,email,role,status,last_login from auth_users where id=%s", (session["user_id"],))
    return cur.fetchone()


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
        if session.get("role") not in ("admin", "manager", "boss"):
            abort(403)
        return function(*args, **kwargs)
    return decorated


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


@app.route("/")
def index():
    return redirect("/dashboard" if "user_id" in session else "/auth/login")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.post("/api/login")
def login_api():
    data = request.get_json(silent=True) or request.form
    user = one("select * from auth_users where username=%s", ((data.get("username") or "").strip(),))
    password = data.get("password") or ""
    if not user or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return jsonify({"ok": False, "message": "用户名或密码错误"}), 401
    if user["status"] != "approved":
        return jsonify({"ok": False, "message": "账号尚未通过审批"}), 403
    session.permanent = True
    session.update(user_id=user["id"], username=user["username"], display_name=user["display_name"], role=user["role"])
    csrf_token()
    cur = get_db().cursor()
    cur.execute("update auth_users set last_login=now() where id=%s", (user["id"],))
    get_db().commit()
    return jsonify({"ok": True, "redirect": "/dashboard"})


@app.post("/api/logout")
@login_required
def logout_api():
    require_csrf()
    session.clear()
    return jsonify({"ok": True, "redirect": "/auth/login"})


@app.route("/dashboard")
@login_required
def dashboard():
    metrics = {
        "agents": one("select count(*) as value from ai_agents where status='active'")["value"],
        "pending_runs": one("select count(*) as value from ai_agent_runs where approval_status='pending'")["value"],
        "pending_tasks": one("select count(*) as value from ai_tasks where approval_status='pending'")["value"],
        "knowledge": one("select count(*) as value from ai_knowledge_items where status='approved'")["value"],
    }
    return render_template("dashboard.html", user=current_user(), metrics=metrics,
                           connections=rows("select * from enterprise_connections order by id"),
                           runs=rows("select * from ai_agent_runs order by updated_at desc limit 8"))


@app.route("/workbench")
@login_required
def workbench():
    return render_template("workbench.html", user=current_user(), agents=rows("select * from ai_agents where status='active' order by id"),
                           runs=rows("select * from ai_agent_runs order by updated_at desc limit 30"))


@app.post("/ops-api/runs")
@login_required
def create_run():
    require_csrf()
    form = request.form
    evidence = evidence_from_form(form)
    validate_ai_run(form.get("question"), evidence)
    run_id = new_id("RUN")
    cur = get_db().cursor()
    cur.execute(
        """insert into ai_agent_runs(run_id,agent_id,question,context_json,evidence_json,created_by)
        values(%s,%s,%s,%s::jsonb,%s::jsonb,%s)""",
        (run_id, form.get("agent_id"), form.get("question").strip(), json.dumps({"object_type": form.get("object_type"), "object_id": form.get("object_id")}, ensure_ascii=False), json.dumps(evidence, ensure_ascii=False), session["user_id"]),
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
@login_required
def agents_page():
    return render_template("agents.html", user=current_user(), agents=rows("select * from ai_agents order by id"))


@app.route("/wecom")
@login_required
def wecom_page():
    return render_template("wecom.html", user=current_user(), connections=rows("select * from wecom_connections order by id"))


@app.route("/knowledge")
@login_required
def knowledge_page():
    return render_template("knowledge.html", user=current_user(), items=rows("select * from ai_knowledge_items order by updated_at desc limit 100"))


@app.post("/ops-api/knowledge")
@login_required
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
@login_required
def tasks_page():
    return render_template("tasks.html", user=current_user(), tasks=rows("select * from ai_tasks order by updated_at desc limit 100"),
                           approved_runs=rows("select run_id,question,evidence_json from ai_agent_runs where approval_status='approved' order by reviewed_at desc limit 50"))


@app.post("/ops-api/tasks")
@login_required
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
@login_required
def feedback_page():
    return render_template("feedback.html", user=current_user(), feedback=rows("select f.*,r.question from ai_feedback f join ai_agent_runs r on r.run_id=f.run_id order by f.created_at desc limit 100"),
                           runs=rows("select run_id,question from ai_agent_runs where approval_status in ('approved','rejected') order by reviewed_at desc limit 50"))


@app.post("/ops-api/feedback")
@login_required
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


if __name__ == "__main__":
    init_db()
    app.run(host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", "5010")), debug=False)
