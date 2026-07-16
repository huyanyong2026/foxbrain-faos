"""Domain rules for the VAFOX Enterprise AI Center collaboration layer."""

from __future__ import annotations

import json
import time
import uuid


AGENT_ROLES = (
    ("business", "经营分析 Agent", "分析销售、利润、门店和经营风险"),
    ("inventory", "库存助手 Agent", "识别库存结构、周转与积压风险"),
    ("brand", "品牌运营 Agent", "形成品牌经营观察与行动建议"),
    ("content", "内容助手 Agent", "基于品牌知识生成内容草稿"),
    ("enterprise", "企业资料 Agent", "整理资料、对象关系和知识引用"),
)

DIGITAL_WORKFORCE_AGENTS = (
    ("ceo", "CEO Agent", "生成 CEO 简报、经营洞察和决策建议"),
    ("supply_chain", "Supply Chain Agent", "识别采购、供应、库存和履约风险"),
    ("store", "Store Agent", "分析门店经营、库存周转和现场行动"),
    ("customer", "Customer Agent", "支持客户洞察、服务建议和体验提升"),
    ("supplier", "Supplier Agent", "协同供应商、品牌资料和供货状态"),
)

CONNECTIONS = (
    ("data_core", "Enterprise Data Core", "https://core.vafox.com", "read_only"),
    ("ceo_brain", "CEO Enterprise Brain", "https://huyan.vafox.com", "approved_exchange"),
    ("living_enterprise", "Living Enterprise", "https://huyan.vafox.com", "read_only"),
    ("wecom", "企业微信", "", "callback_only"),
)

DEFAULT_APPROVAL_POLICY = {
    "business_action": "human_required",
    "task_creation": "human_required",
    "knowledge_promotion": "human_required",
    "memory_promotion": "human_required",
    "feedback_learning": "human_required",
}

SCHEMA_STATEMENTS = (
    "alter table auth_users add column if not exists store_code varchar(40)",
    """create table if not exists ai_agents(
    id bigserial primary key,agent_id varchar(80) unique not null,agent_type varchar(40) not null,
    name varchar(120) not null,description text not null default '',status varchar(20) not null default 'active',
    permission_scope jsonb not null default '{}'::jsonb,tool_scope jsonb not null default '[]'::jsonb,
    approval_policy jsonb not null default '{}'::jsonb,created_at timestamptz not null default now(),
    updated_at timestamptz not null default now())""",
    """create table if not exists enterprise_connections(
    id bigserial primary key,connection_id varchar(80) unique not null,connection_type varchar(40) not null,
    name varchar(120) not null,base_url text not null default '',access_mode varchar(40) not null,
    status varchar(20) not null default 'not_configured',last_checked_at timestamptz,
    last_success_at timestamptz,last_error text,metadata jsonb not null default '{}'::jsonb,
    updated_at timestamptz not null default now())""",
    """create table if not exists ai_agent_runs(
    id bigserial primary key,run_id varchar(80) unique not null,agent_id varchar(80) not null,
    question text not null,context_json jsonb not null default '{}'::jsonb,evidence_json jsonb not null default '[]'::jsonb,
    answer text,result_json jsonb not null default '{}'::jsonb,status varchar(30) not null default 'waiting_ai',
    approval_status varchar(30) not null default 'pending',created_by bigint,reviewed_by bigint,
    reviewed_at timestamptz,created_at timestamptz not null default now(),updated_at timestamptz not null default now())""",
    """create table if not exists ai_knowledge_items(
    id bigserial primary key,knowledge_id varchar(80) unique not null,title varchar(240) not null,
    summary text not null default '',content text not null default '',object_type varchar(60),object_id varchar(120),
    visibility varchar(30) not null default 'internal',source_type varchar(80) not null,
    source_id varchar(160) not null,source_ref text not null,evidence_json jsonb not null default '[]'::jsonb,
    status varchar(30) not null default 'draft',created_by bigint,approved_by bigint,approved_at timestamptz,
    created_at timestamptz not null default now(),updated_at timestamptz not null default now())""",
    """create table if not exists ai_tasks(
    id bigserial primary key,task_id varchar(80) unique not null,title varchar(240) not null,
    description text not null default '',owner_name varchar(120),priority varchar(20) not null default 'normal',
    status varchar(30) not null default 'pending_approval',source_type varchar(80) not null,
    source_id varchar(160) not null,source_ref text not null,evidence_json jsonb not null default '[]'::jsonb,
    approval_status varchar(30) not null default 'pending',approved_by bigint,approved_at timestamptz,
    result_note text,created_by bigint,created_at timestamptz not null default now(),updated_at timestamptz not null default now())""",
    """create table if not exists ai_memory_items(
    id bigserial primary key,memory_id varchar(80) unique not null,memory_type varchar(40) not null,
    title varchar(240) not null,summary text not null default '',source_type varchar(80) not null,
    source_id varchar(160) not null,evidence_json jsonb not null default '[]'::jsonb,
    status varchar(30) not null default 'pending_review',created_by bigint,approved_by bigint,
    approved_at timestamptz,created_at timestamptz not null default now())""",
    """create table if not exists ai_feedback(
    id bigserial primary key,feedback_id varchar(80) unique not null,run_id varchar(80) not null,
    feedback_type varchar(30) not null,comment text not null default '',effect_score integer,
    learning_status varchar(30) not null default 'pending_review',created_by bigint,
    reviewed_by bigint,reviewed_at timestamptz,created_at timestamptz not null default now())""",
    """create table if not exists ai_evidence_links(
    id bigserial primary key,target_type varchar(40) not null,target_id varchar(80) not null,
    source_layer varchar(40) not null,source_type varchar(80) not null,source_id varchar(160) not null,
    source_ref text not null,statement text not null,captured_at timestamptz not null default now(),
    unique(target_type,target_id,source_type,source_id,statement))""",
    """create table if not exists wecom_connections(
    id bigserial primary key,connection_id varchar(80) unique not null,name varchar(120) not null,
    corp_id_masked varchar(120) not null default '',callback_path varchar(240) not null default '/wecom/',
    status varchar(30) not null default 'not_configured',last_event_at timestamptz,
    metadata jsonb not null default '{}'::jsonb,updated_at timestamptz not null default now())""",
    """create table if not exists replenishment_batches(
    id bigserial primary key,batch_id varchar(100) unique not null,business_date date not null,
    source_type varchar(30) not null,source_name varchar(240) not null,data_as_of timestamptz,
    rule_version varchar(40) not null,status varchar(40) not null default 'validating',revision integer not null default 1,
    input_rows integer not null default 0,result_rows integer not null default 0,error_summary text,
    metadata jsonb not null default '{}'::jsonb,created_by bigint,created_at timestamptz not null default now(),
    completed_at timestamptz,unique(business_date,source_type,source_name,rule_version,revision))""",
    """create table if not exists replenishment_items(
    id bigserial primary key,batch_id varchar(100) not null,store_code varchar(40) not null,
    store_name varchar(80) not null,sku_code varchar(100) not null,product_name varchar(300) not null,
    brand_name varchar(160) not null default '',category_name varchar(160) not null default '',
    color varchar(100) not null default '',size varchar(100) not null default '',available_stock integer not null,
    sales_30d integer not null,sales_prev_30d integer not null,sales_60d integer not null,
    avg_daily_sales numeric(14,4) not null,stock_days numeric(14,2),safety_stock integer not null,
    suggested_qty integer not null,priority varchar(20) not null,recommendation varchar(40) not null,
    reason text not null,warning text not null default '',created_at timestamptz not null default now(),
    unique(batch_id,store_code,sku_code))""",
    """create table if not exists replenishment_audit_logs(
    id bigserial primary key,action varchar(60) not null,batch_id varchar(100),store_code varchar(40),
    actor_id bigint,details jsonb not null default '{}'::jsonb,created_at timestamptz not null default now())""",
    "create index if not exists idx_ai_runs_status on ai_agent_runs(status,approval_status,updated_at desc)",
    "create index if not exists idx_ai_tasks_status on ai_tasks(status,approval_status,updated_at desc)",
    "create index if not exists idx_ai_knowledge_object on ai_knowledge_items(object_type,object_id,status)",
    "create index if not exists idx_ai_feedback_run on ai_feedback(run_id,created_at desc)",
    "create index if not exists idx_ai_evidence_target on ai_evidence_links(target_type,target_id)",
    "create index if not exists idx_replenishment_batches_date on replenishment_batches(business_date desc,created_at desc)",
    "create index if not exists idx_replenishment_items_store on replenishment_items(batch_id,store_code,priority)",
    "create index if not exists idx_replenishment_audit_batch on replenishment_audit_logs(batch_id,created_at desc)",
)


def new_id(prefix):
    return "{}-{}-{}".format(prefix, int(time.time()), uuid.uuid4().hex[:8])


def json_value(value, fallback):
    if value in (None, ""):
        return fallback
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return fallback
    return value


def normalize_evidence(evidence):
    evidence = json_value(evidence, [])
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("AI 分析和任务必须包含可追溯依据")
    normalized = []
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("依据格式不正确")
        row = {
            "source_layer": str(item.get("source_layer") or "enterprise_fact").strip(),
            "source_type": str(item.get("source_type") or "").strip(),
            "source_id": str(item.get("source_id") or "").strip(),
            "source_ref": str(item.get("source_ref") or "").strip(),
            "statement": str(item.get("statement") or "").strip(),
        }
        if not all(row.values()):
            raise ValueError("每条依据必须包含来源层、来源类型、来源编号、来源引用和说明")
        normalized.append(row)
    return normalized


def validate_ai_run(question, evidence):
    if not str(question or "").strip():
        raise ValueError("企业问题不能为空")
    return normalize_evidence(evidence)


def validate_task(title, source_type, source_id, source_ref, evidence):
    if not str(title or "").strip():
        raise ValueError("任务名称不能为空")
    if not all(str(value or "").strip() for value in (source_type, source_id, source_ref)):
        raise ValueError("任务必须保留来源")
    return normalize_evidence(evidence)


def validate_feedback(feedback_type, effect_score=None):
    if feedback_type not in ("accepted", "rejected", "modified", "effective", "ineffective"):
        raise ValueError("不支持的反馈类型")
    if effect_score not in (None, ""):
        score = int(effect_score)
        if score < 1 or score > 5:
            raise ValueError("效果评分必须在 1 到 5 之间")
        return score
    return None


def require_human_approval(current_status, action):
    allowed = {
        ("pending", "approve"): "approved",
        ("pending", "reject"): "rejected",
        ("pending_review", "approve"): "approved",
        ("pending_review", "reject"): "rejected",
    }
    result = allowed.get((current_status, action))
    if not result:
        raise ValueError("当前记录不能执行该人工审批操作")
    return result
