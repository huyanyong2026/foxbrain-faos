"""VAFOX Enterprise Brain V1.1 execution contract."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class DriveDomain:
    key: str
    name: str
    purpose: str
    object_types: tuple[str, ...]
    ai_outputs: tuple[str, ...]


@dataclass(frozen=True)
class ObjectModel:
    key: str
    name: str
    primary_sources: tuple[str, ...]
    relationships: tuple[str, ...]
    permissions: tuple[str, ...]


@dataclass(frozen=True)
class PipelineStage:
    key: str
    name: str
    input_type: str
    output_type: str
    audit_requirement: str


DRIVE_2_DOMAINS = (
    DriveDomain("brand_drive", "Brand Drive", "Brand folders become AI-readable brand knowledge assets.", ("brand", "supplier", "contract", "product", "media", "training"), ("brand_profile", "selling_points", "risk_summary", "agent_context")),
    DriveDomain("store_drive", "Store Drive", "Store files become linked store operation knowledge.", ("store", "employee", "sales", "activity", "photo", "task"), ("store_profile", "daily_context", "operation_risk", "task_context")),
    DriveDomain("product_drive", "Product Drive", "Product files connect product knowledge with SAP sales and inventory.", ("product", "sku", "inventory", "sales", "manual", "image"), ("product_card", "sales_script", "inventory_context", "recommendation_context")),
    DriveDomain("contract_drive", "Contract Drive", "Contracts become traceable business objects with renewal and risk reminders.", ("contract", "supplier", "brand", "store", "asset", "decision"), ("contract_summary", "obligation_list", "renewal_alert", "risk_boundary")),
    DriveDomain("media_drive", "Media Drive", "Photos and videos become searchable enterprise media knowledge.", ("image", "video", "event", "store", "product", "brand"), ("media_tags", "content_brief", "timeline_event", "training_material")),
)


OBJECT_ENGINE_MODELS = (
    ObjectModel("company", "Company", ("owner_profile", "archives", "strategy_documents"), ("stores", "brands", "assets", "projects", "decisions"), ("boss", "admin", "finance")),
    ObjectModel("store", "Store", ("SAP", "store_archive", "photos", "tasks"), ("employees", "sales", "inventory", "customers", "activities"), ("boss", "admin", "finance", "store_manager")),
    ObjectModel("brand", "Brand", ("SAP", "brand_drive", "supplier_contracts", "market_research"), ("products", "suppliers", "sales", "inventory", "content"), ("boss", "admin", "finance", "purchasing")),
    ObjectModel("product", "Product", ("SAP", "product_drive", "media_drive"), ("brand", "supplier", "inventory", "sales", "customer_feedback"), ("boss", "admin", "purchasing", "store_manager")),
    ObjectModel("customer", "Customer", ("CRM", "SAP", "wecom", "member_events"), ("orders", "preferences", "store", "employee", "campaigns"), ("boss", "admin", "store_manager")),
    ObjectModel("document", "Document", ("drive_upload", "wiki", "knowledge_items"), ("objects", "chunks", "summaries", "citations", "tasks"), ("boss", "admin", "finance", "store_manager")),
    ObjectModel("memory", "Memory", ("decision_records", "boss_experience", "feedback"), ("objects", "rules", "cases", "future_references"), ("boss", "admin", "finance")),
)


KNOWLEDGE_PIPELINE_STAGES = (
    PipelineStage("ingest", "Document", "file_or_record", "source_record", "source_path_and_owner_required"),
    PipelineStage("ocr", "OCR", "source_record", "text_payload", "ocr_result_keeps_source_file_id"),
    PipelineStage("chunk", "Chunk", "text_payload", "knowledge_chunks", "chunk_offsets_and_version_required"),
    PipelineStage("embedding", "Embedding", "knowledge_chunks", "vector_records", "model_version_and_hash_required"),
    PipelineStage("vector_db", "Vector DB", "vector_records", "retrieval_index", "index_name_and_permission_scope_required"),
    PipelineStage("graph", "Graph", "retrieval_index", "object_edges", "entity_relation_lineage_required"),
    PipelineStage("ai_summary", "AI Summary", "object_edges", "reviewable_summary", "ai_output_requires_evidence"),
    PipelineStage("knowledge_object", "Knowledge Object", "reviewable_summary", "knowledge_object", "human_review_for_sensitive_content"),
    PipelineStage("agent", "Agent", "knowledge_object", "agent_context", "agent_use_logged_and_permission_checked"),
)


CEO_HOME_V11_SECTIONS = (
    ("top_focus", "Top Focus", ("today_sales", "major_risks", "pending_approvals")),
    ("business_brief", "Business Brief", ("sales", "margin", "inventory", "cashflow")),
    ("knowledge_brief", "Knowledge Brief", ("new_drive_items", "pipeline_status", "unreviewed_summaries")),
    ("action_brief", "Action Brief", ("tasks", "approvals", "followups")),
)


V11_ROUTES = {
    "drive": "/drive",
    "objects": "/objects",
    "knowledge_pipeline": "/knowledge-pipeline",
    "ceo_home": "/ceo-home",
}


def build_drive_2_contract() -> dict:
    return {
        "ok": True,
        "version": "VAFOX Drive 2.0",
        "positioning": "Enterprise Knowledge Drive",
        "domains": [asdict(domain) for domain in DRIVE_2_DOMAINS],
        "rules": {
            "folders_become_objects": True,
            "documents_become_knowledge_objects": True,
            "all_ai_outputs_keep_source_lineage": True,
            "sensitive_content_requires_review": True,
        },
    }


def build_object_engine_contract() -> dict:
    return {
        "ok": True,
        "version": "Object Engine V1.1",
        "models": [asdict(model) for model in OBJECT_ENGINE_MODELS],
        "canonical_rule": "every enterprise item has object_id, object_type, source, owner, permissions, timeline and relationships",
    }


def build_knowledge_pipeline_contract() -> dict:
    return {
        "ok": True,
        "version": "Knowledge Pipeline V1.1",
        "pipeline": [asdict(stage) for stage in KNOWLEDGE_PIPELINE_STAGES],
        "flow": [stage.name for stage in KNOWLEDGE_PIPELINE_STAGES],
        "approval_boundary": "AI summaries and sensitive knowledge objects require human review before high-risk use.",
    }


def build_ceo_home_v11_contract() -> dict:
    return {
        "ok": True,
        "version": "CEO Home V1.1",
        "homepage_policy": "root_home_keeps_ten_entries_only_details_after_click",
        "sections": [{"key": key, "name": name, "signals": list(signals)} for key, name, signals in CEO_HOME_V11_SECTIONS],
        "routes": dict(V11_ROUTES),
    }


def build_enterprise_second_brain_v11_contract() -> dict:
    return {
        "ok": True,
        "version": "VAFOX Enterprise Brain V1.1",
        "focus": ["Drive 2.0", "Object Engine", "Knowledge Pipeline", "CEO Home"],
        "drive_2": build_drive_2_contract(),
        "object_engine": build_object_engine_contract(),
        "knowledge_pipeline": build_knowledge_pipeline_contract(),
        "ceo_home": build_ceo_home_v11_contract(),
        "guardrails": {
            "sap_remains_system_of_record": True,
            "high_risk_actions_require_human_approval": True,
            "source_lineage_required": True,
            "no_root_home_content_sprawl": True,
        },
    }
