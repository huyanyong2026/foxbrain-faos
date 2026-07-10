# Sprint016 Enterprise Sync Engine Summary

## Scope

Sprint016 adds the first production-safe Enterprise Sync Engine foundation for huyan.vafox.com.

The implementation is incremental and keeps Sprint001-015.5 features intact. It does not connect to production SAP, does not install anything on the SAP server, and does not commit credentials.

## Implemented

- SQL replica adapter using a local SQLite fixture for development and verification.
- Safe export directory adapter using local CSV fixture files.
- Production SAP read-only source placeholder, disabled by default.
- Connection test and read-only verification actions.
- Full dry-run / dry-run / incremental sync paths.
- Staging table for extracted records before publish.
- Validation for sales, inventory, products, brands, and stores.
- Reconciliation result records for each sync run.
- Manual approval publish into existing `sap_import_batches`, `sap_sales`, `sap_inventory`, and Data Lake rebuild flow.
- Idempotent import via source keys and row hashes.
- Failure recording in `sync_run_errors`.
- Sync Center UI at `/sync-center`.
- CEO homepage data freshness card and Sync Center entry.
- API endpoints under `/api/sync`.

## Database Changes

New or expanded tables:

- `sync_connections`
- `sync_jobs`
- `sync_runs`
- `sync_run_errors`
- `sync_staging_records`
- `sync_reconciliation_results`

The existing `sync_jobs` table name was already present from earlier ecosystem work, so Sprint016 adds compatible columns instead of dropping or renaming the existing table.

## API Changes

- `GET /api/sync`
- `GET /api/sync/status`
- `GET /api/sync/connections`
- `GET /api/sync/jobs`
- `GET /api/sync/runs`
- `GET /api/sync/reconciliation`
- `GET /api/sync/freshness`
- `POST /api/sync/connections/{id}/test`
- `POST /api/sync/connections/{id}/verify-readonly`
- `POST /api/sync/jobs/{id}/dry-run`
- `POST /api/sync/jobs/{id}/full-dry-run`
- `POST /api/sync/jobs/{id}/incremental`
- `POST /api/sync/runs/{id}/publish`
- `POST /api/sync/runs/{id}/retry`
- `POST /api/sync/runs/{id}/discard`

## UI Changes

- Added `/sync-center`
- Added `/sync-center/connections`
- Added `/sync-center/jobs`
- Added `/sync-center/runs`
- Added `/sync-center/reconciliation`
- Added Enterprise Sync status to CEO dashboard.
- Added Enterprise Sync entry to the CEO action cards and core engine entries.

## Safety Notes

- Production SAP source is configured as `sap_b1_sql_readonly` but remains disabled.
- Schedules are seeded as `manual_only` with `is_enabled=0`.
- Credentials are represented only by environment-variable references, never by secret values.
- All publish actions require a user action and write only to FoxBrain local tables.
