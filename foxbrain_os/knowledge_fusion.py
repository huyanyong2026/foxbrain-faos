"""FoxBrain OS Enterprise V1.6.5 knowledge fusion contracts."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FusionKnowledgeLayer:
    key: str
    name: str
    source_system: str
    source_tables: tuple[str, ...]
    trust_rule: str
    update_rule: str
    agent_use: tuple[str, ...]
    approval_rule: str


@dataclass(frozen=True)
class FusionAgentAccess:
    agent_key: str
    agent_name: str
    required_layers: tuple[str, ...]
    retrieval_scope: tuple[str, ...]
    output_requirements: tuple[str, ...]


KNOWLEDGE_FUSION_POLICY = {
    "three_layer_fusion_required": True,
    "sap_enterprise_knowledge_is_business_fact_base": True,
    "external_industry_knowledge_is_context_not_final_truth": True,
    "boss_experience_requires_review_before_active_use": True,
    "conflicts_must_show_source_priority_and_limitation": True,
    "high_risk_actions_require_human_approval": True,
    "ai_outputs_must_be_explainable_traceable_auditable": True,
    "no_sap_writeback_from_fusion": True,
}


FUSION_KNOWLEDGE_LAYERS = (
    FusionKnowledgeLayer(
        "sap_enterprise_knowledge",
        "SAP Enterprise Knowledge Base",
        "SAP Knowledge Engine",
        ("sap_knowledge_snapshots", "products", "sales_orders", "inventory", "customers"),
        "highest_priority_for_company_business_facts",
        "read_only_after_sap_sync",
        ("sales facts", "inventory state", "product facts", "member facts", "gross profit basis"),
        "no_sap_writeback_and_missing_data_must_be_disclosed",
    ),
    FusionKnowledgeLayer(
        "external_industry_knowledge",
        "External Industry Knowledge Base",
        "reviewed external research and industry documents",
        ("knowledge_items", "documents", "external_research_notes"),
        "context_only_must_not_override_sap_or_reviewed_boss_experience",
        "human_review_before_formal_knowledge",
        ("industry trend", "brand benchmark", "retail method", "content inspiration", "market risk"),
        "external_research_needs_human_review_before_agent_decision_use",
    ),
    FusionKnowledgeLayer(
        "boss_experience_knowledge",
        "Boss Experience Knowledge Base",
        "governed memory and decision history",
        ("memories", "decision_memories", "ai_operation_feedback", "user_preferences"),
        "highest_priority_for_company_strategy_and_operating_principles_after_review",
        "reviewed_context_learning_not_autonomous_training",
        ("operating principle", "decision tradeoff", "store experience", "brand preference", "risk tolerance"),
        "boss_experience_requires_review_before_active_ai_use",
    ),
)


FUSION_AGENT_ACCESS = (
    FusionAgentAccess(
        "ceo",
        "CEO Agent",
        ("sap_enterprise_knowledge", "external_industry_knowledge", "boss_experience_knowledge"),
        ("sales", "inventory", "product", "member", "industry", "boss_decision"),
        ("sap_basis", "industry_context", "boss_experience_basis", "source_conflict", "approval_request"),
    ),
    FusionAgentAccess(
        "business",
        "Business Agent",
        ("sap_enterprise_knowledge", "boss_experience_knowledge", "external_industry_knowledge"),
        ("sales", "gross_profit", "store", "operating_policy", "industry_benchmark"),
        ("kpi_basis", "operating_experience", "industry_context", "risk", "task_draft"),
    ),
    FusionAgentAccess(
        "inventory",
        "Inventory Agent",
        ("sap_enterprise_knowledge", "boss_experience_knowledge", "external_industry_knowledge"),
        ("inventory", "product", "brand", "supplier", "markdown_policy", "market_demand"),
        ("stock_basis", "product_context", "boss_rule", "market_context", "approval_request"),
    ),
    FusionAgentAccess(
        "product",
        "Product Agent",
        ("sap_enterprise_knowledge", "external_industry_knowledge", "boss_experience_knowledge"),
        ("sku", "brand", "category", "trend", "selling_point", "boss_preference"),
        ("sku_basis", "industry_trend", "selling_points", "brand_rule", "limitation"),
    ),
    FusionAgentAccess(
        "member",
        "Member Agent",
        ("sap_enterprise_knowledge", "boss_experience_knowledge", "external_industry_knowledge"),
        ("member", "purchase_history", "service_policy", "privacy", "campaign_method"),
        ("segment_basis", "privacy_boundary", "experience_rule", "industry_method", "approval_request"),
    ),
    FusionAgentAccess(
        "content",
        "Content Agent",
        ("sap_enterprise_knowledge", "external_industry_knowledge", "boss_experience_knowledge"),
        ("product", "brand", "content_library", "retail_trend", "boss_tone"),
        ("source_basis", "industry_reference", "boss_tone", "content_draft", "publish_risk"),
    ),
)


def build_knowledge_fusion_contract() -> dict:
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.6.5",
        "module": "knowledge_fusion",
        "strategy": "fuse_sap_enterprise_knowledge_external_industry_knowledge_and_boss_experience_for_agents",
        "layers": [asdict(layer) for layer in FUSION_KNOWLEDGE_LAYERS],
        "agent_access": [asdict(access) for access in FUSION_AGENT_ACCESS],
        "policy": KNOWLEDGE_FUSION_POLICY,
        "source_priority": [
            "SAP facts for company factual state",
            "reviewed boss experience for operating principles and tradeoffs",
            "reviewed external industry knowledge for context and inspiration",
        ],
        "integration_points": {
            "sap_knowledge_engine": "/api/sap-knowledge-engine",
            "external_knowledge": "/api/knowledge/fusion/external-industry",
            "boss_experience": "/api/boss-experience/memory",
            "agent_fusion_context": "/api/agents/v1.6/fusion-knowledge",
            "approval_center": "/api/approvals",
        },
    }


def build_fusion_context(sap_engine: dict | None = None, knowledge_quality: dict | None = None, external_knowledge: dict | None = None) -> dict:
    sap_engine = sap_engine or {}
    knowledge_quality = knowledge_quality or {}
    external_knowledge = external_knowledge or {}
    sap_contract = sap_engine.get("contract") if isinstance(sap_engine.get("contract"), dict) else sap_engine
    sap_models = sap_engine.get("knowledge_models", {}).get("models", []) if isinstance(sap_engine.get("knowledge_models"), dict) else sap_contract.get("knowledge_models", [])
    quality = knowledge_quality.get("knowledge_quality") or knowledge_quality.get("quality_score") or {}
    boss_experience = knowledge_quality.get("boss_experience") or {}
    external_items = external_knowledge.get("items") or []
    layer_readiness = {
        "sap_enterprise_knowledge": "ready" if sap_models else "waiting_for_sap_knowledge_engine",
        "external_industry_knowledge": "ready" if external_items else "foundation_review_required",
        "boss_experience_knowledge": "ready" if int(boss_experience.get("approved_memory") or 0) or int(boss_experience.get("decision_memories") or 0) else "foundation_review_required",
    }
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.6.5",
        "contract": build_knowledge_fusion_contract(),
        "layer_readiness": layer_readiness,
        "fusion_ready": layer_readiness["sap_enterprise_knowledge"] == "ready",
        "sap_models": [model.get("key") for model in sap_models if model.get("key")],
        "external_industry_items": len(external_items),
        "knowledge_quality_level": quality.get("level", "unknown"),
        "boss_experience": {
            "approved_memory": boss_experience.get("approved_memory", 0),
            "decision_memories": boss_experience.get("decision_memories", 0),
            "operation_feedback": boss_experience.get("operation_feedback", 0),
        },
        "retrieval_rule": "retrieve_three_layers_then_rank_by_source_priority_and_permission",
        "conflict_rule": "when_sources_conflict_return_sap_fact_boss_experience_industry_context_and_limitation",
        "approval_boundary": "fusion_recommendations_do_not_execute_high_risk_actions_without_human_approval",
    }


def build_agent_fusion_context(agent_key: str, fusion_context: dict | None = None) -> dict:
    normalized = (agent_key or "").strip().lower() or "ceo"
    access_map = {access.agent_key: asdict(access) for access in FUSION_AGENT_ACCESS}
    access = access_map.get(normalized, access_map["ceo"])
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.6.5",
        "agent": access,
        "fusion_context": fusion_context or {},
        "required_output_basis": access["output_requirements"],
        "agent_instruction": "use_sap_facts_plus_reviewed_boss_experience_plus_reviewed_industry_context_with_citations_and_limitations",
        "approval_required_for_high_risk": True,
    }
