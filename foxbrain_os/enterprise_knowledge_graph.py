"""FoxBrain OS Enterprise V1.9 knowledge graph and AI permission contracts."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class EntityModel:
    key: str
    name: str
    fields: tuple[str, ...]
    relations: tuple[str, ...]


@dataclass(frozen=True)
class AiPermissionRole:
    key: str
    name: str
    data_scope: tuple[str, ...]
    tool_scope: tuple[str, ...]
    approval_rule: str


ENTERPRISE_ENTITY_MODELS = (
    EntityModel("company", "Company", ("company_name", "organization", "goals", "history", "strategy"), ("stores", "brands", "suppliers", "employees")),
    EntityModel("store", "Store", ("address", "area", "rent", "targets"), ("employees", "sales", "inventory", "brands", "customers", "activities")),
    EntityModel("employee", "Employee", ("position", "hire_date", "sales_history", "training", "contribution"), ("store", "brand", "customers", "tasks")),
    EntityModel("brand", "Brand", ("supplier", "market_info", "sales", "inventory", "profit"), ("products", "supplier", "stores", "customers")),
    EntityModel("product", "Product", ("brand", "supplier", "sales_records", "inventory", "reviews"), ("brand", "supplier", "customers", "orders")),
    EntityModel("supplier", "Supplier", ("contracts", "delivery", "payment", "brand_scope"), ("brands", "products", "contracts")),
    EntityModel("customer", "Customer", ("profile", "purchase_history", "points", "preferences"), ("store", "employee", "products", "activities")),
)


AI_PERMISSION_ROLES = (
    AiPermissionRole("ai_chairman_assistant", "AI Chairman Assistant", ("sap", "finance", "purchase", "inventory", "people", "strategy"), ("read_all", "briefing", "risk_alert", "meeting_prep"), "all_high_risk_requires_boss_approval"),
    AiPermissionRole("ai_general_manager", "AI General Manager", ("business", "sales", "stores", "tasks"), ("analysis", "task_assignment", "workflow", "approval_request"), "business_execution_requires_approval"),
    AiPermissionRole("ai_finance_manager", "AI Finance Manager", ("finance", "profit", "cash_flow", "expense", "budget"), ("profit_analysis", "budget_review", "risk_alert"), "finance_actions_require_approval"),
    AiPermissionRole("ai_purchase_manager", "AI Purchase Manager", ("purchase", "inventory", "supplier", "brand"), ("purchase_advice", "inventory_optimization", "supplier_analysis"), "purchase_execution_requires_approval"),
    AiPermissionRole("ai_sales_manager", "AI Sales Manager", ("sales", "employees", "stores", "customers"), ("sales_ranking", "employee_coaching", "campaign_advice"), "campaign_and_incentive_changes_require_approval"),
    AiPermissionRole("ai_content_operator", "AI Content Operator", ("brand_materials", "products", "content"), ("xiaohongshu", "wechat_article", "video_script", "campaign_content"), "external_publishing_requires_approval"),
    AiPermissionRole("employee_ai_assistant", "Employee AI Assistant", ("own_sales", "own_members", "own_commission", "own_training"), ("self_query", "training_guidance"), "employee_sees_own_scope_only"),
    AiPermissionRole("customer_ai_assistant", "Customer AI Assistant", ("customer_profile", "purchase_history", "points", "preferences"), ("customer_query", "product_recommendation", "points_help"), "customer_sees_own_scope_only"),
)


V19_DATA_TABLES = (
    "entities",
    "entity_relations",
    "knowledge_graph_nodes",
    "knowledge_graph_edges",
    "digital_employees",
    "ai_permissions",
    "employee_ai_profiles",
    "customer_ai_profiles",
    "business_relationships",
)


V19_GUARDRAILS = {
    "compatibility_first": True,
    "sap_compatible": True,
    "knowledge_center_compatible": True,
    "workflow_compatible": True,
    "permission_isolation_required": True,
    "database_persistence_required": True,
    "mobile_access_required": True,
    "kg_builder_schedule": "02:30 daily",
}


def build_enterprise_knowledge_graph_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.9",
        "module": "enterprise_knowledge_graph",
        "positioning": "enterprise relationship understanding and AI permission foundation",
        "entity_models": [asdict(model) for model in ENTERPRISE_ENTITY_MODELS],
        "permission_roles": [asdict(role) for role in AI_PERMISSION_ROLES],
        "database_tables": list(V19_DATA_TABLES),
        "guardrails": dict(V19_GUARDRAILS),
        "graph_flow": ["enterprise_entities", "entity_relations", "knowledge_graph", "ai_permission_engine", "role_ai_collaboration", "business_closed_loop"],
    }


def build_kg_builder_plan() -> dict[str, Any]:
    return {
        "ok": True,
        "schedule": "02:30 daily",
        "steps": ["scan_sap", "scan_knowledge_base", "scan_files", "scan_task_records", "update_enterprise_knowledge_graph"],
        "sources": ["SAP readonly", "Knowledge Center", "uploaded files", "tasks", "workflows", "business cases"],
        "outputs": ["entities", "entity_relations", "knowledge_graph_nodes", "knowledge_graph_edges", "business_relationships"],
        "approval_required_for_writeback": True,
        "sap_writeback": False,
    }


def build_relationship_query_plan(question: str) -> dict[str, Any]:
    q = (question or "").strip()
    if "Kailas" in q or "kailas" in q.lower():
        chain = ["Nanshan Store", "Kailas Brand", "employees", "products", "activities", "sales data", "customer feedback"]
        output = {
            "main_reasons": ["new employee training improved", "hero products fit Shenzhen market", "weekend campaign increased traffic"],
            "suggestion": "continue and expand the same strategy after manager review",
        }
    elif "库存" in q:
        chain = ["SAP inventory", "sales trend", "brand profiles", "purchase records", "market knowledge", "boss rules"]
        output = {"required_output": ["risk", "cause", "suggestion", "execution_task"]}
    else:
        chain = ["company", "store", "brand", "employee", "product", "customer", "sales"]
        output = {"required_output": ["relationship", "reason", "suggestion"]}
    return {
        "ok": True,
        "question": q,
        "relationship_chain": chain,
        "output": output,
        "permission_check_required": True,
        "sources": ["knowledge_graph_nodes", "knowledge_graph_edges", "SAP readonly", "knowledge_center", "workflow_records"],
    }


def build_employee_fit_analysis(role_or_brand: str = "Kailas") -> dict[str, Any]:
    return {
        "ok": True,
        "target": role_or_brand,
        "analysis_inputs": ["sales_history", "product_knowledge", "customer_feedback", "training_records"],
        "recommendation": {
            "employee": "best_fit_employee_requires_real_sap_and_hr_data",
            "reason": "rank by sales contribution, product knowledge, training completion and customer feedback",
            "approval_required": True,
        },
    }


def build_ai_permission_matrix(user_role: str = "boss") -> dict[str, Any]:
    role = (user_role or "employee").lower()
    scopes = {
        "employee": ["own_sales", "own_members", "own_commission", "own_training"],
        "store_manager": ["store_sales", "store_employees", "inventory", "members"],
        "boss": ["sap", "finance", "purchase", "inventory", "people"],
        "admin": ["sap", "finance", "purchase", "inventory", "people", "permissions"],
    }
    return {
        "ok": True,
        "user_role": role,
        "data_scope": scopes.get(role, scopes["employee"]),
        "permission_rule": "least_privilege_role_based_ai_access",
        "high_risk_requires_approval": True,
    }


def build_customer_ai_profile_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "assistant": "AI Customer Assistant",
        "connected_data": ["customer profile", "purchase history", "points", "activities", "product preferences"],
        "supported_questions": ["my points", "my purchase records", "recommended equipment", "points redemption"],
        "permission_rule": "customer_can_only_access_own_profile",
    }


def build_employee_ai_profile_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "assistant": "Employee AI Assistant",
        "connected_data": ["own sales", "own commission", "own target", "own training"],
        "guidance": {"weakness_example": "jacket sales insufficient", "suggestion": "learn three product knowledge items"},
        "permission_rule": "employee_can_only_access_own_profile",
    }


def build_business_map_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "map": "business_cockpit_map",
        "dimensions": ["stores", "sales", "inventory", "employees", "brands"],
        "example": [{"store": "Nanshan", "trend": "up"}, {"store": "Zhenxing", "trend": "down"}, {"store": "Hangyuan", "trend": "flat"}],
        "mobile_ready": True,
    }
