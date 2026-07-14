"""VAFOX Enterprise OS V1.6 multi-agent collaboration contracts."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class MultiAgentRole:
    key: str
    name: str
    role: str
    owner_role: str
    shared_sap_models: tuple[str, ...]
    knowledge_scope: tuple[str, ...]
    tool_scope: tuple[str, ...]
    collaboration_scope: tuple[str, ...]
    approval_boundary: tuple[str, ...]
    output_contract: tuple[str, ...]


@dataclass(frozen=True)
class AgentCollaborationFlow:
    key: str
    name: str
    objective: str
    agents: tuple[str, ...]
    shared_context: tuple[str, ...]
    handoff_rule: str
    approval_gate: str


SHARED_SAP_KNOWLEDGE_POLICY = {
    "sap_is_source_of_truth": True,
    "agents_read_shared_sap_knowledge_context": True,
    "direct_sap_production_write_disabled": True,
    "shared_context_from_read_only_sync_and_ai_warehouse": True,
    "missing_or_stale_sap_data_must_be_reported": True,
    "high_risk_operations_require_human_approval": True,
    "ai_outputs_must_be_explainable_traceable_auditable": True,
}


MULTI_AGENT_ROLES = (
    MultiAgentRole(
        "ceo",
        "CEO Agent",
        "executive_orchestrator",
        "boss",
        ("sales_knowledge_model", "inventory_knowledge_model", "product_knowledge_model", "member_knowledge_model"),
        ("boss_experience", "decision_memory", "operating_policy"),
        ("Create Review Plan", "Read Boss Daily Report", "Assign Agent Task"),
        ("business", "inventory", "product", "member", "content"),
        ("final_decision", "target_change", "budget_change", "cross_department_execution"),
        ("objective", "agent_findings", "sap_basis", "business_tradeoff", "approval_request"),
    ),
    MultiAgentRole(
        "business",
        "Business Agent",
        "operating_analysis",
        "operations",
        ("sales_knowledge_model", "inventory_knowledge_model", "member_knowledge_model"),
        ("operating_reviews", "business_rules", "task_feedback"),
        ("Query SAP Analysis", "Search Knowledge", "Create Task Draft", "Create Report Draft"),
        ("ceo", "inventory", "member", "content"),
        ("target_change", "commission_change", "finance_decision"),
        ("kpi_basis", "risk", "opportunity", "task_draft", "approval_request"),
    ),
    MultiAgentRole(
        "inventory",
        "Inventory Agent",
        "inventory_decision_support",
        "purchasing",
        ("inventory_knowledge_model", "product_knowledge_model", "sales_knowledge_model"),
        ("inventory_policy", "supplier_notes", "brand_rules"),
        ("Query SAP Analysis", "Search Knowledge", "Transfer Draft", "Replenishment Draft"),
        ("ceo", "business", "product", "content"),
        ("markdown", "transfer_execution", "purchase_order", "sap_writeback"),
        ("stock_basis", "risk_goods", "product_context", "action_draft", "approval_request"),
    ),
    MultiAgentRole(
        "product",
        "Product Agent",
        "product_knowledge_owner",
        "product",
        ("product_knowledge_model", "sales_knowledge_model", "inventory_knowledge_model"),
        ("product_cards", "brand_guidelines", "supplier_notes"),
        ("Search Knowledge", "Generate Product Card", "Draft Selling Point", "Link SAP Fact"),
        ("ceo", "business", "inventory", "content"),
        ("price_change", "bulk_product_update", "external_publish"),
        ("sku_basis", "brand_basis", "selling_points", "content_constraints", "approval_request"),
    ),
    MultiAgentRole(
        "member",
        "Member Agent",
        "member_growth_support",
        "store_manager",
        ("member_knowledge_model", "sales_knowledge_model", "product_knowledge_model"),
        ("member_feedback", "campaign_playbooks", "privacy_policy"),
        ("Query SAP Analysis", "Search Knowledge", "Draft Follow-up", "Create Task Draft"),
        ("ceo", "business", "product", "content"),
        ("mass_notification", "privacy_sensitive_export", "external_publish"),
        ("segment_basis", "privacy_boundary", "product_fit", "followup_draft", "approval_request"),
    ),
    MultiAgentRole(
        "content",
        "Content Agent",
        "content_operation_support",
        "marketing",
        ("product_knowledge_model", "sales_knowledge_model", "member_knowledge_model"),
        ("brand_guidelines", "content_library", "training_material"),
        ("Search Knowledge", "Draft Content", "Draft Sales Script", "Publish Request Draft"),
        ("ceo", "business", "product", "member"),
        ("external_publish", "mass_notification", "brand_claim"),
        ("source_basis", "content_draft", "publish_risk", "target_audience", "approval_request"),
    ),
)


COLLABORATION_FLOWS = (
    AgentCollaborationFlow(
        "daily_business_review",
        "Daily Business Review",
        "CEO Agent coordinates daily SAP facts, business risks and next actions.",
        ("ceo", "business", "inventory", "product", "member", "content"),
        ("sales", "inventory", "products", "members", "boss_experience"),
        "CEO Agent consolidates findings and sends high-risk actions to approval.",
        "ai_operation_plans.pending_review",
    ),
    AgentCollaborationFlow(
        "inventory_to_content",
        "Inventory Risk to Content Action",
        "Inventory Agent identifies risk goods, Product Agent explains SKU context, Content Agent drafts reviewed content.",
        ("inventory", "product", "content", "ceo"),
        ("inventory", "products", "brands", "sales"),
        "Each handoff must include SAP fact, knowledge source and limitation.",
        "manual_review_before_markdown_transfer_or_publish",
    ),
    AgentCollaborationFlow(
        "member_growth_loop",
        "Member Growth Loop",
        "Member Agent segments customers, Product Agent matches offers, Business Agent checks KPI impact, Content Agent drafts follow-up.",
        ("member", "product", "business", "content", "ceo"),
        ("members", "sales", "products", "campaigns"),
        "Privacy and external messaging stay blocked until approval.",
        "manual_review_before_mass_notification_or_campaign_execution",
    ),
)


def build_multi_agent_system_contract() -> dict:
    return {
        "ok": True,
        "version": "VAFOX Enterprise OS V1.6",
        "module": "multi_agent_system",
        "strategy": "extend_existing_agent_framework_with_shared_sap_knowledge_context_without_rebuilding",
        "roles": [asdict(role) for role in MULTI_AGENT_ROLES],
        "collaboration_flows": [asdict(flow) for flow in COLLABORATION_FLOWS],
        "shared_sap_knowledge_policy": SHARED_SAP_KNOWLEDGE_POLICY,
        "integration_points": {
            "agent_framework": "/api/agents/framework",
            "sap_knowledge_engine": "/api/sap-knowledge-engine",
            "knowledge_quality": "/api/knowledge-quality",
            "knowledge_brain": "/api/knowledge/brain",
            "approval_center": "/api/approvals",
            "collaboration_plan": "/api/agents/v1.6/collaboration-plan",
        },
        "approval_gate": {
            "source_table": "ai_operation_plans",
            "default_status": "pending_review",
            "execution_status_before_approval": "blocked_manual_required",
            "execution_mode": "approval_then_execute",
            "manual_review_required_before_execution": True,
        },
    }


def build_shared_sap_context(sap_engine: dict | None = None, knowledge_quality: dict | None = None) -> dict:
    sap_engine = sap_engine or {}
    knowledge_quality = knowledge_quality or {}
    contract = sap_engine.get("contract") if isinstance(sap_engine.get("contract"), dict) else sap_engine
    models = contract.get("knowledge_models") or sap_engine.get("knowledge_models") or []
    warehouse = sap_engine.get("ai_data_warehouse") or contract.get("ai_data_warehouse") or []
    quality = knowledge_quality.get("quality_score") or knowledge_quality.get("score") or {}
    return {
        "ok": True,
        "version": "VAFOX Enterprise OS V1.6",
        "policy": SHARED_SAP_KNOWLEDGE_POLICY,
        "sap_context_sources": {
            "sap_knowledge_engine": "/api/sap-knowledge-engine",
            "ai_data_warehouse": "/api/sap-knowledge-engine/warehouse",
            "knowledge_quality": "/api/knowledge-quality",
            "knowledge_brain": "/api/knowledge/brain",
        },
        "available_models": [model.get("key") for model in models if model.get("key")],
        "available_entities": [model.get("entity") for model in models if model.get("entity")],
        "warehouse_datasets": [dataset.get("key") for dataset in warehouse if dataset.get("key")],
        "knowledge_quality_level": quality.get("level", "unknown"),
        "readiness": "ready" if models else "waiting_for_sap_knowledge_engine",
        "agent_context_rule": "every_agent_output_must_reference_sap_model_or_show_limitation",
    }


def build_agent_collaboration_plan(objective: str, agents: tuple[str, ...] | list[str] | None = None) -> dict:
    selected = tuple(a.strip().lower() for a in (agents or ()) if str(a).strip())
    if not selected:
        selected = ("ceo", "business", "inventory", "product", "member", "content")
    role_map = {role.key: asdict(role) for role in MULTI_AGENT_ROLES}
    selected_roles = [role_map[key] for key in selected if key in role_map]
    if not selected_roles:
        selected_roles = [asdict(role) for role in MULTI_AGENT_ROLES]
    return {
        "ok": True,
        "version": "VAFOX Enterprise OS V1.6",
        "objective": (objective or "").strip(),
        "agents": selected_roles,
        "execution_mode": "approval_then_execute",
        "execution_status": "blocked_manual_required",
        "approval_required": True,
        "approval_status": "pending_review",
        "risk_level": "high",
        "shared_sap_context_required": True,
        "planned_steps": [
            "ceo_agent_define_objective",
            "load_shared_sap_knowledge_context",
            "assign_agent_subtasks",
            "collect_agent_findings_with_sources",
            "cross_check_sap_facts_and_knowledge_quality",
            "draft_explainable_recommendation",
            "create_human_approval_request",
            "wait_for_manual_decision",
            "execute_only_after_approval",
            "write_audit_and_feedback",
        ],
        "guardrails": SHARED_SAP_KNOWLEDGE_POLICY,
    }
