"""FoxBrain OS Enterprise V1.5 AI knowledge training and quality contracts."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class KnowledgeQualityDimension:
    key: str
    name: str
    weight: int
    evidence: str
    improvement_action: str


@dataclass(frozen=True)
class AiLearningSignal:
    key: str
    name: str
    source: str
    learning_use: str
    approval_required: bool


@dataclass(frozen=True)
class BossExperienceModel:
    key: str
    name: str
    memory_type: str
    source: str
    fields: tuple[str, ...]
    ai_usage: tuple[str, ...]
    review_rule: str


KNOWLEDGE_QUALITY_DIMENSIONS = (
    KnowledgeQualityDimension("source_traceability", "Source Traceability", 25, "source_type source_id source_ref lineage", "add_source_and_lineage_before_ai_use"),
    KnowledgeQualityDimension("human_review", "Human Review", 20, "status owner reviewed memory", "route_low_confidence_knowledge_to_review"),
    KnowledgeQualityDimension("business_relevance", "Business Relevance", 20, "category tags object links SAP model", "link_to_product_sales_inventory_member_or_decision"),
    KnowledgeQualityDimension("freshness", "Freshness", 15, "updated_at version retention policy", "refresh_stale_operating_knowledge"),
    KnowledgeQualityDimension("retrieval_readiness", "Retrieval Readiness", 10, "summary keywords chunks embedding_status", "generate_summary_keywords_and_embeddings"),
    KnowledgeQualityDimension("safety_boundary", "Safety Boundary", 10, "visibility permission retention approval", "set_visibility_and_high_risk_approval_boundary"),
)


AI_LEARNING_SIGNALS = (
    AiLearningSignal("approved_knowledge", "Approved Knowledge", "knowledge_items", "retrieval_and_answer_grounding", False),
    AiLearningSignal("sap_knowledge", "SAP Knowledge Cards", "sap_knowledge_snapshots", "business_fact_grounding", False),
    AiLearningSignal("approved_memory", "Approved Memory", "memories", "long_term_company_context", True),
    AiLearningSignal("decision_memory", "Decision Memory", "decision_memories", "boss_reasoning_and_tradeoff_learning", True),
    AiLearningSignal("operation_feedback", "Operation Feedback", "ai_operation_feedback", "plan_quality_improvement", True),
    AiLearningSignal("user_preference", "User Preference", "user_preferences", "personalized_response_style", True),
)


BOSS_EXPERIENCE_MODELS = (
    BossExperienceModel(
        "boss_principle",
        "Boss Operating Principle",
        "company_principle",
        "memories",
        ("title", "content", "importance", "confidence", "evidence_json", "lineage_json"),
        ("daily_report_context", "decision_risk_review", "agent_instruction"),
        "manager_or_boss_review_required_before_active_memory",
    ),
    BossExperienceModel(
        "boss_decision",
        "Boss Decision Memory",
        "business_decision",
        "decision_memories",
        ("decision_title", "decision_context", "options_considered", "selected_option", "reason", "risks", "follow_up_task"),
        ("similar_case_retrieval", "tradeoff_explanation", "future_decision_prompt"),
        "decision_memory_must_link_to_reviewed_memory_when_used_by_ai",
    ),
    BossExperienceModel(
        "boss_preference",
        "Boss Preference",
        "user_preference",
        "user_preferences",
        ("key", "value", "scope", "updated_at"),
        ("tone_preference", "report_layout", "priority_filtering"),
        "preference_changes_are_audited_and_role_scoped",
    ),
    BossExperienceModel(
        "boss_feedback",
        "Boss Operation Feedback",
        "operation_feedback",
        "ai_operation_feedback",
        ("outcome", "business_result", "operator_note", "next_action"),
        ("planner_improvement", "risk_threshold_adjustment", "task_quality_review"),
        "feedback_informs_ai_but_does_not_auto_change_policy",
    ),
)


def build_knowledge_training_quality_contract() -> dict:
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.5",
        "module": "knowledge_training_quality",
        "strategy": "improve_knowledge_quality_ai_learning_and_boss_experience_memory_without_rebuilding",
        "quality_dimensions": [asdict(item) for item in KNOWLEDGE_QUALITY_DIMENSIONS],
        "ai_learning_signals": [asdict(item) for item in AI_LEARNING_SIGNALS],
        "boss_experience_models": [asdict(item) for item in BOSS_EXPERIENCE_MODELS],
        "rules": {
            "ai_learning_uses_approved_or_reviewable_sources": True,
            "boss_experience_requires_review_before_active_memory": True,
            "high_risk_actions_require_human_approval": True,
            "do_not_train_on_unreviewed_sensitive_customer_or_finance_content": True,
            "knowledge_quality_score_is_advisory_not_final_truth": True,
        },
    }


def score_knowledge_quality(metrics: dict) -> dict:
    total = int(metrics.get("total") or 0)
    reviewed = int(metrics.get("reviewed") or 0)
    with_source = int(metrics.get("with_source") or 0)
    with_summary = int(metrics.get("with_summary") or 0)
    with_keywords = int(metrics.get("with_keywords") or 0)
    sap_items = int(metrics.get("sap_items") or 0)
    approved_memory = int(metrics.get("approved_memory") or 0)
    decisions = int(metrics.get("decisions") or 0)

    def ratio(value: int) -> float:
        return value / total if total else 0.0

    source_score = ratio(with_source) * 25
    review_score = ratio(reviewed) * 20
    relevance_score = min(20, ratio(sap_items) * 10 + (1 if decisions else 0) * 5 + (1 if approved_memory else 0) * 5)
    freshness_score = 10 if total else 0
    retrieval_score = min(10, ratio(with_summary) * 5 + ratio(with_keywords) * 5)
    safety_score = 10 if reviewed or approved_memory else 5 if total else 0
    score = round(source_score + review_score + relevance_score + freshness_score + retrieval_score + safety_score, 1)
    if score >= 80:
        level = "strong"
    elif score >= 60:
        level = "usable"
    elif score >= 35:
        level = "needs_review"
    else:
        level = "foundation"
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.5",
        "score": score,
        "level": level,
        "breakdown": {
            "source_traceability": round(source_score, 1),
            "human_review": round(review_score, 1),
            "business_relevance": round(relevance_score, 1),
            "freshness": round(freshness_score, 1),
            "retrieval_readiness": round(retrieval_score, 1),
            "safety_boundary": round(safety_score, 1),
        },
        "metrics": metrics,
    }


def build_ai_learning_plan(quality_score: dict, boss_experience: dict) -> dict:
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.5",
        "quality_level": quality_score.get("level"),
        "learning_mode": "reviewed_context_learning_not_autonomous_model_training",
        "allowed_sources": [asdict(item) for item in AI_LEARNING_SIGNALS],
        "boss_experience": boss_experience,
        "next_actions": [
            "review_low_quality_knowledge",
            "convert_boss_decisions_to_reviewed_memory",
            "link_ai_operation_feedback_to_future_plans",
            "use_approved_memory_in_boss_daily_report",
        ],
        "approval_boundary": "learning_changes_context_and_recommendations_only_after_review",
    }
