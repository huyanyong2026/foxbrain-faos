# Sprint016: Enterprise Sync Engine｜SAP B1 自动同步引擎

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint007-015.5

---

## 1. Sprint Goal

Build the first production-safe Enterprise Sync Engine for VAFOX.

The goal is to replace manual SAP Excel upload with an automated, auditable and recoverable data-copy pipeline:

```text
SAP B1 source
↓
Read-only extraction
↓
Encrypted transfer
↓
VAFOX staging area
↓
Data validation
↓
Enterprise Data Lake
↓
Calibration / Intelligence / CEO Brain
```

VAFOX must copy data from SAP safely. It must never control, modify or interrupt production SAP.

---

## 2. Mandatory Safety Architecture

Preferred architecture:

```text
SAP-PROD
Production SAP B1 + SQL Server
Read-only source only
        │
        │ scheduled database backup / replication / read-only export
        ▼
SAP-REPLICA or SYNC-SOURCE
Independent replica or export host
        │
        │ encrypted pull by VAFOX
        ▼
VAFOX Sync Engine
        │
        ▼
VAFOX Data Lake
```

### Hard rules

- Do not install AI, Python services, n8n, Dify or experimental programs on SAP-PROD.
- Do not write to SAP company databases.
- Do not execute INSERT, UPDATE, DELETE, MERGE, DDL or stored-procedure writes against SAP.
- Use a dedicated read-only account with minimum permissions.
- Prefer reading from a replica, restored backup database or scheduled export folder.
- Do not store SAP database passwords in GitHub.
- Do not log customer phone numbers, personal identifiers or credentials in plain text.
- A sync failure must never affect SAP business operations.
- The first implementation must support dry-run and manual approval before enabling schedules.

---

## 3. Supported Source Modes

Implement source adapters behind one interface.

### Mode A: Replica Database — preferred

Read from an independent SQL Server database restored or synchronized from SAP-PROD.

```text
source_type = sap_b1_sql_replica
```

### Mode B: Secure Export Folder — safe fallback

Read scheduled CSV/XLSX/TXT exports copied to a secure folder or SFTP location.

```text
source_type = sap_b1_export_folder
```

### Mode C: Production Read-only Database — disabled by default

Only prepare configuration support. Do not enable without explicit approval and connectivity testing.

```text
source_type = sap_b1_sql_readonly
status = disabled
```

The UI must clearly show which source mode is active.

---

## 4. Initial SAP Data Scope

Phase 1 datasets:

```text
sales
inventory
products
brands
stores
employees
customers
suppliers
purchase_orders
sales_orders
```

P0 implementation may activate only:

```text
sales
inventory
products
brands
stores
```

Other datasets can remain configured but disabled.

Do not copy financial journal entries, passwords, attachments or sensitive personal data in the first release unless explicitly approved.

---

## 5. Sync Strategy

Support:

```text
full_sync
incremental_sync
reconciliation_sync
```

### First run

- Full copy into staging.
- Validate counts and totals.
- Do not publish into production Data Lake until approved.

### Daily run

Default planned schedule:

```text
22:00 source backup / export / replica refresh
22:30 VAFOX incremental sync
23:00 calibration and intelligence rebuild
```

Do not create the production schedule automatically in Sprint016. Create the scheduler configuration and manual enable switch.

### Incremental cursor

Use one or more of:

- update timestamp
- document date + document number
- primary key high-water mark
- source row hash

Never rely only on file modified time.

---

## 6. Data Model

Create:

### sync_connections

```text
id
name
source_type
host_reference
database_reference
credential_reference
status
read_only_verified
last_tested_at
created_at
updated_at
```

Credentials must be stored through environment variables or a secret store. `credential_reference` stores only a key name, never the secret.

### sync_jobs

```text
id
job_key
connection_id
dataset_type
sync_mode
schedule_expression
status
is_enabled
last_cursor_json
last_success_at
last_failure_at
created_at
updated_at
```

### sync_runs

```text
id
job_id
run_type
status
started_at
finished_at
source_rows
staged_rows
inserted_rows
updated_rows
skipped_rows
rejected_rows
source_checksum
target_checksum
error_summary
created_at
```

### sync_run_errors

```text
id
run_id
dataset_type
source_key
error_type
error_message
raw_reference
created_at
```

Do not store unrestricted raw sensitive payloads in error records.

### sync_staging_records

```text
id
run_id
dataset_type
source_primary_key
source_updated_at
row_hash
raw_data_json
validation_status
validation_message
created_at
```

### sync_reconciliation_results

```text
id
run_id
dataset_type
check_type
source_value
target_value
difference
status
message
created_at
```

---

## 7. Extraction Layer

Create adapter contract:

```text
test_connection()
verify_read_only()
get_schema()
extract_full(dataset)
extract_incremental(dataset, cursor)
get_source_totals(dataset)
```

SQL adapter requirements:

- parameterized SELECT queries only
- explicit column lists
- query timeout
- row limit for preview
- configurable batch size
- transaction isolation that does not block production
- connection retry with bounded backoff

No arbitrary SQL input from the UI.

---

## 8. Mapping and Normalization

Reuse existing Sprint007/008 import contracts.

The Sync Engine must map source records into the same canonical structures used by:

```text
sap_import_batches
sap_sales
sap_inventory
Data Lake
Business Calibration
```

Create mapping configuration per dataset:

```text
source_field
canonical_field
data_type
required
transform_rule
sensitive_level
```

Store mapping versions and include mapping version in every sync run.

---

## 9. Validation and Reconciliation

Before publishing a run, validate:

- row count
- duplicate source keys
- required fields
- date ranges
- numeric parsing
- source totals versus staged totals
- sales amount totals
- inventory quantity totals
- inventory retail amount totals
- unexpected negative values
- empty dataset detection

Publishing rules:

```text
passed → publish automatically if job policy allows
warning → require configurable approval
failed → never publish
```

The first real run must require manual approval.

---

## 10. Idempotency and History

- Re-running the same source snapshot must not duplicate data.
- Use source key + dataset + row hash or equivalent deterministic identity.
- Preserve all sync run history.
- Preserve source lineage from canonical row back to sync run and source record.
- Do not overwrite original Data Lake records without lineage.

---

## 11. Failure Recovery

Support:

- retry failed run
- resume from cursor
- discard staging run
- republish approved run
- reconciliation-only run

A partial failure must not leave mixed published data.

Use staging → validation → atomic publish semantics where possible.

---

## 12. UI Requirements

Add:

```text
/sync-center
/sync-center/connections
/sync-center/jobs
/sync-center/runs
/sync-center/reconciliation
```

Page name:

```text
SAP 自动同步
```

Display:

- active source mode
- read-only verification status
- last successful sync
- next planned sync
- dataset status
- source/staged/published row counts
- validation warnings
- reconciliation differences
- retry / dry-run / approve controls

The UI must not display database passwords.

---

## 13. API Requirements

Add:

```text
GET  /api/sync/connections
POST /api/sync/connections/test
POST /api/sync/connections/verify-readonly
GET  /api/sync/jobs
PATCH /api/sync/jobs/:id
POST /api/sync/jobs/:id/dry-run
POST /api/sync/jobs/:id/run
GET  /api/sync/runs
GET  /api/sync/runs/:id
POST /api/sync/runs/:id/approve
POST /api/sync/runs/:id/retry
POST /api/sync/runs/:id/discard
GET  /api/sync/runs/:id/reconciliation
```

All state-changing APIs require authenticated owner/admin access.

---

## 14. Pipeline Integration

After an approved successful sync:

```text
Sync publish
↓
Data Lake rebuild / append
↓
Business Calibration
↓
Knowledge Graph refresh
↓
Business Rules
↓
Decision Engine
↓
Business Health
↓
Inventory Intelligence
↓
Brand Intelligence
↓
Store Intelligence
↓
CEO Dashboard refresh
```

Sprint016 should implement the orchestration hooks but keep each stage independently retryable.

---

## 15. Dashboard Integration

CEO Dashboard should show a small data freshness card:

```text
SAP数据状态
最后同步：YYYY-MM-DD HH:mm
状态：正常 / 警告 / 失败
销售数据：最新至 ...
库存数据：最新至 ...
```

Do not overload the homepage.

---

## 16. Security and Audit

Record audit events for:

- connection test
- read-only verification
- job enable/disable
- manual run
- run approval
- retry
- discard
- configuration change

Recommended network rules:

- allow only VAFOX Sync host to reach replica/export host
- restrict SQL port by IP allowlist
- use VPN/private network when available
- use TLS/SFTP for transport
- rotate credentials

---

## 17. Phase 1 Acceptance

Sprint016 passes when:

- Sync Center pages are accessible.
- Source adapters exist for SQL replica and export-folder modes.
- Production SQL mode remains disabled by default.
- Connection test and read-only verification work.
- A full dry-run can stage sales and inventory data.
- Validation and reconciliation reports are generated.
- Approved staging data enters existing SAP import/Data Lake pipeline without duplicates.
- Re-running the same source is idempotent.
- Failure does not publish partial data.
- Data freshness appears on CEO Dashboard.
- Existing Sprint001-015.5 functions remain working.
- No password or private data is committed to GitHub.
- No software is installed on SAP-PROD.
- Smoke tests pass.

---

## 18. Real Environment Rollout Plan

Do not enable production automation immediately.

### Stage 1: Local simulation

- use temporary SQL/export fixtures
- prove full and incremental sync
- prove idempotency and rollback

### Stage 2: Replica or restored backup test

- configure read-only account
- perform connection verification
- run full dry-run
- compare against known SAP exports

### Stage 3: Shadow operation

- run nightly without publishing automatically
- compare 3-7 days of results
- investigate differences

### Stage 4: Controlled production use

- enable approved publishing
- keep automatic downstream intelligence rebuild
- monitor sync quality daily

---

## 19. Required Deliverables

Generate:

```text
SPRINT016_ENTERPRISE_SYNC_ENGINE_SUMMARY.md
SPRINT016_ENTERPRISE_SYNC_ENGINE_TEST_REPORT.md
SPRINT016_SAP_READONLY_SECURITY_CHECKLIST.md
SPRINT016_REAL_ENVIRONMENT_ROLLOUT_GUIDE.md
```

Reports must include:

- database changes
- source adapter design
- mapping strategy
- security controls
- read-only verification
- dry-run results
- reconciliation results
- idempotency test
- failure recovery test
- known limitations
- exact information still needed from the CEO/SAP administrator

---

## 20. Codex Execution Instruction

- Start from latest `main` after pending CEO UI and intelligence PRs are merged.
- Create branch:

```text
sprint016-enterprise-sync-engine
```

- Incremental upgrade only.
- Do not rewrite the existing portal.
- Do not connect to the live SAP production database during development.
- Do not install anything on SAP-PROD.
- Do not enable schedules automatically.
- Do not commit credentials.
- Use temporary fixtures first.
- All copied data must preserve lineage and evidence.
