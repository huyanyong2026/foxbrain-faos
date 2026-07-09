# Sprint011 Business Rule Engine Summary

## Scope

Sprint011 adds the first FoxBrain Business Rule Engine on top of Sprint010 Decision Engine.

This is an incremental upgrade. It does not rebuild the system, does not develop ai.vafox.com, does not connect production SAP, and does not require external AI APIs.

## New Tables

- `business_rules`
- `business_rule_runs`
- `business_rule_results`

Rules are stored as database records with condition JSON, action JSON, source, status, version, priority, and audit timestamps. Rules are not hidden only inside code.

## Seeded Huohu Fox Rules

- `inventory_over_180_amount_50000`
- `inventory_over_365_amount_100000`
- `gross_margin_below_25`
- `negative_gross_profit`
- `inventory_cost_missing_quality`
- `brand_sales_share_over_60`
- `store_margin_decline_three_months` inactive until time-series metrics are available

## Added Pages

- `/business-rules`
- `/business-rules/:id`
- `/business-rules/runs`

The rule center shows active/draft/inactive rules, editable rule detail, rule run history, triggered results, and Decision Engine links.

## Added APIs

- `GET /api/business-rules`
- `GET /api/business-rules/:id`
- `POST /api/business-rules`
- `PATCH /api/business-rules/:id`
- `POST /api/business-rules/rebuild`
- `GET /api/business-rules/runs`
- `GET /api/business-rules/results`

## Decision Engine Integration

When an active business rule matches, Sprint011 creates a Sprint010 `decision_insights` record through `upsert_decision_insight`.

Every rule-triggered insight includes evidence from:

- `business_rules`
- `business_rule_runs`
- `business_rule_results`
- source business data such as `sap_inventory`, `sap_sales`, `business_metrics_snapshots`, or `business_metric_quality`

Generated action options remain manual review actions. No business execution is automatic.

## Dashboard Integration

CEO Dashboard now includes:

- active rule count
- total rule runs
- high/critical rule trigger count
- latest rule run
- Business Rule Engine entry

## Known Limitations

- The first evaluator supports the seeded rule patterns only.
- Store margin decline remains inactive until monthly time-series metrics are available.
- There is no visual rule builder yet; Sprint011 uses structured form/table editing.

## Safety

- `business_rules_are_database_records_viewable_editable_auditable`
- `business_rule_triggered_decision_insights_must_include_evidence`
- `rule_based_no_external_ai_api_no_production_sap_all_triggered_decisions_include_evidence`

