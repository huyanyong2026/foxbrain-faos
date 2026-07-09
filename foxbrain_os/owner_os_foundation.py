"""FoxBrain Owner OS V1 foundation and master blueprint contract."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class OwnerCenter:
    key: str
    name: str
    route: str
    purpose: str
    entries: tuple[str, ...]
    owner_only: bool = True


@dataclass(frozen=True)
class BlueprintDocument:
    key: str
    name: str
    role: str
    sections: tuple[str, ...]


OWNER_HOME_ENTRIES = (
    ("enterprise", "Enterprise", "/owner/enterprise"),
    ("assets", "Assets", "/owner/assets"),
    ("archive", "Archive", "/owner/archive"),
    ("knowledge", "Knowledge", "/owner/knowledge"),
    ("ai", "AI", "/jarvis"),
    ("decision", "Decision", "/owner/decision"),
    ("data", "Data", "/owner/data"),
    ("projects", "Projects", "/owner/projects"),
    ("strategy", "Strategy", "/owner/strategy"),
    ("system", "System", "/owner/system"),
)


OWNER_OS_CENTERS = (
    OwnerCenter("enterprise", "Enterprise Center", "/owner/enterprise", "Companies, stores, brands, suppliers, employees, equity and organization.", ("companies", "stores", "brands", "suppliers", "employees", "equity", "organization")),
    OwnerCenter("assets", "Asset Center", "/owner/assets", "Capital, trademarks, domains, servers, vehicles, equipment, fixed assets and intellectual property.", ("capital", "bank_accounts", "licenses", "trademarks", "domains", "servers", "vehicles", "fixed_assets", "intellectual_property")),
    OwnerCenter("archive", "Archive Center", "/owner/archive", "Company, store, brand, supplier, contract, meeting, historical photo and event archives.", ("company_archives", "store_archives", "brand_archives", "supplier_archives", "contracts", "meetings", "photos", "events")),
    OwnerCenter("knowledge", "Knowledge Center", "/owner/knowledge", "Policies, training, SOP, meeting minutes, Word, Excel, PDF, images and videos.", ("policies", "training", "sop", "meeting_minutes", "word", "excel", "pdf", "images", "videos")),
    OwnerCenter("ai", "AI Center", "/jarvis", "Unified owner AI entrance for asking questions about the enterprise.", ("owner_ai_chat", "recent_questions", "source_citations", "decision_context")),
    OwnerCenter("decision", "Decision Center", "/owner/decision", "Business cockpit, risk analysis, investment analysis and strategic planning.", ("business_cockpit", "risk_analysis", "investment_analysis", "strategy_planning", "ai_daily_report")),
    OwnerCenter("data", "Data Center", "/owner/data", "SAP sync database, business data warehouse, GraphRAG and knowledge graph.", ("sap_sync", "warehouse", "graphrag", "knowledge_graph", "data_quality")),
    OwnerCenter("project", "Project Center", "/owner/projects", "Flagship store, brand upgrade, renovation, VAFOX and FoxBrain projects.", ("flagship_store", "brand_upgrade", "renovation", "vafox", "foxbrain")),
    OwnerCenter("strategy", "Strategy Center", "/owner/strategy", "Three-year plan, five-year plan, organization, brand and investment planning.", ("three_year_plan", "five_year_plan", "organization_plan", "brand_plan", "investment_plan")),
    OwnerCenter("system", "System Center", "/owner/system", "Docker, GitHub, Codex, API, model management, sync, backup and logs.", ("docker", "github", "codex", "api", "model_management", "sync", "backup", "logs")),
)


BLUEPRINT_DOCUMENTS = (
    BlueprintDocument(
        "product_constitution",
        "FoxBrain Product Constitution",
        "The highest product philosophy and boundary document.",
        ("why_foxbrain_exists", "product_philosophy", "design_principles", "things_never_done", "owner_os_enterprise_os_sap_relationship", "ten_year_roadmap"),
    ),
    BlueprintDocument(
        "product_specification",
        "FoxBrain Product Specification",
        "The product design standard for all future Codex development.",
        ("information_architecture", "page_prototypes", "data_models", "permissions", "ai_design", "ui_rules", "api_rules"),
    ),
    BlueprintDocument(
        "technical_architecture",
        "FoxBrain Technical Architecture",
        "The technical architecture for services, deployment and data flows.",
        ("microservices", "docker", "github", "codex", "ci_cd", "data_sync", "warehouse", "mcp", "graphrag", "model_management"),
    ),
    BlueprintDocument(
        "development_handbook",
        "FoxBrain Development Handbook",
        "The Codex development handbook for consistent implementation.",
        ("coding_rules", "naming_rules", "database_migrations", "testing", "release", "git_rules", "pull_request_rules"),
    ),
)


OWNER_OS_PRODUCT_PRINCIPLES = {
    "not_erp": "Owner OS does not create sales orders, purchase orders or inventory transactions; SAP owns those records.",
    "not_oa": "Employee approvals, attendance, leave and routine execution belong to Enterprise OS.",
    "knowledge_first": "Every important object becomes an archive, summary, risk reminder, timeline and relationship node.",
    "relationship_first": "Stores, brands, assets, contracts, suppliers, employees, photos, videos, decisions and AI advice must connect as a graph.",
    "ai_default_entry": "The owner should ask questions directly instead of hunting menus; AI answers with evidence and limits.",
}


OWNER_OS_V1_BLUEPRINT_SECTIONS = (
    ("positioning", "Product positioning and design principles", ("owner_second_brain", "system_of_intelligence", "private_owner_database", "decision_ai")),
    ("information_architecture", "Owner OS information architecture", ("ten_centers", "tree_structure", "no_new_first_level_menus", "details_after_click")),
    ("data_models", "Core data models", ("companies", "stores", "assets", "contracts", "knowledge", "projects", "decisions")),
    ("page_prototypes", "Page prototypes and navigation", ("minimal_home", "center_pages", "entity_detail_pages", "ai_query_entry")),
    ("permissions", "Permission system", ("owner", "admin", "finance", "read_scope", "approval_scope")),
    ("sap_sync", "SAP read-only synchronization architecture", ("sap_b1_system_of_record", "sync_middle_platform", "warehouse", "no_direct_write")),
    ("ai_knowledge_flow", "AI knowledge base and query flow", ("question", "retrieve", "reason", "cite", "recommend", "approval_boundary")),
    ("technical_architecture", "Technical architecture and deployment rules", ("docker", "database", "api", "logs", "backup", "monitoring")),
    ("codex_development", "Codex development rules", ("compatibility_first", "tests_required", "docs_required", "stage_result_required")),
)


OWNER_OS_V1_DELIVERY_PLAN = (
    ("milestone_1", "Master Blueprint V1.0", "Complete the owner product blueprint before adding more pages."),
    ("milestone_2", "Owner OS Foundation", "Build ten stable centers with tree-structured navigation and private owner permissions."),
    ("milestone_3", "Knowledge Graph", "Connect SAP, contracts, stores, brands, assets, documents and decisions as relationships."),
    ("milestone_4", "AI Digital Brain", "Let AI understand the connected enterprise and answer owner questions directly."),
    ("milestone_5", "Automatic Operation", "Generate daily analysis, risks, opportunities and notifications after SAP sync."),
)


OWNER_OS_MILESTONES = (
    ("owner_os_v1_foundation", "Foundation", "Enterprise, asset, archive, knowledge and AI centers."),
    ("owner_os_v2_memory", "Memory", "Business memory, decision history and operating experience."),
    ("owner_os_v3_data", "Data", "SAP sync middle platform, data warehouse and knowledge graph."),
    ("enterprise_os", "Execution", "Move mature owner capabilities into ai.vafox.com for employee execution."),
)


SAP_INDEPENDENCE_PRINCIPLES = {
    "sap_is_system_of_record": True,
    "sap_stays_independent_server": True,
    "no_ai_installed_on_sap": True,
    "no_experiment_installed_on_sap": True,
    "default_sap_access_is_read_only": True,
    "sap_writeback_requires_human_approval": True,
    "owner_os_is_system_of_intelligence": True,
    "enterprise_os_is_system_of_execution": True,
}


def build_owner_home_contract() -> dict:
    return {
        "ok": True,
        "home_entries": [
            {"key": key, "name": name, "route": route}
            for key, name, route in OWNER_HOME_ENTRIES
        ],
        "policy": {
            "owner_home_has_ten_centers_only": True,
            "no_new_first_level_menus": True,
            "no_employee_entry_on_owner_home": True,
            "details_after_click_through": True,
        },
    }


def build_master_blueprint_contract() -> dict:
    return {
        "ok": True,
        "name": "FoxBrain Master Blueprint",
        "version": "Owner OS V1.0",
        "role": "single highest design standard for FoxBrain development",
        "documents": [asdict(doc) for doc in BLUEPRINT_DOCUMENTS],
        "product_principles": dict(OWNER_OS_PRODUCT_PRINCIPLES),
        "v1_blueprint_sections": [
            {"key": key, "name": name, "items": list(items)}
            for key, name, items in OWNER_OS_V1_BLUEPRINT_SECTIONS
        ],
        "delivery_plan": [
            {"key": key, "name": name, "goal": goal}
            for key, name, goal in OWNER_OS_V1_DELIVERY_PLAN
        ],
        "first_stage_delivery": [
            "product_positioning_and_design_principles",
            "owner_os_information_architecture",
            "core_data_models",
            "page_prototypes_and_navigation",
            "permission_system",
            "sap_sync_architecture",
            "ai_knowledge_query_flow",
            "technical_architecture_and_deployment_rules",
        ],
    }


def build_owner_os_foundation_contract() -> dict:
    return {
        "ok": True,
        "version": "FoxBrain Owner OS V1 Foundation",
        "module": "owner_os_foundation",
        "positioning": "owner_enterprise_second_brain_system_of_intelligence",
        "slogan": "FoxBrain Owner OS -- your enterprise second brain.",
        "domain": "huyan.vafox.com",
        "pause_enterprise_os_until_owner_os_foundation_ready": True,
        "current_priority": "complete_master_blueprint_v1_before_more_feature_pages",
        "home": build_owner_home_contract(),
        "centers": [asdict(center) for center in OWNER_OS_CENTERS],
        "master_blueprint": build_master_blueprint_contract(),
        "milestones": [
            {"key": key, "name": name, "goal": goal}
            for key, name, goal in OWNER_OS_MILESTONES
        ],
        "sap_principles": dict(SAP_INDEPENDENCE_PRINCIPLES),
        "relationship": {
            "sap": "System of Record",
            "owner_os": "System of Intelligence",
            "enterprise_os": "System of Execution",
        },
    }
