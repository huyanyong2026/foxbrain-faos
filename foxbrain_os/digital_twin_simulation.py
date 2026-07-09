"""FoxBrain OS Enterprise V2.1 digital twin and simulation contracts."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class TwinModel:
    key: str
    name: str
    dimensions: tuple[str, ...]
    sources: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioType:
    key: str
    name: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    approval_rule: str


DIGITAL_TWIN_MODELS = (
    TwinModel("company", "Company Twin", ("stores", "brands", "products", "employees", "suppliers", "customers", "finance", "operating_rules"), ("SAP", "knowledge_graph", "workflow", "finance")),
    TwinModel("store", "Store Twin", ("area", "rent", "employees", "sales", "traffic", "conversion_rate", "average_order_value", "brand_mix", "inventory", "profit"), ("SAP sales", "store archive", "employee profile", "inventory")),
    TwinModel("inventory", "Inventory Twin", ("purchase", "inbound", "sales", "stock_change", "cash_occupation", "shortage", "overstock"), ("SAP inventory", "purchase records", "sales trend")),
    TwinModel("employee", "Employee Twin", ("sales_ability", "product_ability", "customer_maintenance", "growth_trend", "training_direction"), ("employee profile", "sales history", "training", "customer feedback")),
    TwinModel("investment", "Investment Twin", ("investment", "renovation", "staffing", "inventory", "sales_target", "payback_period"), ("finance", "store model", "market knowledge")),
)


SCENARIO_TYPES = (
    ScenarioType("discount_adjustment", "Discount Adjustment", ("brand", "current_discount", "target_discount"), ("sales_change", "gross_margin_change", "inventory_change", "cash_change"), "price_and_discount_actions_require_approval"),
    ScenarioType("new_store", "New Store", ("area", "location", "investment", "staffing", "inventory"), ("year_1_profit", "break_even", "year_3_growth", "payback_period"), "investment_actions_require_approval"),
    ScenarioType("brand_mix", "Brand Mix Adjustment", ("reduce_brand", "increase_brand", "inventory", "cash"), ("profit_change", "inventory_change", "cash_occupation", "long_term_value"), "brand_strategy_requires_boss_approval"),
    ScenarioType("store_relocation", "Store Relocation", ("mall_data", "historical_sales", "rent", "brand_positioning", "competition", "roi"), ("feasibility_report", "risk", "investment_return"), "relocation_requires_boss_approval"),
    ScenarioType("future_order", "Future Order Pickup", ("future_order_amount", "historical_sales", "inventory", "price_system", "brand_risk", "cashflow", "rebate"), ("pickup_ratio", "risk", "sales_plan", "cash_arrangement"), "purchase_execution_requires_approval"),
)


V21_DATA_TABLES = (
    "digital_twin_models",
    "business_scenarios",
    "simulation_results",
    "strategy_reports",
    "cashflow_forecasts",
    "store_models",
    "employee_models",
    "investment_models",
)


V21_GUARDRAILS = {
    "sap_compatible": True,
    "knowledge_graph_compatible": True,
    "digital_employee_compatible": True,
    "workflow_compatible": True,
    "permission_system_compatible": True,
    "sandbox_only": True,
    "production_writeback_disabled": True,
    "human_approval_required_for_execution": True,
    "model_feedback_loop_required": True,
}


def build_digital_twin_simulation_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V2.1",
        "module": "digital_twin_simulation",
        "positioning": "predict future and simulate business decisions before reality",
        "models": [asdict(model) for model in DIGITAL_TWIN_MODELS],
        "scenario_types": [asdict(scenario) for scenario in SCENARIO_TYPES],
        "database_tables": list(V21_DATA_TABLES),
        "guardrails": dict(V21_GUARDRAILS),
        "simulation_feedback_loop": ["prediction", "actual_result", "variance_compare", "model_adjustment", "accuracy_improvement"],
    }


def build_company_twin_model(metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    metrics = metrics or {}
    return {
        "ok": True,
        "model": "FoxBrain Digital Twin",
        "real_enterprise_sources": ["SAP sales", "inventory", "purchase", "stores", "employees", "brands", "customers", "cash", "market"],
        "company_structure": ["company", "stores", "brands", "products", "employees", "suppliers", "customers", "finance", "operating_rules"],
        "current_metrics": metrics,
        "sandbox_rule": "read_only_twin_simulation_never_modifies_business_data",
    }


def build_discount_adjustment_scenario(brand: str = "Osprey", current_discount: float = 0.62, target_discount: float = 0.59) -> dict[str, Any]:
    sales_lift = round(max(current_discount - target_discount, 0) * 600, 2)
    margin_change = round((target_discount - current_discount) * 100, 2)
    return {
        "ok": True,
        "scenario_type": "discount_adjustment",
        "brand": brand,
        "input": {"current_discount": current_discount, "target_discount": target_discount},
        "options": [
            {"name": "Plan A", "sales_change": f"+{sales_lift}%", "profit_change": f"{margin_change}%", "inventory_change": "-20%", "cash_change": "improves_after_clearance"},
            {"name": "Plan B", "sales_change": "baseline", "profit_change": "better_margin", "inventory_change": "slower", "cash_change": "slower_recovery"},
        ],
        "recommendation": "compare_sell_through_cash_and_brand_price_risk_before_approval",
        "approval_required": True,
    }


def build_new_store_scenario(area: int = 1000, store_type: str = "flagship") -> dict[str, Any]:
    return {
        "ok": True,
        "scenario_type": "new_store",
        "input": {"area": area, "store_type": store_type},
        "needs": ["investment", "renovation", "staffing", "inventory", "sales_target", "payback_period"],
        "forecast": {"year_1": "loss_expected", "year_2": "break_even_expected", "year_3": "growth_expected"},
        "approval_required": True,
    }


def build_brand_mix_scenario(reduce_brand: str = "legacy_brand", increase_brand: str = "VAFOX") -> dict[str, Any]:
    return {
        "ok": True,
        "scenario_type": "brand_mix",
        "input": {"reduce_brand": reduce_brand, "increase_brand": increase_brand},
        "outputs": ["profit_change", "inventory_change", "cash_occupation", "long_term_value"],
        "recommendation": "increase_private_brand_only_after_inventory_cash_and_customer_acceptance_review",
        "approval_required": True,
    }


def build_cashflow_forecast(period_days: int = 90) -> dict[str, Any]:
    return {
        "ok": True,
        "agent": "AI Cash Manager",
        "period_days": period_days,
        "periods": [30, 90, 180],
        "inputs": ["inventory_cash", "purchase_payments", "rent", "salary", "sales_income"],
        "warning": "future_cash_pressure_may_increase_during_autumn_winter_purchase_period",
        "reasons": ["autumn_winter_goods_payment", "inventory_increase"],
        "suggestion": "control_purchase_and_review_cash_plan",
        "approval_required": True,
    }


def build_inventory_twin_forecast(period_days: int = 60) -> dict[str, Any]:
    return {
        "ok": True,
        "model": "Inventory Twin",
        "period_days": period_days,
        "flow": ["purchase", "inbound", "sales", "inventory_change", "cash_occupation"],
        "outputs": ["shortage_risk", "overstock_risk"],
        "source": ["SAP inventory", "SAP sales", "purchase records", "brand trend"],
    }


def build_employee_twin_model() -> dict[str, Any]:
    return {
        "ok": True,
        "model": "Employee Twin",
        "dimensions": ["sales_ability", "product_ability", "customer_maintenance", "growth_trend"],
        "examples": [{"employee": "A", "fit": "Kailas"}, {"employee": "B", "fit": "equipment sales"}],
        "suggestion": "assign_training_direction_by_product_strength_and_customer_feedback",
    }


def build_strategy_agent_report(question: str) -> dict[str, Any]:
    q = (question or "").strip()
    if "Osprey" in q or "期货" in q:
        return {
            "ok": True,
            "report_type": "future_order_strategy_report",
            "question": q,
            "required_reads": ["historical_sales", "inventory", "price_system", "hong_kong_price", "brand_risk", "cashflow", "rebate"],
            "output": ["pickup_ratio", "risk", "sales_plan", "cash_arrangement"],
            "recommendation": "do_not_pickup_all_before_cashflow_inventory_and_price_risk_review",
            "approval_required": True,
        }
    return {
        "ok": True,
        "report_type": "strategy_feasibility_report",
        "question": q,
        "required_reads": ["mall_data", "historical_sales", "rent", "brand_positioning", "competition", "investment_return"],
        "output": ["feasibility", "risk", "investment_return", "decision_options"],
        "approval_required": True,
    }


def build_board_assistant_pack() -> dict[str, Any]:
    return {
        "ok": True,
        "assistant": "AI Board Assistant",
        "materials": ["business_status", "risk", "opportunity", "investment_plan", "future_forecast", "recommendation"],
        "report": "board_meeting_pack_draft",
        "approval_required": True,
    }
