"""CEO AI Strategic Operating System domain services.

This module keeps SAP B1 as business truth by deriving strategy signals from
Core/AI Center read models only; it does not write back to SAP or create a
separate business database.
"""

from __future__ import annotations

from datetime import date


ENTERPRISE_DIMENSIONS = ("Sales", "Margin", "Inventory", "Supply Chain", "Store Performance", "Customer")
HEALTH_SCORE_DIMENSIONS = ("Sales", "Margin", "Inventory", "Supply Chain", "Finance", "Growth", "Organization")


def _status_score(status):
    return {"completed": 92, "completed_with_warnings": 78, "waiting_for_data": 55}.get(status or "waiting_for_data", 65)


def build_ceo_strategy_snapshot(metrics, latest_batch=None, replenishment_summary=None, approved_runs=0, memories=0):
    """Build a deterministic CEO strategy snapshot from existing enterprise facts."""
    replenishment_summary = replenishment_summary or []
    batch_status = latest_batch["status"] if latest_batch else "waiting_for_data"
    urgent_skus = sum(int(item.get("urgent_skus") or 0) for item in replenishment_summary)
    suggested_units = sum(int(item.get("suggested_units") or 0) for item in replenishment_summary)
    pending_runs = int(metrics.get("pending_runs") or 0)
    pending_tasks = int(metrics.get("pending_tasks") or 0)
    base_score = _status_score(batch_status) + min(int(approved_runs or 0), 8) - min(pending_runs + pending_tasks, 12) - min(urgent_skus, 15)
    health_score = max(0, min(100, base_score))
    risk_level = "High" if urgent_skus >= 8 or health_score < 65 else "Medium" if urgent_skus or health_score < 82 else "Low"
    risk_probability = "High" if risk_level == "High" else "Medium" if risk_level == "Medium" else "Low"

    briefing = {
        "what_happened": [
            {"area": "Sales", "summary": "Daily executive signals are ready for CEO review through approved AI runs and store replenishment facts."},
            {"area": "Margin", "summary": "Margin watch remains part of the executive review; no SAP writeback is performed by the AI layer."},
            {"area": "Inventory", "summary": f"{suggested_units} suggested replenishment units and {urgent_skus} urgent SKUs are visible from the latest replenishment batch."},
            {"area": "Supply Chain", "summary": "Supply attention is routed through inventory pressure and supplier lead-time risk indicators."},
            {"area": "Store Performance", "summary": f"{len(replenishment_summary)} stores have current replenishment intelligence in the CEO view."},
            {"area": "Customer", "summary": "Customer demand is represented by sales velocity, brand trend, and content/market signal placeholders until richer Core feeds are connected."},
        ],
        "why_happened": [
            "The CEO layer combines Core read-only facts, AI workbench approvals, and replenishment signals instead of duplicating SAP business truth.",
            "Inventory urgency increases when recent sales velocity consumes safety stock faster than the replenishment rule target.",
            "Pending AI runs and tasks reduce operating confidence until a human decision owner reviews them.",
        ],
        "what_should_do_next": [
            {"priority": "P1", "action": "Review urgent replenishment SKUs with Supply Agent", "expected_impact": "Reduce stockout and fulfillment risk."},
            {"priority": "P2", "action": "Approve or reject pending CEO recommendations", "expected_impact": "Shorten decision latency and improve auditability."},
            {"priority": "P3", "action": "Promote high-confidence decisions into CEO memory", "expected_impact": "Improve repeat-season learning."},
        ],
    }

    risks = [
        {
            "risk": "Inventory pressure",
            "level": risk_level,
            "probability": risk_probability,
            "reason": f"Latest replenishment intelligence shows {urgent_skus} urgent SKUs and {suggested_units} suggested units.",
            "recommendation": "Ask Supply Agent for supplier and brand-level confirmation before purchase action.",
        },
        {
            "risk": "Decision backlog",
            "level": "Medium" if pending_runs or pending_tasks else "Low",
            "probability": "Medium" if pending_runs or pending_tasks else "Low",
            "reason": f"{pending_runs} AI analyses and {pending_tasks} tasks are waiting for human confirmation.",
            "recommendation": "Clear pending approvals in the CEO Decision Center before operational handoff.",
        },
    ]
    opportunities = [
        {
            "opportunity": "Outdoor category demand focus",
            "reason": "Replenishment and content-growth signals can reveal demand growth without changing SAP logic.",
            "recommended_action": "Increase exposure for products with strong velocity and safe margin after Core validation.",
        },
        {
            "opportunity": "Decision memory reuse",
            "reason": f"{memories} CEO memory records are available for pattern comparison.",
            "recommended_action": "Compare current seasonal actions against approved historical learnings.",
        },
    ]
    decision_center = {
        "problem": "Should the enterprise increase selected inventory attention today?",
        "analysis": "Inventory pressure and decision backlog are evaluated from read-only enterprise facts and AI approvals.",
        "options": [
            {"name": "Increase selected models", "tradeoff": "Higher availability with controlled purchase review."},
            {"name": "Maintain current levels", "tradeoff": "Lower cash pressure but potential stockout risk."},
            {"name": "Reduce exposure", "tradeoff": "Protects cash but may miss seasonal demand."},
        ],
        "recommendation": "Increase selected models only after Supply Agent confirmation.",
        "expected_result": "Better availability, lower emergency replenishment pressure, and a human-approved audit trail.",
    }
    simulation = {
        "question": "What happens if we increase inventory for urgent SKUs?",
        "expected": {"sales": "+3% to +8% availability-led lift", "margin": "Stable if discounting is avoided", "inventory": f"+{suggested_units} units under review", "risk": risk_level, "roi": "Positive when sell-through remains above safety-stock threshold"},
    }
    agents = ["Supply Agent", "Finance Agent", "Store Agent", "Growth Agent", "Customer Agent"]
    pipeline_status = [
        {"name": "SAP Sync", "status": "Completed", "detail": "SAP read-only sync has produced the latest enterprise facts."},
        {"name": "Core Update", "status": "Completed", "detail": "Core Enterprise Digital Twin is refreshed from canonical business objects."},
        {"name": "AI Analysis", "status": "Completed", "detail": "Risk, opportunity, and decision signals are generated from Core facts."},
        {"name": "Last Decision Update", "status": "Completed", "detail": "CEO decisions and approved memories are available to Huyan."},
    ]
    router = {
        "mode": "automatic",
        "route": "Huyan question → AI Router → Supply / Finance / Store / Growth / Customer Agents",
        "agents": agents,
    }

    return {
        "as_of": date.today().isoformat(), "enterprise_health_score": health_score,
        "risk_level": risk_level, "dimensions": ENTERPRISE_DIMENSIONS, "health_dimensions": HEALTH_SCORE_DIMENSIONS, "briefing": briefing,
        "risks": risks, "opportunities": opportunities, "decision_center": decision_center,
        "simulation": simulation, "memory": {"records": memories, "learning": "Record decision, reason, action, result, and learning after human confirmation."},
        "agents": agents, "pipeline_status": pipeline_status, "ai_router": router,
        "digital_employees": [
            {"name": "Executive Strategy Agent", "status": "Active", "tasks": pending_runs, "results": approved_runs, "purpose": "Executive risk, opportunity, and decision synthesis"},
            {"name": "Supply Agent", "status": "Active", "tasks": urgent_skus, "results": suggested_units, "purpose": "Inventory pressure and supplier action recommendations"},
            {"name": "Finance Agent", "status": "Active", "tasks": pending_tasks, "results": approved_runs, "purpose": "Cash, margin, and approval impact review"},
            {"name": "Store Agent", "status": "Active", "tasks": len(replenishment_summary), "results": suggested_units, "purpose": "Store-level replenishment and demand intelligence"},
            {"name": "Growth Agent", "status": "Active", "tasks": len(opportunities), "results": memories, "purpose": "Market, brand, and content growth opportunity discovery"},
            {"name": "Customer Agent", "status": "Active", "tasks": len(opportunities), "results": memories, "purpose": "Customer demand and experience signal interpretation"},
        ],
    }
