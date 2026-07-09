"""FoxBrain Enterprise Second Brain product specification contract."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ProductBook:
    key: str
    name: str
    purpose: str
    chapters: tuple[str, ...]


@dataclass(frozen=True)
class BrainEngine:
    key: str
    name: str
    purpose: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]


SECOND_BRAIN_PRINCIPLES = {
    "design_first_then_build": "Every feature enters the product specification before Codex implementation.",
    "one_enterprise_one_brain": "All knowledge, data, workflows and decisions converge into one enterprise brain.",
    "everything_is_an_object": "Stores, employees, brands, products, suppliers, customers, contracts, media, meetings, projects and tasks share a unified object model.",
    "everything_is_connected": "Objects are connected through relationship graphs instead of isolated menus.",
    "ai_first": "Every module has AI capability from the first day, not as a later add-on.",
    "knowledge_never_dies": "Meetings, policies, decisions and operating experience become reusable long-term enterprise assets.",
    "platform_after_firefox": "FireFox is the first complete landing case; the core must later become reusable platform capability.",
}


SECOND_BRAIN_LAYERS = (
    ("data", "Data", ("SAP", "POS", "Excel", "finance", "inventory", "sales", "customers")),
    ("knowledge", "Knowledge", ("PDF", "Word", "images", "videos", "training", "policies", "contracts", "AI summaries")),
    ("memory", "Memory", ("decision reasons", "price changes", "store changes", "inventory changes", "historical results")),
    ("reasoning", "Reasoning", ("profit analysis", "inventory risk", "product structure", "store suggestions")),
    ("action", "Action", ("daily report", "purchase suggestion", "content draft", "task creation", "owner reminders")),
)


SECOND_BRAIN_ENGINES = (
    BrainEngine(
        "object_engine",
        "Object Engine",
        "Unify all enterprise entities into one object model.",
        ("stores", "employees", "brands", "suppliers", "products", "contracts", "media", "customers", "projects", "meetings", "tasks"),
        ("object_profiles", "object_timeline", "object_permissions", "object_relationships"),
    ),
    BrainEngine(
        "knowledge_engine",
        "Knowledge Engine",
        "Turn SAP, documents, media, webpages and conversations into queryable knowledge.",
        ("SAP", "PDF", "Word", "Excel", "images", "videos", "meeting notes", "WeChat chats", "official accounts", "Douyin"),
        ("knowledge_cards", "summaries", "tags", "citations", "retrieval_context"),
    ),
    BrainEngine(
        "memory_engine",
        "Memory Engine",
        "Preserve why the enterprise made historical decisions and what happened afterward.",
        ("purchase decisions", "price changes", "store openings", "store closures", "promotions", "boss decisions"),
        ("decision_cases", "result_feedback", "experience_rules", "future_references"),
    ),
    BrainEngine(
        "decision_engine",
        "Decision Engine",
        "Analyze business questions with data, knowledge, memory and relationships.",
        ("sales", "gross_margin", "weather", "inventory", "employees", "brands", "historical_cases"),
        ("causes", "risks", "recommendations", "approval_boundaries", "action_options"),
    ),
    BrainEngine(
        "relationship_engine",
        "Relationship Engine",
        "Connect every object so AI understands enterprise context instead of searching isolated files.",
        ("objects", "transactions", "documents", "people", "media", "events", "tasks"),
        ("knowledge_graph", "related_objects", "impact_paths", "context_pack"),
    ),
)


PRODUCT_SPEC_BOOKS = (
    ProductBook("constitution", "01 Product Constitution", "Define what FoxBrain is and the principles for the next decade.", ("vision", "mission", "positioning", "core_principles", "enterprise_second_brain_model", "long_term_roadmap")),
    ProductBook("enterprise_architecture", "02 Enterprise Architecture", "Define the full technical and product architecture.", ("servers", "SAP", "databases", "vector_database", "graph", "AI_models", "Dify", "n8n", "permissions", "message_center")),
    ProductBook("data_architecture", "03 Data Architecture", "Define unified enterprise object data models.", ("Store", "Employee", "Customer", "Brand", "Supplier", "Product", "Inventory", "Sales", "Finance", "Knowledge", "Memory")),
    ProductBook("knowledge_engine", "04 Knowledge Engine", "Define the knowledge brain.", ("knowledge_base", "embedding", "tags", "classification", "full_text_search", "OCR", "PDF", "Word", "Excel", "images", "videos", "automatic_learning")),
    ProductBook("ai_agent_center", "05 AI Agent Center", "Define all enterprise AI agents.", ("CEO Agent", "Finance Agent", "HR Agent", "Marketing Agent", "Store Agent", "Inventory Agent", "Supplier Agent", "Brand Agent", "Customer Agent", "Knowledge Agent")),
    ProductBook("memory_engine", "06 Memory Engine", "Define enterprise memory and traceability.", ("meetings", "chats", "decisions", "contracts", "reasons", "history", "future_traceability")),
    ProductBook("decision_engine", "07 Decision Engine", "Define AI analysis flows.", ("sales_decline", "inventory_increase", "profit_drop", "analysis_process", "evidence", "recommendation")),
    ProductBook("content_center", "08 Content Center", "Define AI content generation and publishing center.", ("official_account", "video_account", "Douyin", "Xiaohongshu", "TikTok", "Facebook", "Instagram", "website")),
    ProductBook("sap_connector", "09 SAP Connector", "Define SAP synchronization architecture.", ("22:00_daily_sync", "sync_scope", "rules", "fields", "logs", "permissions", "failure_recovery")),
    ProductBook("ui_design_system", "10 UI Design System", "Define unified UI rules.", ("colors", "fonts", "buttons", "icons", "menus", "interaction", "dashboard", "AI_chat", "knowledge_base")),
    ProductBook("api_plugin", "11 API & Plugin", "Define integrations and extension rules.", ("WeChat", "Enterprise WeChat", "SAP", "OA", "Feishu", "DingTalk", "plugins", "API_governance")),
    ProductBook("codex_execution", "12 Codex Execution Standard", "Define how Codex implements future work.", ("directory_structure", "naming", "interfaces", "database", "development_rules", "testing", "deployment")),
)


SECOND_BRAIN_ROADMAP = (
    ("v1", "Enterprise Second Brain"),
    ("v2", "Knowledge Graph"),
    ("v3", "Memory Engine"),
    ("v4", "Decision Engine"),
    ("v5", "Enterprise Digital Twin"),
    ("v6", "Autonomous Enterprise"),
)


FIREFOX_LANDING_ROUTE = {
    "production_system": "SAP Business One stays stable as system of record.",
    "ai_data_server": "Sync SAP at 22:00 and start knowledge training at 22:30.",
    "owner_portal": "https://huyan.vafox.com is the AI portal and first landing case.",
    "future_platform": "https://ai.vafox.com becomes the reusable FoxBrain product platform.",
}


def build_enterprise_second_brain_contract() -> dict:
    return {
        "ok": True,
        "version": "FoxBrain Enterprise Second Brain V1.0",
        "positioning": "Enterprise AI Operating System",
        "mission": "Connect enterprise data, knowledge, experience, workflows, decisions and history into a continuously learning enterprise second brain.",
        "not": ["ERP", "OA", "CRM", "BI", "standalone knowledge base", "simple LLM chatbot"],
        "principles": dict(SECOND_BRAIN_PRINCIPLES),
        "layers": [{"key": key, "name": name, "sources": list(sources)} for key, name, sources in SECOND_BRAIN_LAYERS],
        "engines": [asdict(engine) for engine in SECOND_BRAIN_ENGINES],
        "product_spec_books": [asdict(book) for book in PRODUCT_SPEC_BOOKS],
        "roadmap": [{"key": key, "name": name} for key, name in SECOND_BRAIN_ROADMAP],
        "firefox_landing_route": dict(FIREFOX_LANDING_ROUTE),
        "codex_rule": "design_first_then_build_all_future_work_follows_the_product_specification",
    }
