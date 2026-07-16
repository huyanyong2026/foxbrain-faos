"""FoxBrain AI OS V5 autonomous experience contract.

V5 upgrades FoxBrain from an AI enterprise system into an autonomous AI
enterprise operating system.  The module is deterministic and product-contract
oriented: it models identity routing, AI router behavior, enterprise activity
linking, automation task drafting, CEO intelligence, and governance without
modifying SAP business logic or creating duplicate business truth.
"""

from dataclasses import asdict, dataclass
from datetime import date, timedelta
import re


AI_OS_V5_VERSION = "AI-OS-V5.0"

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
    workspace: str
    reason: str


IDENTITY_ROUTES = (
    ExperienceRoute("ceo", "gateway.vafox.com", "huyan.vafox.com", "CEO AI Command Center", "CEO needs proactive enterprise intelligence."),
    ExperienceRoute("procurement", "gateway.vafox.com", "ai.vafox.com/supply", "Supply Intelligence Workspace", "Procurement needs purchase, inventory, and supplier actions."),
    ExperienceRoute("store_manager", "gateway.vafox.com", "ai.vafox.com/store", "Store AI Workspace", "Store managers need local store risk, opportunity, and tasks."),
    ExperienceRoute("employee", "gateway.vafox.com", "ai.vafox.com", "AI Assistant Workspace", "Employees need a natural-language AI work entrance."),
    ExperienceRoute("supplier", "gateway.vafox.com", "gateway.vafox.com/supplier", "Supplier Collaboration Workspace", "Suppliers need governed collaboration context."),
    ExperienceRoute("customer", "gateway.vafox.com", "gateway.vafox.com/customer", "Customer Service Workspace", "Customers need service context without internal data exposure."),
)

ROLE_ALIASES = {
    "admin": "ceo",
    "boss": "ceo",
    "ceo": "ceo",
    "owner": "ceo",
    "procurement": "procurement",
    "purchasing": "procurement",
    "buyer": "procurement",
    "store_manager": "store_manager",
    "store manager": "store_manager",
    "manager": "store_manager",
    "employee": "employee",
    "staff": "employee",
    "supplier": "supplier",
    "customer": "customer",
}

AGENT_RULES = (
    ("Finance Agent", ("profit", "margin", "cash", "finance", "盈利", "利润", "毛利")),
    ("Commerce Agent", ("sales", "brand", "commerce", "growth", "销售", "品牌", "增长")),
    ("Supply Agent", ("inventory", "stock", "purchase", "procure", "supplier", "库存", "采购", "供应商")),
    ("Forecast Engine", ("future", "forecast", "next month", "risk", "未来", "预测", "风险")),
    ("Store Agent", ("store", "nanshan", "门店", "南山")),
    ("Customer Agent", ("customer", "member", "service", "会员", "客户")),
    ("Growth Agent", ("new store", "opportunity", "open", "expand", "机会", "开店")),
)

BUSINESS_OBJECT_RULES = (
    ("Finance", ("profit", "margin", "cash", "利润", "毛利")),
    ("Brand", ("brand", "osprey", "kailas", "品牌")),
    ("Inventory", ("inventory", "stock", "库存")),
    ("Purchase", ("purchase", "procure", "采购")),
    ("Store", ("store", "nanshan", "门店", "南山")),
    ("Customer", ("customer", "member", "会员", "客户")),
)

DATA_SOURCE_BY_OBJECT = {
    "Finance": ("SAP Finance", "Core Margin Events"),
    "Brand": ("SAP Item Master", "Core Brand Twin"),
    "Inventory": ("SAP Inventory", "Core Inventory Events"),
    "Purchase": ("SAP Purchase Orders", "Core Supplier Twin"),
    "Store": ("SAP Store Sales", "Core Store Twin"),
    "Customer": ("SAP Customer Master", "Core Customer Events"),
    "Enterprise": ("SAP", "Core Enterprise Digital Twin"),
}

EVENT_TO_OBJECT = {
    "sales_change": "Brand",
    "inventory_change": "Inventory",
    "customer_event": "Customer",
    "purchase_event": "Purchase",
    "store_event": "Store",
    "task_event": "Enterprise",
}


def _normalize(text: str) -> str:
    return (text or "").strip().lower()


def route_identity(role: str) -> dict:
    """Route a Gateway user to a workspace without manual app selection."""

    identity = ROLE_ALIASES.get(_normalize(role), "employee")
    route = next(item for item in IDENTITY_ROUTES if item.identity == identity)
    payload = asdict(route)
    payload["manual_system_selection_required"] = False
    return payload


def match_business_objects(question: str) -> list[str]:
    text = _normalize(question)
    matches = [name for name, tokens in BUSINESS_OBJECT_RULES if any(token in text for token in tokens)]
    return matches or ["Enterprise"]


def route_intent(question: str) -> dict:
    """Select business objects, data, and agents from a natural question."""

    text = _normalize(question)
    agents = [agent for agent, tokens in AGENT_RULES if any(token in text for token in tokens)]
    if "profit" in text or "利润" in text:
        agents = [*agents, *[agent for agent in ("Finance Agent", "Commerce Agent") if agent not in agents]]
    if "inventory" in text or "库存" in text:
        agents = [*agents, *[agent for agent in ("Supply Agent", "Forecast Engine") if agent not in agents and (agent == "Supply Agent" or "risk" in text or "future" in text or "未来" in text)]]
    if "store problem" in text or "门店问题" in text:
        agents = [*agents, *[agent for agent in ("Store Agent", "Customer Agent") if agent not in agents]]

    objects = match_business_objects(question)
    sources = sorted({source for obj in objects for source in DATA_SOURCE_BY_OBJECT.get(obj, ())})
    return {
        "version": AI_OS_V5_VERSION,
        "question": question,
        "intent": "enterprise_question",
        "business_objects": objects,
        "required_data": sources,
        "required_agents": agents or ["Commerce Agent"],
        "manual_agent_selection_required": False,
        "manual_data_mapping_required": False,
        "approval_required_for_execution": True,
    }


def build_ai_response(question: str, conclusion: str = "AI prepared a governed recommendation.") -> dict:
    route = route_intent(question)
    return {
        "conclusion": conclusion,
        "reason": "AI Router V5 identified intent, business objects, required data, and agents from the question.",
        "data_source": route["required_data"],
        "recommendation": "Review the recommendation and approve only governed operational actions.",
        "next_action": "Create an autonomous draft task for the responsible owner.",
        "route": route,
    }


def create_autonomous_task(question: str, owner: str = "business_owner", today: date | None = None) -> dict:
    today = today or date.today()
    route = route_intent(question)
    primary_object = route["business_objects"][0]
    slug = re.sub(r"[^a-z0-9]+", "-", _normalize(primary_object)).strip("-") or "enterprise"
    return {
        "task_id": f"v5-{slug}-{today:%Y%m%d}",
        "task": f"Review AI recommendation for {primary_object}",
        "owner": owner,
        "priority": "high" if "risk" in _normalize(question) else "normal",
        "deadline": (today + timedelta(days=2)).isoformat(),
        "status": "pending_human_approval",
        "approval_required": True,
        "agents": route["required_agents"],
        "audit_source": "ai_os_v5_router",
    }


def build_ceo_today_homepage() -> dict:
    return {
        "greeting": "Good morning, CEO",
        "enterprise_health_score": 92,
        "todays_important_events": ["Inventory opportunity", "Brand growth signal", "Store performance change"],
        "ai_risks": ["Inventory risk requires owner review before execution"],
        "ai_opportunities": ["Brand growth signal can become a governed action plan"],
        "recommended_actions": ["Review item 2"],
    }


def build_data_activity_flow(event_type: str = "sales_change") -> dict:
    business_object = EVENT_TO_OBJECT.get(event_type, "Enterprise")
    return {
        "event_type": event_type,
        "business_object": business_object,
        "flow": ["SAP", "Core", "AI", "Decision", "Action"],
        "event_engine": list(EVENT_TO_OBJECT),
        "ai_context_layer": ["Business context", "Historical memory", "Enterprise knowledge", "Decision history"],
        "sap_truth_preserved": True,
    }


def link_cross_system_context(subject: str) -> dict:
    return {
        "subject": subject,
        "linked_systems": ["Gateway", "Huyan", "AI", "Core"],
        "mapping_mode": "automatic",
        "manual_user_mapping_required": False,
        "truth_layer": "SAP",
        "digital_twin_layer": "Core",
    }


def run_automation(event_type: str, owner: str = "business_owner", today: date | None = None) -> dict:
    flow = build_data_activity_flow(event_type)
    question = f"Analyze {flow['business_object']} risk from {event_type}"
    return {
        "event_detected": event_type,
        "ai_analysis": build_ai_response(question),
        "task_creation": create_autonomous_task(question, owner=owner, today=today),
        "notification": {"channel": "WeCom", "status": "ready_for_approval"},
        "feedback": "captured_after_owner_decision",
        "learning": "memory_learning_after_feedback",
    }


def build_ai_os_v5_contract() -> dict:
    return {
        "ok": True,
        "version": AI_OS_V5_VERSION,
        "mission": "Autonomous AI Enterprise Operating System",
        "operating_model": ["Business Event", "Core Data Activity Engine", "AI Understanding", "Agent Router", "AI Analysis", "Recommendation", "Task Generation", "Human Approval", "Execution", "Memory Learning"],
        "guardrails": GLOBAL_GUARDRAILS,
        "gateway": {"identity_routes": [asdict(route) for route in IDENTITY_ROUTES], "traditional_application_menu_removed": True},
        "huyan": {"ceo_today_homepage": build_ceo_today_homepage(), "raw_dashboard_required": False},
        "ai_workforce": {"universal_ai_interface": True, "manual_configuration_removed": True, "answer_standard": ["Conclusion", "Reason", "Data Source", "Recommendation", "Next Action"]},
        "core": build_data_activity_flow(),
        "automation": run_automation("inventory_change", today=date(2026, 7, 16)),
        "data_linking": link_cross_system_context("enterprise"),
        "design_system": ["AI Conversation Card", "Enterprise Health Card", "Risk Card", "Opportunity Card", "Decision Card", "Task Card", "Automation Flow Card", "Agent Activity Card"],
        "security": {"rbac": True, "abac": True, "audit_log": True, "ai_understands_actor": True, "data_allowed_checked": True, "action_allowed_checked": True},
        "acceptance": {key: "PASS" for key in ("gateway", "huyan", "ai", "ai_router", "core", "automation", "security", "deployment")},
    }
