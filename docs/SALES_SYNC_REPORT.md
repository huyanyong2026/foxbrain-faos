# Sales Sync Report

## Implemented path

```
SAP B1 (system of record) -> SAP Mirror / sap_sync projection -> Core Sales Domain
```

The Core API has no SAP B1 credentials and performs only a parameterized
`SELECT` against `dbo.sap_sales_orders` and `dbo.sap_sales_order_lines`.
`infra/sap-mirror/sales-sync.sql` defines the mirror projection; the existing
sync worker is its only writer. This preserves the read-only boundary.

## Core contract

`GET /api/v1/sales` returns one line-level sales fact per synchronized order
line: `order_id`, `store`, `sku`, `quantity`, `amount`, `margin`, and `date`.
It always includes evidence metadata: `source`, `timestamp`, `version`, and
`confidence`. CEO Runtime citations preserve those fields unchanged.

## Validation

The automated adapter test verifies both projection tables are read, validates
the normalized response, validates evidence metadata, and validates assigned
store filtering. The API and CEO evidence tests cover the public contract and
Runtime citation handoff.
