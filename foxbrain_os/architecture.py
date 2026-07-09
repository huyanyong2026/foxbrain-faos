"""Enterprise V1.0 architecture contract for the gradual FoxBrain OS refactor.

The current production portal remains compatibility-first. This module defines
the target operating-system boundaries so code can migrate out of portal_v2.py
without losing existing routes, data, approvals or audit trails.
"""

from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class EnterpriseModule:
    key: str
    name: str
    layer: str
    owner: str
    source_of_truth: str
    api_prefix: str
    page_route: str
    risk_level: str
    approval_required: bool
    migration_status: str


@dataclass(frozen=True)
class UpgradePhase:
    phase: str
    name: str
    objective: str
    deliverables: tuple[str, ...]
    acceptance: tuple[str, ...]
    status: str


HIGH_RISK_ACTIONS = {
    "sap_writeback",
    "external_publish",
    "price_change",
    "contract_change",
    "finance_payment",
    "permission_change",
    "bulk_data_change",
    "plugin_install_high_risk",
    "api_policy_change",
    "tenant_data_change",
}


ENTERPRISE_MODULES = (
    EnterpriseModule("identity", "Identity and RBAC", "kernel", "platform", "users", "/api/security", "/settings", "high", True, "legacy_in_portal"),
    EnterpriseModule("sap", "SAP DataHub", "data", "datahub", "SAP B1", "/api/sap", "/sap-sync", "high", True, "service_contract_ready"),
    EnterpriseModule("knowledge", "Knowledge Platform", "knowledge", "knowledge", "knowledge_items", "/api/knowledge", "/knowledge", "medium", False, "service_contract_ready"),
    EnterpriseModule("knowledge_brain", "AI Knowledge Brain", "knowledge", "knowledge", "SAP_B1_and_knowledge_items", "/api/knowledge/brain", "/knowledge", "medium", False, "service_contract_ready"),
    EnterpriseModule("sap_knowledge_engine", "SAP Knowledge Engine", "knowledge", "datahub", "SAP_readonly_snapshots_and_ai_warehouse", "/api/sap-knowledge-engine", "/knowledge/sap", "high", True, "service_contract_ready"),
    EnterpriseModule("knowledge_training_quality", "Knowledge Training and Quality", "knowledge", "knowledge", "knowledge_items_memories_decision_memories_feedback", "/api/knowledge-quality", "/knowledge", "medium", True, "service_contract_ready"),
    EnterpriseModule("knowledge_fusion", "Knowledge Fusion Engine", "knowledge", "knowledge", "SAP_knowledge_external_industry_knowledge_boss_experience", "/api/knowledge/fusion", "/knowledge", "medium", True, "service_contract_ready"),
    EnterpriseModule("knowledge_training_rules_engine", "Knowledge Training Rules Engine", "knowledge", "knowledge", "fusion_knowledge_operating_rules_decision_guardrails", "/api/knowledge-training-engine", "/knowledge", "medium", True, "service_contract_ready"),
    EnterpriseModule("jarvis", "Jarvis AI Console", "ai", "ai_operations", "knowledge_and_sap", "/api/jarvis", "/jarvis", "medium", False, "legacy_in_portal"),
    EnterpriseModule("agents", "Digital Workforce", "ai", "ai_operations", "agent_roles", "/api/digital-workforce", "/digital-workforce", "high", True, "service_contract_ready"),
    EnterpriseModule("agent_orchestration", "AI Agent Orchestration", "ai", "ai_operations", "agent_roles_and_ai_operation_plans", "/api/agents/v1.2", "/agents/v1.2", "high", True, "service_contract_ready"),
    EnterpriseModule("multi_agent_system", "Multi-Agent Collaboration System", "ai", "ai_operations", "shared_SAP_knowledge_and_agent_roles", "/api/agents/v1.6", "/agents/v1.6", "high", True, "service_contract_ready"),
    EnterpriseModule("auto_operation_loop", "AI Auto Operation Loop", "operations", "operations", "SAP_B1_readonly_and_ai_operation_plans", "/api/auto-operation", "/auto-operation", "high", True, "service_contract_ready"),
    EnterpriseModule("ai_business_management_center", "AI Business Management Center", "ai", "operations", "SAP_knowledge_rules_forecasts_risks_approvals", "/api/decision/today", "/ai-business-center", "high", True, "service_contract_ready"),
    EnterpriseModule("workflow_automation_engine", "AI Workflow Automation Engine", "operations", "operations", "workflows_tasks_notifications_approvals_feedback_cases", "/api/workflow-automation", "/workflow-automation", "high", True, "service_contract_ready"),
    EnterpriseModule("enterprise_knowledge_graph", "Enterprise Knowledge Graph and AI Permissions", "knowledge", "platform", "entities_relations_kg_nodes_edges_ai_permissions", "/api/enterprise-knowledge-graph", "/enterprise-knowledge-graph", "high", True, "service_contract_ready"),
    EnterpriseModule("digital_twin_simulation", "Enterprise Digital Twin and Business Simulator", "strategy", "strategy", "digital_twin_models_business_scenarios_simulation_results", "/api/v2.1", "/ai-strategy-center", "high", True, "service_contract_ready"),
    EnterpriseModule("business_autopilot", "Autonomous Business Operation System", "operations", "operations", "business_health_alerts_actions_learning_rules", "/api/v2.2", "/business-autopilot", "high", True, "service_contract_ready"),
    EnterpriseModule("enterprise_ecosystem_hub", "Enterprise Ecosystem Integration Hub", "platform", "platform", "data_sources_sync_jobs_customer_profiles_channel_orders_content_assets_integration_logs", "/api/v2.3", "/ecosystem-hub", "high", True, "service_contract_ready"),
    EnterpriseModule("ux_information_architecture", "FoxBrain OS UX 2.0 Information Architecture", "platform", "product", "navigation_layers_and_user_experience_contract", "/api/ux", "/", "medium", False, "service_contract_ready"),
    EnterpriseModule("owner_enterprise_planning", "Owner OS and Enterprise OS Boundary Planning", "platform", "platform", "owner_private_data_enterprise_operations_sync_policy", "/api/owner-enterprise", "/owner-enterprise-plan", "high", True, "service_contract_ready"),
    EnterpriseModule("owner_os_foundation", "FoxBrain Owner OS V1 Foundation", "platform", "product", "owner_second_brain_master_blueprint", "/api/owner-os", "/", "high", True, "service_contract_ready"),
    EnterpriseModule("enterprise_second_brain", "FoxBrain Enterprise Second Brain V1.0", "platform", "product", "product_specification_baseline", "/api/second-brain", "/second-brain", "high", True, "service_contract_ready"),
    EnterpriseModule("approvals", "Approval Center", "governance", "operations", "approvals", "/api/approvals", "/approvals", "high", True, "legacy_in_portal"),
    EnterpriseModule("brain", "Enterprise Digital Brain", "ai", "strategy", "enterprise_digital_brain_recommendations", "/api/digital-brain", "/digital-brain", "high", True, "service_contract_ready"),
    EnterpriseModule("platform", "Enterprise AI Platform", "platform", "platform", "platform_plugins", "/api/enterprise-ai-platform", "/enterprise-ai-platform", "high", True, "service_contract_ready"),
    EnterpriseModule("monitoring", "Platform Monitoring", "operations", "operations", "system_logs", "/api/enterprise-ai-platform/monitoring", "/platform-monitoring", "medium", False, "service_contract_ready"),
)


ENTERPRISE_UPGRADE_PHASES = (
    UpgradePhase(
        "stage_0",
        "V6 structure audit",
        "Map the current codebase, dependencies, deployment scripts and risk boundaries before refactoring.",
        ("structure audit", "module inventory", "risk register", "compatibility rules"),
        ("portal_v2.py remains runnable", "current smoke tests pass", "migration boundaries documented"),
        "completed",
    ),
    UpgradePhase(
        "stage_1",
        "Architecture baseline",
        "Create Enterprise V1.0 module contracts and approval rules while keeping legacy routes stable.",
        ("architecture contract module", "platform architecture API", "stage result document", "smoke tests"),
        ("contract imports successfully", "API exposes module boundaries", "high-risk actions remain approval gated"),
        "in_progress",
    ),
    UpgradePhase(
        "stage_2",
        "Data and knowledge services",
        "Move SAP, knowledge and retrieval logic behind service modules with compatibility adapters.",
        ("sap data understanding", "AI knowledge brain", "SAP Knowledge Engine", "knowledge fusion engine", "knowledge training rules engine", "enterprise knowledge graph", "entity center", "AI permission engine", "operating rule library", "knowledge quality scoring", "AI learning plan", "boss experience memory", "adapter tests"),
        ("existing /api/sap and /api/knowledge responses stay compatible", "SAP stays source of truth", "knowledge brain cites SAP or knowledge sources", "fusion context combines SAP, external industry and boss experience sources", "AI decision logic follows reviewed FireFox operating rules", "entity relationships are queryable", "AI permissions isolate employee, manager and boss scopes", "SAP production database is not modified", "boss experience requires review before active memory"),
        "in_progress",
    ),
    UpgradePhase(
        "stage_3",
        "AI operations and digital workforce",
        "Move planner, approvals, digital employees and AI recommendations into governed services.",
        ("agent orchestration service", "multi-agent collaboration system", "shared SAP knowledge context", "business agent", "inventory agent", "product agent", "membership agent", "content agent", "approval service", "audit service"),
        ("high-risk operations cannot auto execute", "every AI action has role, scope and audit metadata", "all AI execution requests create approval plans first", "agents share SAP Knowledge Engine context", "AI business tasks call SAP sales, inventory, brand profiles and operating rules before advice"),
        "in_progress",
    ),
    UpgradePhase(
        "stage_4",
        "Platform observability and release hardening",
        "Add monitoring, module health, developer docs and deployment checks around the refactored services.",
        ("daily auto operation loop", "sap read-only sync contract", "boss daily report", "AI business management center", "workflow automation engine", "enterprise digital twin", "business simulator", "scenario engine", "prediction engine", "sales forecast", "inventory analysis", "risk engine", "AI advice approval center", "business memory", "task center connection", "approval flow connection", "decision feedback learning", "business case library", "UX 2.0 information architecture", "minimal home page contract", "module health checks"),
        ("SAP production server stays independent", "daily loop is approval gated", "AI advice history is persisted", "business forecasts and risks enter database tables", "AI workflow creates tasks notifications and approvals before execution", "simulations never modify production data", "strategy execution requires human approval", "production smoke tests pass", "release gate documents risk and rollback"),
        "in_progress",
    ),
)


def approval_required_for(action: str, risk_level: str = "") -> bool:
    normalized = (action or "").strip().lower()
    if normalized in HIGH_RISK_ACTIONS:
        return True
    return (risk_level or "").strip().lower() == "high"


def enterprise_v1_architecture_contract() -> dict:
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.0",
        "strategy": "compatibility_first_modular_refactor",
        "current_runtime": {
            "portal": "portal_v2.py",
            "sap_sync": "sync_sap_b1.py",
            "tests": "tests/v6_smoke_check.py",
            "deployment": "docker-compose.yml",
        },
        "layers": [
            "kernel",
            "data",
            "knowledge",
            "ai",
            "governance",
            "platform",
            "operations",
        ],
        "modules": [asdict(module) for module in ENTERPRISE_MODULES],
        "upgrade_phases": [asdict(phase) for phase in ENTERPRISE_UPGRADE_PHASES],
        "high_risk_actions": sorted(HIGH_RISK_ACTIONS),
        "rules": {
            "sap_source_of_truth": True,
            "do_not_delete_existing_capabilities": True,
            "legacy_routes_remain_compatible": True,
            "high_risk_actions_require_human_approval": True,
            "ai_outputs_must_be_explainable_traceable_auditable": True,
            "stage_results_required": True,
        },
    }


def module_keys(modules: Iterable[EnterpriseModule] = ENTERPRISE_MODULES) -> list[str]:
    return [module.key for module in modules]
