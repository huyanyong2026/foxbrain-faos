# Sprint018.5 Copilot Real Data Calibration Summary

## Goal

Move Enterprise Copilot from functional foundation to real-business calibrated use on `huyan.vafox.com`.

This Sprint is an incremental upgrade on Sprint018. It does not rebuild the system, does not develop `ai.vafox.com`, and does not add SAP write access.

## What Changed

### Copilot Context Calibration

The Copilot Context Engine now adds calibrated evidence from:

- Enterprise Sync freshness
- Data Lake business metrics
- Business Health
- Inventory Intelligence
- Brand Intelligence
- Store Intelligence
- SAP imported sales rows
- SAP imported inventory rows
- Business Rules
- Decision Insights
- Daily Intelligence
- Enterprise Memory
- Knowledge Graph

### Entity-Specific Evidence

Copilot now recognizes important real-business entities in questions:

- Osprey
- Kailas
- Mammut
- Salomon
- Deuter
- 南山店
- 振兴店
- 航苑店
- 金沙店

When a question names an entity, Copilot requires entity-specific evidence before presenting a reliable conclusion.

### Data Sufficiency Guardrail

If the required evidence is missing, Copilot answers:

```text
当前数据不足，无法形成可靠结论。
```

The answer lists missing evidence categories such as:

- `brand_evidence:...`
- `store_evidence:...`
- `inventory_intelligence`
- `business_health`
- `decision_insight`
- `sync_freshness`

### Data Freshness

Every evidence item now includes:

- `updated_at`
- `updated_at_text`
- `freshness`
- `stale_warning`

Freshness status:

- `fresh`: updated within 24 hours
- `stale`: updated within 72 hours
- `outdated`: older than 72 hours
- `unknown`: source update time unavailable

### UI Calibration

`/copilot` now displays:

- answer reliability
- confidence label
- evidence source type and source id
- evidence update time
- freshness status
- stale-data warning
- feedback buttons
- memory draft confirmation

### Feedback Calibration

Feedback types now include:

- `useful`
- `not_useful`
- `needs_review`
- `correction`
- `missing_evidence`

Feedback is stored for later quality review. It does not modify business rules or enterprise memory.

### Test Data Cleanup

Added selective cleanup for Sprint018.5 test data:

```text
POST /api/copilot/test-cleanup
```

Cleanup is blocked unless `test_run_id` starts with:

```text
SPRINT0185_TEST
```

The cleanup archives only matching test memory drafts and deletes only matching test sessions/messages/feedback.

## Safety

- No SAP write permission added.
- No production SAP modification.
- No program installed on SAP production server.
- No external AI API required.
- No credentials committed.
- Test cleanup is scoped by `test_run_id`.

## Production Calibration Outcome

Production deployment was completed on `huyan.vafox.com`.

Key finding:

```text
Enterprise overview has enough evidence for a reliable answer.
Osprey, Kailas and 南山店 currently lack entity-specific production evidence, so Copilot correctly returns data-insufficient responses.
Enterprise Sync freshness reports no_published_sync and is displayed in Copilot freshness context.
```

This means Sprint018.5 passed the main safety requirement: Copilot does not invent conclusions when real production evidence is incomplete.
