"""FoxBrain OS Enterprise V1.4 SAP Knowledge Engine contracts."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ReadOnlySyncLayer:
    key: str
    name: str
    source: str
    target: str
    sync_mode: str
    schedule: str
    writeback_allowed: bool
    audit_source: str


@dataclass(frozen=True)
class AiWarehouseDataset:
    key: str
    name: str
    source_tables: tuple[str, ...]
    warehouse_tables: tuple[str, ...]
    grain: str
    refresh_policy: str
    pii_level: str


@dataclass(frozen=True)
class SapKnowledgeModel:
    key: str
    name: str
    entity: str
    primary_sources: tuple[str, ...]
    facts: tuple[str, ...]
    relationships: tuple[str, ...]
    ai_use_cases: tuple[str, ...]
    approval_required_for: tuple[str, ...]


SAP_PRODUCTION_BOUNDARY = {
    "sap_production_server_independent": True,
    "direct_production_write_disabled": True,
    "read_only_sync_only": True,
    "no_sap_schema_change": True,
    "credentials_in_server_environment_only": True,
    "ai_warehouse_is_downstream_copy": True,
}


READ_ONLY_SYNC_LAYERS = (
    ReadOnlySyncLayer("sap_products", "SAP Product Read Layer", "SAP B1 item master", "ai_warehouse.products", "read_only_incremental", "daily_or_manual", False, "sap_sync_history"),
    ReadOnlySyncLayer("sap_sales", "SAP Sales Read Layer", "SAP B1 sales documents", "ai_warehouse.sales", "read_only_incremental", "daily_or_manual", False, "sap_sync_history"),
    ReadOnlySyncLayer("sap_inventory", "SAP Inventory Read Layer", "SAP B1 stock by warehouse", "ai_warehouse.inventory", "read_only_incremental", "daily_or_manual", False, "sap_sync_history"),
    ReadOnlySyncLayer("sap_members", "SAP Member Read Layer", "SAP B1 business partners", "ai_warehouse.members", "read_only_incremental", "daily_or_manual", False, "sap_sync_history"),
)


AI_WAREHOUSE_DATASETS = (
    AiWarehouseDataset("products", "Product Warehouse", ("sap_items", "products", "brands"), ("products", "sap_knowledge_snapshots"), "product_sku", "after_sap_sync", "internal"),
    AiWarehouseDataset("sales", "Sales Warehouse", ("sap_daily_sales_summary", "sap_store_sales_summary", "sales_orders", "sales_order_items"), ("sales_orders", "sales_order_items"), "day_store_product", "after_sap_sync", "internal"),
    AiWarehouseDataset("inventory", "Inventory Warehouse", ("sap_stock_by_whs", "inventory"), ("inventory", "inventory_decision_risks"), "store_product_day", "after_sap_sync", "internal"),
    AiWarehouseDataset("members", "Member Warehouse", ("sap_customers", "customers", "customer_segments"), ("customers", "customer_segments", "customer_followups"), "member", "after_sap_sync", "sensitive"),
)


SAP_KNOWLEDGE_MODELS = (
    SapKnowledgeModel(
        "product_knowledge_model",
        "Product Knowledge Model",
        "product",
        ("sap_items", "products", "brands", "sap_knowledge_snapshots"),
        ("sku", "brand", "category", "season", "price_band", "sales_context", "inventory_context"),
        ("brand", "supplier", "store_inventory", "sales_history"),
        ("sales_script", "product_portfolio", "replenishment_review", "content_draft"),
        ("price_change", "external_publish", "bulk_product_update"),
    ),
    SapKnowledgeModel(
        "sales_knowledge_model",
        "Sales Knowledge Model",
        "sales",
        ("sap_daily_sales_summary", "sap_store_sales_summary", "sales_orders", "sales_order_items"),
        ("sales_amount", "gross_profit", "gross_margin", "store", "brand", "product", "period"),
        ("store", "product", "customer", "campaign"),
        ("boss_daily_report", "store_review", "growth_analysis", "risk_alert"),
        ("target_change", "commission_change", "finance_decision"),
    ),
    SapKnowledgeModel(
        "inventory_knowledge_model",
        "Inventory Knowledge Model",
        "inventory",
        ("sap_stock_by_whs", "inventory", "inventory_decision_risks"),
        ("on_hand", "committed", "available", "avg_price", "inventory_amount", "aging", "risk_level"),
        ("product", "store", "brand", "supplier"),
        ("inventory_risk", "transfer_suggestion", "replenishment_review", "markdown_review"),
        ("markdown", "transfer_execution", "purchase_order", "sap_writeback"),
    ),
    SapKnowledgeModel(
        "member_knowledge_model",
        "Member Knowledge Model",
        "member",
        ("sap_customers", "customers", "customer_segments", "customer_followups"),
        ("member_id", "level", "purchase_history", "preferences", "points", "last_purchase", "privacy_boundary"),
        ("store", "sales_history", "followup_task", "campaign"),
        ("member_segmentation", "private_domain_followup", "service_prompt", "churn_review"),
        ("mass_notification", "external_publish", "privacy_sensitive_export"),
    ),
)


def build_sap_knowledge_engine_contract() -> dict:
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.4",
        "module": "sap_knowledge_engine",
        "strategy": "build_read_only_sync_layer_ai_warehouse_and_business_knowledge_models",
        "production_boundary": SAP_PRODUCTION_BOUNDARY,
        "read_only_sync_layers": [asdict(layer) for layer in READ_ONLY_SYNC_LAYERS],
        "ai_data_warehouse": [asdict(dataset) for dataset in AI_WAREHOUSE_DATASETS],
        "knowledge_models": [asdict(model) for model in SAP_KNOWLEDGE_MODELS],
        "rules": {
            "do_not_directly_connect_modify_sap_production_database": True,
            "sap_is_source_of_truth": True,
            "ai_reads_downstream_warehouse_or_snapshots": True,
            "missing_sap_data_must_show_limitation": True,
            "high_risk_actions_require_human_approval": True,
        },
    }


def build_warehouse_readiness(sync_status: dict, sap_knowledge_metrics: dict | None = None) -> dict:
    sap_knowledge_metrics = sap_knowledge_metrics or {}
    freshness = sync_status.get("freshness") or "unknown"
    datasets = []
    for dataset in AI_WAREHOUSE_DATASETS:
        ready = freshness in ("fresh", "ok", "success") or int(sap_knowledge_metrics.get("sap_knowledge_items") or 0) > 0
        datasets.append({
            **asdict(dataset),
            "readiness": "ready" if ready else "waiting_for_read_only_sync",
            "source_policy": "read_from_downstream_copy_not_sap_production",
        })
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.4",
        "sap_freshness": freshness,
        "warehouse_boundary": SAP_PRODUCTION_BOUNDARY,
        "datasets": datasets,
    }


def build_model_catalog(model_key: str = "") -> dict:
    models = [asdict(model) for model in SAP_KNOWLEDGE_MODELS]
    normalized = (model_key or "").strip().lower()
    if normalized:
        models = [model for model in models if model["key"] == normalized or model["entity"] == normalized]
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.4",
        "models": models,
        "model_count": len(models),
        "approval_boundary": "models_can_recommend_but_must_not_write_sap_or_execute_high_risk_actions",
    }
