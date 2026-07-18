# AI Backup Execution Plan

## Target

- **Production domain:** `ai.vafox.com`
- **Current system:** VAFOX Enterprise AI
- **Application root:** `/opt/ai-vafox`
- **Purpose:** Prepare a production-safe backup before Genesis migration.

## Non-Negotiable Rules

1. **NO CUTOVER**: This plan does not switch traffic, DNS, services, volumes, credentials, or runtime ownership.
2. **NO DATA CHANGE**: All commands must be read-only or export-only. Do not run migrations, writes, deletes, truncates, restores, reindexes, compactions, or bucket mutations.
3. **NO SERVICE INTERRUPTION**: Do not stop, restart, recreate, upgrade, or pause production services. Avoid operations that acquire exclusive locks or saturate I/O.
4. **NO SECRET EXPOSURE**: Secrets must be inventoried by location, key name, owner, and rotation status. Do not print secret values into logs, tickets, chat, or this backup report.
5. **PRODUCTION CHANGE FREEZE**: Run during an approved backup window with monitoring active and rollback contacts online.

## Backup Objectives

The backup must capture enough information to reconstruct the current production state before Genesis migration while preserving service continuity:

- PostgreSQL database dumps, schemas, roles, grants, and user inventory.
- Milvus collections, collection schemas, indexes, partitions, aliases, and metadata.
- MinIO bucket inventory, bucket policies, lifecycle/config metadata, and object data.
- n8n workflows and credentials metadata without exposing credential secrets.
- WeCom callback configuration and secrets inventory without exposing secret values.
- Nginx site configuration for `ai.vafox.com`.
- Docker Compose definition, image inventory, container state, volumes, networks, and runtime metadata.

## Backup Location and Naming

Use a dedicated backup directory on a host volume with sufficient free space:

```bash
export BACKUP_ROOT="/opt/ai-vafox/backups/pre-genesis-$(date -u +%Y%m%dT%H%M%SZ)"
install -d -m 0700 "$BACKUP_ROOT"/{postgresql,milvus,minio,n8n,wecom,nginx,docker,manifests,logs,checksums}
```

Expected output structure:

```text
$BACKUP_ROOT/
├── postgresql/
├── milvus/
├── minio/
├── n8n/
├── wecom/
├── nginx/
├── docker/
├── manifests/
├── logs/
└── checksums/
```

## Pre-Flight Safety Checklist

Complete these checks before collecting backups:

1. Confirm the target host is the production host for `ai.vafox.com`.
2. Confirm the active application root is `/opt/ai-vafox`.
3. Confirm no Genesis cutover, migration, deployment, restore, or schema change is scheduled during the backup window.
4. Confirm disk space is sufficient for PostgreSQL dump, MinIO objects, Milvus metadata/export, Docker metadata, and compressed artifacts.
5. Confirm monitoring dashboards are open for CPU, memory, disk I/O, network I/O, PostgreSQL connections, MinIO health, Milvus health, n8n health, and Nginx response codes.
6. Confirm credentials for read-only backup access are available through the approved secret manager.
7. Confirm all shell history logging that could capture secret values is disabled or sanitized.
8. Confirm backup operators will not paste secret values into command lines when safer file-based or environment-based methods are available.

Suggested read-only environment capture:

```bash
hostnamectl > "$BACKUP_ROOT/manifests/host_identity.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$BACKUP_ROOT/manifests/backup_started_at_utc.txt"
df -h > "$BACKUP_ROOT/manifests/disk_free_before.txt"
free -h > "$BACKUP_ROOT/manifests/memory_before.txt"
uptime > "$BACKUP_ROOT/manifests/uptime_before.txt"
```

## 1. PostgreSQL Backup

### Scope

- Full logical database dump.
- Schema-only dump.
- Role/user dump.
- Grants, extensions, database metadata, and version information.

### Safety Requirements

- Use `pg_dump` and `pg_dumpall --roles-only`; do not run write queries.
- Prefer a read-only backup user when available.
- Use custom-format dumps for restore flexibility.
- Avoid `--clean` and restore-oriented destructive flags during backup capture.

### Execution Steps

1. Identify the PostgreSQL container, host, port, database name, and read-only backup credential source from `/opt/ai-vafox` deployment configuration.
2. Capture server version and database list:

```bash
psql "$POSTGRES_URL" -Atc 'select version();' > "$BACKUP_ROOT/postgresql/version.txt"
psql "$POSTGRES_URL" -Atc "select datname from pg_database where datistemplate = false order by datname;" > "$BACKUP_ROOT/postgresql/databases.txt"
```

3. Create full logical dump:

```bash
pg_dump "$POSTGRES_URL" \
  --format=custom \
  --blobs \
  --verbose \
  --file="$BACKUP_ROOT/postgresql/database_full.dump" \
  2> "$BACKUP_ROOT/logs/postgresql_pg_dump_full.log"
```

4. Create schema-only dump:

```bash
pg_dump "$POSTGRES_URL" \
  --schema-only \
  --no-owner \
  --no-privileges \
  --file="$BACKUP_ROOT/postgresql/schema.sql" \
  2> "$BACKUP_ROOT/logs/postgresql_pg_dump_schema.log"
```

5. Capture users and roles without passwords:

```bash
pg_dumpall "$POSTGRES_ADMIN_URL" \
  --roles-only \
  --no-role-passwords \
  --file="$BACKUP_ROOT/postgresql/roles_no_passwords.sql" \
  2> "$BACKUP_ROOT/logs/postgresql_roles.log"
```

6. Capture grants and ownership metadata for review:

```bash
psql "$POSTGRES_URL" -Atc "
select grantee, table_schema, table_name, privilege_type
from information_schema.role_table_grants
order by grantee, table_schema, table_name, privilege_type;
" > "$BACKUP_ROOT/postgresql/table_grants.tsv"
```

### Validation

```bash
pg_restore --list "$BACKUP_ROOT/postgresql/database_full.dump" > "$BACKUP_ROOT/postgresql/database_full.dump.list"
test -s "$BACKUP_ROOT/postgresql/database_full.dump"
test -s "$BACKUP_ROOT/postgresql/schema.sql"
test -s "$BACKUP_ROOT/postgresql/roles_no_passwords.sql"
```

## 2. Milvus Backup

### Scope

- Collection names.
- Collection schemas.
- Index definitions.
- Partition names.
- Aliases.
- Metadata required to recreate vector storage layout.

### Safety Requirements

- Do not drop, compact, load, release, rebuild, or mutate collections.
- Use Milvus backup/export tooling in read-only mode when available.
- If the Milvus Backup Tool is configured, run only a backup operation to a dedicated backup path or object store prefix.

### Execution Steps

1. Identify Milvus endpoint, authentication method, and object storage backend from `/opt/ai-vafox` Docker Compose and environment configuration.
2. Capture Milvus service metadata:

```bash
python3 - <<'PY' > "$BACKUP_ROOT/milvus/metadata.json"
import json
from pymilvus import connections, utility

connections.connect(alias="default")
collections = utility.list_collections()
print(json.dumps({"collections": collections}, ensure_ascii=False, indent=2))
PY
```

3. Capture detailed collection definitions using an approved Milvus client script:

```bash
python3 - <<'PY' > "$BACKUP_ROOT/milvus/collections_detail.json"
import json
from pymilvus import connections, Collection, utility

connections.connect(alias="default")
result = []
for name in utility.list_collections():
    c = Collection(name)
    result.append({
        "name": name,
        "schema": c.schema.to_dict(),
        "indexes": [idx.to_dict() for idx in c.indexes],
        "partitions": [p.name for p in c.partitions],
    })
print(json.dumps(result, ensure_ascii=False, indent=2))
PY
```

4. If Milvus Backup Tool is installed and already configured, create a named backup without changing collection state:

```bash
milvus-backup create \
  --name "pre-genesis-$(date -u +%Y%m%dT%H%M%SZ)" \
  2> "$BACKUP_ROOT/logs/milvus_backup.log"
```

5. Record the Milvus backup tool configuration with secrets redacted:

```bash
milvus-backup check > "$BACKUP_ROOT/milvus/backup_tool_check.txt" 2> "$BACKUP_ROOT/logs/milvus_backup_check.log"
```

### Validation

```bash
test -s "$BACKUP_ROOT/milvus/metadata.json"
test -s "$BACKUP_ROOT/milvus/collections_detail.json"
```

## 3. MinIO Backup

### Scope

- Bucket list.
- Bucket policies and lifecycle/configuration metadata.
- Object data.
- Object inventory and checksums where practical.

### Safety Requirements

- Use `mc mirror` or equivalent read-only object copy from production to backup storage.
- Do not delete destination files with production-derived commands unless destination is isolated and empty.
- Do not change bucket policies, lifecycle rules, retention settings, or object locks.

### Execution Steps

1. Configure a temporary MinIO client alias from approved secret storage without printing secrets:

```bash
mc alias set prod-minio "$MINIO_ENDPOINT" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY" --api S3v4
```

2. Capture bucket inventory:

```bash
mc ls prod-minio > "$BACKUP_ROOT/minio/buckets.txt"
```

3. For each bucket, capture bucket metadata and mirror objects:

```bash
while read -r bucket_line; do
  bucket="$(printf '%s' "$bucket_line" | awk '{print $NF}' | sed 's#/$##')"
  [ -n "$bucket" ] || continue

  mkdir -p "$BACKUP_ROOT/minio/buckets/$bucket"
  mc stat "prod-minio/$bucket" > "$BACKUP_ROOT/minio/buckets/$bucket/stat.txt" || true
  mc anonymous get "prod-minio/$bucket" > "$BACKUP_ROOT/minio/buckets/$bucket/anonymous_policy.txt" || true
  mc version info "prod-minio/$bucket" > "$BACKUP_ROOT/minio/buckets/$bucket/versioning.txt" || true
  mc ilm export "prod-minio/$bucket" > "$BACKUP_ROOT/minio/buckets/$bucket/lifecycle.json" || true
  mc ls --recursive --versions "prod-minio/$bucket" > "$BACKUP_ROOT/minio/buckets/$bucket/object_inventory.txt" || true

  install -d -m 0700 "$BACKUP_ROOT/minio/objects/$bucket"
  mc mirror --preserve --watch=false "prod-minio/$bucket" "$BACKUP_ROOT/minio/objects/$bucket" \
    2> "$BACKUP_ROOT/logs/minio_mirror_$bucket.log"
done < "$BACKUP_ROOT/minio/buckets.txt"
```

### Validation

```bash
test -s "$BACKUP_ROOT/minio/buckets.txt"
find "$BACKUP_ROOT/minio/objects" -type f | sort > "$BACKUP_ROOT/minio/object_files.txt"
```

## 4. n8n Backup

### Scope

- Workflows.
- Workflow activation metadata.
- Credentials metadata without credential secret values.
- n8n version and runtime configuration inventory.

### Safety Requirements

- Do not activate, deactivate, edit, import, or execute workflows.
- Export only; do not expose credential secrets.
- Protect exported metadata as sensitive because workflow definitions may include endpoints, headers, or business logic.

### Execution Steps

1. Identify n8n container name, data directory, encryption key location, and database backend from Docker Compose and environment files.
2. Capture n8n version:

```bash
docker compose -f /opt/ai-vafox/docker-compose.yml exec -T n8n n8n --version > "$BACKUP_ROOT/n8n/version.txt"
```

3. Export all workflows:

```bash
docker compose -f /opt/ai-vafox/docker-compose.yml exec -T n8n \
  n8n export:workflow --all --output=/tmp/n8n-workflows.json

docker cp "$(docker compose -f /opt/ai-vafox/docker-compose.yml ps -q n8n):/tmp/n8n-workflows.json" \
  "$BACKUP_ROOT/n8n/workflows.json"
```

4. Export credentials metadata only where supported by approved n8n tooling. If credential export includes encrypted secret payloads, store it encrypted and restrict access:

```bash
docker compose -f /opt/ai-vafox/docker-compose.yml exec -T n8n \
  n8n export:credentials --all --output=/tmp/n8n-credentials-encrypted.json

docker cp "$(docker compose -f /opt/ai-vafox/docker-compose.yml ps -q n8n):/tmp/n8n-credentials-encrypted.json" \
  "$BACKUP_ROOT/n8n/credentials_encrypted.json"

chmod 0600 "$BACKUP_ROOT/n8n/credentials_encrypted.json"
```

5. Create a redacted credential metadata inventory:

```bash
python3 - <<'PY' "$BACKUP_ROOT/n8n/credentials_encrypted.json" > "$BACKUP_ROOT/n8n/credentials_metadata_redacted.json"
import json, sys
path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
items = data if isinstance(data, list) else data.get('data', []) if isinstance(data, dict) else []
redacted = []
for item in items:
    redacted.append({
        'id': item.get('id'),
        'name': item.get('name'),
        'type': item.get('type'),
        'createdAt': item.get('createdAt'),
        'updatedAt': item.get('updatedAt'),
    })
print(json.dumps(redacted, ensure_ascii=False, indent=2))
PY
```

### Validation

```bash
test -s "$BACKUP_ROOT/n8n/workflows.json"
test -s "$BACKUP_ROOT/n8n/credentials_metadata_redacted.json"
```

## 5. WeCom Backup

### Scope

- Callback URL configuration.
- Callback token inventory by name/location only.
- EncodingAESKey inventory by name/location only.
- Corp ID, agent ID, application mapping, and owner metadata where allowed.
- Secret inventory including storage location, key name, owner, rotation date, and last verified date without secret values.

### Safety Requirements

- Do not print or store WeCom secret values in plain text.
- Do not update callback URLs, tokens, AES keys, apps, menus, or webhook settings.
- If values must be verified, verify by hash or presence check only in an approved secret manager.

### Execution Steps

1. Locate WeCom configuration references in `/opt/ai-vafox` without printing secret values:

```bash
find /opt/ai-vafox -maxdepth 4 -type f \
  \( -name '*.env' -o -name '*.yml' -o -name '*.yaml' -o -name '*.json' -o -name '*.toml' \) \
  -print > "$BACKUP_ROOT/wecom/config_candidate_files.txt"
```

2. Create a redacted key inventory:

```bash
while read -r file; do
  awk -F= '
    BEGIN { IGNORECASE=1 }
    /wecom|wechat|corp|agent|callback|aes|token|secret/ {
      key=$1; gsub(/^[[:space:]]+|[[:space:]]+$/, "", key);
      if (key != "") print FILENAME "\t" key "\t<redacted>"
    }
  ' "$file"
done < "$BACKUP_ROOT/wecom/config_candidate_files.txt" \
  > "$BACKUP_ROOT/wecom/secrets_inventory_redacted.tsv"
```

3. Capture callback endpoint metadata without secret values:

```bash
cat > "$BACKUP_ROOT/wecom/callback_config_inventory.md" <<'EOF_CALLBACK'
# WeCom Callback Configuration Inventory

- Production domain: ai.vafox.com
- Callback URL(s): to be confirmed from WeCom admin console and redacted deployment config.
- Token value: DO NOT RECORD; inventory location only.
- EncodingAESKey value: DO NOT RECORD; inventory location only.
- Corp secret value: DO NOT RECORD; inventory location only.
- Verification owner:
- Last verified at UTC:
- Rotation status:
EOF_CALLBACK
```

4. If WeCom admin console screenshots or exports are required, store them in the restricted backup folder and redact secret values before sharing outside the backup operator group.

### Validation

```bash
test -s "$BACKUP_ROOT/wecom/config_candidate_files.txt"
test -s "$BACKUP_ROOT/wecom/secrets_inventory_redacted.tsv"
test -s "$BACKUP_ROOT/wecom/callback_config_inventory.md"
```

## 6. Nginx Backup

### Scope

- `/etc/nginx/sites-enabled/ai-vafox`
- Referenced site files, upstream snippets, included TLS/proxy snippets, and syntax status.

### Safety Requirements

- Do not reload or restart Nginx.
- Use `nginx -t` for validation only if it is known to be safe in this environment.
- Do not modify certificates, symlinks, enabled sites, or upstream targets.

### Execution Steps

```bash
install -d -m 0700 "$BACKUP_ROOT/nginx/sites-enabled"
cp -a /etc/nginx/sites-enabled/ai-vafox "$BACKUP_ROOT/nginx/sites-enabled/ai-vafox"
readlink -f /etc/nginx/sites-enabled/ai-vafox > "$BACKUP_ROOT/nginx/ai-vafox_realpath.txt" || true
nginx -T > "$BACKUP_ROOT/nginx/nginx_full_config.txt" 2> "$BACKUP_ROOT/logs/nginx_T.log"
nginx -t > "$BACKUP_ROOT/nginx/nginx_test.txt" 2> "$BACKUP_ROOT/logs/nginx_test.log"
```

### Validation

```bash
test -s "$BACKUP_ROOT/nginx/sites-enabled/ai-vafox"
test -s "$BACKUP_ROOT/nginx/nginx_full_config.txt"
```

## 7. Docker Backup

### Scope

- Docker Compose file and related `.env` inventory.
- Image list and image digests.
- Container state and inspect metadata.
- Volumes, networks, ports, mounts, restart policies, and health checks.

### Safety Requirements

- Do not run `docker compose down`, `up`, `restart`, `pull`, `build`, `prune`, `rm`, or `stop`.
- Do not print secret values from `.env` files into shared reports.
- Use inspect and listing commands only.

### Execution Steps

1. Copy Compose files and create redacted environment inventories:

```bash
install -d -m 0700 "$BACKUP_ROOT/docker/compose"
cp -a /opt/ai-vafox/docker-compose.yml "$BACKUP_ROOT/docker/compose/docker-compose.yml"
find /opt/ai-vafox -maxdepth 2 -type f \( -name '.env' -o -name '*.env' \) -print \
  > "$BACKUP_ROOT/docker/env_files.txt"

while read -r env_file; do
  base="$(basename "$env_file")"
  awk -F= '
    /^[[:space:]]*#/ { print; next }
    /^[[:space:]]*$/ { print; next }
    {
      key=$1; gsub(/^[[:space:]]+|[[:space:]]+$/, "", key);
      print key "=<redacted>"
    }
  ' "$env_file" > "$BACKUP_ROOT/docker/compose/${base}.redacted"
done < "$BACKUP_ROOT/docker/env_files.txt"
```

2. Capture Docker image and container inventory:

```bash
docker version > "$BACKUP_ROOT/docker/docker_version.txt"
docker compose -f /opt/ai-vafox/docker-compose.yml config > "$BACKUP_ROOT/docker/compose_config_resolved.txt"
docker compose -f /opt/ai-vafox/docker-compose.yml ps --all > "$BACKUP_ROOT/docker/compose_ps_all.txt"
docker images --digests > "$BACKUP_ROOT/docker/images_digests.txt"
docker ps --all --no-trunc > "$BACKUP_ROOT/docker/containers_all.txt"
docker volume ls > "$BACKUP_ROOT/docker/volumes.txt"
docker network ls > "$BACKUP_ROOT/docker/networks.txt"
```

3. Capture inspect metadata:

```bash
docker ps -aq | while read -r cid; do
  [ -n "$cid" ] || continue
  docker inspect "$cid" > "$BACKUP_ROOT/docker/container_${cid}.inspect.json"
done

docker volume ls -q | while read -r volume; do
  [ -n "$volume" ] || continue
  docker volume inspect "$volume" > "$BACKUP_ROOT/docker/volume_${volume}.inspect.json"
done

docker network ls -q | while read -r network; do
  [ -n "$network" ] || continue
  docker network inspect "$network" > "$BACKUP_ROOT/docker/network_${network}.inspect.json"
done
```

### Validation

```bash
test -s "$BACKUP_ROOT/docker/compose/docker-compose.yml"
test -s "$BACKUP_ROOT/docker/images_digests.txt"
test -s "$BACKUP_ROOT/docker/containers_all.txt"
```

## Integrity, Packaging, and Access Control

1. Generate file manifest and checksums:

```bash
find "$BACKUP_ROOT" -type f -print | sort > "$BACKUP_ROOT/manifests/files.txt"
while read -r file; do
  sha256sum "$file"
done < "$BACKUP_ROOT/manifests/files.txt" > "$BACKUP_ROOT/checksums/SHA256SUMS"
```

2. Record backup completion state:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ > "$BACKUP_ROOT/manifests/backup_completed_at_utc.txt"
df -h > "$BACKUP_ROOT/manifests/disk_free_after.txt"
free -h > "$BACKUP_ROOT/manifests/memory_after.txt"
```

3. Restrict permissions:

```bash
chmod -R go-rwx "$BACKUP_ROOT"
```

4. Optional encrypted archive for transfer to approved storage:

```bash
tar -C "$(dirname "$BACKUP_ROOT")" -czf "${BACKUP_ROOT}.tar.gz" "$(basename "$BACKUP_ROOT")"
sha256sum "${BACKUP_ROOT}.tar.gz" > "${BACKUP_ROOT}.tar.gz.sha256"
```

If encryption is required, use the organization-approved encryption workflow and store keys only in the approved secret manager.

## Restore Readiness Review

Do not restore into production during this plan. For readiness only, review the following in an isolated non-production environment:

- PostgreSQL dump list is readable with `pg_restore --list`.
- PostgreSQL schema dump parses in a disposable database.
- Milvus collection metadata is complete enough to recreate schemas, indexes, partitions, and aliases.
- MinIO object inventory count aligns with mirrored file count or documented exclusions.
- n8n workflow export is valid JSON and credentials metadata is present.
- WeCom callback and secret inventory identifies all required values by owner and storage location.
- Nginx site config and full `nginx -T` capture are present.
- Docker Compose, resolved Compose config, images, containers, volumes, and networks are captured.

## Abort Criteria

Abort the backup immediately and notify the production owner if any of the following occurs:

- Increased 5xx rate or degraded `ai.vafox.com` availability.
- PostgreSQL connection exhaustion, lock contention, or I/O saturation.
- MinIO or Milvus health check degradation.
- Disk free space falls below the approved production threshold.
- Backup commands require service restart, downtime, schema mutation, credential rotation, or cutover activity.
- Any secret value is accidentally written to an unsafe location.

## Completion Evidence

The backup is complete only when all evidence below exists:

- `$BACKUP_ROOT/postgresql/database_full.dump`
- `$BACKUP_ROOT/postgresql/schema.sql`
- `$BACKUP_ROOT/postgresql/roles_no_passwords.sql`
- `$BACKUP_ROOT/milvus/collections_detail.json`
- `$BACKUP_ROOT/minio/buckets.txt`
- `$BACKUP_ROOT/minio/object_files.txt`
- `$BACKUP_ROOT/n8n/workflows.json`
- `$BACKUP_ROOT/n8n/credentials_metadata_redacted.json`
- `$BACKUP_ROOT/wecom/secrets_inventory_redacted.tsv`
- `$BACKUP_ROOT/nginx/sites-enabled/ai-vafox`
- `$BACKUP_ROOT/docker/compose/docker-compose.yml`
- `$BACKUP_ROOT/docker/images_digests.txt`
- `$BACKUP_ROOT/docker/containers_all.txt`
- `$BACKUP_ROOT/checksums/SHA256SUMS`

## Operator Sign-Off

| Role | Name | UTC Timestamp | Status | Notes |
| --- | --- | --- | --- | --- |
| Backup operator |  |  |  |  |
| Production owner |  |  |  |  |
| Security reviewer |  |  |  |  |
| Genesis migration owner |  |  |  |  |
