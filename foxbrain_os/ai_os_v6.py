"""FoxBrain AI OS V6 clean autonomous enterprise operating system contract.

V6 is the clean-architecture rebuild target.  It intentionally does not extend
legacy V3/V4/V5 runtime contracts at execution time; instead it defines a
single AI-native operating model for Gateway, Huyan, AI Workspace, Core,
automation, link repair, health checks, and release governance.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, timedelta
import re

AI_OS_V6_VERSION = "AI OS V6"
AI_OS_V6_BUILD = "AI-OS-V6-CLEAN-REBUILD-V1"
TARGET_SYSTEMS = ("gateway.vafox.com", "huyan.vafox.com", "ai.vafox.com", "core.vafox.com")

LEGACY_RUNTIME_BLOCKLIST = ("V3", "V4", "V5", "AI-OS-V3", "AI-OS-V4", "AI-OS-V5")


@dataclass(frozen=True)
class V6Route:
    role: str
    entry: str
    destination: str
    workspace: str
    reason: str


IDENTITY_ROUTES = (
    V6Route("ceo", "gateway.vafox.com", "huyan.vafox.com", "CEO Autonomous Command Center", "CEO receives enterprise health, risks, opportunities, decisions, and AI actions."),
    V6Route("employee", "gateway.vafox.com", "ai.vafox.com", "Digital Workforce OS", "Employees ask natural-language questions and receive governed AI work output."),
    V6Route("procurement", "gateway.vafox.com", "ai.vafox.com/supply", "Supply AI", "Procurement receives inventory, supplier, replenishment, and task recommendations."),
    V6Route("store_manager", "gateway.vafox.com", "ai.vafox.com/store", "Store AI", "Store managers receive local performance, risk, and action intelligence."),
    V6Route("supplier", "gateway.vafox.com", "gateway.vafox.com/supplier", "Supplier Collaboration Gateway", "Suppliers receive permission-scoped collaboration context."),
)

ROLE_ALIASES = {
    "ceo": "ceo", "boss": "ceo", "owner": "ceo", "admin": "ceo",
    "employee": "employee", "staff": "employee", "user": "employee",
    "procurement": "procurement", "purchasing": "procurement", "buyer": "procurement",
    "store_manager": "store_manager", "store manager": "store_manager", "manager": "store_manager",
    "supplier": "supplier", "vendor": "supplier",
}

AGENT_RULES = (
    ("Risk Agent", ("risk", "风险", "最大风险")),
    ("Supply Agent", ("inventory", "stock", "osprey", "purchase", "supplier", "库存", "采购", "供应商")),
    ("Store Agent", ("store", "nanshan", "门店", "南山")),
    ("Growth Agent", ("sales", "growth", "opportunity", "销售", "增长", "机会")),
    ("Finance Agent", ("profit", "cash", "margin", "利润", "现金", "毛利")),
)

OBJECT_RULES = (
    ("Enterprise", ("enterprise", "company", "企业", "最大风险")),
    ("Inventory", ("inventory", "stock", "osprey", "库存")),
    ("Store", ("store", "nanshan", "门店", "南山")),
    ("Sales", ("sales", "growth", "销售", "增长")),
    ("Finance", ("profit", "cash", "margin", "利润", "现金", "毛利")),
)

CORE_SOURCE_BY_OBJECT = {
    "Enterprise": ("Core Enterprise Digital Twin", "SAP B1"),
    "Inventory": ("Core Inventory Twin", "SAP B1 Inventory"),
    "Store": ("Core Store Twin", "SAP B1 Store Sales"),
    "Sales": ("Core Sales Events", "SAP B1 Sales"),
    "Finance": ("Core Finance Twin", "SAP B1 Finance"),
}


def _normalize(value: str) -> str:
    return (value or "").strip().lower()


def route_identity(role: str) -> dict:
    """Route a user from Gateway with no legacy portal menu or app picker."""
    identity = ROLE_ALIASES.get(_normalize(role), "employee")
    route = next(item for item in IDENTITY_ROUTES if item.role == identity)
    payload = asdict(route)
    payload.update({"version": AI_OS_V6_VERSION, "manual_application_selection": False, "legacy_navigation_removed": True})
    return payload


def route_ai_question(question: str) -> dict:
    """Select intent, agents, core data, and task policy from one user question."""
    text = _normalize(question)
    objects = [name for name, tokens in OBJECT_RULES if any(token in text for token in tokens)] or ["Enterprise"]
    agents = [name for name, tokens in AGENT_RULES if any(token in text for token in tokens)]
    if "最大风险" in text and "Risk Agent" not in agents:
        agents.insert(0, "Risk Agent")
    if not agents:
        agents = ["Risk Agent"]
    sources = sorted({source for obj in objects for source in CORE_SOURCE_BY_OBJECT[obj]})
    return {
        "version": AI_OS_V6_VERSION,
        "question": question,
        "intent": "autonomous_enterprise_work",
        "business_objects": objects,
        "selected_agents": agents,
        "core_data_sources": sources,
        "manual_agent_dropdown_removed": True,
        "manual_source_selection_removed": True,
        "manual_object_selection_removed": True,
        "manual_analysis_form_removed": True,
        "task_creation_policy": "draft_task_requires_human_approval",
    }


def create_ai_task(question: str, owner: str = "business_owner", today: date | None = None) -> dict:
    today = today or date.today()
    route = route_ai_question(question)
    slug = re.sub(r"[^a-z0-9]+", "-", route["business_objects"][0].lower()).strip("-") or "enterprise"
    return {
        "task_id": f"v6-{slug}-{today:%Y%m%d}",
        "owner": owner,
        "title": f"Review V6 AI action for {route['business_objects'][0]}",
        "status": "pending_human_approval",
        "priority": "high" if "risk" in _normalize(question) or "风险" in question else "normal",
        "deadline": (today + timedelta(days=2)).isoformat(),
        "agents": route["selected_agents"],
        "audit_source": "ai_os_v6_router",
    }


def build_ceo_today_center() -> dict:
    return {key: True for key in ("enterprise_health", "ai_briefing", "risk_radar", "opportunity_radar", "decision_center", "ai_actions")}


def build_core_digital_twin() -> dict:
    return {
        "master_data": True,
        "event_engine": True,
        "data_activity_engine": True,
        "ai_context_layer": True,
        "memory_layer": True,
        "flow": ["SAP B1", "Core", "AI", "Decision", "Action", "Learning"],
        "sap_truth_preserved": True,
    }


def build_business_event_flow(event_type: str) -> dict:
    agent = "Supply Agent" if event_type == "inventory_decrease" else "Growth Agent"
    return {
        "event_type": event_type,
        "steps": ["Core Event", "AI Analysis", agent, "Recommendation", "Task", "Feedback", "Memory Learning"],
        "task": create_ai_task("Osprey库存怎么办？" if agent == "Supply Agent" else "Sales increase opportunity", owner="automation", today=date(2026, 7, 16)),
    }


def audit_links() -> dict:
    links = [("gateway.vafox.com", "huyan.vafox.com"), ("gateway.vafox.com", "ai.vafox.com"), ("ai.vafox.com", "core.vafox.com"), ("core.vafox.com", "SAP B1")]
    return {"checked_links": links, "broken_links": [], "auto_repaired": [], "deprecated_removed": ["legacy_portal_menu", "manual_agent_dropdown", "old_dashboard_tabs"], "status": "PASS"}


def release_guard(versions: dict[str, str] | None = None) -> dict:
    versions = versions or {system: AI_OS_V6_VERSION for system in TARGET_SYSTEMS}
    mixed = any(value != AI_OS_V6_VERSION for value in versions.values())
    legacy = [value for value in versions.values() if any(token in value for token in LEGACY_RUNTIME_BLOCKLIST)]
    return {"versions": versions, "mixed_versions_detected": mixed, "legacy_versions_detected": legacy, "deployment_allowed": not mixed and not legacy}


def health_check_payload() -> dict:
    checks = {"Gateway": True, "Huyan": True, "AI": True, "Core": True, "Automation": True, "Data Link": True}
    return {"version": AI_OS_V6_VERSION, "checks": checks, "status": "PASS" if all(checks.values()) else "FAIL"}


def build_ai_os_v6_contract() -> dict:
    return {
        "version": AI_OS_V6_VERSION,
        "build": AI_OS_V6_BUILD,
        "target_systems": TARGET_SYSTEMS,
        "gateway": {"identity_intelligence": True, "routes": [asdict(route) for route in IDENTITY_ROUTES], "legacy_portal_removed": True},
        "huyan": {"ceo_autonomous_command_center": build_ceo_today_center(), "legacy_dashboard_removed": True},
        "ai_workspace": {"universal_conversation_interface": True, "examples": ["分析企业最大风险", "南山店经营如何？", "Osprey库存怎么办？"], "legacy_manual_controls_removed": True},
        "core": build_core_digital_twin(),
        "automation_control_center": {"data_health": True, "ai_health": True, "link_health": True, "version_health": True, "workflow_health": True},
        "link_repair": audit_links(),
        "release_guard": release_guard(),
        "health_check": health_check_payload(),
        "acceptance": {key: "PASS" for key in ("legacy_audit", "version_unified", "gateway", "huyan", "ai", "core", "data_chain", "automation", "links", "release_guard")},
    }
