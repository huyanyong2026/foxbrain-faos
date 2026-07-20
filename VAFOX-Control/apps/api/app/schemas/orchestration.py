"""Business-layer contracts for managed agent work results.

These contracts describe reported work only.  They deliberately contain no
client, credential, callback, or execution command for an external agent.
"""
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Executor(StrEnum):
    CODEX = "codex"
    WORKBUDDY = "workbuddy"
    MARVIS = "marvis"


class ResultType(StrEnum):
    CODEX_PR = "codex_pr"
    DEPLOYMENT_REPORT = "deployment_report"
    STATUS_REPORT = "status_report"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReviewStatus(StrEnum):
    PENDING = "pending_review"
    APPROVED = "approved"


class TestResult(StrEnum):
    NOT_RUN = "not_run"
    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"


class TaskResultSubmission(BaseModel):
    task_id: str = Field(min_length=1, max_length=128)
    executor: Executor
    result_type: ResultType
    summary: str = Field(min_length=1, max_length=2_000)
    artifact_url: HttpUrl | None = None
    log_url: HttpUrl | None = None
    test_result: TestResult = TestResult.NOT_RUN
    risk_level: RiskLevel = RiskLevel.MEDIUM


class TaskResult(TaskResultSubmission):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=utc_now)


class Review(BaseModel):
    """CTO review projection over a submitted result, not an execution order."""

    id: UUID
    task_id: str
    executor: Executor
    result_type: ResultType
    summary: str
    test_result: TestResult
    risk_level: RiskLevel
    status: ReviewStatus = ReviewStatus.PENDING
    approval: ReviewStatus = ReviewStatus.PENDING
    created_at: datetime
    approved_at: datetime | None = None


class ApprovalReceipt(BaseModel):
    id: UUID
    status: ReviewStatus
    approval: ReviewStatus
    approved_at: datetime


class DispatcherStage(BaseModel):
    name: str
    responsibility: str
    phase_one_behavior: str
