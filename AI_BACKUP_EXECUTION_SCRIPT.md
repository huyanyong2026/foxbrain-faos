# AI Backup Execution Script

## Target and Purpose

This repository includes `scripts/ai_production_backup.sh` to generate production backup evidence for the Genesis migration preparation window.

- **Target:** `ai.vafox.com`
- **Application location:** `/opt/ai-vafox`
- **Backup purpose:** create pre-Genesis production backup evidence.

## Non-Negotiable Operating Rules

The script is designed for evidence collection only:

1. **NO CUTOVER** — it does not switch DNS, traffic, service ownership, credentials, volumes, or runtime targets.
2. **NO SERVICE INTERRUPTION** — it does not stop, restart, recreate, pause, upgrade, pull, build, prune, or reload services.
3. **NO DATA CHANGE** — it performs read-only dumps, exports, inventories, mirrors, and configuration copies only.
4. **NO SECRET EXPOSURE** — environment and WeCom references are redacted; operators must not paste secret values into logs, chat, tickets, or reports.

## Script Location

```bash
scripts/ai_production_backup.sh
```

Run it from an approved operator shell on the production host only after the preflight checklist in `AI_BACKUP_EXECUTION_PLAN.md` is approved.

## Dry-Run Mode

Dry-run mode prints the actions the script would take and creates only local dry-run/log placeholder files needed by shell redirection. It must be used first to validate command paths and required environment variables without collecting production backup data.

```bash
scripts/ai_production_backup.sh --dry-run
```

## Required Environment

Set sensitive values through the approved secret manager or secure environment injection. Do not place secret values directly into shell history.

```bash
export POSTGRES_URL='postgresql://...'
export POSTGRES_ADMIN_URL='postgresql://...'   # optional; defaults to POSTGRES_URL
export MINIO_ENDPOINT='https://...'
export MINIO_ACCESS_KEY='...'
export MINIO_SECRET_KEY='...'
export MILVUS_HOST='localhost'                 # optional
export MILVUS_PORT='19530'                     # optional
export MILVUS_USER='...'                       # optional
export MILVUS_PASSWORD='...'                   # optional
```

Optional path overrides:

```bash
export APP_ROOT=/opt/ai-vafox
export BACKUP_PARENT=/opt/ai-vafox/backups
```

## Production Execution

After dry-run review, execute the backup during the approved backup window:

```bash
scripts/ai_production_backup.sh
```

Optional flags:

```bash
scripts/ai_production_backup.sh \
  --run-milvus-backup-tool \
  --run-nginx-dump \
  --run-nginx-test
```

Use optional flags only when those tools are approved and known safe in the production environment. The default path skips `milvus-backup create`, `nginx -T`, and `nginx -t` unless explicitly enabled.

## What the Script Collects

The script creates a timestamped directory under `/opt/ai-vafox/backups` by default:

```text
/opt/ai-vafox/backups/pre-genesis-YYYYMMDDTHHMMSSZ/
├── postgresql/
├── milvus/
├── minio/
├── n8n/
├── wecom/
├── nginx/
├── docker/
├── manifests/
├── logs/
├── checksums/
└── AI_BACKUP_REPORT.md
```

It collects:

1. Preflight and host identity evidence.
2. PostgreSQL full dump, schema-only dump, role dump without passwords, grants, version, and dump listing.
3. Milvus collection metadata, schemas, indexes, partitions, and optional backup-tool output.
4. MinIO bucket inventory, bucket metadata, lifecycle/versioning/policy references, object mirror, and object file inventory.
5. n8n version, workflow export, encrypted credential export, and redacted credential metadata.
6. WeCom configuration candidate references and redacted secret-key inventory.
7. Nginx `ai-vafox` site configuration and optional syntax/full-config evidence.
8. Docker Compose file, resolved config, container state, images, volumes, networks, and inspect metadata.
9. SHA256 checksums for collected files.
10. `AI_BACKUP_REPORT.md` with target, timestamps, evidence summary, and operator sign-off table.

## Failure Stop and Logs

The script uses strict shell behavior:

```bash
set -Eeuo pipefail
```

A failing required command stops the run and writes a clear error to:

```text
$BACKUP_ROOT/logs/ai_production_backup.log
```

Component-specific stderr logs are stored under:

```text
$BACKUP_ROOT/logs/
```

## Completion Evidence

A successful run must produce at least these evidence files:

- `postgresql/database_full.dump`
- `postgresql/schema.sql`
- `postgresql/roles_no_passwords.sql`
- `milvus/collections_detail.json`
- `minio/buckets.txt`
- `minio/object_files.txt`
- `n8n/workflows.json`
- `n8n/credentials_metadata_redacted.json`
- `wecom/secrets_inventory_redacted.tsv`
- `nginx/sites-enabled/ai-vafox`
- `docker/compose/docker-compose.yml`
- `docker/images_digests.txt`
- `docker/containers_all.txt`
- `checksums/SHA256SUMS`
- `AI_BACKUP_REPORT.md`

## Abort Criteria

Abort and notify the production owner if the run requires any service-changing action, causes monitoring degradation, exposes a secret value, or encounters disk-space/connection/health issues described in `AI_BACKUP_EXECUTION_PLAN.md`.
