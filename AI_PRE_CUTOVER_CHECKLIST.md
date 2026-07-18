# AI Pre-Cutover Checklist

Target domain: `ai.vafox.com`  
Basis: `AI_GENESIS_IMPLEMENTATION_PLAN.md`  
Purpose: prepare a future production cutover package for `VAFOX AI Workforce` + `AI-OS-V6-CLEAN-REBUILD-V1`.

## Non-Negotiable Rules

- **NO CUTOVER.**
- **Do not modify production.**
- **Do not change DNS, nginx production routing, WeCom production callbacks, n8n production workflow active states, PostgreSQL production schema/data, Milvus production collections, or MinIO production objects.**
- Prefer staging, restored copies, read-only discovery, dry runs, exports, and evidence capture.
- Backup operations must use approved secure backup paths and owner-approved windows.
- Replace placeholders such as `<host>`, `<database_name>`, `<bucket>`, `<workflow_id>`, and `<token>` before execution.

## 1. Backup Checklist

| Pass/Fail | Item | Command | Expected result |
| --- | --- | --- | --- |
| [ ] Pass / [ ] Fail | Capture current release baseline. | `cd /opt/ai-vafox && git rev-parse HEAD && git status --short` | Commit hash is recorded, expected baseline is `fba3c17`, and working tree status is understood before any future work. |
| [ ] Pass / [ ] Fail | Capture current container inventory. | `docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' > /secure-backups/ai-vafox-containers.$(date -u +%Y%m%dT%H%M%SZ).txt` | Timestamped container inventory file exists in `/secure-backups`; production containers are not restarted or changed. |
| [ ] Pass / [ ] Fail | Capture current image inventory. | `docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}' > /secure-backups/ai-vafox-images.$(date -u +%Y%m%dT%H%M%SZ).txt` | Timestamped image inventory file exists and includes current runtime images. |
| [ ] Pass / [ ] Fail | Backup nginx rendered configuration. | `nginx -T > /secure-backups/ai-vafox-nginx.baseline.$(date -u +%Y%m%dT%H%M%SZ).conf` | Rendered nginx baseline is captured without editing or reloading nginx. |
| [ ] Pass / [ ] Fail | Validate current nginx syntax without changing routes. | `nginx -t` | Command exits successfully and reports configuration syntax is OK. |
| [ ] Pass / [ ] Fail | Backup PostgreSQL globals. | `pg_dumpall --globals-only > /secure-backups/ai-vafox-postgres-globals.$(date -u +%Y%m%dT%H%M%SZ).sql` | Globals backup file is created in secure storage and contains roles/tablespace metadata. |
| [ ] Pass / [ ] Fail | Backup PostgreSQL application database. | `pg_dump --format=custom --file=/secure-backups/ai-vafox-<database_name>.$(date -u +%Y%m%dT%H%M%SZ).dump <database_name>` | Custom-format dump exists in secure storage; no production schema or data is modified. |
| [ ] Pass / [ ] Fail | Backup Milvus with approved tooling. | `milvus-backup create --config /etc/milvus/backup.yaml --name ai-vafox-milvus-$(date -u +%Y%m%dT%H%M%SZ)` | Milvus backup job completes successfully and records collection metadata, indexes, and row counts. |
| [ ] Pass / [ ] Fail | Capture MinIO bucket inventory. | `mc ls <alias> > /secure-backups/minio-buckets.$(date -u +%Y%m%dT%H%M%SZ).txt && mc ls --recursive <alias>/<bucket> > /secure-backups/minio-<bucket>-objects.$(date -u +%Y%m%dT%H%M%SZ).txt` | Bucket and object inventories are created; no objects are deleted, rewritten, or lifecycle-modified. |
| [ ] Pass / [ ] Fail | Export n8n workflows. | `n8n export:workflow --all --output=/secure-backups/n8n-workflows.$(date -u +%Y%m%dT%H%M%SZ).json` | Workflow export file exists and includes IDs, names, active flags, nodes, and webhook paths. |
| [ ] Pass / [ ] Fail | Capture WeCom callback configuration evidence. | `printf '%s\n' '<document callback URL, token location, encoding secret location, event types, and recovery owner in the secure evidence bundle>'` | Secure evidence bundle includes callback URL, secret locations, allowed events, and recovery instructions; secrets are not pasted into the checklist. |

## 2. Data Verification Checklist

| Pass/Fail | Item | Command | Expected result |
| --- | --- | --- | --- |
| [ ] Pass / [ ] Fail | Inventory PostgreSQL databases. | `psql -XAtc "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;"` | Database list is recorded and matches known Dify, n8n, auth, and application databases. |
| [ ] Pass / [ ] Fail | Inventory PostgreSQL table row estimates. | `psql -d <database_name> -XAtc "SELECT schemaname, relname, n_live_tup FROM pg_stat_user_tables ORDER BY schemaname, relname;" > /secure-backups/postgres-row-estimates.$(date -u +%Y%m%dT%H%M%SZ).tsv` | Row-estimate file exists for later comparison with staging restore. |
| [ ] Pass / [ ] Fail | Restore PostgreSQL backup to staging only. | `pg_restore --clean --if-exists --dbname=<staging_database_name> /secure-backups/ai-vafox-<database_name>.<timestamp>.dump` | Restore succeeds against staging/restored copy only; production database remains untouched. |
| [ ] Pass / [ ] Fail | Compare staging row estimates. | `psql -d <staging_database_name> -XAtc "SELECT schemaname, relname, n_live_tup FROM pg_stat_user_tables ORDER BY schemaname, relname;"` | Critical staging table counts are consistent with captured source inventory or documented variance. |
| [ ] Pass / [ ] Fail | Verify no destructive SQL in migration scripts. | `rg -n --ignore-case '\b(DROP\s+TABLE|DROP\s+DATABASE|TRUNCATE|DELETE\s+FROM)\b' <migration_script_or_directory>` | No destructive statements are found, or each finding is explicitly documented as safe and non-production-only before approval. |
| [ ] Pass / [ ] Fail | Inventory Milvus collections. | `python3 -m pymilvus.tools.list_collections --uri <staging_or_readonly_milvus_uri>` | Collection names, dimensions, indexes, aliases, partitions, and row counts are recorded. |
| [ ] Pass / [ ] Fail | Verify MinIO sample checksums. | `mc stat --json <alias>/<bucket>/<sample_object_key> && mc cat <alias>/<bucket>/<sample_object_key> | sha256sum` | Sample object metadata and checksum are captured and match the staging mirror sample. |
| [ ] Pass / [ ] Fail | Verify Dify dataset references. | `psql -d <staging_database_name> -XAtc "SELECT id, name FROM datasets ORDER BY name LIMIT 50;"` | Expected datasets are visible in the restored/staging metadata store. |

## 3. Service Readiness Checklist

| Pass/Fail | Item | Command | Expected result |
| --- | --- | --- | --- |
| [ ] Pass / [ ] Fail | Confirm V6 health endpoint in staging. | `curl -fsS https://<staging-host>/api/ai-workforce/health` | HTTP 200 response reports healthy service status. |
| [ ] Pass / [ ] Fail | Confirm V6 release identity. | `curl -fsS https://<staging-host>/api/ai-workforce/version` | Response includes `AI-OS-V6-CLEAN-REBUILD-V1`. |
| [ ] Pass / [ ] Fail | Confirm production routes remain unchanged. | `curl -fsSI https://ai.vafox.com/ && curl -fsSI https://ai.vafox.com/auth/ && curl -fsSI https://ai.vafox.com/console && curl -fsSI https://ai.vafox.com/n8n` | Current production endpoints respond as before; no preview/V6 route is exposed by accident. |
| [ ] Pass / [ ] Fail | Confirm staging service inventory. | `docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}' | rg 'ai-workforce|ai-identity-adapter|ai-agent-router|ai-knowledge-adapter|ai-workflow-adapter|ai-wecom-adapter'` | Expected V6 staging services are running; command is executed in staging environment only. |
| [ ] Pass / [ ] Fail | Confirm staging API dependencies. | `curl -fsS https://<staging-host>/api/ai-workforce/dependencies` | Response marks PostgreSQL, Milvus, MinIO, Dify adapter, n8n adapter, and WeCom adapter as reachable or intentionally disabled for test. |

## 4. Auth Validation

| Pass/Fail | Item | Command | Expected result |
| --- | --- | --- | --- |
| [ ] Pass / [ ] Fail | Verify current auth route is stable. | `curl -fsSI https://ai.vafox.com/auth/` | Production auth route returns the expected status and redirect/header behavior; no route change is made. |
| [ ] Pass / [ ] Fail | Verify staging identity adapter health. | `curl -fsS https://<staging-host>/api/ai-workforce/auth/health` | Staging identity adapter reports healthy. |
| [ ] Pass / [ ] Fail | Validate shadow role mapping. | `curl -fsS -H 'Authorization: Bearer <staging_test_token>' https://<staging-host>/api/ai-workforce/auth/shadow-role` | Response shows current claim input and intended V6 role mapping without changing production sessions or roles. |
| [ ] Pass / [ ] Fail | Verify admin access remains preserved. | `curl -fsSI -H 'Cookie: <admin_test_session_cookie>' https://ai.vafox.com/console` | Existing admin console access behavior is unchanged. |

## 5. Agent Validation

| Pass/Fail | Item | Command | Expected result |
| --- | --- | --- | --- |
| [ ] Pass / [ ] Fail | Export Dify app metadata from staging/restored source. | `curl -fsS -H 'Authorization: Bearer <dify_staging_token>' https://<staging-dify-host>/v1/apps > /secure-backups/dify-apps.staging.$(date -u +%Y%m%dT%H%M%SZ).json` | Export succeeds from staging or approved read-only endpoint; app metadata file is captured. |
| [ ] Pass / [ ] Fail | Verify agent router health. | `curl -fsS https://<staging-host>/api/ai-workforce/agents/health` | Agent router reports healthy and connected to its app/agent registry. |
| [ ] Pass / [ ] Fail | Validate known prompt routing. | `curl -fsS -X POST https://<staging-host>/api/ai-workforce/agents/route -H 'Content-Type: application/json' -d '{"input":"<known_test_prompt>","dry_run":true}'` | Response selects the expected agent/app and marks the request as dry-run/no side effects. |
| [ ] Pass / [ ] Fail | Confirm no manual agent selection is required for employee flow. | `curl -fsS https://<staging-host>/api/ai-workforce/agents/ui-policy` | Response indicates employee flow uses inferred routing; admin diagnostics remain available separately. |

## 6. Knowledge Validation

| Pass/Fail | Item | Command | Expected result |
| --- | --- | --- | --- |
| [ ] Pass / [ ] Fail | Verify knowledge adapter health. | `curl -fsS https://<staging-host>/api/ai-workforce/knowledge/health` | Knowledge adapter reports healthy connections to staging PostgreSQL, Milvus, and MinIO. |
| [ ] Pass / [ ] Fail | Validate fixed retrieval query set. | `curl -fsS -X POST https://<staging-host>/api/ai-workforce/knowledge/query -H 'Content-Type: application/json' -d '{"query":"<known_query>","top_k":5,"dry_run":true}'` | Expected known documents appear in top-k results; no vectors or objects are rewritten. |
| [ ] Pass / [ ] Fail | Confirm vector dimensions. | `curl -fsS https://<staging-host>/api/ai-workforce/knowledge/collections` | Collection metadata shows expected dimensions, indexes, and source dataset mappings. |
| [ ] Pass / [ ] Fail | Confirm object read through staging prefix. | `mc cat <staging-alias>/<staging-bucket>/<sample_object_key> | sha256sum` | Staging object is readable and checksum matches the captured source sample. |

## 7. WeCom Validation

| Pass/Fail | Item | Command | Expected result |
| --- | --- | --- | --- |
| [ ] Pass / [ ] Fail | Verify production callback URL has not changed. | `printf '%s\n' '<compare current WeCom admin callback URL to captured baseline evidence>'` | Current WeCom production callback URL matches baseline evidence. |
| [ ] Pass / [ ] Fail | Verify staging WeCom adapter health. | `curl -fsS https://<staging-host>/api/compat/wecom/health` | Staging adapter reports healthy. |
| [ ] Pass / [ ] Fail | Validate WeCom signature sample. | `curl -fsS -X POST 'https://<staging-host>/api/compat/wecom/callback?msg_signature=<signature>&timestamp=<timestamp>&nonce=<nonce>' -H 'Content-Type: application/xml' --data-binary @fixtures/wecom/sample-message.xml` | Valid signed sample is accepted and normalized; invalid signatures are rejected in separate negative testing. |
| [ ] Pass / [ ] Fail | Validate duplicate callback idempotency. | `for i in 1 2; do curl -fsS -X POST 'https://<staging-host>/api/compat/wecom/callback?msg_signature=<signature>&timestamp=<timestamp>&nonce=<nonce>' -H 'Content-Type: application/xml' --data-binary @fixtures/wecom/sample-message.xml; done` | First delivery is processed once; duplicate delivery is acknowledged without duplicate downstream task/workflow effects. |

## 8. n8n Validation

| Pass/Fail | Item | Command | Expected result |
| --- | --- | --- | --- |
| [ ] Pass / [ ] Fail | Confirm production workflow active states are unchanged. | `n8n list:workflow` | Active workflow list matches the captured baseline; no duplicate workflows were activated. |
| [ ] Pass / [ ] Fail | Import workflows into staging disabled. | `n8n import:workflow --input=/secure-backups/n8n-workflows.<timestamp>.json` | Workflows import into staging only and remain disabled unless manually enabled for isolated tests. |
| [ ] Pass / [ ] Fail | Verify workflow adapter health. | `curl -fsS https://<staging-host>/api/compat/n8n/health` | Staging workflow adapter reports healthy and can read workflow metadata. |
| [ ] Pass / [ ] Fail | Run selected manual staging workflow. | `curl -fsS -X POST https://<staging-host>/api/compat/n8n/workflows/<workflow_id>/test -H 'Content-Type: application/json' -d '{"dry_run":true}'` | Manual test completes with staging-safe credentials and no production side effects. |
| [ ] Pass / [ ] Fail | Validate webhook path preservation map. | `curl -fsS https://<staging-host>/api/compat/n8n/webhook-map` | Response lists source webhook paths, target aliases/proxies, and conflict status for each callback workflow. |

## 9. Nginx Validation

| Pass/Fail | Item | Command | Expected result |
| --- | --- | --- | --- |
| [ ] Pass / [ ] Fail | Test staging nginx syntax. | `nginx -t -c /etc/nginx/nginx.conf` | Syntax test passes in staging or preview environment. |
| [ ] Pass / [ ] Fail | Capture staging rendered nginx config. | `nginx -T > /secure-backups/ai-vafox-nginx.staging.$(date -u +%Y%m%dT%H%M%SZ).conf` | Rendered staging config is captured for route review. |
| [ ] Pass / [ ] Fail | Probe staging route map. | `for path in / /auth/ /workbench /agents /knowledge /tasks /api/ai-workforce/health /console /n8n; do curl -fsSI "https://<staging-host>$path" || exit 1; done` | Every target staging route returns the expected HTTP status and upstream behavior. |
| [ ] Pass / [ ] Fail | Verify production nginx route behavior remains baseline. | `for path in / /auth/ /api /console /n8n; do curl -fsSI "https://ai.vafox.com$path" || exit 1; done` | Production routes respond according to baseline and do not expose staging-only V6 behavior. |
| [ ] Pass / [ ] Fail | Validate websocket upgrade path where applicable. | `curl -fsS -i -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==' -H 'Sec-WebSocket-Version: 13' https://<staging-host>/n8n/` | Staging nginx preserves expected websocket upgrade handling for n8n/Dify paths, or documented service-specific expected response is recorded. |
| [ ] Pass / [ ] Fail | Validate upload path where applicable. | `curl -fsS -X POST https://<staging-host>/api/ai-workforce/knowledge/upload-test -F 'file=@<small_test_file>' -F 'dry_run=true'` | Upload path reaches staging service and stores only in staging/test location or dry-run mode. |

## 10. Rollback Readiness

| Pass/Fail | Item | Command | Expected result |
| --- | --- | --- | --- |
| [ ] Pass / [ ] Fail | Verify baseline nginx artifact exists. | `test -s /secure-backups/ai-vafox-nginx.baseline.<timestamp>.conf && sha256sum /secure-backups/ai-vafox-nginx.baseline.<timestamp>.conf` | Baseline nginx artifact exists, is non-empty, and checksum is recorded. |
| [ ] Pass / [ ] Fail | Rehearse nginx rollback in staging only. | `cp /secure-backups/ai-vafox-nginx.baseline.<timestamp>.conf /tmp/rollback-nginx.conf && nginx -t -c /tmp/rollback-nginx.conf` | Rollback config syntax validates in staging; production nginx is not reloaded. |
| [ ] Pass / [ ] Fail | Verify rollback route probes in staging. | `for path in / /auth/ /api /console /n8n; do curl -fsSI "https://<rollback-rehearsal-host>$path" || exit 1; done` | Baseline route behavior is restored in rollback rehearsal within the target rollback time objective. |
| [ ] Pass / [ ] Fail | Confirm V6 can be disabled without affecting production. | `docker compose -f <staging_compose_file> stop ai-workforce-web ai-workforce-api ai-identity-adapter ai-agent-router ai-knowledge-adapter ai-workflow-adapter ai-wecom-adapter` | Staging V6 services stop cleanly; production `ai.vafox.com` continues serving baseline runtime. |
| [ ] Pass / [ ] Fail | Confirm data rollback posture is no-op for production. | `printf '%s\n' 'Production PostgreSQL, Milvus, and MinIO were not modified; rollback is no-op unless a future separately approved write occurs.'` | Evidence confirms production data stores were untouched by pre-cutover work. |
| [ ] Pass / [ ] Fail | Confirm rollback owners and communication channel. | `printf '%s\n' '<record rollback owner, data owner, operations owner, business approver, and incident channel in evidence bundle>'` | Named owners and communication channel are documented before any future cutover plan is considered. |

## Future Cutover Gate

A future production cutover plan may be drafted only after every checklist item above is completed or has an owner-approved exception. This document does not authorize executing that cutover.
