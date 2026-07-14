# VAFOX OS 2.0 Unified Data Service

## Purpose

The unified data service is the read-first data layer for VAFOX OS 2.0. It makes SAP B1, local archives, knowledge, memory, tasks and reports available through consistent, permission-aware APIs.

## Source Priority

1. SAP B1 synced tables are the source of record for sales, inventory, items, customers and purchasing.
2. Local archive tables enrich SAP data with photos, notes, documents, operating tags and management context.
3. Knowledge and memory provide explanation, policy, historical decisions and training context.
4. AI-generated outputs are derived artifacts and must cite their sources.

## Core Data Contracts

- Sales metrics: date, store, sales amount, gross profit, gross margin and completion rate.
- Inventory metrics: item, warehouse/store, on hand, committed, on order, average price, stock amount and risk flags.
- Customer/member metrics: customer code, name, contact fields, balance, credit and purchase relationship.
- Sync health: last run, status, freshness, source tables, counts and warnings.
- Lineage: every management payload should describe where the data came from.

## Current Priority APIs

- `/api/sap/datahub`
- `/api/sap/items`
- `/api/sap/inventory`
- `/api/sap/customers`
- `/api/sap/sales`
- `/api/sap/business-analysis`
- `/api/dashboard/overview`
- `/api/dashboard/kpis`
- `/api/executive-command-center/dashboard`

## Data Quality Rules

- If SAP is stale or missing, return a warning instead of confident recommendations.
- If a metric is estimated, label it as estimated.
- If a module still uses placeholders, expose the missing upstream table or mapping.
- Do not mix raw business data with AI recommendations; keep both visible but separate.

