"""VAFOX Enterprise OS V1.1 AI Knowledge Brain contracts.

This module does not replace the existing portal implementation. It gives the
current SAP and knowledge features a stable service-shaped contract so they can
be migrated safely in later stages.
"""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class KnowledgeBrainSignal:
    key: str
    name: str
    source: str
    status: str
    explanation: str
    next_action: str


SAP_UNDERSTANDING_DIMENSIONS = (
    "sales",
    "gross_margin",
    "inventory",
    "brand",
    "product",
    "store",
    "customer",
    "supplier",
    "employee",
)


KNOWLEDGE_BRAIN_GUARDRAILS = {
    "sap_is_source_of_truth": True,
    "do_not_invent_business_facts": True,
    "cite_knowledge_or_sap_source": True,
    "high_risk_actions_require_human_approval": True,
    "sap_writeback_disabled": True,
    "knowledge_generation_is_reviewable": True,
}


def _status_from_count(count: int, ready_when_positive: str = "ready") -> str:
    return ready_when_positive if int(count or 0) > 0 else "waiting_for_data"


def build_sap_data_understanding(
    metrics: dict[str, Any] | None = None,
    sap_status: dict[str, Any] | None = None,
    sap_knowledge: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metrics = metrics or {}
    sap_status = sap_status or {}
    sap_knowledge = sap_knowledge or {}
    sap_items = int((sap_knowledge.get("metrics") or {}).get("sap_knowledge_items") or 0)
    candidate_count = int((sap_knowledge.get("metrics") or {}).get("candidate_count") or 0)
    has_sales = bool(float(metrics.get("month_sales") or 0) or float(metrics.get("yesterday_sales") or 0))
    has_inventory = bool(float(metrics.get("inventory_amount") or 0) or int(metrics.get("risk_count") or 0))
    freshness = sap_status.get("freshness") or sap_status.get("last_status") or "unknown"
    signals = [
        KnowledgeBrainSignal(
            "sap_freshness",
            "SAP freshness",
            "sap_sync_status",
            "ready" if freshness in ("fresh", "ok", "success") else "review",
            "SAP sync freshness determines whether AI can make current business statements.",
            "Check /sap-sync before using time-sensitive analysis.",
        ),
        KnowledgeBrainSignal(
            "sales_understanding",
            "Sales understanding",
            "cockpit_metrics",
            "ready" if has_sales else "waiting_for_data",
            "Sales and gross margin reasoning depends on synced sales amount and profit fields.",
            "Sync SAP sales summaries and store sales summaries.",
        ),
        KnowledgeBrainSignal(
            "inventory_understanding",
            "Inventory understanding",
            "cockpit_metrics",
            "ready" if has_inventory else "waiting_for_data",
            "Inventory reasoning depends on stock amount and risk count.",
            "Sync SAP stock-by-warehouse data and generate inventory knowledge cards.",
        ),
        KnowledgeBrainSignal(
            "sap_knowledge_cards",
            "SAP knowledge cards",
            "sap_knowledge",
            _status_from_count(sap_items),
            "AI answers become more precise when SAP entities are converted into knowledge cards.",
            "Open /knowledge/sap and generate or update SAP knowledge cards.",
        ),
        KnowledgeBrainSignal(
            "candidate_coverage",
            "Candidate coverage",
            "sap_knowledge_candidates",
            _status_from_count(candidate_count, "available"),
            "Candidates show which brands, products, stores, employees, customers or suppliers can become knowledge.",
            "Review candidate preview before bulk generation.",
        ),
    ]
    return {
        "ok": True,
        "service": "sap_data_understanding",
        "dimensions": list(SAP_UNDERSTANDING_DIMENSIONS),
        "data_freshness": freshness,
        "signals": [asdict(signal) for signal in signals],
        "metrics_used": {
            "month_sales": metrics.get("month_sales"),
            "yesterday_sales": metrics.get("yesterday_sales"),
            "gross_margin": metrics.get("gross_margin"),
            "inventory_amount": metrics.get("inventory_amount"),
            "risk_count": metrics.get("risk_count"),
            "sap_knowledge_items": sap_items,
            "sap_knowledge_candidates": candidate_count,
        },
        "limitations": [
            "No SAP facts are invented when synced data is missing.",
            "Brand, product and customer detail require SAP entity sync or generated knowledge cards.",
            "High-risk actions remain approval-only.",
        ],
    }


def build_enterprise_knowledge_brain(
    knowledge_metrics: dict[str, Any] | None = None,
    sap_understanding: dict[str, Any] | None = None,
    recent_sources: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    knowledge_metrics = knowledge_metrics or {}
    sap_understanding = sap_understanding or {}
    recent_sources = recent_sources or []
    total = int(knowledge_metrics.get("knowledge_items") or knowledge_metrics.get("total") or 0)
    chunks = int(knowledge_metrics.get("chunks") or 0)
    pending = int(knowledge_metrics.get("pending_review") or 0)
    sap_signals = sap_understanding.get("signals") or []
    gaps = []
    if total <= 0:
        gaps.append("knowledge_base_empty")
    if chunks <= 0:
        gaps.append("knowledge_chunks_missing")
    if pending > 0:
        gaps.append("knowledge_pending_review")
    if any(signal.get("status") in ("waiting_for_data", "review") for signal in sap_signals):
        gaps.append("sap_understanding_needs_data_or_review")
    return {
        "ok": True,
        "version": "VAFOX Enterprise OS V1.1",
        "service": "ai_knowledge_brain",
        "positioning": "SAP data understanding + enterprise knowledge retrieval + explainable AI context",
        "knowledge_metrics": {
            "knowledge_items": total,
            "chunks": chunks,
            "pending_review": pending,
        },
        "sap_understanding": sap_understanding,
        "recent_sources": recent_sources[:10],
        "knowledge_gaps": gaps,
        "query_flow": [
            "detect_intent",
            "load_sap_context",
            "load_enterprise_knowledge",
            "filter_by_permission",
            "rank_sources",
            "answer_with_citations",
            "show_limitations",
            "route_high_risk_actions_to_approval",
        ],
        "guardrails": KNOWLEDGE_BRAIN_GUARDRAILS,
        "recommended_next_actions": [
            "Generate SAP knowledge cards for available synced entities.",
            "Review pending knowledge before using it as official policy.",
            "Add missing brand, product, customer and supplier SAP dimensions.",
        ],
    }


def build_query_plan(question: str, scope: str = "all") -> dict[str, Any]:
    q = (question or "").strip()
    lower = q.lower()
    needs_sap = any(token in lower for token in ("sap", "sales", "inventory", "margin", "销售", "库存", "毛利", "门店", "品牌"))
    needs_knowledge = True
    return {
        "ok": True,
        "question": q,
        "scope": scope or "all",
        "needs_sap_context": needs_sap,
        "needs_knowledge_context": needs_knowledge,
        "retrieval_scopes": ["sap_knowledge", "knowledge_items"] if needs_sap else ["knowledge_items"],
        "answer_contract": {
            "must_cite_sources": True,
            "must_show_limitations": True,
            "must_not_auto_execute": True,
        },
    }
