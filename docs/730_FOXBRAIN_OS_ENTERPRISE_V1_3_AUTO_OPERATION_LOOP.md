# VAFOX Enterprise OS V1.3 Auto Operation Loop

## Objective

Continue from VAFOX Enterprise OS V1.0 to V1.2 without rebuilding the system. V1.3 connects the existing SAP sync, AI analysis, boss daily report, task center and approval flow into one automatic operation loop.

## Loop

1. SAP daily sync reads business data from SAP B1.
2. AI analysis reviews SAP freshness, operating metrics, risks and knowledge context.
3. Boss daily report produces a reviewable daily briefing draft.
4. Task center receives approved internal work items.
5. Approval flow blocks high-risk AI execution until a human reviewer approves or rejects it.

## SAP Production Rule

SAP production server remains independent. VAFOX only performs read-only sync:

- No SAP writeback.
- No production database schema changes.
- Credentials stay on the server environment or secret store.
- Daily schedule uses `SAP_SYNC_TIME`, default `22:00`.

## Routes

- Page: `/auto-operation`
- API: `/api/auto-operation`
- Contract: `/api/auto-operation/contract`
- SAP policy: `/api/auto-operation/sap-readonly`
- Boss daily report: `/api/auto-operation/boss-daily-report`
- Tasks: `/api/auto-operation/tasks`
- Approvals: `/api/auto-operation/approvals`
- Plan generation: `POST /api/auto-operation/run-daily-loop`

## Approval Rule

The daily loop can generate a reviewable AI operation plan. It does not auto execute high-risk actions and does not write to SAP. Generated loop plans are stored in `ai_operation_plans` with:

- `approval_status = pending_review`
- `execution_status = blocked_manual_required`
- `execution_mode = approval_then_execute`
- `risk_level = high`
