# Sprint017 Daily Intelligence Engine Summary

## Status

Sprint017 is implemented as an incremental upgrade on top of Sprint015.5, Sprint016, and Sprint016.5.

No production SAP write access was added. Automatic scheduling remains disabled by default.

## Implemented

- Added Daily Intelligence database model.
- Added Daily Intelligence generation pipeline.
- Added `/daily-intelligence` CEO briefing page.
- Added `/api/daily-intelligence/*` APIs.
- Added CEO homepage integration.
- Added Memory integration for turning important daily items into draft enterprise memories.
- Added scheduler foundation with `enabled=0` and approval status `disabled_until_approved`.

## Data Model

New tables:

- `daily_intelligence_reports`
- `daily_intelligence_items`
- `daily_intelligence_schedules`

Default scheduler seed:

- `daily_intelligence_0730`
- time: `07:30`
- enabled: `0`
- approval: `disabled_until_approved`

## Daily Report Model

Each report stores:

- report date
- daily summary
- health summary
- decision summary
- risk summary
- opportunity summary
- execution summary
- evidence JSON
- status

Each item stores:

- item type: risk or opportunity
- severity
- title
- description
- related entity
- evidence JSON
- recommended action

All report items require evidence.

## Generation Pipeline

Manual rebuild currently runs:

1. Sync freshness check
2. Business Health calculation
3. Decision Engine rebuild
4. Inventory Intelligence analysis
5. Brand Intelligence analysis
6. Store Intelligence analysis
7. Daily Intelligence report generation

The pipeline records stage results in the report execution summary.

## API

- `GET /api/daily-intelligence/latest`
- `GET /api/daily-intelligence/history`
- `POST /api/daily-intelligence/rebuild`
- `GET /api/daily-intelligence/items/{id}`
- `POST /api/daily-intelligence/items/{id}/memory-draft`

## UI

New page:

- `/daily-intelligence`

Displays:

- daily summary
- top risks
- top opportunities
- recommended actions
- evidence count
- historical reports
- memory draft actions

## CEO Homepage Changes

CEO Brain now includes:

- Daily Intelligence metric
- Daily Intelligence action card
- Daily Intelligence core entry
- risk / opportunity / report date summary

## Memory Integration

Any Daily Intelligence item can create a draft `enterprise_memories` record.

Memory drafts keep:

- source item id
- evidence text
- recommended action
- risk level
- relation to the Daily Intelligence item

## Safety

- No SAP write access.
- No ai.vafox.com work.
- No scheduler activation.
- No high-risk automatic execution.
