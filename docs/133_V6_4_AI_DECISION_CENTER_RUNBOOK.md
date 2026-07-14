# VAFOX V6.4 AI Decision Center Runbook

## Scope

V6.4 turns operational data, KPI snapshots and AI suggestions into reviewable decision cases.

## Pages

- `/decision-center`: mobile-friendly AI decision center.

## APIs

- `GET /api/v6.4/status`
- `GET /api/v6.4/decision-center`
- `POST /api/v6.4/decision-cases`
- `GET /api/v6.4/executive-brief`
- `GET /api/v6.4/store-intelligence`
- `GET /api/v6.4/brand-intelligence`
- `GET /api/v6.4/customer-intelligence`

## Tables

- `decision_cases`
- `decision_recommendations`

## Safety Rules

- Recommendations are advisory drafts.
- Pricing, finance, purchasing, contracts and external publishing require human approval.
- Evidence and source fields are stored with decision cases.
- SAP remains read-only; daily sync time is 22:00.

