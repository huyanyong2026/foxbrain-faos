"""Evidence-backed CEO Enterprise Brain composition layer.

The module reads local FoxBrain facts derived from the Data Core and stores only
Founder-authored constitution and memory records. It never connects to SAP.
"""

from __future__ import annotations

import json
import time
import uuid


def _now():
    return int(time.time())


def _table_exists(conn, table):
    return bool(conn.execute("select 1 from sqlite_master where type='table' and name=?", (table,)).fetchone())


def _columns(conn, table):
    return {row[1] for row in conn.execute("pragma table_info({})".format(table)).fetchall()} if _table_exists(conn, table) else set()


def _json(value, fallback):
    if value in (None, ""):
        value = fallback
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            value = [item.strip() for item in value.replace("\r", "").split("\n") if item.strip()]
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _source(source_type, source_id, source_ref):
    source = {
        "source_type": str(source_type or "").strip(),
        "source_id": str(source_id or "").strip(),
        "source_ref": str(source_ref or "").strip(),
    }
    missing = [key for key, value in source.items() if not value]
    if missing:
        raise ValueError("企业大脑记录缺少来源：{}".format("、".join(missing)))
    return source


def ensure_enterprise_brain_schema(conn):
    conn.execute(
        """create table if not exists enterprise_constitutions(
        id integer primary key autoincrement,
        constitution_id text not null unique,
        version integer not null,
        title text not null,
        mission text not null,
        vision text,
        values_json text not null default '[]',
        principles_json text not null default '[]',
        status text not null default 'draft',
        source_type text not null check(length(trim(source_type))>0),
        source_id text not null check(length(trim(source_id))>0),
        source_ref text not null check(length(trim(source_ref))>0),
        created_by integer,
        approved_by integer,
        approved_at integer,
        created_at integer not null,
        updated_at integer not null,
        unique(version))"""
    )
    conn.execute(
        """create table if not exists founder_memories(
        id integer primary key autoincrement,
        memory_id text not null unique,
        title text not null,
        memory_type text not null default 'operating_judgment',
        situation text not null,
        judgment text not null,
        lesson text,
        future_guidance text,
        related_object_type text,
        related_object_id integer,
        evidence_json text not null default '[]',
        status text not null default 'draft',
        access_scope text not null default 'owner',
        source_type text not null check(length(trim(source_type))>0),
        source_id text not null check(length(trim(source_id))>0),
        source_ref text not null check(length(trim(source_ref))>0),
        created_by integer,
        confirmed_by integer,
        confirmed_at integer,
        occurred_at integer,
        created_at integer not null,
        updated_at integer not null)"""
    )
    conn.execute("create index if not exists idx_constitution_status on enterprise_constitutions(status,version)")
    conn.execute("create index if not exists idx_founder_memory_status on founder_memories(status,memory_type,updated_at)")
    conn.execute("create index if not exists idx_founder_memory_object on founder_memories(related_object_type,related_object_id)")


def create_constitution_draft(conn, title, mission, vision="", values=None, principles=None, created_by=None, source_type="founder_input", source_id="", source_ref=""):
    ensure_enterprise_brain_schema(conn)
    if not str(title or "").strip() or not str(mission or "").strip():
        raise ValueError("企业宪章必须填写标题和使命")
    source = _source(source_type, source_id, source_ref)
    version = int(conn.execute("select coalesce(max(version),0)+1 from enterprise_constitutions").fetchone()[0])
    now = _now()
    constitution_id = "CON-{}-{}".format(now, uuid.uuid4().hex[:8])
    conn.execute(
        """insert into enterprise_constitutions(
        constitution_id,version,title,mission,vision,values_json,principles_json,status,
        source_type,source_id,source_ref,created_by,created_at,updated_at)
        values(?,?,?,?,?,?,?,'draft',?,?,?,?,?,?)""",
        (constitution_id, version, str(title).strip(), str(mission).strip(), str(vision or "").strip(),
         _json(values, []), _json(principles, []), source["source_type"], source["source_id"],
         source["source_ref"], created_by, now, now),
    )
    return {"ok": True, "constitution_id": constitution_id, "version": version, "status": "draft"}


def activate_constitution(conn, constitution_id, approved_by):
    ensure_enterprise_brain_schema(conn)
    row = conn.execute("select * from enterprise_constitutions where constitution_id=?", (constitution_id,)).fetchone()
    if not row:
        raise ValueError("企业宪章不存在")
    now = _now()
    conn.execute("update enterprise_constitutions set status='archived',updated_at=? where status='active'", (now,))
    conn.execute(
        "update enterprise_constitutions set status='active',approved_by=?,approved_at=?,updated_at=? where constitution_id=?",
        (approved_by, now, now, constitution_id),
    )
    return {"ok": True, "constitution_id": constitution_id, "status": "active", "approved_at": now}


def create_founder_memory(conn, title, situation, judgment, lesson="", future_guidance="", memory_type="operating_judgment", related_object_type="", related_object_id=None, evidence=None, created_by=None, source_type="founder_input", source_id="", source_ref="", occurred_at=None):
    ensure_enterprise_brain_schema(conn)
    if not all(str(value or "").strip() for value in (title, situation, judgment)):
        raise ValueError("创始人记忆必须填写标题、当时情况和判断")
    source = _source(source_type, source_id, source_ref)
    now = _now()
    memory_id = "FM-{}-{}".format(now, uuid.uuid4().hex[:8])
    conn.execute(
        """insert into founder_memories(
        memory_id,title,memory_type,situation,judgment,lesson,future_guidance,related_object_type,
        related_object_id,evidence_json,status,access_scope,source_type,source_id,source_ref,
        created_by,occurred_at,created_at,updated_at)
        values(?,?,?,?,?,?,?,?,?,?,'draft','owner',?,?,?,?,?,?,?)""",
        (memory_id, str(title).strip(), str(memory_type or "operating_judgment"), str(situation).strip(),
         str(judgment).strip(), str(lesson or "").strip(), str(future_guidance or "").strip(),
         str(related_object_type or "").strip(), related_object_id, _json(evidence, []),
         source["source_type"], source["source_id"], source["source_ref"], created_by,
         int(occurred_at or now), now, now),
    )
    return {"ok": True, "memory_id": memory_id, "status": "draft"}


def confirm_founder_memory(conn, memory_id, confirmed_by):
    ensure_enterprise_brain_schema(conn)
    row = conn.execute("select id from founder_memories where memory_id=?", (memory_id,)).fetchone()
    if not row:
        raise ValueError("创始人记忆不存在")
    now = _now()
    conn.execute(
        "update founder_memories set status='confirmed',confirmed_by=?,confirmed_at=?,updated_at=? where memory_id=?",
        (confirmed_by, now, now, memory_id),
    )
    return {"ok": True, "memory_id": memory_id, "status": "confirmed"}


def _count(conn, table, where=""):
    if not _table_exists(conn, table):
        return 0
    return int(conn.execute("select count(*) from {} {}".format(table, where)).fetchone()[0] or 0)


def _latest_sync(conn):
    if not _table_exists(conn, "sync_runs"):
        return {"status": "no_data", "updated_at": None, "source": "Data Core 副本同步记录"}
    columns = _columns(conn, "sync_runs")
    time_field = "finished_at" if "finished_at" in columns else "started_at"
    row = conn.execute(
        "select status,{} updated_at from sync_runs where status in ('success','published','completed') order by coalesce({},0) desc limit 1".format(time_field, time_field)
    ).fetchone()
    return {"status": row["status"] if row else "no_success", "updated_at": row["updated_at"] if row else None, "source": "Data Core 副本同步记录"}


def enterprise_asset_map(conn):
    ensure_enterprise_brain_schema(conn)
    assets = [
        ("enterprise_objects", "企业对象", _count(conn, "enterprise_objects", "where archived_at is null"), "企业数字档案"),
        ("living_objects", "生命对象", _count(conn, "living_objects", "where status='active'"), "Living Enterprise"),
        ("documents", "企业资料", _count(conn, "documents", "where deleted_at is null"), "企业资料中心"),
        ("ceo_vault_items", "保险库资料", _count(conn, "ceo_vault_items", "where status='active'"), "CEO Vault"),
        ("knowledge_items", "企业知识", _count(conn, "knowledge_items", "where deleted_at is null"), "知识中心"),
        ("enterprise_memories", "企业记忆", _count(conn, "enterprise_memories", "where archived_at is null"), "Memory Engine"),
        ("founder_memories", "创始人记忆", _count(conn, "founder_memories"), "Founder人工输入"),
        ("knowledge_graph_edges", "企业关系", _count(conn, "knowledge_graph_edges", "where status='active'"), "企业知识网络"),
    ]
    return {
        "ok": True,
        "assets": [
            {"key": key, "name": name, "count": count, "source": source, "evidence": {"source_type": key, "metric": "record_count", "value": count}}
            for key, name, count, source in assets
        ],
        "source_policy": "企业事实来自本地 Data Core 副本链路；不直接连接 SAP",
    }


def enterprise_timeline(conn, limit=60):
    ensure_enterprise_brain_schema(conn)
    events = []
    if _table_exists(conn, "timeline_events"):
        for row in conn.execute(
            """select id,title,coalesce(description,body,'') description,coalesce(occurred_at,created_at) occurred_at,
            coalesce(source_type,'timeline_events') source_type,coalesce(source_id,cast(id as text)) source_id
            from timeline_events where coalesce(source_type,'')!='' order by coalesce(occurred_at,created_at) desc limit ?""",
            (limit,),
        ).fetchall():
            events.append({"kind": "enterprise_event", **dict(row)})
    for row in conn.execute("select * from founder_memories order by coalesce(occurred_at,created_at) desc limit ?", (limit,)).fetchall():
        events.append({"kind": "founder_memory", "id": row["id"], "title": row["title"], "description": row["judgment"], "occurred_at": row["occurred_at"], "source_type": row["source_type"], "source_id": row["source_id"]})
    if _table_exists(conn, "decision_insights"):
        for row in conn.execute("select id,title,summary,updated_at,evidence from decision_insights where coalesce(evidence,'')!='' order by updated_at desc limit ?", (limit,)).fetchall():
            events.append({"kind": "ai_advice", "id": row["id"], "title": row["title"], "description": row["summary"] or "", "occurred_at": row["updated_at"], "source_type": "decision_insights", "source_id": str(row["id"])})
    events.sort(key=lambda item: int(item.get("occurred_at") or 0), reverse=True)
    return {"ok": True, "events": events[:limit]}


def enterprise_brain_summary(conn):
    ensure_enterprise_brain_schema(conn)
    active = conn.execute("select * from enterprise_constitutions where status='active' order by version desc limit 1").fetchone()
    drafts = [dict(row) for row in conn.execute("select * from enterprise_constitutions order by version desc limit 10").fetchall()]
    memories = [dict(row) for row in conn.execute("select * from founder_memories order by updated_at desc limit 10").fetchall()]
    ai_total = 0
    ai_with_evidence = 0
    if _table_exists(conn, "decision_insights"):
        ai_total = _count(conn, "decision_insights", "where status in ('new','reviewing','active')")
        ai_with_evidence = _count(conn, "decision_insights", "where status in ('new','reviewing','active') and length(trim(coalesce(evidence,'')))>2")
    return {
        "ok": True,
        "constitution": dict(active) if active else None,
        "constitution_versions": drafts,
        "founder_memories": memories,
        "founder_memory_confirmed": _count(conn, "founder_memories", "where status='confirmed'"),
        "facts": {"sync": _latest_sync(conn), "assets": enterprise_asset_map(conn)["assets"]},
        "ai_analysis": {"total": ai_total, "with_evidence": ai_with_evidence, "role": "辅助分析，不替代决策"},
        "principle": "事实来自 Data Core，智慧来自 Founder Memory，AI 只辅助、不替代决策",
        "sap_write": False,
    }
