"""FoxBrain dual-system planning contract for Owner OS and Enterprise OS."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SystemBoundary:
    key: str
    domain: str
    name: str
    positioning: str
    primary_users: tuple[str, ...]
    core_modules: tuple[str, ...]
    data_scope: tuple[str, ...]


@dataclass(frozen=True)
class SyncDomain:
    key: str
    name: str
    direction: str
    policy: str
    approval_required: bool


OWNER_ENTERPRISE_SYSTEMS = (
    SystemBoundary(
        "owner_os",
        "huyan.vafox.com",
        "FoxBrain Owner OS",
        "Owner private enterprise brain for assets, knowledge, decisions and high-permission management.",
        ("owner", "boss"),
        (
            "personal_business_brain",
            "private_asset_database",
            "company_structure_library",
            "license_contract_archive",
            "trademark_brand_library",
            "capital_management",
            "store_asset_library",
            "decision_ai_assistant",
        ),
        (
            "business_licenses",
            "company_structure",
            "equity_relationships",
            "capital_accounts",
            "registered_trademarks",
            "rental_contracts",
            "utilities",
            "supplier_contracts",
            "important_meetings",
            "historical_decisions",
            "owner_operating_notes",
        ),
    ),
    SystemBoundary(
        "enterprise_os",
        "ai.vafox.com",
        "FoxBrain Enterprise OS",
        "Employee-facing enterprise operations and collaboration system.",
        ("boss", "finance", "store_manager", "employee", "operations"),
        (
            "enterprise_management_platform",
            "employee_workspace",
            "store_operations",
            "member_points",
            "enterprise_wechat",
            "training",
            "supplier_collaboration",
            "content_promotion",
            "ai_business_assistant",
        ),
        (
            "stores",
            "employees",
            "payroll_commission",
            "training",
            "sales",
            "members",
            "points_redemption",
            "supplier_collaboration",
            "wecom_groups",
            "mini_program",
            "official_account",
            "campaigns",
            "daily_reports",
            "task_collaboration",
        ),
    ),
)


SYNC_ALLOWED_DOMAINS = (
    SyncDomain("stores", "Store profile data", "owner_to_enterprise", "summary_sync", False),
    SyncDomain("brands", "Brand profile data", "owner_to_enterprise", "summary_sync", False),
    SyncDomain("suppliers", "Supplier profile data", "owner_to_enterprise", "summary_sync", False),
    SyncDomain("contract_summaries", "Contract summaries", "owner_to_enterprise", "summary_only_no_original_files", True),
    SyncDomain("employee_basic", "Employee basic profile", "bidirectional", "minimum_required_fields", True),
    SyncDomain("member_summary", "Member operating summary", "enterprise_to_owner", "aggregated_summary", False),
    SyncDomain("sales_operations", "Sales operating data", "enterprise_to_owner", "aggregated_or_permissioned_detail", False),
    SyncDomain("rent_fee_summary", "Rent and fee summary", "bidirectional", "summary_sync", True),
    SyncDomain("inventory_sales_analysis", "Inventory and sales analysis", "enterprise_to_owner", "analysis_only", False),
    SyncDomain("training_policy", "Training policy", "owner_to_enterprise", "approved_policy_only", True),
)


SYNC_BLOCKED_DOMAINS = (
    "personal_capital",
    "equity_structure",
    "family_company",
    "firewall_company",
    "core_contract_original_files",
    "sensitive_finance_documents",
    "executive_decision_records",
    "owner_operating_notes",
)


ROLE_BOUNDARIES = {
    "owner": ("owner_os_full", "enterprise_os_full_review"),
    "finance": ("finance_summary", "rent_fee_summary", "payroll_review"),
    "store_manager": ("own_store_operations", "employee_basic", "member_operations"),
    "employee": ("own_tasks", "own_training", "own_sales", "approved_knowledge"),
    "customer": ("own_profile", "own_points", "approved_customer_service"),
}


DATA_MIDDLE_PLATFORM_FLOW = (
    "SAP independent server keeps original operating data",
    "Nightly read-only sync",
    "Data middle platform cleans sales, inventory, members, products, employees and suppliers",
    "Owner OS receives decision, asset, contract and structure views",
    "Enterprise OS receives store, employee, member, WeCom and promotion views",
)


def classify_data_domain(domain_key: str) -> dict:
    normalized = (domain_key or "").strip().lower()
    allowed = {item.key: item for item in SYNC_ALLOWED_DOMAINS}
    if normalized in allowed:
        item = allowed[normalized]
        return {
            "ok": True,
            "domain": normalized,
            "sync_allowed": True,
            "policy": item.policy,
            "approval_required": item.approval_required,
            "direction": item.direction,
        }
    if normalized in SYNC_BLOCKED_DOMAINS:
        return {
            "ok": True,
            "domain": normalized,
            "sync_allowed": False,
            "policy": "blocked_never_sync_between_owner_and_enterprise",
            "approval_required": True,
            "direction": "none",
        }
    return {
        "ok": False,
        "domain": normalized,
        "sync_allowed": False,
        "policy": "unknown_domain_requires_architecture_review",
        "approval_required": True,
        "direction": "none",
    }


def build_sync_policy() -> dict:
    return {
        "ok": True,
        "allowed_domains": [asdict(item) for item in SYNC_ALLOWED_DOMAINS],
        "blocked_domains": list(SYNC_BLOCKED_DOMAINS),
        "role_boundaries": dict(ROLE_BOUNDARIES),
        "rules": {
            "not_fully_connected": True,
            "partial_sync_only": True,
            "sensitive_owner_data_never_syncs_to_employee_system": True,
            "contract_original_files_never_sync": True,
            "high_risk_permission_changes_require_human_approval": True,
        },
    }


def build_owner_enterprise_planning_contract() -> dict:
    return {
        "ok": True,
        "version": "FoxBrain Owner/Enterprise OS 7.9",
        "module": "owner_enterprise_planning",
        "strategy": "one_private_owner_system_one_employee_enterprise_system",
        "systems": [asdict(system) for system in OWNER_ENTERPRISE_SYSTEMS],
        "data_middle_platform_flow": list(DATA_MIDDLE_PLATFORM_FLOW),
        "sync_policy": build_sync_policy(),
        "development_priority": [
            "rebuild_huyan_vafox_as_owner_private_knowledge_and_asset_database",
            "keep_ai_vafox_as_employee_enterprise_operations_system",
            "establish_data_sync_rules",
            "establish_role_permission_boundaries",
            "then_connect_sap_wecom_mini_program_and_official_account",
        ],
        "conclusion": {
            "huyan.vafox.com": "FoxBrain Owner OS",
            "ai.vafox.com": "FoxBrain Enterprise OS",
        },
    }
