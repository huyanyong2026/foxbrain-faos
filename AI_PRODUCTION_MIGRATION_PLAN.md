# AI Production Migration Plan — ai.vafox.com Genesis Migration Audit

Date: 2026-07-18 UTC  
Target domain: `ai.vafox.com`  
Target server: `1.13.254.217`  
Current production directory to audit: `/opt/ai-vafox`  
Current runtime family: legacy Dify AI runtime  
Target runtime family: VAFOX AI Workforce / `AI-OS-V6-CLEAN-REBUILD-V1`  
Cutover status: **NOT STARTED — AUDIT AND PLAN ONLY**

## 1. Executive summary

This document is the first-phase migration audit and implementation plan for upgrading `ai.vafox.com` from the current legacy Dify-centered employee AI experience to the VAFOX Genesis Workforce Home architecture.

No production cutover is approved by this plan. The first production action must be evidence capture from `/opt/ai-vafox`, `/etc/nginx/sites-enabled/ai-vafox`, Docker, volumes, backups, exposed ports, and runtime health. The current Dify, n8n, PostgreSQL, Milvus, MinIO, Redis, WeCom bot, workflows, knowledge assets, and persisted data must remain intact until backups are verified and rollback has been tested.

## 2. Non-destructive preservation rules

The migration must not delete, truncate, reinitialize, or detach the following production assets:

- PostgreSQL data, including Dify metadata, application metadata, user/workspace configuration, and n8n database content if PostgreSQL-backed.
- Milvus data, including vector collections, indexes, partitions, and insert logs.
- MinIO data, including uploaded knowledge files, Dify datasets/documents, workflow files, and object buckets.
- n8n workflows, credentials, execution history needed for operations, and `.n8n` storage.
- Knowledge assets, uploaded documents, dataset metadata, embeddings, and object storage references.
- Redis persistence if append-only or RDB data is used by the current runtime.
- WeCom bot configuration, webhook secrets, message templates, and callback routes.

Any command that could remove volumes or data is prohibited during audit and pre-cutover work, including `docker compose down -v`, `docker volume rm`, `docker system prune --volumes`, manual deletion under `/var/lib/docker/volumes`, manual deletion under `/opt/ai-vafox`, and database recreation commands.

## 3. Current architecture to verify on production

The supplied production inventory states that `/opt/ai-vafox` currently runs these services:

| Layer | Current service | Primary audit objective | Preservation requirement |
|---|---|---|---|
| Web UI | Dify Web | Confirm image tag, container name, upstream port, env, and public routes. | Keep legacy web available for rollback. |
| API | Dify API | Confirm image tag, API port, database DSN, storage backend, and worker coupling. | Keep API config and DB references unchanged until migration validation. |
| Worker | Dify Worker | Confirm queues, Redis binding, model provider env, and dataset jobs. | Do not interrupt active ingestion jobs during backup. |
| Vector DB | Milvus | Confirm standalone/cluster mode, bind mounts/volumes, collection count, index state. | Snapshot data before any Dify upgrade or app switch. |
| Object store | MinIO | Confirm buckets, lifecycle rules, access keys, volume path, and console exposure. | Preserve buckets and credentials; take bucket inventory. |
| Relational DB | PostgreSQL | Confirm database names, users, volume path, size, and extensions. | Take logical and physical backup before cutover. |
| Cache/queue | Redis | Confirm persistence mode, volume path, maxmemory, and queue keys. | Preserve AOF/RDB if configured. |
| Automation | n8n | Confirm image tag, persistence mode, workflows, credentials, webhook URLs. | Export workflows and preserve credentials storage. |
| Integration | WeCom bot | Confirm container/process, webhook paths, env secrets, callback URLs. | Preserve env and routing; no secret rotation during audit. |
| Edge | Nginx | Confirm `/etc/nginx/sites-enabled/ai-vafox`, SSL paths, upstreams, route precedence. | Copy config before editing; cutover by switchable include/upstream only. |

## 4. Target architecture baseline

The target `ai.vafox.com` experience is VAFOX Workforce Home under `AI-OS-V6-CLEAN-REBUILD-V1`. Repository architecture defines `ai.vafox.com` as the Workforce Home for employees and active internal operating roles, organizing daily work, mission context, AI assistance, learning, and growth into a mobile-first employee operating surface.

The target runtime should preserve Gateway-owned identity boundaries: users should enter through `gateway.vafox.com`, then be routed to `ai.vafox.com` by verified identity, role, permission, and mission context. Local login flows on the Workforce Home should remain disabled or subordinate to Gateway session context.

Target home areas:

- Today: short operating-day summary, tasks, priorities, reminders, assigned work, and alerts.
- Mission: connection between daily work and VAFOX business objectives.
- AI Companion: contextual help, summarization, next-step suggestions, and guided task support without bypassing permissions.
- Learning: role-relevant guides, onboarding, operating content, and skill development.
- Growth: transparent personal development and performance-support prompts.

## 5. Current vs target comparison

| Topic | Current Dify runtime | Target VAFOX Workforce / Genesis | Migration implication |
|---|---|---|---|
| Product entry | General Dify web application and chat/workspace UX. | VAFOX Workforce Home first, with AI Companion embedded into employee context. | Public `/` should eventually route to Workforce Home, not Dify console. |
| Identity | Likely Dify-local users plus possible reverse-proxy auth or custom employee flow. | Gateway-owned VID, role, department, store, team, permission, and growth context. | Preserve Dify accounts, but do not make Dify the long-term identity root. |
| Knowledge | Dify datasets backed by PostgreSQL, MinIO, Milvus, and workers. | Knowledge assets remain available to Workforce AI through approved adapters. | No dataset rebuild until backups and export inventory are verified. |
| Automation | n8n and WeCom integrated with legacy AI flows. | n8n and WeCom continue as operational integration services. | Keep `/n8n`, webhook, and WeCom routes stable during UI switch. |
| Data layer | PostgreSQL, Milvus, MinIO, Redis coupled to Dify runtime. | Preserve Dify data while adding Genesis app layer and adapters. | Run side-by-side first; do not replace data services in-place. |
| Nginx routing | Existing `/etc/nginx/sites-enabled/ai-vafox` likely routes root/API/console/Dify/n8n/WeCom. | Workforce routes should proxy to Genesis app while Dify admin/API routes stay reachable. | Use reversible upstream switch and explicit route priority. |
| Release | Current enterprise AI release must be confirmed on host. | `AI-OS-V6-CLEAN-REBUILD-V1`. | Health endpoint and container labels must expose version and commit. |
| Rollback | Legacy Dify should remain available. | Genesis can be disabled by reverting Nginx upstream/include and stopping new app. | Do not mutate legacy data during first cutover. |

## 6. Audit commands to run before implementation

Run these on `1.13.254.217` with sufficient privileges. They are read-only except where explicitly writing audit output files under a new timestamped audit directory.

```bash
set -euo pipefail
AUDIT_DIR="/opt/ai-vafox/audit-$(date -u +%Y%m%dT%H%M%SZ)"
sudo mkdir -p "$AUDIT_DIR"
sudo chmod 700 "$AUDIT_DIR"

cd /opt/ai-vafox
pwd | sudo tee "$AUDIT_DIR/pwd.txt"
sudo cp -a docker-compose.yml "$AUDIT_DIR/docker-compose.yml.copy"
sudo cp -a /etc/nginx/sites-enabled/ai-vafox "$AUDIT_DIR/nginx-ai-vafox.copy"

docker compose config | sudo tee "$AUDIT_DIR/docker-compose.config.txt"
docker compose ps | sudo tee "$AUDIT_DIR/docker-compose.ps.txt"
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}' | sudo tee "$AUDIT_DIR/docker-ps.txt"
docker image ls | sudo tee "$AUDIT_DIR/docker-images.txt"
docker volume ls | sudo tee "$AUDIT_DIR/docker-volumes.txt"
docker network ls | sudo tee "$AUDIT_DIR/docker-networks.txt"

sudo nginx -T | sudo tee "$AUDIT_DIR/nginx-T.txt"
sudo ss -lntup | sudo tee "$AUDIT_DIR/listening-ports.txt"
sudo du -h -d 2 /opt/ai-vafox | sudo tee "$AUDIT_DIR/du-opt-ai-vafox.txt"
sudo du -h -d 2 /var/lib/docker/volumes | sudo tee "$AUDIT_DIR/du-docker-volumes.txt"

docker inspect $(docker compose ps -q) | sudo tee "$AUDIT_DIR/docker-inspect.json"
```

Optional service-specific read-only checks after identifying service names:

```bash
# PostgreSQL inventory; replace service/user/db if compose uses different names.
docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\l+' | sudo tee "$AUDIT_DIR/postgres-databases.txt"
docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\dt+ *.*' | sudo tee "$AUDIT_DIR/postgres-tables.txt"

# MinIO inventory; use configured credentials and alias if mc exists.
docker compose exec -T minio sh -lc 'find /data -maxdepth 3 -type d | sort | head -500' | sudo tee "$AUDIT_DIR/minio-tree.txt"

# Redis persistence and keyspace summary.
docker compose exec -T redis redis-cli INFO persistence | sudo tee "$AUDIT_DIR/redis-persistence.txt"
docker compose exec -T redis redis-cli INFO keyspace | sudo tee "$AUDIT_DIR/redis-keyspace.txt"

# n8n export if n8n CLI is available in the container.
docker compose exec -T n8n n8n export:workflow --all --output=/tmp/n8n-workflows.json || true
docker compose cp n8n:/tmp/n8n-workflows.json "$AUDIT_DIR/n8n-workflows.json" || true
```

## 7. Backup plan

Create backups only after the audit confirms actual service names, database credentials, and volume names. Store backups outside the active Docker volumes, preferably under `/opt/ai-vafox/backups/<timestamp>` and a second off-host location.

Minimum backup set:

1. `docker-compose.yml`, `.env`, Nginx site config, custom scripts, WeCom bot config, and any systemd units.
2. PostgreSQL logical dump with `pg_dumpall` or per-database `pg_dump -Fc`.
3. Docker volume archive for PostgreSQL after clean checkpoint or service stop window.
4. Milvus volume archive, plus collection/index inventory.
5. MinIO bucket/object inventory and object data archive or replicated bucket backup.
6. Redis AOF/RDB files if persistence is enabled.
7. n8n workflow export and credentials persistence backup.
8. Dify app configuration, environment variables, dataset metadata, and upload storage references.

Before any cutover, restore-test at least PostgreSQL, MinIO, Milvus, and n8n workflow export on a staging host or isolated compose project. A backup that has not been restore-tested is not sufficient for production migration.

## 8. Migration approach

Use side-by-side migration instead of replacing the Dify stack in place.

### Phase A — Audit only

- Capture compose, Nginx, release, backups, volumes, ports, and data directories.
- Confirm current-enterprise-ai release using container labels, image tags, Git commit, `/version`, `/health`, or app env.
- Confirm whether public root `/` currently maps to Dify Web, a custom portal, or static Nginx content.
- Confirm all data paths and backup state.

### Phase B — Prepare Genesis app without routing public traffic

- Deploy VAFOX Workforce app on an internal-only loopback port such as `127.0.0.1:5010` or an isolated Docker network.
- Set `FOXBRAIN_VERSION=AI-OS-V6-CLEAN-REBUILD-V1`, `GIT_COMMIT`, `BUILD_TIME`, and `DEPLOY_TIME`.
- Add health/version endpoints and verify from localhost only.
- Keep Dify Web/API/Worker, Milvus, MinIO, PostgreSQL, Redis, n8n, and WeCom running unchanged.

### Phase C — Adapter and route validation

- Build read-only adapters from Genesis Workforce to legacy Dify/knowledge services where needed.
- Validate that n8n webhooks and WeCom callback routes remain untouched.
- Validate no Genesis request writes to Dify PostgreSQL, Milvus, or MinIO during first release unless explicitly approved.

### Phase D — Controlled Nginx switch

- Add a new Nginx include or upstream for Workforce Home routes.
- Route only selected frontend paths to Genesis first: `/`, `/home`, `/health/runtime`, `/health/version`, `/static/`, and Workforce-specific paths.
- Preserve legacy Dify admin/API routes such as `/console`, `/api`, `/v1`, `/files`, `/datasets`, `/workspaces`, and any existing Dify callback paths until owners approve a second migration stage.
- Preserve `/n8n` and WeCom webhook/callback routes exactly.

### Phase E — Post-cutover observation

- Watch Nginx access/error logs, application health, Dify worker queues, PostgreSQL connections, Redis queues, MinIO access, Milvus metrics, n8n executions, and WeCom callback delivery.
- Keep legacy Dify route reachable through a protected path or temporary internal hostname for operators.

## 9. Nginx switch plan

The Nginx change should be a small, reversible routing change. Do not rewrite the whole site file during cutover.

Recommended route priority:

1. ACME/Certbot challenge paths.
2. n8n webhook and UI paths.
3. WeCom callback/webhook paths.
4. Dify API/admin/data paths.
5. Genesis Workforce public home paths.
6. Static assets with cache-control appropriate to asset fingerprinting.

Example switch strategy:

```nginx
# Keep existing Dify, n8n, and WeCom locations above this block.
upstream vafox_workforce_genesis {
    server 127.0.0.1:5010;
}

location = / {
    proxy_pass http://vafox_workforce_genesis;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    add_header Cache-Control "no-store" always;
}

location ~ ^/(home|dashboard|health/version|health/runtime|version|store|supply)$ {
    proxy_pass http://vafox_workforce_genesis;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    add_header Cache-Control "no-store" always;
}
```

Validation before reload:

```bash
sudo nginx -t
curl -fsS http://127.0.0.1:5010/health/runtime
sudo systemctl reload nginx
curl -k -fsS https://ai.vafox.com/health/runtime
curl -k -I https://ai.vafox.com/
```

## 10. Rollback plan

Rollback must be possible without database restore for the first cutover, because Genesis should not mutate legacy Dify data during the first stage.

Immediate rollback steps:

1. Revert `/etc/nginx/sites-enabled/ai-vafox` to the audited copy.
2. Run `sudo nginx -t`.
3. Reload Nginx with `sudo systemctl reload nginx`.
4. Stop only the new Genesis app container/process if needed.
5. Confirm Dify root, Dify API, n8n, WeCom bot, PostgreSQL, Milvus, MinIO, Redis, and workers remain healthy.
6. Preserve incident logs and do not delete the failed Genesis deployment directory until reviewed.

Rollback verification commands:

```bash
sudo nginx -t
sudo systemctl reload nginx
docker compose ps
curl -k -I https://ai.vafox.com/
curl -k -fsS https://ai.vafox.com/health || true
```

Database restore should be required only if an approved later phase performs data writes. If restore is required, restore in this order: PostgreSQL, MinIO, Milvus, Redis, n8n, then application containers.

## 11. Required implementation steps before cutover approval

- [ ] Complete the production audit and attach the audit directory manifest.
- [ ] Confirm exact current-enterprise-ai release, image tags, Git commit, and public response headers.
- [ ] Confirm all Docker volumes and bind mounts for PostgreSQL, Milvus, MinIO, Redis, n8n, Dify, and WeCom.
- [ ] Confirm listening ports and Nginx upstream route precedence.
- [ ] Confirm recent backups and perform restore test for PostgreSQL, MinIO, Milvus, and n8n workflows.
- [ ] Deploy Genesis Workforce app internally without public route changes.
- [ ] Verify `AI-OS-V6-CLEAN-REBUILD-V1` health/version response from localhost.
- [ ] Confirm Gateway identity expectations and disable local Workforce identity roots unless explicitly approved.
- [ ] Confirm Dify, n8n, and WeCom protected routes remain reachable after staging Nginx config test.
- [ ] Prepare final Nginx switch diff and audited rollback copy.
- [ ] Schedule a low-traffic cutover window.
- [ ] Execute Nginx switch only after owner approval.

## 12. Open questions for the production audit

- Which exact compose file is active in `/opt/ai-vafox`: a Dify upstream compose, custom VAFOX compose, or a combined file?
- What exact Nginx routes are present in `/etc/nginx/sites-enabled/ai-vafox`, and which route owns `/` today?
- Which service owns `current-enterprise-ai`, and how does it expose its release version?
- Are PostgreSQL, Milvus, MinIO, Redis, and n8n using named Docker volumes, bind mounts, or external managed services?
- Are existing backups local only, off-host, or both?
- Are n8n credentials stored in SQLite, PostgreSQL, or encrypted local storage?
- Which WeCom bot endpoints must remain publicly reachable during the UI switch?
- Is there a CDN or cloud load balancer in front of `ai.vafox.com` that must be purged after Nginx reload?
