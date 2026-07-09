"""FoxBrain OS Enterprise V1.6.6 knowledge training and operating rules engine."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class KnowledgeTrainingSignal:
    key: str
    name: str
    source_layer: str
    source_objects: tuple[str, ...]
    training_use: str
    review_rule: str


@dataclass(frozen=True)
class OperatingRule:
    key: str
    name: str
    domain: str
    rule_basis: tuple[str, ...]
    fire_fox_logic: str
    decision_use: tuple[str, ...]
    approval_required_for: tuple[str, ...]


@dataclass(frozen=True)
class DecisionGuardrail:
    key: str
    name: str
    applies_to: tuple[str, ...]
    rule: str
    blocked_until: str


KNOWLEDGE_TRAINING_POLICY = {
    "reviewed_context_learning_not_autonomous_model_training": True,
    "sap_data_external_knowledge_and_boss_experience_must_be_fused": True,
    "operating_rules_are_company_logic_not_unreviewed_ai_opinion": True,
    "ai_decisions_must_follow_fire_fox_operating_logic": True,
    "high_risk_actions_require_human_approval": True,
    "no_sap_writeback_from_training_engine": True,
    "rule_changes_require_review_and_audit": True,
    "ai_outputs_must_be_explainable_traceable_auditable": True,
}


TRAINING_SIGNALS = (
    KnowledgeTrainingSignal(
        "sap_business_facts",
        "SAP Business Facts",
        "sap_enterprise_knowledge",
        ("sales", "gross_profit", "inventory", "products", "members"),
        "ground_ai_decisions_in_real_business_state",
        "read_only_after_sap_sync_no_writeback",
    ),
    KnowledgeTrainingSignal(
        "external_industry_context",
        "External Industry Context",
        "external_industry_knowledge",
        ("industry_trends", "brand_benchmarks", "retail_methods", "market_risks"),
        "add_market_context_without_overriding_company_facts",
        "human_review_required_before_formal_rule_use",
    ),
    KnowledgeTrainingSignal(
        "boss_operating_experience",
        "Boss Operating Experience",
        "boss_experience_knowledge",
        ("operating_principles", "decision_memories", "preferences", "operation_feedback"),
        "teach_ai_fire_fox_tradeoffs_risk_tolerance_and_action_style",
        "reviewed_memory_or_decision_history_only",
    ),
    KnowledgeTrainingSignal(
        "operation_feedback_loop",
        "Operation Feedback Loop",
        "ai_operation_feedback",
        ("accepted_plans", "rejected_plans", "business_outcomes", "operator_notes"),
        "improve_future_recommendation_quality",
        "feedback_informs_recommendations_but_must_not_auto_change_policy",
    ),
)


OPERATING_RULE_LIBRARY = (
    OperatingRule(
        "inventory_risk_first",
        "Inventory Risk First",
        "inventory",
        ("SAP inventory", "sales velocity", "boss markdown experience"),
        "High inventory risk must be reviewed before growth suggestions are treated as executable.",
        ("inventory transfer draft", "markdown review", "purchase delay suggestion"),
        ("markdown", "transfer_execution", "purchase_order", "sap_writeback"),
    ),
    OperatingRule(
        "gross_profit_before_sales_volume",
        "Gross Profit Before Sales Volume",
        "business",
        ("SAP sales", "gross profit", "boss profit principle"),
        "Sales growth is not positive when gross margin or cash occupation worsens beyond reviewed tolerance.",
        ("boss daily report", "store review", "business radar", "task priority"),
        ("target_change", "commission_change", "finance_decision"),
    ),
    OperatingRule(
        "brand_context_matters",
        "Brand Context Matters",
        "product",
        ("SAP product facts", "brand guideline", "external brand benchmark"),
        "Product recommendations must consider brand positioning, season, inventory state and boss brand experience.",
        ("selling point", "product portfolio", "content draft", "replenishment review"),
        ("price_change", "bulk_product_update", "external_publish"),
    ),
    OperatingRule(
        "member_privacy_and_fit",
        "Member Privacy and Product Fit",
        "member",
        ("SAP member history", "service policy", "campaign method"),
        "Member growth actions must match purchase history and privacy boundaries before messaging is drafted.",
        ("member segment", "follow-up draft", "private-domain campaign"),
        ("mass_notification", "privacy_sensitive_export", "external_publish"),
    ),
    OperatingRule(
        "content_must_have_business_basis",
        "Content Must Have Business Basis",
        "content",
        ("SAP product facts", "industry context", "boss tone preference"),
        "Content may be creative, but claims must be grounded in product facts, brand rules and reviewed context.",
        ("sales script", "content draft", "training material"),
        ("external_publish", "mass_notification", "brand_claim"),
    ),
    OperatingRule(
        "human_approval_before_execution",
        "Human Approval Before Execution",
        "governance",
        ("approval policy", "audit log", "risk register"),
        "AI may recommend and explain, but high-risk execution remains blocked until a human approves.",
        ("all agent plans", "decision recommendations", "automation loop"),
        ("sap_writeback", "finance_payment", "price_change", "external_publish", "bulk_data_change"),
    ),
)


DECISION_GUARDRAILS = (
    DecisionGuardrail(
        "source_basis_required",
        "Source Basis Required",
        ("all_ai_recommendations",),
        "Every recommendation must cite SAP fact, reviewed boss experience or reviewed external context.",
        "source_basis_available",
    ),
    DecisionGuardrail(
        "conflict_disclosure_required",
        "Conflict Disclosure Required",
        ("business", "inventory", "product", "member", "content"),
        "When SAP facts, external context and boss experience disagree, AI must disclose the conflict and prefer SAP for factual state.",
        "conflict_explained",
    ),
    DecisionGuardrail(
        "fire_fox_logic_required",
        "FireFox Operating Logic Required",
        ("all_agents", "decision_engine", "business_radar"),
        "AI recommendations must follow reviewed FireFox operating rules before being shown as decision support.",
        "rules_matched",
    ),
    DecisionGuardrail(
        "approval_before_high_risk",
        "Approval Before High Risk",
        ("price", "finance", "inventory_execution", "sap", "publish", "member_message"),
        "High-risk actions must create approval items and stay blocked before approval.",
        "manual_approval",
    ),
)


def build_knowledge_training_engine_contract() -> dict:
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.6.6",
        "module": "knowledge_training_rules_engine",
        "strategy": "turn_fusion_knowledge_into_reviewed_training_signals_operating_rules_and_decision_guardrails",
        "training_signals": [asdict(signal) for signal in TRAINING_SIGNALS],
        "operating_rules": [asdict(rule) for rule in OPERATING_RULE_LIBRARY],
        "decision_guardrails": [asdict(guardrail) for guardrail in DECISION_GUARDRAILS],
        "policy": KNOWLEDGE_TRAINING_POLICY,
        "integration_points": {
            "knowledge_fusion": "/api/knowledge/fusion",
            "training_engine": "/api/knowledge-training-engine",
            "operating_rules": "/api/knowledge-training-engine/rules",
            "decision_logic": "/api/knowledge-training-engine/decision-logic",
            "agents": "/api/agents/v1.6/fusion-knowledge",
            "approval_center": "/api/approvals",
        },
    }


def build_operating_rule_library(domain: str = "") -> dict:
    normalized = (domain or "").strip().lower()
    rules = [asdict(rule) for rule in OPERATING_RULE_LIBRARY]
    if normalized:
        rules = [rule for rule in rules if rule["domain"] == normalized or normalized in rule["decision_use"]]
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.6.6",
        "rules": rules,
        "rule_count": len(rules),
        "rule_change_policy": "review_required_before_rule_becomes_active_company_logic",
    }


def build_training_cycle_plan(fusion_context: dict | None = None, knowledge_quality: dict | None = None) -> dict:
    fusion_context = fusion_context or {}
    knowledge_quality = knowledge_quality or {}
    quality = knowledge_quality.get("knowledge_quality") or {}
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.6.6",
        "cycle": [
            "collect_sap_business_facts",
            "collect_reviewed_external_industry_context",
            "collect_reviewed_boss_experience",
            "score_knowledge_quality",
            "extract_candidate_operating_rules",
            "route_rule_changes_to_human_review",
            "publish_active_rules_to_agents",
            "write_audit_and_feedback",
        ],
        "fusion_context_readiness": fusion_context.get("layer_readiness", {}),
        "knowledge_quality_level": quality.get("level", "unknown"),
        "execution_mode": "reviewed_context_learning",
        "approval_required": True,
    }


def build_ai_decision_logic(fusion_context: dict | None = None, operating_metrics: dict | None = None) -> dict:
    fusion_context = fusion_context or {}
    operating_metrics = operating_metrics or {}
    active_rules = [asdict(rule) for rule in OPERATING_RULE_LIBRARY]
    guardrails = [asdict(guardrail) for guardrail in DECISION_GUARDRAILS]
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.6.6",
        "decision_logic": {
            "source_priority": [
                "SAP facts define current company state",
                "reviewed boss experience defines FireFox operating preference and tradeoff",
                "reviewed external knowledge adds industry context",
            ],
            "fire_fox_operating_logic": active_rules,
            "guardrails": guardrails,
            "operating_metrics": operating_metrics,
            "fusion_context": fusion_context,
            "recommendation_contract": [
                "objective",
                "sap_basis",
                "external_context",
                "boss_experience_basis",
                "matched_operating_rules",
                "risks_and_limitations",
                "approval_request_for_high_risk",
            ],
        },
        "approval_boundary": "ai_decision_support_only_high_risk_execution_requires_human_approval",
    }
