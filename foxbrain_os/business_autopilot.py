"""FoxBrain OS Enterprise V2.2 autonomous business operation contracts."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class HealthDimension:
    key: str
    name: str
    signals: tuple[str, ...]
    weight: int


@dataclass(frozen=True)
class AutopilotJob:
    key: str
    name: str
    schedule: str
    output: str


BUSINESS_HEALTH_DIMENSIONS = (
    HealthDimension("sales", "Sales Health", ("sales_growth", "traffic", "conversion_rate", "average_order_value"), 25),
    HealthDimension("inventory", "Inventory Health", ("inventory_turnover", "inventory_age", "cash_occupation"), 25),
    HealthDimension("profit", "Profit Health", ("gross_margin", "expense", "cashflow"), 20),
    HealthDimension("brand", "Brand Health", ("brand_growth", "price_system", "market_trend"), 15),
    HealthDimension("people", "People Health", ("employee_sales", "turnover_risk", "training_status"), 15),
)


AUTOPILOT_JOBS = (
    AutopilotJob("health_scan", "Enterprise health scan", "06:00 daily", "business_health_scores"),
    AutopilotJob("daily_report", "AI daily report", "07:00 daily", "ceo_daily_reports"),
    AutopilotJob("boss_push", "Boss priority push", "08:00 daily", "notifications"),
    AutopilotJob("task_creation", "Automatic task creation", "09:00 daily", "action_tasks"),
    AutopilotJob("execution_followup", "Execution follow-up", "10:00 daily", "action_results"),
    AutopilotJob("sap_sync", "SAP sync", "22:00 daily", "sap_sync_history"),
    AutopilotJob("daily_review", "Daily business review", "23:00 daily", "ai_learning_records"),
)


V22_DATA_TABLES = (
    "business_health_scores",
    "monitor_rules",
    "business_alerts",
    "action_tasks",
    "action_results",
    "ai_learning_records",
    "rule_evolution",
    "ceo_daily_reports",
)


V22_GUARDRAILS = {
    "sap_sync_compatible": True,
    "knowledge_graph_compatible": True,
    "digital_twin_compatible": True,
    "digital_employee_compatible": True,
    "workflow_compatible": True,
    "human_approval_for_high_risk": True,
    "autopilot_creates_tasks_not_unsafe_execution": True,
    "continuous_learning_required": True,
}


def build_business_autopilot_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V2.2",
        "module": "business_autopilot",
        "positioning": "AI autonomous business operation center",
        "flow": [
            "monitor_real_business",
            "detect_anomaly",
            "analyze_reason",
            "generate_solution",
            "create_task",
            "owner_execution",
            "result_feedback",
            "ai_learning",
        ],
        "health_dimensions": [asdict(d) for d in BUSINESS_HEALTH_DIMENSIONS],
        "autopilot_jobs": [asdict(j) for j in AUTOPILOT_JOBS],
        "database_tables": list(V22_DATA_TABLES),
        "guardrails": dict(V22_GUARDRAILS),
    }


def calculate_business_health_score(metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    metrics = metrics or {}
    risk_count = int(metrics.get("risk_count") or 0)
    gross_margin = float(metrics.get("gross_margin") or 0)
    sales_score = 82 if float(metrics.get("month_sales") or 0) >= 0 else 60
    inventory_score = max(45, 90 - min(risk_count, 45))
    profit_score = 86 if gross_margin >= 25 else 72 if gross_margin else 70
    brand_score = 82
    people_score = 78
    total = round((sales_score * 25 + inventory_score * 25 + profit_score * 20 + brand_score * 15 + people_score * 15) / 100)
    return {
        "ok": True,
        "score": total,
        "dimensions": {
            "sales": sales_score,
            "inventory": inventory_score,
            "profit": profit_score,
            "brand": brand_score,
            "people": people_score,
        },
        "strengths": ["Kailas sales growth"],
        "risks": ["Osprey inventory pressure"] if risk_count else [],
        "suggestions": ["optimize purchase structure", "review inventory and price system together"],
    }


def build_daily_inspection_plan() -> dict[str, Any]:
    return {
        "ok": True,
        "schedule": "06:00 daily",
        "checks": [
            {"type": "sales_anomaly", "rule": "store_sales_declines_for_7_days", "analysis": ["traffic", "employees", "brand", "campaign"]},
            {"type": "inventory_anomaly", "rule": "product_no_sales_for_180_days", "outputs": ["clearance_plan", "promotion_advice", "display_advice"]},
            {"type": "price_anomaly", "rule": "hong_kong_price_lower_than_domestic", "outputs": ["brand_price_risk_alert"]},
        ],
        "report": "daily_inspection_report",
    }


def build_early_warning_forecast() -> dict[str, Any]:
    return {
        "ok": True,
        "engine": "Early Warning Engine",
        "periods": [7, 30, 90],
        "risks": [
            {"type": "sales_risk", "prediction": "possible_decline"},
            {"type": "inventory_risk", "prediction": "overstock_may_increase"},
            {"type": "cash_risk", "prediction": "cash_pressure_may_increase"},
            {"type": "supply_chain_risk", "prediction": "supplier_change_watch"},
        ],
    }


def build_action_plan(problem: str = "Nanshan backpack sales declined 25%") -> dict[str, Any]:
    return {
        "ok": True,
        "problem": problem,
        "solution": "redesign backpack display plan",
        "task": {
            "title": "Redesign backpack display plan",
            "owner": "store_manager",
            "due_days": 7,
            "required_uploads": ["display_photo", "sales_change"],
        },
        "tracking": ["task_created", "owner_followup", "result_review"],
        "approval_required": True,
    }


def build_ceo_dashboard_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "dashboard": "CEO Dashboard",
        "top_10_metrics": [
            "today_sales",
            "profit",
            "inventory_risk",
            "cashflow",
            "store_ranking",
            "brand_ranking",
            "employee_status",
            "major_risk",
            "ai_advice",
            "pending_approvals",
        ],
        "display_rule": "show_only_boss_top_10_metrics_click_for_detail",
    }


def build_rule_evolution_plan() -> dict[str, Any]:
    return {
        "ok": True,
        "engine": "Rule Evolution Engine",
        "example_rule": "outdoor_brand_purchase_decision_should_not_only_use_sales",
        "purchase_weights": {"sales": 30, "inventory": 30, "brand_value": 20, "market_trend": 20},
        "optimization": "adjust_weights_after_result_feedback_and_boss_review",
        "approval_required": True,
    }


def build_learning_record_template() -> dict[str, Any]:
    return {
        "ok": True,
        "learning_center": "AI Enterprise Learning Center",
        "fields": ["problem", "ai_advice", "boss_decision", "execution_result", "final_effect"],
        "case_library": ["Osprey price adjustment", "Kailas purchase case", "store relocation case", "large store investment case", "campaign marketing case"],
    }


def build_chairman_agent_brief() -> dict[str, Any]:
    return {
        "ok": True,
        "agent": "Chairman Agent",
        "question": "What should I focus on today?",
        "top_focus": ["Osprey inventory risk", "Nanshan store sales decline", "autumn-winter purchase cash plan"],
        "suggested_schedule": ["handle inventory plan in the morning", "hold purchase meeting in the afternoon"],
        "permission": "highest_read_permission_execution_still_approval_gated",
    }


def build_biggest_risk_analysis() -> dict[str, Any]:
    return {
        "ok": True,
        "request": "check_current_biggest_business_risk",
        "required_calls": ["SAP", "knowledge_graph", "digital_twin", "historical_cases", "market_research"],
        "top_5_risks": [
            {"risk": "Osprey inventory pressure", "impact": "cash and margin", "solution": "review clearance and pickup ratio", "task": "inventory action plan"},
            {"risk": "store sales decline", "impact": "revenue", "solution": "traffic and display review", "task": "store improvement task"},
            {"risk": "cash pressure", "impact": "purchase payment", "solution": "control purchase rhythm", "task": "cashflow review"},
            {"risk": "price system change", "impact": "brand margin", "solution": "monitor Hong Kong price", "task": "price risk alert"},
            {"risk": "staff capability gap", "impact": "conversion", "solution": "targeted product training", "task": "training task"},
        ],
        "approval_required": True,
    }
