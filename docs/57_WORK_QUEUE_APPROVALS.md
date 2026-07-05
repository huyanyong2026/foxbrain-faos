# 57 Work Queue Approvals

## Goal

Work Queue and Approval Inbox unify pending work across modules.

## Routes

- `/work-queue`
- `/approvals`

## APIs

- `GET /api/work-queue`
- `GET /api/approvals`
- `POST /api/approvals/{id}/approve`
- `POST /api/approvals/{id}/reject`

Approval actions are audited. V1 does not silently mutate source objects.
