"""Evidence-backed Life Object Framework for the FireFox Living Enterprise."""

from __future__ import annotations

import hashlib
import json
import time


LIFE_DIMENSIONS = (
    "identity",
    "origin",
    "timeline",
    "state",
    "relationship",
    "memory",
    "decision",
    "future",
)

LIFE_OBJECT_TYPES = {
    "store_life": "门店生命",
    "people_life": "人才生命",
    "brand_life": "品牌生命",
    "supplier_life": "供应商生命",
    "explorer_life": "探索者生命",
}

ENTERPRISE_OBJECT_TYPE_MAP = {
    "store": "store_life",
    "employee": "people_life",
    "people": "people_life",
    "person": "people_life",
    "brand": "brand_life",
    "supplier": "supplier_life",
    "customer": "explorer_life",
    "explorer": "explorer_life",
}


def _now():
    return int(time.time())


def _json(value, fallback):
    if value in (None, ""):
        value = fallback
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            value = {"value": value}
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _source(source_type, source_id, source_ref, source_time=None, evidence=None):
    values = {
        "source_type": str(source_type or "").strip(),
        "source_id": str(source_id or "").strip(),
        "source_ref": str(source_ref or "").strip(),
        "source_time": str(source_time or "").strip(),
        "evidence_json": _json(evidence, []),
    }
    missing = [name for name in ("source_type", "source_id", "source_ref") if not values[name]]
    if missing:
        raise ValueError("生命对象数据缺少来源：" + "、".join(missing))
    return values


def _life_id(object_type, object_ref_type, object_ref_id):
    raw = "|".join((object_type, object_ref_type, str(object_ref_id)))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16].upper()
    return "LIFE-{}-{}".format(object_type.replace("_life", "").upper(), digest)


def _table_exists(conn, table_name):
    return bool(conn.execute("select 1 from sqlite_master where type='table' and name=?", (table_name,)).fetchone())


def ensure_living_enterprise_schema(conn):
    conn.execute(
        """create table if not exists living_objects(
        id integer primary key autoincrement,
        life_id text not null unique,
        object_type text not null check(object_type in ('store_life','people_life','brand_life','supplier_life','explorer_life')),
        object_ref_type text not null,
        object_ref_id text not null,
        display_name text not null,
        identity_json text not null default '{}',
        origin_json text not null default '{}',
        state_json text not null default '{}',
        future_json text not null default '{}',
        status text not null default 'active',
        version integer not null default 1,
        created_at integer not null,
        updated_at integer not null,
        unique(object_type,object_ref_type,object_ref_id))"""
    )
    conn.execute(
        """create table if not exists living_object_sources(
        id integer primary key autoincrement,
        life_id text not null,
        dimension text not null check(dimension in ('identity','origin','timeline','state','relationship','memory','decision','future')),
        source_type text not null check(length(trim(source_type))>0),
        source_id text not null check(length(trim(source_id))>0),
        source_ref text not null check(length(trim(source_ref))>0),
        source_time text,
        evidence_json text not null default '[]',
        recorded_at integer not null,
        unique(life_id,dimension,source_type,source_id,source_ref))"""
    )
    conn.execute(
        """create table if not exists living_timeline_events(
        id integer primary key autoincrement,
        event_id text not null unique,
        life_id text not null,
        event_type text not null,
        title text not null,
        description text,
        occurred_at text not null,
        source_type text not null check(length(trim(source_type))>0),
        source_id text not null check(length(trim(source_id))>0),
        source_ref text not null check(length(trim(source_ref))>0),
        evidence_json text not null default '[]',
        created_at integer not null)"""
    )
    conn.execute(
        """create table if not exists living_relationships(
        id integer primary key autoincrement,
        relationship_id text not null unique,
        from_life_id text not null,
        to_life_id text not null,
        relationship_type text not null,
        state text not null default 'active',
        source_type text not null check(length(trim(source_type))>0),
        source_id text not null check(length(trim(source_id))>0),
        source_ref text not null check(length(trim(source_ref))>0),
        evidence_json text not null default '[]',
        created_at integer not null,
        updated_at integer not null,
        unique(from_life_id,to_life_id,relationship_type,source_type,source_id))"""
    )
    conn.execute(
        """create table if not exists living_memory_links(
        id integer primary key autoincrement,
        life_id text not null,
        memory_type text not null,
        memory_id text not null,
        summary text,
        source_type text not null check(length(trim(source_type))>0),
        source_id text not null check(length(trim(source_id))>0),
        source_ref text not null check(length(trim(source_ref))>0),
        evidence_json text not null default '[]',
        created_at integer not null,
        unique(life_id,memory_type,memory_id))"""
    )
    conn.execute(
        """create table if not exists living_decision_links(
        id integer primary key autoincrement,
        life_id text not null,
        decision_type text not null,
        decision_id text not null,
        summary text,
        decision_status text not null default 'recorded',
        source_type text not null check(length(trim(source_type))>0),
        source_id text not null check(length(trim(source_id))>0),
        source_ref text not null check(length(trim(source_ref))>0),
        evidence_json text not null default '[]',
        created_at integer not null,
        unique(life_id,decision_type,decision_id))"""
    )
    conn.execute(
        """create table if not exists living_future_items(
        id integer primary key autoincrement,
        future_id text not null unique,
        life_id text not null,
        title text not null,
        hypothesis text,
        target_date text,
        status text not null default 'proposed',
        approval_required integer not null default 1,
        source_type text not null check(length(trim(source_type))>0),
        source_id text not null check(length(trim(source_id))>0),
        source_ref text not null check(length(trim(source_ref))>0),
        evidence_json text not null default '[]',
        created_at integer not null,
        updated_at integer not null)"""
    )
    for statement in (
        "create index if not exists idx_living_objects_type on living_objects(object_type,status,updated_at)",
        "create index if not exists idx_living_sources_life on living_object_sources(life_id,dimension,recorded_at)",
        "create index if not exists idx_living_timeline_life on living_timeline_events(life_id,occurred_at)",
        "create index if not exists idx_living_relationships_from on living_relationships(from_life_id,state)",
        "create index if not exists idx_living_relationships_to on living_relationships(to_life_id,state)",
        "create index if not exists idx_living_memory_life on living_memory_links(life_id,created_at)",
        "create index if not exists idx_living_decision_life on living_decision_links(life_id,created_at)",
        "create index if not exists idx_living_future_life on living_future_items(life_id,status,target_date)",
    ):
        conn.execute(statement)


def _record_dimension_source(conn, life_id, dimension, source, recorded_at=None):
    conn.execute(
        """insert or ignore into living_object_sources(
        life_id,dimension,source_type,source_id,source_ref,source_time,evidence_json,recorded_at)
        values(?,?,?,?,?,?,?,?)""",
        (life_id, dimension, source["source_type"], source["source_id"], source["source_ref"],
         source["source_time"], source["evidence_json"], recorded_at or _now()),
    )


def upsert_life_object(
    conn,
    object_type,
    object_ref_type,
    object_ref_id,
    display_name,
    identity=None,
    origin=None,
    state=None,
    future=None,
    source_type="",
    source_id="",
    source_ref="",
    source_time=None,
    evidence=None,
):
    ensure_living_enterprise_schema(conn)
    if object_type not in LIFE_OBJECT_TYPES:
        raise ValueError("不支持的生命对象类型：" + str(object_type))
    if not str(object_ref_type or "").strip() or not str(object_ref_id or "").strip() or not str(display_name or "").strip():
        raise ValueError("生命对象必须包含对象引用和名称")
    source = _source(source_type, source_id, source_ref, source_time, evidence)
    life_id = _life_id(object_type, str(object_ref_type), str(object_ref_id))
    now = _now()
    identity_json = _json(identity, {})
    origin_json = _json(origin, {})
    state_json = _json(state, {})
    future_json = _json(future, {})
    existing = conn.execute("select * from living_objects where life_id=?", (life_id,)).fetchone()
    if existing:
        changed = any((
            existing["display_name"] != str(display_name).strip(),
            existing["identity_json"] != identity_json,
            existing["origin_json"] != origin_json,
            existing["state_json"] != state_json,
            existing["future_json"] != future_json,
        ))
        if changed:
            conn.execute(
                """update living_objects set display_name=?,identity_json=?,origin_json=?,state_json=?,future_json=?,
                version=version+1,updated_at=? where life_id=?""",
                (str(display_name).strip(), identity_json, origin_json, state_json, future_json, now, life_id),
            )
        created = False
    else:
        conn.execute(
            """insert into living_objects(
            life_id,object_type,object_ref_type,object_ref_id,display_name,identity_json,origin_json,state_json,
            future_json,status,version,created_at,updated_at) values(?,?,?,?,?,?,?,?,?,'active',1,?,?)""",
            (life_id, object_type, str(object_ref_type), str(object_ref_id), str(display_name).strip(),
             identity_json, origin_json, state_json, future_json, now, now),
        )
        created = True
        changed = True
    for dimension in ("identity", "origin", "state", "future"):
        _record_dimension_source(conn, life_id, dimension, source, now)
    return {"life_id": life_id, "created": created, "changed": changed, "object_type": object_type}


def record_timeline_event(conn, life_id, event_type, title, occurred_at, description="", **source_input):
    ensure_living_enterprise_schema(conn)
    if not conn.execute("select 1 from living_objects where life_id=?", (life_id,)).fetchone():
        raise ValueError("生命对象不存在")
    source = _source(**source_input)
    raw = "|".join((life_id, event_type, title, str(occurred_at), source["source_type"], source["source_id"]))
    event_id = "LIFE-EVENT-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:18].upper()
    conn.execute(
        """insert or ignore into living_timeline_events(
        event_id,life_id,event_type,title,description,occurred_at,source_type,source_id,source_ref,evidence_json,created_at)
        values(?,?,?,?,?,?,?,?,?,?,?)""",
        (event_id, life_id, event_type, title, description, str(occurred_at), source["source_type"],
         source["source_id"], source["source_ref"], source["evidence_json"], _now()),
    )
    _record_dimension_source(conn, life_id, "timeline", source)
    return event_id


def relate_life_objects(conn, from_life_id, to_life_id, relationship_type, state="active", **source_input):
    ensure_living_enterprise_schema(conn)
    for life_id in (from_life_id, to_life_id):
        if not conn.execute("select 1 from living_objects where life_id=?", (life_id,)).fetchone():
            raise ValueError("关系中的生命对象不存在：" + life_id)
    source = _source(**source_input)
    raw = "|".join((from_life_id, to_life_id, relationship_type, source["source_type"], source["source_id"]))
    relationship_id = "LIFE-REL-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:18].upper()
    now = _now()
    conn.execute(
        """insert into living_relationships(
        relationship_id,from_life_id,to_life_id,relationship_type,state,source_type,source_id,source_ref,
        evidence_json,created_at,updated_at) values(?,?,?,?,?,?,?,?,?,?,?)
        on conflict(from_life_id,to_life_id,relationship_type,source_type,source_id)
        do update set state=excluded.state,evidence_json=excluded.evidence_json,updated_at=excluded.updated_at""",
        (relationship_id, from_life_id, to_life_id, relationship_type, state, source["source_type"],
         source["source_id"], source["source_ref"], source["evidence_json"], now, now),
    )
    _record_dimension_source(conn, from_life_id, "relationship", source, now)
    _record_dimension_source(conn, to_life_id, "relationship", source, now)
    return relationship_id


def add_future_item(conn, life_id, title, hypothesis="", target_date="", **source_input):
    ensure_living_enterprise_schema(conn)
    if not conn.execute("select 1 from living_objects where life_id=?", (life_id,)).fetchone():
        raise ValueError("生命对象不存在")
    source = _source(**source_input)
    now = _now()
    raw = "|".join((life_id, title, target_date, source["source_type"], source["source_id"]))
    future_id = "LIFE-FUTURE-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:18].upper()
    conn.execute(
        """insert or ignore into living_future_items(
        future_id,life_id,title,hypothesis,target_date,status,approval_required,source_type,source_id,source_ref,
        evidence_json,created_at,updated_at) values(?,?,?,?,?,'proposed',1,?,?,?,?,?,?)""",
        (future_id, life_id, title, hypothesis, target_date, source["source_type"], source["source_id"],
         source["source_ref"], source["evidence_json"], now, now),
    )
    _record_dimension_source(conn, life_id, "future", source, now)
    return future_id


def link_life_memory(conn, life_id, memory_type, memory_id, summary="", **source_input):
    ensure_living_enterprise_schema(conn)
    if not conn.execute("select 1 from living_objects where life_id=?", (life_id,)).fetchone():
        raise ValueError("生命对象不存在")
    source = _source(**source_input)
    conn.execute(
        """insert or ignore into living_memory_links(
        life_id,memory_type,memory_id,summary,source_type,source_id,source_ref,evidence_json,created_at)
        values(?,?,?,?,?,?,?,?,?)""",
        (life_id, memory_type, str(memory_id), summary, source["source_type"], source["source_id"],
         source["source_ref"], source["evidence_json"], _now()),
    )
    inserted = conn.execute("select changes()").fetchone()[0]
    _record_dimension_source(conn, life_id, "memory", source)
    return inserted


def link_life_decision(conn, life_id, decision_type, decision_id, summary="", decision_status="recorded", **source_input):
    ensure_living_enterprise_schema(conn)
    if not conn.execute("select 1 from living_objects where life_id=?", (life_id,)).fetchone():
        raise ValueError("生命对象不存在")
    source = _source(**source_input)
    conn.execute(
        """insert or ignore into living_decision_links(
        life_id,decision_type,decision_id,summary,decision_status,source_type,source_id,source_ref,evidence_json,created_at)
        values(?,?,?,?,?,?,?,?,?,?)""",
        (life_id, decision_type, str(decision_id), summary, decision_status, source["source_type"],
         source["source_id"], source["source_ref"], source["evidence_json"], _now()),
    )
    inserted = conn.execute("select changes()").fetchone()[0]
    _record_dimension_source(conn, life_id, "decision", source)
    return inserted


def _life_for_enterprise_object(conn, object_type, object_id):
    life_type = ENTERPRISE_OBJECT_TYPE_MAP.get(str(object_type or "").lower())
    if not life_type or object_id in (None, ""):
        return None
    row = conn.execute(
        "select life_id from living_objects where object_type=? and object_ref_type='enterprise_object' and object_ref_id=?",
        (life_type, str(object_id)),
    ).fetchone()
    return row[0] if row else None


def sync_life_context_links(conn):
    """Connect local timelines, reviewed memories and evidence-backed decisions."""
    results = {"timeline_links": 0, "memory_links": 0, "decision_links": 0, "context_skipped": 0}
    if _table_exists(conn, "timeline_events"):
        rows = conn.execute(
            """select * from timeline_events where coalesce(entity_type,target_type,'')!=''
            and coalesce(entity_id,target_id) is not null and coalesce(source_type,'')!='' and coalesce(source_id,'')!=''"""
        ).fetchall()
        for row in rows:
            entity_type = row["entity_type"] or row["target_type"]
            entity_id = row["entity_id"] if row["entity_id"] is not None else row["target_id"]
            life_id = _life_for_enterprise_object(conn, entity_type, entity_id)
            if not life_id:
                results["context_skipped"] += 1
                continue
            before = conn.total_changes
            record_timeline_event(
                conn, life_id, row["event_type"] or "recorded_event", row["title"],
                row["occurred_at"] or row["created_at"], row["description"] or row["body"] or "",
                source_type=row["source_type"], source_id=row["source_id"],
                source_ref="{}#{}".format(row["source_type"], row["source_id"]),
                source_time=row["occurred_at"] or row["created_at"], evidence=row["metadata"] or [],
            )
            results["timeline_links"] += 1 if conn.total_changes > before else 0
    if _table_exists(conn, "enterprise_memories"):
        rows = conn.execute(
            """select * from enterprise_memories where archived_at is null
            and status in ('approved','active','published') and related_object_type is not null and related_object_id is not null"""
        ).fetchall()
        for row in rows:
            life_id = _life_for_enterprise_object(conn, row["related_object_type"], row["related_object_id"])
            if not life_id:
                results["context_skipped"] += 1
                continue
            results["memory_links"] += link_life_memory(
                conn, life_id, row["memory_type"], row["id"], row["summary"] or row["title"],
                source_type="enterprise_memories", source_id=row["id"],
                source_ref="enterprise_memories#{}".format(row["id"]), source_time=row["updated_at"],
                evidence=[{"field": "status", "value": row["status"]}],
            )
    if _table_exists(conn, "decision_insights"):
        rows = conn.execute(
            """select * from decision_insights where entity_type is not null and entity_id is not null
            and length(trim(coalesce(evidence,'')))>2"""
        ).fetchall()
        for row in rows:
            life_id = _life_for_enterprise_object(conn, row["entity_type"], row["entity_id"])
            if not life_id:
                results["context_skipped"] += 1
                continue
            results["decision_links"] += link_life_decision(
                conn, life_id, row["insight_type"], row["id"], row["summary"] or row["title"], row["status"],
                source_type="decision_insights", source_id=row["id"],
                source_ref="decision_insights#{}".format(row["id"]), source_time=row["updated_at"],
                evidence=row["evidence"],
            )
    return results


def sync_life_objects_from_confirmed_sources(conn):
    """Build the understanding layer from confirmed local data. Never reads or writes SAP directly."""
    ensure_living_enterprise_schema(conn)
    results = {key: 0 for key in LIFE_OBJECT_TYPES}
    results.update({"created": 0, "updated": 0, "unchanged": 0, "skipped": 0})
    if _table_exists(conn, "enterprise_objects"):
        columns = {row[1] for row in conn.execute("pragma table_info(enterprise_objects)").fetchall()}
        archived_filter = " and archived_at is null" if "archived_at" in columns else ""
        rows = conn.execute(
            "select id,object_type,name,code,status,metadata,updated_at from enterprise_objects where status!='archived'" + archived_filter
        ).fetchall()
        for row in rows:
            object_type = ENTERPRISE_OBJECT_TYPE_MAP.get(str(row["object_type"] or "").lower())
            if not object_type or not str(row["name"] or "").strip():
                results["skipped"] += 1
                continue
            metadata = row["metadata"] or "{}"
            item = upsert_life_object(
                conn,
                object_type,
                "enterprise_object",
                row["id"],
                row["name"],
                identity={"name": row["name"], "code": row["code"], "enterprise_object_type": row["object_type"]},
                origin={"system": "FoxBrain Enterprise Object Engine"},
                state={"status": row["status"], "metadata": metadata},
                future={"status": "awaiting_evidence"},
                source_type="enterprise_objects",
                source_id=row["id"],
                source_ref="enterprise_objects#{}".format(row["id"]),
                source_time=row["updated_at"],
                evidence=[{"field": "name", "value": row["name"]}, {"field": "metadata", "value": metadata}],
            )
            results["created" if item["created"] else ("updated" if item["changed"] else "unchanged")] += 1
            results[object_type] += 1
    if _table_exists(conn, "brand_life_profiles"):
        for row in conn.execute("select * from brand_life_profiles where status='active'").fetchall():
            item = upsert_life_object(
                conn,
                "brand_life",
                "brand_life_profile",
                row["id"],
                row["brand_name"],
                identity={"brand_code": row["brand_code"], "brand_name": row["brand_name"], "identity": row["brand_identity"]},
                origin={"brand_story": row["brand_story"], "brand_philosophy": row["brand_philosophy"]},
                state={"product_system": row["product_system"], "store_system": row["store_system"], "people_system": row["people_system"]},
                future={"future_plan": row["future_plan"]},
                source_type="brand_life_profiles",
                source_id=row["id"],
                source_ref="brand_life_profiles#{}".format(row["id"]),
                source_time=row["updated_at"],
                evidence=[{"field": "brand_code", "value": row["brand_code"]}],
            )
            results["created" if item["created"] else ("updated" if item["changed"] else "unchanged")] += 1
            results["brand_life"] += 1
    results.update(sync_life_context_links(conn))
    return results


def living_object_payload(conn, life_id):
    ensure_living_enterprise_schema(conn)
    row = conn.execute("select * from living_objects where life_id=?", (life_id,)).fetchone()
    if not row:
        return {"ok": False, "message": "生命对象不存在"}
    obj = dict(row)
    for field in ("identity_json", "origin_json", "state_json", "future_json"):
        try:
            obj[field] = json.loads(obj[field] or "{}")
        except (TypeError, ValueError):
            obj[field] = {}
    queries = {
        "sources": "select * from living_object_sources where life_id=? order by recorded_at desc",
        "timeline": "select * from living_timeline_events where life_id=? order by occurred_at desc,created_at desc",
        "relationships": "select * from living_relationships where from_life_id=? or to_life_id=? order by updated_at desc",
        "memories": "select * from living_memory_links where life_id=? order by created_at desc",
        "decisions": "select * from living_decision_links where life_id=? order by created_at desc",
        "future": "select * from living_future_items where life_id=? order by target_date,created_at desc",
    }
    payload = {"ok": True, "object": obj, "dimensions": list(LIFE_DIMENSIONS)}
    for name, sql in queries.items():
        params = (life_id, life_id) if name == "relationships" else (life_id,)
        payload[name] = [dict(item) for item in conn.execute(sql, params).fetchall()]
    return payload


def living_enterprise_summary(conn):
    ensure_living_enterprise_schema(conn)
    counts = {key: 0 for key in LIFE_OBJECT_TYPES}
    for row in conn.execute("select object_type,count(*) c from living_objects where status='active' group by object_type").fetchall():
        counts[row["object_type"]] = int(row["c"] or 0)
    source_count = conn.execute("select count(*) c from living_object_sources").fetchone()[0]
    missing_sources = conn.execute(
        """select count(*) from living_objects o where not exists(
        select 1 from living_object_sources s where s.life_id=o.life_id)"""
    ).fetchone()[0]
    recent = [dict(row) for row in conn.execute(
        "select life_id,object_type,display_name,status,version,updated_at from living_objects order by updated_at desc limit 20"
    ).fetchall()]
    return {
        "ok": True,
        "object_counts": counts,
        "total_objects": sum(counts.values()),
        "source_records": int(source_count or 0),
        "objects_without_source": int(missing_sources or 0),
        "dimensions": list(LIFE_DIMENSIONS),
        "recent_objects": recent,
        "sap_boundary": "read_only_local_replica_and_confirmed_objects_only",
    }
