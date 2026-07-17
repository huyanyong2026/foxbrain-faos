"""FoxBrain Foundation V2.0 enterprise operating system contracts.

The module is intentionally declarative: it standardizes domains, security
boundaries, health checks, and rollout gates without changing SAP business
logic or rebuilding existing applications.
"""

from __future__ import annotations

from datetime import datetime, timezone

FOUNDATION_VERSION = "2.0"
DOMAINS = {
    "gateway": "gateway.vafox.com",
    "huyan": "huyan.vafox.com",
    "ai": "ai.vafox.com",
    "core": "core.vafox.com",
}
SAP_GUARDRAILS = (
    "SAP remains the business truth layer.",
    "AI and Huyan use Core read-only business APIs instead of direct SAP writes.",
    "Accounting and approval workflows are never bypassed.",
)
MASTER_DATA_MODELS = ("Product", "Brand", "Store", "Supplier", "Customer", "Employee", "Event")
EVENT_TYPES = ("Sales", "Inventory", "Purchase", "Customer", "Task", "Approval")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def gateway_policy_contract() -> dict:
    """Return the unified entry-layer contract for identity, permission, and routing."""
    return {
        "domain": DOMAINS["gateway"],
        "responsibility": "Unified Enterprise Entry Layer",
        "identity_roles": ["CEO", "Employee", "Store Manager", "Procurement", "Supplier", "Customer"],
        "rbac": {
            "CEO": ["enterprise.full_visibility"],
            "Procurement": ["supply_chain.read", "purchase.read", "supplier.read"],
            "Store Manager": ["store.own.read", "inventory.own_store.read"],
            "Supplier": ["brand.own.read", "supplier.portal.read"],
            "Customer": ["customer.own.read", "orders.own.read"],
        },
        "abac": {
            "store_scope": "store managers can access only assigned store ids",
            "brand_scope": "suppliers can access only approved brand ids",
            "customer_scope": "customers can access only their verified account",
        },
        "api_gateway": ["token_management", "api_routing", "rate_limiting", "audit_logging", "security_middleware"],
        "health_router": [DOMAINS["huyan"], DOMAINS["ai"], DOMAINS["core"]],
    }


def huyan_ceo_os_contract() -> dict:
    return {
        "domain": DOMAINS["huyan"],
        "responsibility": "CEO Operating System",
        "command_center": ["Sales", "Gross Margin", "Inventory", "Supply Chain Risk", "Business Health", "AI Recommendations"],
        "daily_briefing": ["What happened", "Why happened", "Recommended actions"],
        "risk_radar": ["Sales risk", "Inventory risk", "Supply risk", "Operation risk"],
        "decision_center": ["Problem", "Reason", "Recommendation", "Action"],
    }


def ai_workforce_contract() -> dict:
    agents = ["CEO Agent", "Supply Chain Agent", "Store Agent", "Finance Agent", "Growth Agent"]
    return {
        "domain": DOMAINS["ai"],
        "responsibility": "Digital Workforce Platform",
        "agent_registry": [{"name": name, "fields": ["purpose", "permission", "knowledge_source", "version", "status"]} for name in agents],
        "workspace": ["Chat", "Analysis", "Task", "Query", "Report generation"],
        "knowledge_connections": ["Enterprise documents", "Product data", "Brand data", "Outdoor knowledge", "Business knowledge"],
        "memory_system": ["User feedback", "Business experience", "Historical decisions"],
        "sap_write_policy": "forbidden",
    }


def core_digital_twin_contract() -> dict:
    return {
        "domain": DOMAINS["core"],
        "responsibility": "Enterprise Digital Twin Layer",
        "master_data_models": list(MASTER_DATA_MODELS),
        "event_engine": list(EVENT_TYPES),
        "business_api_consumers": [DOMAINS["ai"], DOMAINS["huyan"], DOMAINS["gateway"], "future_applications"],
        "data_governance": ["data_quality_check", "data_source_tracking", "audit_information"],
        "sap_access": "read_only_mirror_and_approved_business_api",
    }


def devops_release_contract() -> dict:
    return {
        "pipeline": ["Codex Cloud", "GitHub", "Automated Test", "Build", "Deploy", "Health Check", "Release"],
        "pre_deploy_gates": ["Backup", "Test environment verification", "Health check", "Rollback plan"],
        "rollback": {"required": True, "strategy": "redeploy previous artifact and restore verified backup when data changes are involved"},
    }


def foundation_v2_contract() -> dict:
    return {
        "version": FOUNDATION_VERSION,
        "generated_at": utc_now(),
        "architecture": [DOMAINS["gateway"], DOMAINS["huyan"], DOMAINS["ai"], DOMAINS["core"], "SAP B1"],
        "sap_guardrails": list(SAP_GUARDRAILS),
        "gateway": gateway_policy_contract(),
        "huyan": huyan_ceo_os_contract(),
        "ai": ai_workforce_contract(),
        "core": core_digital_twin_contract(),
        "devops": devops_release_contract(),
    }


def acceptance_matrix() -> dict:
    return {
        "Gateway": ["Authentication", "Routing", "Permission"],
        "Huyan": ["CEO Dashboard", "Risk Radar", "Daily Briefing"],
        "AI": ["Agent Registry", "Workspace", "Knowledge", "Memory"],
        "Core": ["Master Data", "Event Engine", "Business API"],
        "Security": ["RBAC", "ABAC", "Audit", "No direct SAP writes from AI"],
        "CI/CD": ["Automated Test", "Build", "Deploy", "Health Check"],
        "Rollback": ["Backup", "Previous artifact", "Health verification"],
    }
