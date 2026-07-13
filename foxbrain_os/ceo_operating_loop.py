"""CEO Operating Loop persistence and evidence chain.

Facts are snapshots of the local Data Core replica. AI analysis may only be
attached with an explicit ai.vafox.com source and evidence. Every suggestion is
stored as pending review until a human confirms it.
"""

from __future__ import annotations

import json
import time
import uuid
from urllib.parse import urlparse


def _now():
    return int(time.time())


def _json(value, fallback=None):
    if value in (None, ""):
        value = [] if fallback is None else fallback
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            value = {"text": value}
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _source(source_type, source_id, source_ref):
    source = {
        "source_type": str(source_type or "").strip(),
        "source_id": str(source_id or "").strip(),
        "source_ref": str(source_ref or "").strip(),
    }
    missing = [key for key, value in source.items() if not value]
    if missing:
        raise ValueError("经营闭环记录缺少来源：{}".format("、".join(missing)))
    return source


def _evidence(evidence):
    if isinstance(evidence, str):
        try:
            evidence = json.loads(evidence)
        except (TypeError, ValueError):
            evidence = []
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("经营建议必须包含可追溯依据")
    for item in evidence:
        if not isinstance(item, dict) or not str(item.get("source_type") or item.get("source") or "").strip():
            raise ValueError("每条依据必须标明来源")
    return evidence


def ensure_ceo_operating_loop_schema(conn):
    conn.execute(
        """create table if not exists ceo_morning_briefs(
        id integer primary key autoincrement,brief_id text not null unique,brief_date text not null,
        title text not null,fact_snapshot_json text not null,evidence_json text not null,
        ai_analysis text,ai_source_ref text,status text not null default 'waiting_ai',
        source_type text not null,source_id text not null,source_ref text not null,
        created_by integer,confirmed_by integer,confirmed_at integer,created_at integer not null,
        updated_at integer not null,unique(brief_date))"""
    )
    conn.execute(
        """create table if not exists enterprise_questions(
        id integer primary key autoincrement,question_id text not null unique,question text not null,
        context_json text not null default '{}',fact_snapshot_json text not null default '{}',
        evidence_json text not null default '[]',ai_analysis text,ai_source_ref text,
        status text not null default 'waiting_ai',created_by integer,reviewed_by integer,
        reviewed_at integer,created_at integer not null,updated_at integer not null)"""
    )
    conn.execute(
        """create table if not exists ceo_decision_memories(
        id integer primary key autoincrement,decision_id text not null unique,question_id text,
        title text not null,decision text not null,rationale text,evidence_json text not null,
        status text not null default 'draft',source_type text not null,source_id text not null,
        source_ref text not null,decided_by integer,confirmed_by integer,confirmed_at integer,
        created_at integer not null,updated_at integer not null)"""
    )
    conn.execute(
        """create table if not exists operating_evidence_links(
        id integer primary key autoincrement,target_type text not null,target_id text not null,
        evidence_role text not null,statement text,source_layer text not null,
        source_type text not null,source_id text not null,source_ref text not null,
        captured_at integer not null,unique(target_type,target_id,evidence_role,source_type,source_id))"""
    )
    conn.execute(
        """create table if not exists operating_reviews(
        id integer primary key autoincrement,review_id text not null unique,decision_id text,
        period_start text,period_end text,expected_result text,actual_result text not null,
        variance_analysis text,lessons text,next_action text,status text not null default 'draft',
        evidence_json text not null,source_type text not null,source_id text not null,
        source_ref text not null,created_by integer,confirmed_by integer,confirmed_at integer,
        created_at integer not null,updated_at integer not null)"""
    )
    for sql in (
        "create index if not exists idx_morning_briefs_date on ceo_morning_briefs(brief_date,status)",
        "create index if not exists idx_enterprise_questions_status on enterprise_questions(status,updated_at)",
        "create index if not exists idx_ceo_decisions_status on ceo_decision_memories(status,updated_at)",
        "create index if not exists idx_operating_evidence_target on operating_evidence_links(target_type,target_id)",
        "create index if not exists idx_operating_reviews_decision on operating_reviews(decision_id,status)",
    ):
        conn.execute(sql)


def _link_evidence(conn, target_type, target_id, evidence):
    now = _now()
    for index, item in enumerate(_evidence(evidence), 1):
        source_type = str(item.get("source_type") or item.get("source") or "").strip()
        source_id = str(item.get("source_id") or item.get("record_id") or item.get("metric") or index)
        source_ref = str(item.get("source_ref") or item.get("url") or "{}#{}".format(source_type, source_id))
        layer = str(item.get("source_layer") or ("ai_analysis" if source_type == "ai.vafox.com" else "data_core"))
        conn.execute(
            """insert or ignore into operating_evidence_links(
            target_type,target_id,evidence_role,statement,source_layer,source_type,source_id,source_ref,captured_at)
            values(?,?,?,?,?,?,?,?,?)""",
            (target_type, str(target_id), str(item.get("role") or "supporting_fact"),
             str(item.get("statement") or item.get("value") or ""), layer, source_type, source_id, source_ref, now),
        )


def create_morning_brief(conn, brief_date, fact_snapshot, evidence, created_by=None):
    ensure_ceo_operating_loop_schema(conn)
    evidence = _evidence(evidence)
    existing = conn.execute("select * from ceo_morning_briefs where brief_date=?", (brief_date,)).fetchone()
    if existing:
        return {"ok": True, "brief_id": existing["brief_id"], "status": existing["status"], "duplicate": True}
    now = _now()
    brief_id = "MB-{}-{}".format(str(brief_date).replace("-", ""), uuid.uuid4().hex[:8])
    source = _source("core.vafox.com", "daily-facts-{}".format(brief_date), "Data Core企业事实快照/{}".format(brief_date))
    conn.execute(
        """insert into ceo_morning_briefs(
        brief_id,brief_date,title,fact_snapshot_json,evidence_json,status,source_type,source_id,
        source_ref,created_by,created_at,updated_at) values(?,?,?,?,?,'waiting_ai',?,?,?,?,?,?)""",
        (brief_id, brief_date, "CEO Morning Brief {}".format(brief_date), _json(fact_snapshot, {}),
         _json(evidence, []), source["source_type"], source["source_id"], source["source_ref"], created_by, now, now),
    )
    _link_evidence(conn, "morning_brief", brief_id, evidence)
    return {"ok": True, "brief_id": brief_id, "status": "waiting_ai", "duplicate": False}


def create_enterprise_question(conn, question, fact_snapshot, evidence, context=None, created_by=None):
    ensure_ceo_operating_loop_schema(conn)
    if not str(question or "").strip():
        raise ValueError("企业问题不能为空")
    evidence = _evidence(evidence)
    now = _now()
    question_id = "EQ-{}-{}".format(now, uuid.uuid4().hex[:8])
    conn.execute(
        """insert into enterprise_questions(
        question_id,question,context_json,fact_snapshot_json,evidence_json,status,created_by,created_at,updated_at)
        values(?,?,?,?,?,'waiting_ai',?,?,?)""",
        (question_id, str(question).strip(), _json(context, {}), _json(fact_snapshot, {}), _json(evidence, []), created_by, now, now),
    )
    _link_evidence(conn, "enterprise_question", question_id, evidence)
    return {"ok": True, "question_id": question_id, "status": "waiting_ai"}


def attach_ai_analysis(conn, target_type, target_id, analysis, evidence, source_ref):
    ensure_ceo_operating_loop_schema(conn)
    if target_type not in ("morning_brief", "enterprise_question"):
        raise ValueError("不支持的 AI 分析目标")
    if not str(analysis or "").strip():
        raise ValueError("AI 分析内容不能为空")
    source_host = (urlparse(str(source_ref or "")).hostname or "").lower()
    if source_host != "ai.vafox.com" and not source_host.endswith(".ai.vafox.com"):
        raise ValueError("CEO Operating Loop 的 AI 分析必须来自 ai.vafox.com")
    evidence = _evidence(evidence)
    table, key = ("ceo_morning_briefs", "brief_id") if target_type == "morning_brief" else ("enterprise_questions", "question_id")
    if not conn.execute("select 1 from {} where {}=?".format(table, key), (target_id,)).fetchone():
        raise ValueError("AI 分析目标不存在")
    now = _now()
    conn.execute(
        "update {} set ai_analysis=?,ai_source_ref=?,evidence_json=?,status='pending_review',updated_at=? where {}=?".format(table, key),
        (str(analysis).strip(), str(source_ref).strip(), _json(evidence, []), now, target_id),
    )
    _link_evidence(conn, target_type, target_id, evidence + [{
        "source_type": "ai.vafox.com", "source_id": target_id, "source_ref": source_ref,
        "source_layer": "ai_analysis", "role": "analysis_candidate", "statement": "AI分析候选，等待人工确认",
    }])
    return {"ok": True, "target_id": target_id, "status": "pending_review"}


def review_ai_analysis(conn, target_type, target_id, accepted, reviewed_by):
    ensure_ceo_operating_loop_schema(conn)
    if target_type not in ("morning_brief", "enterprise_question"):
        raise ValueError("不支持的 AI 分析目标")
    table, key = ("ceo_morning_briefs", "brief_id") if target_type == "morning_brief" else ("enterprise_questions", "question_id")
    now = _now()
    status = "confirmed" if accepted else "rejected"
    if target_type == "morning_brief":
        updated = conn.execute("update ceo_morning_briefs set status=?,confirmed_by=?,confirmed_at=?,updated_at=? where brief_id=? and status='pending_review'", (status, reviewed_by, now, now, target_id)).rowcount
    else:
        updated = conn.execute("update enterprise_questions set status=?,reviewed_by=?,reviewed_at=?,updated_at=? where question_id=? and status='pending_review'", (status, reviewed_by, now, now, target_id)).rowcount
    if not updated:
        raise ValueError("AI 分析不存在或尚未进入人工复核状态")
    return {"ok": True, "target_id": target_id, "status": status}


def create_decision_memory(conn, title, decision, rationale, evidence, decided_by, question_id=""):
    ensure_ceo_operating_loop_schema(conn)
    if not str(title or "").strip() or not str(decision or "").strip():
        raise ValueError("决策记忆必须填写标题和最终决定")
    evidence = _evidence(evidence)
    if question_id:
        question = conn.execute("select status from enterprise_questions where question_id=?", (question_id,)).fetchone()
        if not question or question["status"] != "confirmed":
            raise ValueError("关联的 AI 分析尚未经过人工确认")
    now = _now()
    decision_id = "DM-{}-{}".format(now, uuid.uuid4().hex[:8])
    source = _source("founder_decision", decision_id, "huyan.vafox.com/CEO人工决策")
    conn.execute(
        """insert into ceo_decision_memories(
        decision_id,question_id,title,decision,rationale,evidence_json,status,source_type,
        source_id,source_ref,decided_by,created_at,updated_at)
        values(?,?,?,?,?,?,'draft',?,?,?,?,?,?)""",
        (decision_id, question_id or None, str(title).strip(), str(decision).strip(), str(rationale or "").strip(),
         _json(evidence, []), source["source_type"], source["source_id"], source["source_ref"], decided_by, now, now),
    )
    _link_evidence(conn, "decision_memory", decision_id, evidence)
    return {"ok": True, "decision_id": decision_id, "status": "draft"}


def confirm_decision_memory(conn, decision_id, confirmed_by):
    ensure_ceo_operating_loop_schema(conn)
    now = _now()
    updated = conn.execute(
        "update ceo_decision_memories set status='confirmed',confirmed_by=?,confirmed_at=?,updated_at=? where decision_id=? and status='draft'",
        (confirmed_by, now, now, decision_id),
    ).rowcount
    if not updated:
        raise ValueError("决策记忆不存在或已经处理")
    return {"ok": True, "decision_id": decision_id, "status": "confirmed"}


def create_operating_review(conn, decision_id, actual_result, evidence, created_by, period_start="", period_end="", expected_result="", variance_analysis="", lessons="", next_action=""):
    ensure_ceo_operating_loop_schema(conn)
    decision = conn.execute("select * from ceo_decision_memories where decision_id=? and status='confirmed'", (decision_id,)).fetchone()
    if not decision:
        raise ValueError("只能复盘已经人工确认的决策")
    if not str(actual_result or "").strip():
        raise ValueError("经营复盘必须填写实际结果")
    evidence = _evidence(evidence)
    now = _now()
    review_id = "OR-{}-{}".format(now, uuid.uuid4().hex[:8])
    source = _source("founder_review", review_id, "huyan.vafox.com/CEO经营复盘")
    conn.execute(
        """insert into operating_reviews(
        review_id,decision_id,period_start,period_end,expected_result,actual_result,variance_analysis,
        lessons,next_action,status,evidence_json,source_type,source_id,source_ref,created_by,created_at,updated_at)
        values(?,?,?,?,?,?,?,?,?,'draft',?,?,?,?,?,?,?)""",
        (review_id, decision_id, period_start, period_end, expected_result, str(actual_result).strip(),
         variance_analysis, lessons, next_action, _json(evidence, []), source["source_type"],
         source["source_id"], source["source_ref"], created_by, now, now),
    )
    _link_evidence(conn, "operating_review", review_id, evidence)
    return {"ok": True, "review_id": review_id, "status": "draft"}


def confirm_operating_review(conn, review_id, confirmed_by):
    ensure_ceo_operating_loop_schema(conn)
    now = _now()
    updated = conn.execute("update operating_reviews set status='confirmed',confirmed_by=?,confirmed_at=?,updated_at=? where review_id=? and status='draft'", (confirmed_by, now, now, review_id)).rowcount
    if not updated:
        raise ValueError("经营复盘不存在或已经处理")
    return {"ok": True, "review_id": review_id, "status": "confirmed"}


def evidence_chain(conn, target_type="", target_id="", limit=200):
    ensure_ceo_operating_loop_schema(conn)
    where, params = [], []
    if target_type:
        where.append("target_type=?")
        params.append(target_type)
    if target_id:
        where.append("target_id=?")
        params.append(str(target_id))
    sql = "select * from operating_evidence_links"
    if where:
        sql += " where " + " and ".join(where)
    sql += " order by captured_at desc limit ?"
    params.append(int(limit))
    return {"ok": True, "evidence": [dict(row) for row in conn.execute(sql, params).fetchall()]}


def operating_loop_summary(conn):
    ensure_ceo_operating_loop_schema(conn)
    def count(table, where=""):
        return int(conn.execute("select count(*) from {} {}".format(table, where)).fetchone()[0] or 0)
    latest_brief = conn.execute("select * from ceo_morning_briefs order by brief_date desc,updated_at desc limit 1").fetchone()
    return {
        "ok": True,
        "latest_brief": dict(latest_brief) if latest_brief else None,
        "briefs": count("ceo_morning_briefs"),
        "questions_waiting_ai": count("enterprise_questions", "where status='waiting_ai'"),
        "questions_pending_review": count("enterprise_questions", "where status='pending_review'"),
        "decisions_confirmed": count("ceo_decision_memories", "where status='confirmed'"),
        "reviews_confirmed": count("operating_reviews", "where status='confirmed'"),
        "evidence_links": count("operating_evidence_links"),
        "guardrails": {
            "facts": "core.vafox.com via local read-only replica",
            "ai": "ai.vafox.com only",
            "decisions": "human confirmation required",
            "sap_write": False,
        },
    }
