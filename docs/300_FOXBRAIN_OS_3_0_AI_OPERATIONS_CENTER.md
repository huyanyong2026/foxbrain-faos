# FoxBrain OS 3.0 AI Operations Center

## Purpose

FoxBrain OS 3.0 adds an AI Operations Center on top of the 1.0 release baseline and the 2.0 unified architecture target. It turns AI suggestions into reviewable operating plans, approval records, safe internal execution and business feedback loops.

## Operating Principle

AI can plan, recommend, draft and prepare work. AI must not directly execute high-risk operations.

High-risk operations include:

- Price, discount and markdown execution.
- Finance payment or account changes.
- Contract execution or supplier commitment.
- SAP B1 write-back.
- External publishing or mass messaging.
- Bulk data changes, deletes or destructive operations.

These actions must remain human-approved and manually executed or separately controlled by an approved business workflow.

## Core Modules

### AI Operations Center

- Route: `/ai-operations`
- API: `/api/ai-operations`
- Tracks AI operation plans, approvals, execution status and feedback.
- Shows high-risk plans as manual-only even after approval.

### AI Task Planner

- Route: `/ai-task-planner`
- API: `/api/ai-task-planner`
- Converts a business objective into reviewable plan steps.
- Creates operation plans through `/api/ai-task-planner/plans`.

### Approval Then Execute

- Approval inbox includes AI operation plans.
- API: `/api/approvals/aiop-{plan_id}/approve`
- Low-risk internal task creation may execute after approval.
- High-risk operations are marked `blocked_manual_required` and must not auto execute.

### Feedback Loop

- API: `/api/ai-operations/feedback`
- Records outcome, business result, operator note and next action.
- Feedback is used as the next improvement input for future AI plans.

## Data Model

- `ai_operation_plans`: plan, objective, action type, risk level, approval status, execution status, evidence and result.
- `ai_operation_feedback`: plan outcome, business result, operator note and next action.

## Acceptance Criteria

- AI plans default to `pending_review`.
- High-risk plans are never auto executed.
- Safe internal task creation happens only after approval.
- Approval and execution status are visible from API and page.
- Business feedback can be recorded and linked to the plan.

