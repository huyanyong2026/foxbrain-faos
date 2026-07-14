# VAFOX V6.1 DataHub, SAP and RAG Runbook

## Purpose

V6.1 upgrades VAFOX from a runnable portal into the first version of an enterprise data center:

- Enterprise Data Hub base schema
- SAP nightly sync center
- Document knowledge base and RAG foundation
- CEO cockpit data APIs

## Enterprise Data Hub

The application initializes these base tables without overwriting existing records:

- `stores`
- `employees`
- `brands`
- `products`
- `customers`
- `suppliers`
- `inventory`
- `sales_orders`
- `sales_order_items`
- `documents`
- `ai_query_logs`

The current SQLite deployment keeps this schema locally. A future Docker / PostgreSQL migration should preserve the same entity names and fields.

## SAP Nightly Sync Center

Current production SAP sync remains read-only and scheduled at `22:00`.

V6.1 adds file-sync skeleton scripts:

- `deploy/sap_sync_daily.sh`
- `deploy/refresh_ai_context.sh`

Recommended future cron:

```cron
0 22 * * * /bin/bash /opt/foxbrain/scripts/sap_sync_daily.sh >> /opt/foxbrain/sap_sync/logs/cron.log 2>&1
30 22 * * * /bin/bash /opt/foxbrain/scripts/refresh_ai_context.sh >> /opt/foxbrain/logs/ai_refresh.log 2>&1
```

Do not expose SAP SQL Server to public AI tools. Keep direct database access read-only.

## RAG Foundation

Uploaded files now enter both:

- `knowledge_items`
- `documents`

Extracted text is chunked in `knowledge_chunks`. AI questions are logged in `ai_query_logs` with cited sources.

Qdrant production embeddings remain a later worker task. Until that worker exists, the system uses internal keyword retrieval and records `embedding_status=pending`.

## Dashboard APIs

V6.1 adds:

- `GET /api/dashboard/overview`
- `GET /api/dashboard/stores`
- `GET /api/dashboard/products`

These APIs return real existing data and explicit empty states. They must not invent store, product, sales, inventory, employee, customer, contract or salary facts.

## Acceptance

- Login still works.
- Upload still works.
- `/api/health` includes V6.1 DataHub and RAG statuses.
- `/api/dashboard/overview` returns JSON.
- SAP timer remains `22:00`.
- Backup timer remains `02:30`.
- No secrets are committed to GitHub.
