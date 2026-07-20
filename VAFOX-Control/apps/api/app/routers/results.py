"""Result intake and explicit CTO review endpoints.

These routes are metadata-only. In particular, no route invokes an external
agent or changes the state of an external system.
"""
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.registry import ResultApprovalStatus, TaskResult, TaskResultSubmission
from app.store import results

router = APIRouter(tags=["results"])


def require_result(result_id: UUID) -> TaskResult:
    result = results.get(result_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Result {result_id} was not found")
    return result


@router.post("/results", response_model=TaskResult, status_code=status.HTTP_201_CREATED)
def submit_result(request: TaskResultSubmission) -> TaskResult:
    """Record a submitted result and place it in the CTO review queue."""
    return results.create(TaskResult(**request.model_dump()))


@router.get("/results", response_model=list[TaskResult])
def list_results() -> list[TaskResult]:
    return sorted(results.list(), key=lambda result: result.created_at, reverse=True)


@router.get("/tasks/{task_id}/results", response_model=list[TaskResult])
def list_task_results(task_id: UUID) -> list[TaskResult]:
    return sorted(
        (result for result in results.list() if result.task_id == task_id),
        key=lambda result: result.created_at,
        reverse=True,
    )


@router.post("/results/{result_id}/approve", response_model=TaskResult)
def approve_result(result_id: UUID) -> TaskResult:
    """Apply the explicit CTO decision that completes a submitted result."""
    result = require_result(result_id)
    if result.approval_status == ResultApprovalStatus.CTO_APPROVED:
        return result
    return results.replace(
        result.model_copy(update={"approval_status": ResultApprovalStatus.CTO_APPROVED})
    )
