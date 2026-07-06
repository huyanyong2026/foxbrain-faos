# Task062 V6.1 DataHub SAP RAG

## Source

Uploaded package: `FoxBrain_V6_1_DataHub_SAP_RAG_Codex_Package.zip`

## Status

In progress.

## Completed In Repository

- Added Enterprise Data Hub base tables in portal initialization.
- Added `documents` table write during file upload.
- Added `ai_query_logs` write during AI assistant queries.
- Added dashboard APIs:
  - `/api/dashboard/overview`
  - `/api/dashboard/stores`
  - `/api/dashboard/products`
- Added V6.1 health statuses.
- Added SAP file-sync skeleton: `deploy/sap_sync_daily.sh`.
- Added AI context refresh skeleton: `deploy/refresh_ai_context.sh`.
- Added completion report template.
- Added V6.1 runbook.

## Not Yet Completed

- Real SAP field mapping into Data Hub tables.
- Production Qdrant embedding worker.
- Full PostgreSQL migration of local SQLite records.
- Dify / n8n execution workflows.

## Safety Notes

- SAP remains read-only.
- No production data is overwritten.
- Empty states are used when data is unavailable.
- High-risk suggestions remain review-only.
