"""FoxBrain OS Enterprise V1.3 automatic operation loop contract."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class OperationLoopStage:
    key: str
    name: str
    owner: str
    source: str
    output: str
    route: str
    risk_level: str
    approval_required: bool


SAP_READ_ONLY_POLICY = {
    "sap_production_server_independent": True,
    "sync_mode": "read_only",
    "writeback_allowed": False,
    "credentials_location": "server_environment_only",
    "daily_schedule_env": "SAP_SYNC_TIME",
    "default_daily_schedule": "22:00",
}


AUTO_OPERATION_STAGES = (
    OperationLoopStage("sap_daily_sync", "SAP Daily Sync", "datahub", "SAP B1 read-only snapshot", "freshness and metrics", "/sap-sync", "high", True),
    OperationLoopStage("ai_analysis", "AI Analysis", "ai_operations", "SAP snapshot and knowledge brain", "explainable analysis", "/ai-operations", "medium", True),
    OperationLoopStage("boss_daily_report", "Boss Daily Report", "boss", "AI analysis and business cockpit", "daily briefing draft", "/ai-ceo", "medium", True),
    OperationLoopStage("task_center", "Task Center", "operations", "approved daily plan", "reviewable tasks", "/tasks", "medium", True),
    OperationLoopStage("approval_flow", "Approval Flow", "governance", "AI operation plans", "manual decision", "/approvals", "high", True),
)


def build_auto_operation_contract() -> dict:
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.3",
        "module": "auto_operation_loop",
        "strategy": "connect_existing_v1_0_to_v1_2_capabilities_without_rebuilding",
        "sap_read_only_policy": SAP_READ_ONLY_POLICY,
        "stages": [asdict(stage) for stage in AUTO_OPERATION_STAGES],
        "loop_rule": {
            "daily_loop_creates_reviewable_plan": True,
            "ai_execution_requires_approval": True,
            "high_risk_operations_must_not_auto_execute": True,
            "tasks_are_created_after_approval_or_manual_creation": True,
            "audit_required": True,
        },
        "integration_points": {
            "sap_status": "/api/sap/sync/status",
            "ai_analysis": "/api/ai-operations",
            "boss_daily_report": "/api/ai-ceo/daily-briefing",
            "task_center": "/api/tasks",
            "approval_flow": "/api/approvals",
        },
    }


def build_daily_loop_plan(sap_status: dict, ai_context: dict, briefing: dict, task_plan: dict, approvals: dict) -> dict:
    return {
        "ok": True,
        "version": "FoxBrain OS Enterprise V1.3",
        "plan_type": "daily_auto_operation_loop",
        "sap": {
            "freshness": sap_status.get("freshness"),
            "last_status": sap_status.get("last_status"),
            "last_sync_time": sap_status.get("last_sync_time"),
            "next_run_time": sap_status.get("next_run_time"),
            "read_only": True,
        },
        "ai_analysis": {
            "metrics": ai_context.get("metrics", {}),
            "risks": ai_context.get("active_risks", []),
            "rule": "analysis_only_until_approved",
        },
        "boss_daily_report": briefing,
        "task_plan": task_plan,
        "approvals": approvals,
        "approval_required": True,
        "approval_status": "pending_review",
        "execution_mode": "approval_then_execute",
        "execution_status": "blocked_manual_required",
        "risk_level": "high",
    }
