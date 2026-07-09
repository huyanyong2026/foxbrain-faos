"""FoxBrain OS Enterprise V1.7 AI business management contracts.

This module keeps V1.7 additive. It produces deterministic planning payloads
that the portal can persist, audit and route through approval before any
business execution happens.
"""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class BusinessCenterModule:
    key: str
    name: str
    purpose: str
    api_route: str
    database_table: str
    approval_required: bool


@dataclass(frozen=True)
class AutomatedDecisionJob:
    key: str
    name: str
    schedule: str
    source: tuple[str, ...]
    output: str
    approval_required_for_execution: bool


AI_BUSINESS_CENTER_MODULES = (
    BusinessCenterModule("today_report", "Today Business Report", "Daily AI report from SAP, knowledge and rules", "/api/decision/today", "ai_recommendation_history", True),
    BusinessCenterModule("sales_forecast", "Sales Forecast", "Forecast store and brand sales with explainable drivers", "/api/forecast/sales", "sales_forecasts", True),
    BusinessCenterModule("inventory_manager", "AI Inventory Manager", "Score inventory health and slow-moving risk", "/api/inventory/risk", "inventory_analysis", True),
    BusinessCenterModule("purchase_manager", "AI Purchase Manager", "Recommend buy, cautious buy, stop buy or clearance", "/api/purchase/recommend", "ai_recommendation_history", True),
    BusinessCenterModule("profit_center", "AI Profit Center", "Rank real profit contribution by brand and store", "/api/profit/analysis", "ai_recommendation_history", True),
    BusinessCenterModule("risk_engine", "Risk Engine", "Detect sales, inventory, brand and supply-chain risks", "/api/risk/list", "risk_alerts", True),
    BusinessCenterModule("ai_memory", "AI Business Memory", "Apply boss operating experience as reviewed rules", "/api/business-memory", "business_memory", True),
    BusinessCenterModule("ai_task_center", "AI Task Center", "Turn natural language requests into governed AI tasks", "/api/ai/task/create", "ai_tasks", True),
)


AI_BUSINESS_AUTOMATIONS = (
    AutomatedDecisionJob("daily_business_report", "Daily AI business report", "08:00 daily", ("SAP readonly sync", "enterprise knowledge", "operating rules"), "boss_daily_report", True),
    AutomatedDecisionJob("inventory_risk_scan", "Inventory risk scan", "09:00 daily", ("SAP inventory", "sales velocity", "gross margin"), "inventory_analysis", True),
    AutomatedDecisionJob("sales_forecast_update", "Sales forecast update", "10:00 daily", ("historical sales", "seasonality", "inventory", "brand trend"), "sales_forecasts", True),
    AutomatedDecisionJob("post_sap_analysis", "Post SAP sync analysis", "22:00 daily", ("SAP sync summary", "risk engine", "AI memory"), "decision_analysis_job", True),
    AutomatedDecisionJob("weekly_business_report", "Weekly business report", "Monday weekly", ("SAP", "knowledge", "rules"), "weekly_report", True),
    AutomatedDecisionJob("monthly_business_report", "Monthly business report", "1st monthly", ("SAP", "profit", "inventory", "risk"), "monthly_report", True),
)


V17_DATA_TABLES = (
    "sales_forecasts",
    "inventory_analysis",
    "risk_alerts",
    "business_memory",
    "ai_recommendation_history",
)


V17_GUARDRAILS = {
    "sap_source_of_truth": True,
    "sap_writeback_disabled": True,
    "high_risk_requires_human_approval": True,
    "ai_advice_history_required": True,
    "explainable_traceable_auditable": True,
    "mobile_access_required": True,
}


def _num(metrics: dict[str, Any], key: str, default: float = 0) -> float:
    try:
        return float(metrics.get(key, default) or 0)
    except Exception:
        return default


def build_ai_business_center_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.7",
        "module": "ai_business_management_center",
        "positioning": "AI business management system",
        "data_flow": [
            "enterprise_data",
            "ai_analysis_engine",
            "business_forecast",
            "risk_discovery",
            "decision_advice",
            "boss_approval",
            "execution_closed_loop",
        ],
        "modules": [asdict(module) for module in AI_BUSINESS_CENTER_MODULES],
        "automations": [asdict(job) for job in AI_BUSINESS_AUTOMATIONS],
        "database_tables": list(V17_DATA_TABLES),
        "guardrails": dict(V17_GUARDRAILS),
    }


def build_daily_business_report(metrics: dict[str, Any], knowledge_context: dict[str, Any] | None = None, operating_rules: dict[str, Any] | None = None) -> dict[str, Any]:
    yesterday_sales = _num(metrics, "yesterday_sales")
    gross_margin = _num(metrics, "gross_margin")
    risk_count = int(_num(metrics, "risk_count"))
    inventory_amount = _num(metrics, "inventory_amount")
    summary = "sales_need_attention" if yesterday_sales <= 0 or risk_count > 0 else "business_stable"
    return {
        "ok": True,
        "report_type": "daily_business_report",
        "schedule": "08:00 daily",
        "data_sources": ["SAP sales", "SAP inventory", "brand profiles", "enterprise knowledge", "operating rules"],
        "yesterday_sales_summary": {"sales": yesterday_sales, "status": summary},
        "rankings": {
            "stores": [{"store": "Nanshan", "rank": 1, "basis": "latest SAP sales placeholder"}],
            "brands": [{"brand": "Kailas", "rank": 1, "basis": "gross margin and growth opportunity"}],
            "products": [{"product": "core outdoor products", "rank": 1, "basis": "sales velocity"}],
        },
        "gross_profit": {"gross_margin": gross_margin, "rule": "gross_profit_before_sales_volume"},
        "inventory_change": {"inventory_amount": inventory_amount, "risk_count": risk_count},
        "abnormal_alerts": ["inventory_risk_requires_review"] if risk_count else [],
        "ai_advice": [
            "review_zero_sales_or_delayed_store_report" if yesterday_sales <= 0 else "keep_daily_followup",
            "prioritize_inventory_risk_before_purchase",
            "boss_approval_required_before_execution",
        ],
        "explainability": {
            "knowledge_context_ready": bool(knowledge_context),
            "operating_rules_ready": bool(operating_rules),
            "sap_readonly": True,
        },
        "approval_required": True,
        "execution_mode": "advice_only_until_boss_approval",
    }


def build_sales_forecast(metrics: dict[str, Any], forecast_period: str = "7d") -> dict[str, Any]:
    base_sales = _num(metrics, "month_sales") / 30 if _num(metrics, "month_sales") else _num(metrics, "yesterday_sales")
    multiplier = 1.15 if forecast_period in ("7d", "future_7_days") else 1.08
    forecast_sales = round(max(base_sales, 0) * (7 if forecast_period.startswith("7") else 30) * multiplier, 2)
    return {
        "ok": True,
        "forecast_period": forecast_period,
        "forecast_sales": forecast_sales,
        "confidence": 0.72,
        "analysis": {
            "drivers": ["historical_sales", "month_on_month", "seasonality", "holiday", "weather", "campaign", "inventory", "brand_trend"],
            "store_examples": [{"store": "Nanshan", "expected_change": "+15%", "reason": "weekend_activity", "recommendation": "increase Kailas display"}],
            "brand_examples": [{"brand": "Osprey", "risk": "increasing"}, {"brand": "Mammut", "risk": "normal"}, {"brand": "Kailas", "opportunity": "increasing"}],
        },
        "recommendation": "increase_display_for_growth_brands_and_review_osprey_inventory_risk",
        "approval_required": True,
        "source": ["SAP sales", "SAP inventory", "brand trend", "operating rules"],
    }


def build_inventory_analysis(metrics: dict[str, Any]) -> dict[str, Any]:
    risk_count = int(_num(metrics, "risk_count"))
    inventory_amount = _num(metrics, "inventory_amount")
    score = 92 if risk_count == 0 else 68 if risk_count < 20 else 48
    level = "healthy" if score >= 90 else "normal" if score >= 70 else "attention" if score >= 50 else "risk"
    return {
        "ok": True,
        "agent": "AI Inventory Manager",
        "health_score": score,
        "risk_level": level,
        "score_rule": {"90-100": "healthy", "70-90": "normal", "50-70": "attention", "<50": "risk"},
        "slow_moving_items": ["review_slow_moving_skus_from_SAP_inventory_age"] if risk_count else [],
        "inventory_amount": inventory_amount,
        "expected_sales_cycle": "requires_sap_inventory_age_detail",
        "recommendation": "clearance_plan_requires_boss_approval" if score < 70 else "keep_monitoring",
        "source": ["SAP inventory", "SAP sales", "purchase history", "inventory age", "gross margin"],
        "approval_required": True,
    }


def build_purchase_recommendation(metrics: dict[str, Any], inventory_analysis: dict[str, Any] | None = None) -> dict[str, Any]:
    score = int((inventory_analysis or {}).get("health_score", 70))
    action = "clear_inventory" if score < 50 else "cautious_purchase" if score < 70 else "recommended_purchase"
    return {
        "ok": True,
        "agent": "AI Purchase Manager",
        "analysis_inputs": ["sales_velocity", "inventory", "brand_trend", "market_change", "historical_purchase"],
        "decision": action,
        "recommendations": [
            {"brand": "Kailas", "action": "recommended_purchase", "reason": "growth opportunity"},
            {"brand": "Osprey", "action": "cautious_purchase", "reason": "inventory risk must be checked"},
            {"brand": "slow_moving_products", "action": "clear_inventory", "reason": "cash and inventory health first"},
        ],
        "report": "purchase_analysis_report",
        "approval_required": True,
        "execution_mode": "proposal_only_until_boss_approval",
    }


def build_profit_analysis(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "module": "AI Profit Center",
        "inputs": ["sales_amount", "cost", "gross_profit", "discount", "rebate", "inventory_occupation"],
        "real_profit_contribution_ranking": [
            {"rank": 1, "brand": "Kailas", "basis": "margin and growth opportunity"},
            {"rank": 2, "brand": "Mammut", "basis": "stable margin"},
            {"rank": 3, "brand": "Osprey", "basis": "risk review required"},
        ],
        "gross_profit": _num(metrics, "gross_profit"),
        "gross_margin": _num(metrics, "gross_margin"),
        "recommendation": "increase_resource_input_after_reviewing_inventory_and_brand_rules",
        "approval_required": True,
    }


def build_risk_alerts(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    alerts = []
    if _num(metrics, "yesterday_sales") <= 0:
        alerts.append({
            "type": "sales_risk",
            "level": "high",
            "description": "Yesterday sales is zero or delayed.",
            "source": "SAP sales",
            "suggestion": "Confirm data delay or store reporting before any execution.",
            "status": "pending_review",
        })
    if int(_num(metrics, "risk_count")) > 0:
        alerts.append({
            "type": "inventory_risk",
            "level": "medium",
            "description": "Inventory risk items need review.",
            "source": "SAP inventory",
            "suggestion": "Run AI Inventory Manager and approve clearance task manually.",
            "status": "pending_review",
        })
    alerts.append({
        "type": "brand_risk",
        "level": "watch",
        "description": "Brand trend and price system should be reviewed with operating rules.",
        "source": "brand profile + boss memory",
        "suggestion": "Keep discount policy aligned with brand positioning.",
        "status": "pending_review",
    })
    return alerts


def build_ai_task_plan(question: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    normalized = (question or "").strip()
    return {
        "ok": True,
        "task_type": "ai_business_analysis",
        "question": normalized,
        "required_calls": ["SAP sales", "SAP inventory", "brand profiles", "operating rules"],
        "analysis_steps": [
            "create_task",
            "read_sap_sales",
            "read_sap_inventory",
            "load_brand_profile",
            "load_operating_rules",
            "generate_problem_cause_advice_execution_plan",
            "wait_for_boss_approval",
        ],
        "expected_output": ["problem", "cause", "advice", "execution_plan"],
        "context_ready": bool(context),
        "risk_level": "high",
        "approval_required": True,
        "execution_mode": "approval_then_execute",
    }
