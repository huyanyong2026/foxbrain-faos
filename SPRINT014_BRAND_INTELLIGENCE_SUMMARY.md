# Sprint014 Brand Intelligence Summary

## Goal

Sprint014 adds VAFOX Brand Intelligence Engine to the existing huyan.vafox.com system.

The implementation is incremental. It does not rebuild the project, does not develop ai.vafox.com, and does not connect to production SAP. It only reads already imported SAP export data in `sap_sales` and `sap_inventory`.

## Brand Metrics Model

The first rule-based model calculates:

- `brand_sales_amount`
- `brand_sales_share`
- `brand_gross_profit`
- `brand_gross_margin`
- `brand_inventory_amount`
- `brand_inventory_pressure`
- `brand_growth_rate`
- `brand_health_score`

Each brand receives:

- Authority score
- Sales score
- Profit score
- Inventory score
- Growth score
- Overall brand health score
- Status: `risk`, `watch`, `healthy`, or `opportunity`

Every score and suggestion stores evidence in `evidence_json`.

## Data Table Changes

Added tables:

- `brand_intelligence_snapshots`
- `brand_analysis_details`
- `brand_intelligence_rules`

Added indexes:

- `idx_brand_intelligence_snapshots_date`
- `idx_brand_intelligence_snapshots_brand`
- `idx_brand_analysis_details_brand`
- `idx_brand_intelligence_rules_status`

## Initial Brand Rules

Seeded rules:

- `brand_inventory_pressure_high`
- `brand_margin_below_25`
- `brand_dependency_over_60`
- `brand_growth_opportunity_high_score`

Rules are stored in `brand_intelligence_rules` for future audit and expansion.

## API

Added:

- `GET /api/brand-intelligence`
- `GET /api/brand-intelligence/snapshots`
- `GET /api/brand-intelligence/details`
- `POST /api/brand-intelligence/recalculate`

## Page

Added:

- `/brand-intelligence`

The page displays:

- Brand ranking
- Sales contribution
- Profit contribution
- Inventory pressure
- Brand health
- Risks
- Opportunities

## Decision Engine Integration

The engine creates evidence-backed Decision Insights when:

- Brand inventory pressure is high.
- Brand margin is weak.
- Brand dependency is risky.
- Brand growth opportunity appears.

Every Decision Insight includes evidence from:

- `sap_sales`
- `sap_inventory`
- `brand_intelligence_rules`

All actions remain manual review.

## Business Health Integration

Business Health `brand_health` now reads the latest `brand_intelligence_snapshots` as an evidence source.

Risky brand snapshots reduce the brand health dimension with traceable evidence.

## Knowledge Graph Integration

Brand Intelligence writes Knowledge Graph nodes and relationships:

- Brand node
- Sales node
- Inventory node
- Decision node
- `HAS_SALES`
- `HAS_INVENTORY`
- `DECISION_ABOUT`

All graph relationships include source metadata.

## Dashboard Integration

CEO Dashboard now includes:

- `Brand Intelligence` core entry
- Brand health card
- Brand count
- Average brand health
- Risky brand count
- Opportunity brand count

## Guardrails

- `all_brand_analysis_and_recommendations_must_include_evidence`
- `brand_intelligence_all_recommendations_have_evidence_no_production_sap`
- `brand_intelligence_file_import_only_no_production_sap_no_external_ai_api`

No production SAP connection was introduced.

No external AI API is required.
