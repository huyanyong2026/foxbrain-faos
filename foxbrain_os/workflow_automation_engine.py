"""FoxBrain OS Enterprise V1.8 workflow automation engine contracts."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class WorkflowNodeType:
    key: str
    name: str
    purpose: str
    approval_boundary: str


@dataclass(frozen=True)
class DigitalEmployeeRole:
    key: str
    name: str
    responsibilities: tuple[str, ...]
    tool_scope: tuple[str, ...]
    approval_rules: tuple[str, ...]
    performance_metrics: tuple[str, ...]


WORKFLOW_NODE_TYPES = (
    WorkflowNodeType("start", "Start", "Receive trigger or scheduled event", "safe"),
    WorkflowNodeType("condition", "Condition", "Check business threshold or rule", "safe"),
    WorkflowNodeType("ai_analysis", "AI Analysis", "Analyze SAP, knowledge and rules", "advice_only"),
    WorkflowNodeType("database_query", "Database Query", "Read persisted enterprise data", "readonly"),
    WorkflowNodeType("generate_report", "Generate Report", "Create report draft", "review_required"),
    WorkflowNodeType("send_notification", "Send Notification", "Notify responsible person", "review_or_policy_required"),
    WorkflowNodeType("human_approval", "Human Approval", "Wait for boss or manager decision", "mandatory_for_high_risk"),
    WorkflowNodeType("execute_action", "Execute Action", "Create approved task or internal workflow action", "approval_then_execute"),
    WorkflowNodeType("end", "End", "Record result and learning feedback", "audited"),
)


V18_DIGITAL_EMPLOYEES = (
    DigitalEmployeeRole(
        "ai_general_manager",
        "AI General Manager",
        ("daily business analysis", "problem discovery", "proposal creation", "task assignment", "result follow-up"),
        ("SAP readonly", "AI business center", "workflow center", "task center", "approval center"),
        ("high-risk actions require boss approval", "no SAP writeback"),
        ("problem discovery count", "task closure rate", "approval pass rate", "forecast accuracy"),
    ),
    DigitalEmployeeRole(
        "ai_purchase_manager",
        "AI Purchase Manager",
        ("inventory analysis", "purchase advice", "supplier analysis", "price risk detection"),
        ("SAP inventory", "purchase records", "supplier profiles", "risk engine"),
        ("purchase execution requires approval", "discount and price actions require approval"),
        ("inventory risk reduction", "purchase advice accuracy", "slow-moving follow-up rate"),
    ),
    DigitalEmployeeRole(
        "ai_sales_manager",
        "AI Sales Manager",
        ("store ranking", "employee performance", "sales opportunity", "campaign advice"),
        ("SAP sales", "store profiles", "employee profiles", "task center"),
        ("campaign execution and incentive changes require approval",),
        ("sales opportunity conversion", "store follow-up closure", "sales issue response time"),
    ),
    DigitalEmployeeRole(
        "ai_content_operator",
        "AI Content Operator",
        ("product introduction", "social content", "article draft", "campaign plan", "video script"),
        ("product knowledge", "content center", "brand rules", "approval center"),
        ("external publishing requires approval", "brand sensitive content requires review"),
        ("draft acceptance rate", "publishing approval rate", "content feedback quality"),
    ),
)


V18_DATA_TABLES = (
    "workflows",
    "workflow_nodes",
    "tasks",
    "task_logs",
    "approvals",
    "notifications",
    "ai_agents",
    "ai_memory",
    "decision_feedback",
    "business_cases",
)


V18_GUARDRAILS = {
    "compatibility_first": True,
    "database_persistence_required": True,
    "mobile_access_required": True,
    "permission_control_required": True,
    "high_risk_requires_human_approval": True,
    "ai_executes_workflow_only_with_approval": True,
    "sap_writeback_disabled": True,
}


def build_workflow_automation_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.8",
        "module": "workflow_automation_engine",
        "positioning": "AI workflow automation center",
        "closed_loop": [
            "ai_discovers_problem",
            "automatic_analysis",
            "automatic_task_creation",
            "automatic_notification",
            "human_approval",
            "execution_feedback",
            "ai_learning_optimization",
        ],
        "node_types": [asdict(node) for node in WORKFLOW_NODE_TYPES],
        "digital_employees": [asdict(role) for role in V18_DIGITAL_EMPLOYEES],
        "database_tables": list(V18_DATA_TABLES),
        "guardrails": dict(V18_GUARDRAILS),
    }


def build_inventory_warning_workflow() -> dict[str, Any]:
    nodes = [
        {"key": "start", "name": "SAP inventory sync", "type": "start"},
        {"key": "ai_inventory_analysis", "name": "AI inventory analysis", "type": "ai_analysis", "inputs": ["SAP inventory", "sales velocity", "inventory age"]},
        {"key": "condition_inventory_age", "name": "Inventory age over 180 days", "type": "condition", "rule": "inventory_age_days > 180"},
        {"key": "generate_plan", "name": "Generate handling plan", "type": "generate_report"},
        {"key": "notify_purchase_owner", "name": "Notify purchase owner", "type": "send_notification"},
        {"key": "boss_approval", "name": "Boss approval", "type": "human_approval", "required": True},
        {"key": "create_promotion_task", "name": "Create promotion task", "type": "execute_action", "requires_approval": True},
        {"key": "record_result", "name": "Record result", "type": "end"},
    ]
    return {
        "ok": True,
        "workflow_key": "inventory_warning_workflow",
        "name": "Inventory Warning Workflow",
        "trigger": "after_sap_inventory_sync",
        "nodes": nodes,
        "approval_required": True,
        "execution_rule": "analysis_and_task_draft_auto_generated_execution_after_human_approval",
    }


def build_ai_operating_task(problem: str, source: str = "risk_engine", owner: str = "store_manager") -> dict[str, Any]:
    title = (problem or "Review AI discovered business issue").strip()
    return {
        "ok": True,
        "task_name": title[:120],
        "source": source,
        "priority": "high",
        "owner": owner,
        "due_in_days": 3,
        "status": "pending_approval",
        "ai_advice": "Analyze SAP evidence, business context and operating rules before execution.",
        "execution_result": "",
        "approval_required": True,
    }


def build_notification_plan(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "channels_reserved": ["enterprise_wechat", "email", "sms", "app_push", "feishu", "dingtalk"],
        "default_channel": "in_app",
        "recipient_role": task.get("owner", "store_manager"),
        "title": "AI task requires review",
        "body": task.get("task_name", ""),
        "categories": ["sales_exception", "inventory_risk", "profit_drop", "purchase_reminder", "sap_sync_failure", "server_exception", "knowledge_update_done"],
        "approval_required": True,
    }


def build_decision_feedback_learning(advice: str, decision: str = "pending", result: str = "") -> dict[str, Any]:
    accuracy = "waiting_for_result" if not result else "needs_review"
    return {
        "ok": True,
        "ai_advice": advice,
        "boss_decision": decision,
        "actual_result": result,
        "accuracy_status": accuracy,
        "learning_rule": "approved_results_raise_similar_advice_weight_after_review",
        "approval_required": True,
    }


def build_business_case_template(title: str = "2026 Osprey price adjustment case") -> dict[str, Any]:
    return {
        "ok": True,
        "title": title,
        "case_type": "business_decision_case",
        "fields": ["historical_problem", "boss_decision", "execution_process", "final_result", "ai_reuse_rule"],
        "example": {
            "historical_problem": "Hong Kong price impact",
            "boss_decision": "Control discount around 62%",
            "execution_process": "Review brand rules, inventory age and gross margin before action",
            "final_result": "Sales change recorded after execution",
        },
        "knowledge_upgrade": "document_knowledge_base_to_enterprise_experience_base",
    }


def build_periodic_report_plan(period: str = "daily") -> dict[str, Any]:
    if period == "weekly":
        sections = ["sales trend", "inventory trend", "profit trend", "employee performance", "brand performance", "risk", "advice"]
        title = "AI business weekly report"
    elif period == "monthly":
        sections = ["sales trend", "inventory trend", "profit trend", "brand review", "board review", "shareholder review", "business recap"]
        title = "AI business monthly report"
    else:
        sections = ["yesterday business", "abnormal issues", "AI analysis", "today tasks", "boss focus items"]
        title = "FireFox daily business report"
    return {
        "ok": True,
        "period": period,
        "title": title,
        "schedule": "08:00 daily" if period == "daily" else "weekly" if period == "weekly" else "monthly",
        "sections": sections,
        "approval_required": True,
    }


def build_workflow_acceptance_plan(request_text: str) -> dict[str, Any]:
    return {
        "ok": True,
        "request": request_text,
        "workflow": [
            "call_sap",
            "analyze_inventory",
            "generate_risk",
            "create_task",
            "notify_owner",
            "wait_for_approval",
        ],
        "required_outputs": ["risk", "task", "notification", "approval_record"],
        "approval_required": True,
        "execution_status": "waiting_for_human_approval",
    }
