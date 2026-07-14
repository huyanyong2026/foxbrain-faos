"""VAFOX Enterprise OS V1.2 governed agent orchestration contract."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BusinessAgentProfile:
    key: str
    name: str
    role: str
    owner_role: str
    data_scope: tuple[str, ...]
    knowledge_scope: tuple[str, ...]
    tool_scope: tuple[str, ...]
    risk_level: str
    approval_required: bool
    output_contract: tuple[str, ...]


AGENT_EXECUTION_POLICY = {
    "all_ai_execution_requires_approval": True,
    "execution_mode": "approval_then_execute",
    "execution_status_before_approval": "blocked_manual_required",
    "no_direct_tool_execution": True,
    "sap_writeback_disabled_without_explicit_approval": True,
    "audit_required": True,
    "explainable_traceable_auditable": True,
}


AGENT_DOMAINS = (
    BusinessAgentProfile(
        "business",
        "Business Operations Agent",
        "operating_analysis",
        "boss",
        ("sales", "profit", "tasks", "risks", "store_performance"),
        ("management_policy", "operating_reviews", "decision_history"),
        ("Query SAP Analysis", "Search Knowledge", "Create Task", "Create Report"),
        "high",
        True,
        ("objective", "sap_basis", "knowledge_basis", "risk", "recommended_plan", "approval_request"),
    ),
    BusinessAgentProfile(
        "inventory",
        "Inventory Agent",
        "inventory_decision_support",
        "purchasing",
        ("inventory", "products", "brands", "stores", "purchasing"),
        ("inventory_policy", "brand_rules", "supplier_notes"),
        ("Query SAP Analysis", "Search Knowledge", "Price Decision Draft", "Create Task"),
        "high",
        True,
        ("objective", "stock_basis", "brand_basis", "risk_goods", "recommended_plan", "approval_request"),
    ),
    BusinessAgentProfile(
        "membership",
        "Member Growth Agent",
        "member_growth_support",
        "store_manager",
        ("customers", "members", "sales", "followups", "campaigns"),
        ("customer_service_policy", "member_feedback", "campaign_playbooks"),
        ("Query SAP Analysis", "Search Knowledge", "Draft Content", "Create Task"),
        "high",
        True,
        ("objective", "member_segment_basis", "privacy_boundary", "recommended_plan", "approval_request"),
    ),
    BusinessAgentProfile(
        "content",
        "Content Agent",
        "content_operation_support",
        "marketing",
        ("products", "brands", "campaigns", "knowledge_items"),
        ("brand_guidelines", "content_library", "training_material"),
        ("Search Knowledge", "Draft Content", "Send Notification Draft", "Create Task"),
        "high",
        True,
        ("objective", "brand_basis", "content_draft", "publish_risk", "approval_request"),
    ),
)


def build_agent_orchestration_contract() -> dict:
    return {
        "ok": True,
        "version": "VAFOX Enterprise OS V1.2",
        "module": "agent_orchestration",
        "strategy": "extend_existing_agent_framework_without_database_refactor",
        "domains": [asdict(profile) for profile in AGENT_DOMAINS],
        "execution_policy": AGENT_EXECUTION_POLICY,
        "approval_gate": {
            "source_table": "ai_operation_plans",
            "default_status": "pending_review",
            "manual_review_required_before_execution": True,
            "high_risk_operations_must_not_auto_execute": True,
        },
        "integration_points": {
            "sap_understanding": "/api/knowledge/sap-understanding",
            "knowledge_brain": "/api/knowledge/brain",
            "agent_framework": "/api/agents/framework",
            "approval_center": "/api/approvals",
        },
    }


def find_agent_domain(domain_key: str) -> dict:
    normalized = (domain_key or "").strip().lower()
    for profile in AGENT_DOMAINS:
        if profile.key == normalized:
            return asdict(profile)
    return asdict(AGENT_DOMAINS[0])


def build_agent_plan_request(domain_key: str, objective: str, created_by_role: str = "") -> dict:
    domain = find_agent_domain(domain_key)
    return {
        "ok": True,
        "version": "VAFOX Enterprise OS V1.2",
        "domain": domain,
        "objective": (objective or "").strip(),
        "created_by_role": created_by_role or "unknown",
        "execution_mode": AGENT_EXECUTION_POLICY["execution_mode"],
        "execution_status": AGENT_EXECUTION_POLICY["execution_status_before_approval"],
        "approval_required": True,
        "approval_status": "pending_review",
        "risk_level": "high",
        "planned_steps": [
            "permission_check",
            "retrieve_enterprise_knowledge",
            "read_sap_understanding",
            "draft_recommendation",
            "create_approval_request",
            "wait_for_human_decision",
            "execute_only_after_approval",
            "write_audit_and_feedback",
        ],
        "guardrails": AGENT_EXECUTION_POLICY,
    }
