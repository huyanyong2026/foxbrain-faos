# Sprint015 Store Intelligence Summary

## Goal

Sprint015 adds FoxBrain Store Intelligence Engine to the existing huyan.vafox.com system.

The implementation is incremental. It does not rebuild the project, does not develop ai.vafox.com, and does not connect to production SAP. It only reads already imported SAP export data in `sap_sales` and `sap_inventory`.

## Store Metrics Model

The first rule-based model calculates:

- `store_sales_amount`
- `store_sales_share`
- `store_gross_profit`
- `store_gross_margin`
- `store_inventory_amount`
- `store_inventory_pressure`
- `store_health_score`
- `store_growth_rate`
- `store_efficiency`

Each store receives:

- Sales score
- Margin score
- Inventory score
- Efficiency score
- Overall store health score
- Status: `risk`, `watch`, `healthy`, or `opportunity`

Every store analysis stores evidence in `evidence_json`.

## Data Table Changes

Added tables:

- `store_intelligence_snapshots`
- `store_analysis_details`
- `store_intelligence_rules`

Added indexes:

- `idx_store_intelligence_snapshots_date`
- `idx_store_intelligence_snapshots_store`
- `idx_store_analysis_details_store`
- `idx_store_intelligence_rules_status`

## Initial Store Rules

Seeded rules:

- `store_inventory_pressure_high`
- `store_margin_below_25`
- `store_sales_share_opportunity`
- `store_watch_low_sales`

Rules are stored in `store_intelligence_rules` for audit and later expansion.

## Page

Added:

- `/store-intelligence`

The page displays:

- Store ranking
- Store health score
- Sales
- Margin
- Inventory pressure
- Risks
- Opportunities

## API

Added:

- `GET /api/store-intelligence`
- `GET /api/store-intelligence/snapshots`
- `GET /api/store-intelligence/details`
- `POST /api/store-intelligence/recalculate`

## Decision Engine Integration

The engine creates evidence-backed Decision Insights when:

- Store inventory pressure is high.
- Store margin is weak.
- Store performance needs review.
- Store improvement opportunity appears.

Every Decision Insight includes evidence from:

- `sap_sales`
- `sap_inventory`
- `store_intelligence_rules`

All actions remain manual review.

## Knowledge Graph Integration

Store Intelligence writes Knowledge Graph nodes and relationships:

- Store node
- Sales node
- Inventory node
- Brand node
- Decision node
- `HAS_SALES`
- `HAS_INVENTORY`
- `SELLS_BRAND`
- `DECISION_ABOUT`

All graph relationships include source metadata.

## Dashboard Integration

CEO Dashboard now includes:

- `Store Intelligence` core entry
- Store health card
- Store count
- Average store health
- Risky store count
- Opportunity store count

## Guardrails

- `all_store_analysis_must_include_evidence`
- `store_intelligence_all_analysis_has_evidence_no_production_sap`
- `store_intelligence_file_import_only_no_production_sap_no_external_ai_api`

No production SAP connection was introduced.

No external AI API is required.
