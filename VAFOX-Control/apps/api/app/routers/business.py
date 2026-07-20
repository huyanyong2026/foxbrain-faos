from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.orchestration import (ApprovalReceipt, DispatcherStage, Review,
                                       ReviewStatus, TaskResult,
                                       TaskResultSubmission)
from app.store import reviews, task_results

router = APIRouter(tags=["orchestrator-business"])


def review_for(result: TaskResult, review_status: ReviewStatus = ReviewStatus.PENDING,
               approved_at: datetime | None = None) -> Review:
    return Review(
        id=result.id, task_id=result.task_id, executor=result.executor,
        result_type=result.result_type, summary=result.summary,
        test_result=result.test_result, risk_level=result.risk_level,
        status=review_status, approval=review_status,
        created_at=result.created_at, approved_at=approved_at,
    )


@router.post("/results", response_model=TaskResult, status_code=status.HTTP_201_CREATED)
def report_result(request: TaskResultSubmission) -> TaskResult:
    """Record an externally produced result; V1 never invokes its executor."""
    result = task_results.create(TaskResult(**request.model_dump()))
    reviews.create(review_for(result))
    return result


@router.get("/results", response_model=list[TaskResult])
def list_results() -> list[TaskResult]:
    return sorted(task_results.list(), key=lambda item: item.created_at, reverse=True)


@router.get("/reviews", response_model=list[Review])
def list_reviews() -> list[Review]:
    return sorted(reviews.list(), key=lambda item: item.created_at, reverse=True)


@router.post("/reviews/{review_id}/approve", response_model=ApprovalReceipt)
def approve_review(review_id: UUID) -> ApprovalReceipt:
    review = reviews.get(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail=f"Review {review_id} was not found")
    if review.status == ReviewStatus.APPROVED:
        raise HTTPException(status_code=409, detail=f"Review {review_id} is already approved")

    approved_at = datetime.now(timezone.utc)
    updated = reviews.replace(review.model_copy(update={
        "status": ReviewStatus.APPROVED,
        "approval": ReviewStatus.APPROVED,
        "approved_at": approved_at,
    }))
    return ApprovalReceipt(id=updated.id, status=updated.status,
                           approval=updated.approval, approved_at=approved_at)


@router.get("/dispatcher", response_model=list[DispatcherStage])
def dispatcher_design() -> list[DispatcherStage]:
    """Expose the future Task → Executor → Result design without dispatching."""
    return [
        DispatcherStage(name="task", responsibility="Select a registered task",
                        phase_one_behavior="management-only; no task is started"),
        DispatcherStage(name="executor", responsibility="Route to Codex, WorkBuddy, or Marvis",
                        phase_one_behavior="design-only; no external agent is called"),
        DispatcherStage(name="result", responsibility="Collect a typed TaskResult for CTO review",
                        phase_one_behavior="accept submitted management metadata only"),
    ]
