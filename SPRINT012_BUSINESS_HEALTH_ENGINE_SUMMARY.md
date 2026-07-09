# Sprint012 Business Health Engine Summary

## Goal

Sprint012 adds the Business Health Engine on top of the current huyan.vafox.com system without rebuilding the project, without ai.vafox.com work, and without any production SAP connection.

The engine converts existing imported SAP-derived operating data, Business Calibration signals, Business Rule Engine output, and Decision Engine alerts into an evidence-backed enterprise health score.

## Database Changes

Added tables:

- `business_health_snapshots`
- `business_health_details`
- `business_health_weights`

Added indexes:

- `idx_business_health_snapshots_date`
- `idx_business_health_details_snapshot`
- `idx_business_health_weights_status`

Seeded configurable weights:

- `sales_health`
- `margin_health`
- `inventory_health`
- `brand_health`
- `store_health`
- `operation_health`
- `data_health`

## Health Indicator Model

The first Sprint012 model includes seven dimensions:

- `sales_health`: validates whether imported sales metrics are available.
- `margin_health`: evaluates gross margin and negative gross-profit rows.
- `inventory_health`: evaluates inventory amount, quantity, and aged inventory risk.
- `brand_health`: evaluates brand concentration and top-brand share.
- `store_health`: evaluates store-level sales coverage.
- `operation_health`: evaluates high Business Rule triggers and high-severity Decision Insights.
- `data_health`: evaluates metric quality warnings and pending object suggestions.

All dimensions write score, status, summary, and `evidence_json` into `business_health_details`.

## API

Added:

- `GET /api/business-health`
- `GET /api/business-health/snapshots`
- `GET /api/business-health/details`
- `POST /api/business-health/recalculate`

## Page

Added:

- `/business-health`

The page displays:

- Overall health score
- Dimension scores
- Evidence count per dimension
- Recent trend
- Active health weights

## Dashboard Integration

CEO Dashboard now includes:

- `Business Health Engine` core entry
- `Business Health` summary card
- `business_health_score`
- `business_health_status`
- Business alert line for current health score/status
- System status check for `business_health_snapshots`

## Decision Engine Integration

When the overall health score is low or a dimension becomes critical, the engine creates a Decision Insight with evidence.

Decision integration includes:

- `upsert_decision_insight`
- evidence from `business_health_snapshots`
- evidence from low/critical `business_health_details`
- manual-review action option

Guardrail:

- `all_business_health_scores_must_include_evidence`

## Business Rule Engine Readiness

The scoring weights are stored in `business_health_weights`, not hidden in code. This makes the scoring layer ready for future Business Rule Engine control and audit.

Guardrail:

- `business_health_weights_are_configurable_and_ready_for_business_rule_engine`

## Safety Rules

This Sprint keeps the existing system stable and only adds incremental capability.

- No production SAP connection.
- No external AI API required.
- No automatic business-data execution.
- All health scores require evidence.
- Decision suggestions remain review-only.

Runtime safety marker:

- `business_health_scores_are_evidence_backed_no_external_ai_api_no_production_sap`
