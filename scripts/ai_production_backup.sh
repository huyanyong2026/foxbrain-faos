#!/usr/bin/env bash
# Production evidence backup helper for ai.vafox.com before Genesis migration.
# Rules: NO CUTOVER. NO SERVICE INTERRUPTION. NO DATA CHANGE.

set -Eeuo pipefail
IFS=$'\n\t'

TARGET_DOMAIN="${TARGET_DOMAIN:-ai.vafox.com}"
APP_ROOT="${APP_ROOT:-/opt/ai-vafox}"
BACKUP_PARENT="${BACKUP_PARENT:-/opt/ai-vafox/backups}"
DRY_RUN=0
RUN_MILVUS_BACKUP_TOOL=0
RUN_NGINX_TEST=0
RUN_NGINX_DUMP=0

usage() {
  cat <<'USAGE'
Usage: scripts/ai_production_backup.sh [--dry-run] [--backup-parent PATH] [--run-milvus-backup-tool] [--run-nginx-test] [--run-nginx-dump]

Creates production backup evidence for ai.vafox.com under a timestamped backup directory.
Default behavior is conservative and avoids optional commands that may be unavailable/noisy.

Required environment for selected sections:
  POSTGRES_URL             PostgreSQL connection URL for database dump/read-only queries.
  POSTGRES_ADMIN_URL       PostgreSQL admin URL for roles-only dump (defaults to POSTGRES_URL if unset).
  MINIO_ENDPOINT           MinIO endpoint for mc alias set.
  MINIO_ACCESS_KEY         MinIO access key (not logged).
  MINIO_SECRET_KEY         MinIO secret key (not logged).
  MILVUS_HOST              Optional Milvus host for pymilvus connection.
  MILVUS_PORT              Optional Milvus port for pymilvus connection.
  MILVUS_USER              Optional Milvus username.
  MILVUS_PASSWORD          Optional Milvus password (not logged).

Options:
  --dry-run                Print actions without executing commands or writing backup data.
  --backup-parent PATH     Parent directory for timestamped backup directory.
  --run-milvus-backup-tool Run configured milvus-backup create/check commands.
  --run-nginx-test         Run nginx -t validation.
  --run-nginx-dump         Run nginx -T full config dump.
  -h, --help               Show help.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --backup-parent) BACKUP_PARENT="${2:?missing --backup-parent value}"; shift ;;
    --run-milvus-backup-tool) RUN_MILVUS_BACKUP_TOOL=1 ;;
    --run-nginx-test) RUN_NGINX_TEST=1 ;;
    --run-nginx-dump) RUN_NGINX_DUMP=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_ROOT="${BACKUP_ROOT:-${BACKUP_PARENT}/pre-genesis-${STAMP}}"
export BACKUP_ROOT
LOG_DIR="$BACKUP_ROOT/logs"
MAIN_LOG="$LOG_DIR/ai_production_backup.log"

log() { printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$MAIN_LOG"; }
run() {
  log "+ $*"
  if [[ "$DRY_RUN" -eq 1 ]]; then return 0; fi
  "$@"
}
require_cmd() { command -v "$1" >/dev/null 2>&1 || { log "ERROR: required command not found: $1"; exit 1; }; }
run_sensitive() {
  local description="$1"
  shift
  log "+ ${description}"
  if [[ "$DRY_RUN" -eq 1 ]]; then return 0; fi
  "$@"
}

on_error() { log "ERROR: backup stopped at line $1. No cutover/service-changing action was requested by this script."; }
trap 'on_error $LINENO' ERR

if [[ "$DRY_RUN" -eq 1 ]]; then
  mkdir -p /tmp/ai-production-backup-dry-run-logs
  LOG_DIR=/tmp/ai-production-backup-dry-run-logs
  MAIN_LOG="$LOG_DIR/ai_production_backup.log"
fi
mkdir -p "$LOG_DIR"
log "Starting backup evidence collection for ${TARGET_DOMAIN}; dry_run=${DRY_RUN}; backup_root=${BACKUP_ROOT}"
log "Safety rules: NO CUTOVER. NO SERVICE INTERRUPTION. NO DATA CHANGE."

preflight() {
  log "Preflight checks"
  for cmd in date find sort sha256sum awk sed hostname df free uptime docker; do require_cmd "$cmd"; done
  [[ -d "$APP_ROOT" ]] || { log "ERROR: APP_ROOT does not exist: $APP_ROOT"; exit 1; }
  [[ -f "$APP_ROOT/docker-compose.yml" ]] || { log "ERROR: compose file missing: $APP_ROOT/docker-compose.yml"; exit 1; }
  if command -v getent >/dev/null 2>&1; then run getent hosts "$TARGET_DOMAIN" > "$BACKUP_ROOT/manifests/target_dns.txt"; fi
}

init_dirs() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    mkdir -p "$BACKUP_ROOT"/{postgresql,milvus,minio,n8n,wecom,nginx,docker,manifests,logs,checksums}
    log "+ install -d -m 0700 $BACKUP_ROOT/{postgresql,milvus,minio,n8n,wecom,nginx,docker,manifests,logs,checksums}"
  else
    install -d -m 0700 "$BACKUP_ROOT"/{postgresql,milvus,minio,n8n,wecom,nginx,docker,manifests,logs,checksums}
  fi
}

capture_host() {
  run hostnamectl > "$BACKUP_ROOT/manifests/host_identity.txt" || true
  run date -u +%Y-%m-%dT%H:%M:%SZ > "$BACKUP_ROOT/manifests/backup_started_at_utc.txt"
  run df -h > "$BACKUP_ROOT/manifests/disk_free_before.txt"
  run free -h > "$BACKUP_ROOT/manifests/memory_before.txt"
  run uptime > "$BACKUP_ROOT/manifests/uptime_before.txt"
}

backup_postgresql() {
  log "PostgreSQL backup"
  [[ -n "${POSTGRES_URL:-}" ]] || { log "ERROR: POSTGRES_URL is required"; exit 1; }
  require_cmd psql; require_cmd pg_dump; require_cmd pg_dumpall; require_cmd pg_restore
  : "${POSTGRES_ADMIN_URL:=$POSTGRES_URL}"
  run_sensitive "psql POSTGRES_URL -Atc" psql "$POSTGRES_URL" -Atc 'select version();' > "$BACKUP_ROOT/postgresql/version.txt"
  run_sensitive "psql POSTGRES_URL -Atc" psql "$POSTGRES_URL" -Atc "select datname from pg_database where datistemplate = false order by datname;" > "$BACKUP_ROOT/postgresql/databases.txt"
  run_sensitive "pg_dump POSTGRES_URL" pg_dump "$POSTGRES_URL" --format=custom --blobs --verbose --file="$BACKUP_ROOT/postgresql/database_full.dump" 2> "$BACKUP_ROOT/logs/postgresql_pg_dump_full.log"
  run_sensitive "pg_dump POSTGRES_URL" pg_dump "$POSTGRES_URL" --schema-only --no-owner --no-privileges --file="$BACKUP_ROOT/postgresql/schema.sql" 2> "$BACKUP_ROOT/logs/postgresql_pg_dump_schema.log"
  run_sensitive "pg_dumpall POSTGRES_ADMIN_URL" pg_dumpall "$POSTGRES_ADMIN_URL" --roles-only --no-role-passwords --file="$BACKUP_ROOT/postgresql/roles_no_passwords.sql" 2> "$BACKUP_ROOT/logs/postgresql_roles.log"
  run_sensitive "psql POSTGRES_URL -Atc" psql "$POSTGRES_URL" -Atc "select grantee, table_schema, table_name, privilege_type from information_schema.role_table_grants order by grantee, table_schema, table_name, privilege_type;" > "$BACKUP_ROOT/postgresql/table_grants.tsv"
  run pg_restore --list "$BACKUP_ROOT/postgresql/database_full.dump" > "$BACKUP_ROOT/postgresql/database_full.dump.list"
}

backup_milvus() {
  log "Milvus metadata/state backup"
  require_cmd python3
  if [[ "$DRY_RUN" -eq 0 ]]; then
    python3 - <<'PY' > "$BACKUP_ROOT/milvus/collections_detail.json"
import json, os
from pymilvus import connections, Collection, utility
kwargs = {"alias": "default", "host": os.getenv("MILVUS_HOST", "localhost"), "port": os.getenv("MILVUS_PORT", "19530")}
if os.getenv("MILVUS_USER"): kwargs["user"] = os.getenv("MILVUS_USER")
if os.getenv("MILVUS_PASSWORD"): kwargs["password"] = os.getenv("MILVUS_PASSWORD")
connections.connect(**kwargs)
result = []
for name in utility.list_collections():
    c = Collection(name)
    result.append({"name": name, "schema": c.schema.to_dict(), "indexes": [idx.to_dict() for idx in c.indexes], "partitions": [p.name for p in c.partitions]})
print(json.dumps(result, ensure_ascii=False, indent=2))
PY
    python3 - <<'PY' > "$BACKUP_ROOT/milvus/metadata.json"
import json
from pathlib import Path
items = json.loads(Path(__import__('os').environ['BACKUP_ROOT'] + '/milvus/collections_detail.json').read_text())
print(json.dumps({"collections": [i["name"] for i in items]}, ensure_ascii=False, indent=2))
PY
  else log "DRY-RUN: would export Milvus collection metadata using pymilvus"; fi
  if [[ "$RUN_MILVUS_BACKUP_TOOL" -eq 1 ]]; then require_cmd milvus-backup; run milvus-backup create --name "pre-genesis-${STAMP}" 2> "$BACKUP_ROOT/logs/milvus_backup.log"; run milvus-backup check > "$BACKUP_ROOT/milvus/backup_tool_check.txt" 2> "$BACKUP_ROOT/logs/milvus_backup_check.log"; fi
}

backup_minio() {
  log "MinIO objects/config backup"
  require_cmd mc
  [[ -n "${MINIO_ENDPOINT:-}" && -n "${MINIO_ACCESS_KEY:-}" && -n "${MINIO_SECRET_KEY:-}" ]] || { log "ERROR: MINIO_ENDPOINT, MINIO_ACCESS_KEY, and MINIO_SECRET_KEY are required"; exit 1; }
  run_sensitive "mc alias set prod-minio MINIO_ENDPOINT MINIO_ACCESS_KEY <redacted> --api S3v4" mc alias set prod-minio "$MINIO_ENDPOINT" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY" --api S3v4 >/dev/null
  run mc ls prod-minio > "$BACKUP_ROOT/minio/buckets.txt"
  if [[ "$DRY_RUN" -eq 0 ]]; then
    while read -r bucket_line; do
      bucket="$(printf '%s' "$bucket_line" | awk '{print $NF}' | sed 's#/$##')"; [[ -n "$bucket" ]] || continue
      install -d -m 0700 "$BACKUP_ROOT/minio/buckets/$bucket" "$BACKUP_ROOT/minio/objects/$bucket"
      mc stat "prod-minio/$bucket" > "$BACKUP_ROOT/minio/buckets/$bucket/stat.txt" || true
      mc anonymous get "prod-minio/$bucket" > "$BACKUP_ROOT/minio/buckets/$bucket/anonymous_policy.txt" || true
      mc version info "prod-minio/$bucket" > "$BACKUP_ROOT/minio/buckets/$bucket/versioning.txt" || true
      mc ilm export "prod-minio/$bucket" > "$BACKUP_ROOT/minio/buckets/$bucket/lifecycle.json" || true
      mc ls --recursive --versions "prod-minio/$bucket" > "$BACKUP_ROOT/minio/buckets/$bucket/object_inventory.txt" || true
      mc mirror --preserve --watch=false "prod-minio/$bucket" "$BACKUP_ROOT/minio/objects/$bucket" 2> "$BACKUP_ROOT/logs/minio_mirror_${bucket}.log"
    done < "$BACKUP_ROOT/minio/buckets.txt"
    find "$BACKUP_ROOT/minio/objects" -type f | sort > "$BACKUP_ROOT/minio/object_files.txt"
  else log "DRY-RUN: would inventory and mirror each MinIO bucket"; fi
}

backup_n8n() {
  log "n8n workflow export"
  compose=(docker compose -f "$APP_ROOT/docker-compose.yml")
  run "${compose[@]}" exec -T n8n n8n --version > "$BACKUP_ROOT/n8n/version.txt"
  run "${compose[@]}" exec -T n8n n8n export:workflow --all --output=/tmp/n8n-workflows.json
  cid="$(${compose[@]} ps -q n8n)"; [[ -n "$cid" ]] || { log "ERROR: n8n container not found"; exit 1; }
  run docker cp "${cid}:/tmp/n8n-workflows.json" "$BACKUP_ROOT/n8n/workflows.json"
  run "${compose[@]}" exec -T n8n n8n export:credentials --all --output=/tmp/n8n-credentials-encrypted.json
  run docker cp "${cid}:/tmp/n8n-credentials-encrypted.json" "$BACKUP_ROOT/n8n/credentials_encrypted.json"
  run chmod 0600 "$BACKUP_ROOT/n8n/credentials_encrypted.json"
  if [[ "$DRY_RUN" -eq 0 ]]; then python3 - "$BACKUP_ROOT/n8n/credentials_encrypted.json" > "$BACKUP_ROOT/n8n/credentials_metadata_redacted.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1], encoding='utf-8'))
items=data if isinstance(data, list) else data.get('data', []) if isinstance(data, dict) else []
print(json.dumps([{k:i.get(k) for k in ('id','name','type','createdAt','updatedAt')} for i in items], ensure_ascii=False, indent=2))
PY
  fi
}

backup_wecom() {
  log "WeCom configuration reference backup"
  run find "$APP_ROOT" -maxdepth 4 -type f \( -name '*.env' -o -name '*.yml' -o -name '*.yaml' -o -name '*.json' -o -name '*.toml' \) -print > "$BACKUP_ROOT/wecom/config_candidate_files.txt"
  if [[ "$DRY_RUN" -eq 0 ]]; then
    while read -r file; do awk -F= 'BEGIN { IGNORECASE=1 } /wecom|wechat|corp|agent|callback|aes|token|secret/ { key=$1; gsub(/^[[:space:]]+|[[:space:]]+$/, "", key); if (key != "") print FILENAME "\t" key "\t<redacted>" }' "$file"; done < "$BACKUP_ROOT/wecom/config_candidate_files.txt" > "$BACKUP_ROOT/wecom/secrets_inventory_redacted.tsv"
  fi
  cat > "$BACKUP_ROOT/wecom/callback_config_inventory.md" <<EOF_CALLBACK
# WeCom Callback Configuration Inventory

- Production domain: ${TARGET_DOMAIN}
- Callback URL(s): confirm from WeCom admin console and redacted deployment config.
- Token value: DO NOT RECORD; inventory location only.
- EncodingAESKey value: DO NOT RECORD; inventory location only.
- Corp secret value: DO NOT RECORD; inventory location only.
- Verification owner:
- Last verified at UTC:
- Rotation status:
EOF_CALLBACK
}

backup_nginx() {
  log "Nginx config backup"
  run install -d -m 0700 "$BACKUP_ROOT/nginx/sites-enabled"
  [[ -e /etc/nginx/sites-enabled/ai-vafox ]] && run cp -a /etc/nginx/sites-enabled/ai-vafox "$BACKUP_ROOT/nginx/sites-enabled/ai-vafox" || log "WARN: /etc/nginx/sites-enabled/ai-vafox not found"
  run readlink -f /etc/nginx/sites-enabled/ai-vafox > "$BACKUP_ROOT/nginx/ai-vafox_realpath.txt" || true
  [[ "$RUN_NGINX_DUMP" -eq 1 ]] && run nginx -T > "$BACKUP_ROOT/nginx/nginx_full_config.txt" 2> "$BACKUP_ROOT/logs/nginx_T.log" || log "Skipped nginx -T; pass --run-nginx-dump to enable"
  [[ "$RUN_NGINX_TEST" -eq 1 ]] && run nginx -t > "$BACKUP_ROOT/nginx/nginx_test.txt" 2> "$BACKUP_ROOT/logs/nginx_test.log" || log "Skipped nginx -t; pass --run-nginx-test to enable"
}

backup_docker() {
  log "Docker compose and container state backup"
  run install -d -m 0700 "$BACKUP_ROOT/docker/compose"
  run cp -a "$APP_ROOT/docker-compose.yml" "$BACKUP_ROOT/docker/compose/docker-compose.yml"
  run find "$APP_ROOT" -maxdepth 2 -type f \( -name '.env' -o -name '*.env' \) -print > "$BACKUP_ROOT/docker/env_files.txt"
  if [[ "$DRY_RUN" -eq 0 ]]; then while read -r env_file; do base="$(basename "$env_file")"; awk -F= '/^[[:space:]]*#/ { print; next } /^[[:space:]]*$/ { print; next } { key=$1; gsub(/^[[:space:]]+|[[:space:]]+$/, "", key); print key "=<redacted>" }' "$env_file" > "$BACKUP_ROOT/docker/compose/${base}.redacted"; done < "$BACKUP_ROOT/docker/env_files.txt"; fi
  run docker version > "$BACKUP_ROOT/docker/docker_version.txt"
  run docker compose -f "$APP_ROOT/docker-compose.yml" config > "$BACKUP_ROOT/docker/compose_config_resolved.txt"
  run docker compose -f "$APP_ROOT/docker-compose.yml" ps --all > "$BACKUP_ROOT/docker/compose_ps_all.txt"
  run docker images --digests > "$BACKUP_ROOT/docker/images_digests.txt"
  run docker ps --all --no-trunc > "$BACKUP_ROOT/docker/containers_all.txt"
  run docker volume ls > "$BACKUP_ROOT/docker/volumes.txt"
  run docker network ls > "$BACKUP_ROOT/docker/networks.txt"
  if [[ "$DRY_RUN" -eq 0 ]]; then docker ps -aq | while read -r cid; do [[ -n "$cid" ]] && docker inspect "$cid" > "$BACKUP_ROOT/docker/container_${cid}.inspect.json"; done; docker volume ls -q | while read -r v; do [[ -n "$v" ]] && docker volume inspect "$v" > "$BACKUP_ROOT/docker/volume_${v}.inspect.json"; done; docker network ls -q | while read -r n; do [[ -n "$n" ]] && docker network inspect "$n" > "$BACKUP_ROOT/docker/network_${n}.inspect.json"; done; fi
}

finish() {
  log "Generating checksums and report"
  run date -u +%Y-%m-%dT%H:%M:%SZ > "$BACKUP_ROOT/manifests/backup_completed_at_utc.txt"
  run df -h > "$BACKUP_ROOT/manifests/disk_free_after.txt"
  run free -h > "$BACKUP_ROOT/manifests/memory_after.txt"
  run find "$BACKUP_ROOT" -type f -print | sort > "$BACKUP_ROOT/manifests/files.txt"
  if [[ "$DRY_RUN" -eq 0 ]]; then while read -r file; do sha256sum "$file"; done < "$BACKUP_ROOT/manifests/files.txt" > "$BACKUP_ROOT/checksums/SHA256SUMS"; fi
  cat > "$BACKUP_ROOT/AI_BACKUP_REPORT.md" <<EOF_REPORT
# AI Production Backup Report

- Target: ${TARGET_DOMAIN}
- Application root: ${APP_ROOT}
- Backup root: ${BACKUP_ROOT}
- Started UTC: $(cat "$BACKUP_ROOT/manifests/backup_started_at_utc.txt" 2>/dev/null || true)
- Completed UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- Rules observed: NO CUTOVER; NO SERVICE INTERRUPTION; NO DATA CHANGE.

## Evidence

- PostgreSQL: postgresql/
- Milvus: milvus/
- MinIO: minio/
- n8n: n8n/
- WeCom references: wecom/
- Nginx: nginx/
- Docker: docker/
- Checksums: checksums/SHA256SUMS

## Operator Sign-Off

| Role | Name | UTC Timestamp | Status | Notes |
| --- | --- | --- | --- | --- |
| Backup operator |  |  |  |  |
| Production owner |  |  |  |  |
| Security reviewer |  |  |  |  |
| Genesis migration owner |  |  |  |  |
EOF_REPORT
  run chmod -R go-rwx "$BACKUP_ROOT"
  log "Backup evidence collection complete: $BACKUP_ROOT"
}

init_dirs
preflight
capture_host
backup_postgresql
backup_milvus
backup_minio
backup_n8n
backup_wecom
backup_nginx
backup_docker
finish
