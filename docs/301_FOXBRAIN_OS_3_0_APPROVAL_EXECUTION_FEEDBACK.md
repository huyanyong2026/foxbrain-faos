# FoxBrain OS 3.0 Approval, Execution and Feedback

## Flow

```text
Business objective
  -> AI Task Planner
  -> AI operation plan
  -> Human approval
  -> Safe internal execution or manual-only high-risk block
  -> Business feedback
  -> Next plan improvement
```

## Approval Rules

- All AI operation plans require review.
- Boss, admin, finance, purchasing and store manager roles can approve within their business scope.
- Rejection cancels execution.
- Approval of high-risk plans does not mean automatic execution.

## Execution Rules

- Low-risk and medium-risk internal actions can create internal tasks after approval.
- High-risk actions remain `blocked_manual_required`.
- SAP write-back, finance payment, price changes, contracts, external publishing and bulk deletes cannot be performed automatically by this mechanism.
- Unsupported actions remain logged as plans and require module-specific implementation.

## Feedback Rules

Feedback should capture:

- Outcome: success, partial, failed, cancelled or pending.
- Business result: measurable result or observed effect.
- Operator note: what actually happened.
- Next action: follow-up task, new plan or stop condition.

## Required API Contracts

- `GET /api/ai-operations`
- `GET /api/ai-task-planner`
- `POST /api/ai-task-planner/plans`
- `POST /api/ai-operations/plans`
- `POST /api/ai-operations/plans/{plan_id}/approve`
- `POST /api/ai-operations/plans/{plan_id}/reject`
- `POST /api/ai-operations/feedback`
- `POST /api/approvals/aiop-{plan_id}/approve`
- `POST /api/approvals/aiop-{plan_id}/reject`

## Non-Negotiable Safety Constraint

All high-risk operations must retain human approval and must not auto execute.

