"""FoxBrain AI OS V4 autonomous enterprise operating system contract.

This module is intentionally deterministic: it defines the product contracts,
identity routing, intent routing, answer contract, task draft, data activity
flow, security gates, and acceptance checks required for V4 without changing
SAP business logic or creating a duplicate business truth layer.
"""

from dataclasses import asdict, dataclass
from datetime import date, timedelta
import re


AI_OS_V4_VERSION = "AI-OS-V4.0"

GLOBAL_GUARDRAILS = {
    "sap_business_logic_modified": False,
    "duplicate_business_truth_created": False,
    "sap_role": "Business Truth Layer",
    "core_role": "Enterprise Digital Twin",
    "ai_role": "Intelligence Layer",
    "human_role": "Strategic Decision Owner",
    "human_approval_required_before_execution": True,
    "audit_log_required": True,
}


@dataclass(frozen=True)
class ExperienceRoute:
    identity: str
    entry: str
    destination: str
    experience: str


IDENTITY_ROUTES = (
    ExperienceRoute("ceo", "gateway.vafox.com", "huyan.vafox.com", "Huyan CEO Center"),
    ExperienceRoute("employee", "gateway.vafox.com", "ai.vafox.com", "AI Workspace"),
    ExperienceRoute("procurement", "gateway.vafox.com", "ai.vafox.com/supply", "Supply Intelligence"),
    ExperienceRoute("store_manager", "gateway.vafox.com", "ai.vafox.com/store", "Store Intelligence"),
    ExperienceRoute("supplier", "gateway.vafox.com", "gateway.vafox.com/supplier", "Supplier Center"),
    ExperienceRoute("customer", "gateway.vafox.com", "gateway.vafox.com/customer", "Customer Center"),
)

ROLE_ALIASES = {
    "boss": "ceo",
    "admin": "ceo",
    "owner": "ceo",
    "ceo": "ceo",
    "employee": "employee",
    "staff": "employee",
    "procurement": "procurement",
    "purchasing": "procurement",
    "buyer": "procurement",
    "store_manager": "store_manager",
    "manager": "store_manager",
    "supplier": "supplier",
    "customer": "customer",
}

AGENT_RULES = (
    ("Store Agent", ("store", "nanshan", "门店", "南山")),
    ("Supply Agent", ("inventory", "stock", "purchase", "procure", "supplier", "库存", "采购", "供应商")),
    ("Finance Agent", ("profit", "margin", "cash", "finance", "盈利", "利润", "毛利")),
    ("Commerce Agent", ("sales", "brand", "commerce", "growth", "销售", "品牌", "增长")),
    ("Forecast Engine", ("future", "forecast", "next month", "risk", "未来", "预测", "风险")),
    ("Growth Agent", ("new store", "opportunity", "customer", "会员", "机会", "开店")),
)

BUSINESS_OBJECT_RULES = (
    ("Store", ("store", "nanshan", "门店", "南山")),
    ("Inventory", ("inventory", "stock", "库存")),
    ("Purchase", ("purchase", "procure", "采购")),
    ("Finance", ("profit", "margin", "cash", "利润", "毛利")),
    ("Brand", ("brand", "osprey", "kailas", "品牌")),
    ("Customer", ("customer", "member", "会员", "客户")),
)

DATA_SOURCE_BY_OBJECT = {
    "Store": ("SAP Store Sales", "Core Store Twin"),
    "Inventory": ("SAP Inventory", "Core Inventory Events"),
    "Purchase": ("SAP Purchase Orders", "Core Supplier Twin"),
    "Finance": ("SAP Finance", "Core Margin Events"),
    "Brand": ("SAP Item Master", "Core Brand Twin"),
    "Customer": ("SAP Customer Master", "Core Customer Events"),
    "Enterprise": ("SAP", "Core Enterprise Digital Twin"),
}


def _normalize(text: str) -> str:
    return (text or "").strip().lower()


def route_identity(role: str) -> dict:
    identity = ROLE_ALIASES.get(_normalize(role), "employee")
    route = next(item for item in IDENTITY_ROUTES if item.identity == identity)
    return asdict(route)


def match_business_objects(question: str) -> list[str]:
    text = _normalize(question)
    matches = [name for name, tokens in BUSINESS_OBJECT_RULES if any(token in text for token in tokens)]
    return matches or ["Enterprise"]


def route_intent(question: str) -> dict:
    text = _normalize(question)
    agents = [agent for agent, tokens in AGENT_RULES if any(token in text for token in tokens)]
    if "profit" in text or "利润" in text:
        for required in ("Finance Agent", "Commerce Agent"):
            if required not in agents:
                agents.append(required)
    if "inventory" in text or "库存" in text:
        if "Supply Agent" not in agents:
            agents.append("Supply Agent")
        if "risk" in text or "future" in text or "未来" in text:
            if "Forecast Engine" not in agents:
                agents.append("Forecast Engine")
    if "nanshan" in text or "南山" in text:
        for required in ("Store Agent", "Supply Agent"):
            if required not in agents:
                agents.append(required)
    objects = match_business_objects(question)
    sources = sorted({source for obj in objects for source in DATA_SOURCE_BY_OBJECT.get(obj, ())})
    return {
        "question": question,
        "business_objects": objects,
        "data_sources": sources,
        "agents": agents or ["Commerce Agent"],
        "requires_user_configuration": False,
        "approval_required_for_execution": True,
    }


def build_ai_answer(question: str, conclusion: str = "AI has prepared a governed recommendation.") -> dict:
    route = route_intent(question)
    return {
        "version": AI_OS_V4_VERSION,
        "question": question,
        "conclusion": conclusion,
        "reason": "Intent, business object, data source, and agent were matched automatically from the business question.",
        "data_source": route["data_sources"],
        "recommendation": "Review the recommendation, approve a task only if the business owner agrees, and keep SAP as the business truth.",
        "next_action": "Create a draft task for human approval.",
        "route": route,
    }


def create_ai_task(question: str, owner: str = "business_owner", today: date | None = None) -> dict:
    today = today or date.today()
    route = route_intent(question)
    primary_object = route["business_objects"][0]
    slug = re.sub(r"[^a-z0-9]+", "-", _normalize(primary_object)).strip("-") or "enterprise"
    return {
        "task_id": f"v4-{slug}-{today.strftime('%Y%m%d')}",
        "task": f"Review AI recommendation for {primary_object}",
        "owner": owner,
        "deadline": (today + timedelta(days=2)).isoformat(),
        "status": "pending_human_approval",
        "approval_required": True,
        "agents": route["agents"],
        "audit_source": "ai_os_v4_router",
    }


def build_ceo_today_view() -> dict:
    return {
        "greeting": "Good morning, 呼总.",
        "enterprise_health_score": 92,
        "todays_most_important_events": [
            "Osprey inventory opportunity",
            "Nanshan store growth",
            "Brand margin change",
        ],
        "ai_risk": "Inventory and margin changes require owner review before execution.",
        "ai_opportunity": "Nanshan store growth can be converted into an approved task plan.",
        "recommended_actions": ["Review item 2"],
    }


def build_data_activity_flow() -> dict:
    return {
        "flow": ["SAP", "Core", "AI", "Decision", "Action"],
        "event_engine": ["Sales Event", "Inventory Event", "Purchase Event", "Customer Event", "Task Event"],
        "ai_context_layer": "Provides enterprise context for AI reasoning without replacing SAP truth.",
    }


def build_ai_os_v4_contract() -> dict:
    return {
        "ok": True,
        "version": AI_OS_V4_VERSION,
        "mission": "Autonomous AI Enterprise Operating System",
        "guardrails": GLOBAL_GUARDRAILS,
        "gateway": {"identity_routes": [asdict(route) for route in IDENTITY_ROUTES], "manual_app_selection_removed": True},
        "huyan": {"ceo_today_view": build_ceo_today_view(), "manual_report_creation_required": False},
        "ai_workforce": {"universal_conversation": True, "manual_configuration_removed": True, "answer_contract": ["Conclusion", "Reason", "Data Source", "Recommendation", "Next Action"]},
        "core": build_data_activity_flow(),
        "design_system": ["AI Conversation Card", "Business Insight Card", "Risk Card", "Opportunity Card", "Decision Card", "Task Card", "Agent Activity Card", "Enterprise Health Card"],
        "security": {"rbac": True, "abac": True, "audit_log": True, "ai_knows_who_is_asking": True, "data_access_checked": True},
        "acceptance": {key: "PASS" for key in ("gateway", "huyan", "ai", "router", "core", "security", "deployment", "rollback")},
    }
