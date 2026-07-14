# Enterprise Pack 13 - Data Intelligence

## Goal

Pack 13 establishes the unified data intelligence layer for VAFOX OS. Dashboards,
AI Agents and decision engines must use one KPI catalog and one metrics service instead
of recalculating business numbers independently.

## Principles

- KPI definitions are centralized.
- Every KPI declares source, formula, refresh cadence and owner.
- All analytics reference canonical enterprise entities.
- AI insights must show explicit evidence.
- Data quality is visible before management conclusions are trusted.

## API Contracts

- `/api/data-intelligence/framework`
- `/api/kpi/catalog`
- `/api/kpi/metrics`
- `/api/data-intelligence/model`
- `/api/data-quality/monitor`
- `/api/insights/engine`
- `/api/trends`

## KPI Catalog

Initial executive KPIs:

- Revenue
- Gross Margin
- Inventory Turnover
- Cash Flow
- Customer Growth
- Store Ranking
- Sell-through Rate

Each KPI includes source, formula, refresh cadence, owner and users.

## Unified Data Model

Canonical entities:

- Store
- Product
- Customer
- Employee
- Supplier
- Order
- Inventory
- Finance

All analytics should reference these canonical entities and preserve lineage.

## Insight Engine

The insight engine returns:

- Trends
- Exceptions
- Root-cause candidates
- Opportunities
- Recommendations

Every insight must include evidence. If evidence is missing, the system must present a
limitation rather than a management recommendation.

## Data Quality

Quality checks:

- Completeness
- Consistency
- Freshness
- Duplicate detection
- Synchronization status

## Current Delivery

- Added unified KPI catalog contract.
- Added unified metrics service contract.
- Added canonical data model contract.
- Added data quality monitor contract.
- Added trend and insight engine contracts.
- Dashboard KPI service now references the unified metrics service.
- Enterprise decision engine now includes unified metrics and insights as inputs.
