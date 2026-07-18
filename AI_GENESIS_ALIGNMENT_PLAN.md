# AI Genesis Alignment Plan

Target domain: `ai.vafox.com`  
Current runtime: `VAFOX Enterprise AI runtime`  
Current app location: `/opt/ai-vafox`  
Current release: `fba3c17`  
Target alignment: `VAFOX AI Workforce` + `AI-OS-V6-CLEAN-REBUILD-V1`  
Safety rules: **NO CUTOVER** and **NO DATA DELETE**.

## 1. Executive Summary

This document is an audit-only alignment plan for moving the current `ai.vafox.com` enterprise AI runtime toward the VAFOX Genesis target without production cutover or destructive data actions. The existing release `fba3c17` should be treated as the preservation baseline until discovery confirms every service, route, persistent volume, credential, workflow, and knowledge collection is restorable.

The Genesis target is represented in this repository by the V6 clean rebuild contract. V6 defines `AI-OS-V6-CLEAN-REBUILD-V1`, routes identity through Gateway, uses `ai.vafox.com` as the employee Digital Workforce OS, removes manual legacy AI controls, preserves Core/SAP truth, and keeps human approval in the task-creation loop.

## 2. Current Architecture Snapshot

### 2.1 Known production components

| Component | Known endpoint / role | Preservation requirement | Audit action only |
| --- | --- | --- | --- |
| `vafox-auth` | `:5010` | Preserve active auth behavior, sessions policy, role mapping, secrets, and nginx routes. | Inventory routes, env vars, systemd/container definition, health endpoints, and login redirects. |
| WeCom bot | `:5679` | Preserve bot callbacks, tokens, chat history references, and workflow triggers. | Record callback URLs, secret storage, message/event handlers, and n8n/Dify dependencies. |
| Dify API | `:5001` | Preserve app definitions, API keys, datasets, embeddings references, and provider configuration. | Export app/dataset metadata where supported; verify DB/vector/object storage bindings. |
| Dify Web | `:3000` | Preserve console access during coexistence. | Record nginx paths, auth assumptions, and static asset proxy rules. |
| n8n | `:5678` | Preserve workflows, credentials, execution history policy, and webhook URLs. | Export workflows/credentials metadata by supported backup process; do not alter active workflows. |
| Milvus | vector database | Preserve collections, partitions, indexes, and embedding dimensions. | Inventory collections and backup procedure; do not drop/rebuild indexes in production. |
| MinIO | object storage | Preserve buckets, object prefixes, policies, and access keys. | Inventory buckets and lifecycle policies; do not delete or rewrite objects. |
| PostgreSQL | relational database | Preserve all schemas, users, extensions, and application data. | Inventory databases/schema versions and backup/restore commands; do not run migrations against production. |

### 2.2 Current traffic model to verify

1. Public HTTPS traffic reaches nginx for `ai.vafox.com`.
2. nginx routes selected UI/auth/workbench paths to `vafox-auth` on `127.0.0.1:5010`.
3. Dify API and Dify Web remain available on their current ports and existing proxied paths.
4. WeCom callbacks enter through the bot service on `:5679` and may trigger n8n or Dify flows.
5. n8n executes workflow automation and depends on PostgreSQL plus external credentials.
6. Dify and knowledge services depend on PostgreSQL, Milvus, and MinIO for metadata, vectors, and files.

## 3. Genesis Target Architecture

### 3.1 Target operating model

The Genesis target is a clean V6 AI operating model with four public systems: `gateway.vafox.com`, `huyan.vafox.com`, `ai.vafox.com`, and `core.vafox.com`. In the target contract, employees route from Gateway to `ai.vafox.com` as the Digital Workforce OS, while CEO users route to Huyan and specialized roles route to supply, store, or supplier workspaces.

### 3.2 AI Workforce behavior

The target AI Workforce behavior removes manual agent dropdowns, object selection, source selection, and analysis forms. A natural-language question should infer business objects, select agents, bind Core data sources, produce recommendations, and draft tasks requiring human approval.

### 3.3 Data truth and action governance

V6 keeps SAP/Core as the business truth and uses AI as the intelligence layer. Tasks are drafts requiring human approval; AI must not create an ungoverned duplicate source of truth. Persistent assets in PostgreSQL, Milvus, MinIO, n8n, WeCom, and knowledge stores must be carried forward by coexistence, backup, or read-only reference until validated.

## 4. Release Comparison: Current Enterprise AI vs. Genesis Target

| Area | Current release `fba3c17` / Enterprise AI runtime | Genesis target `AI-OS-V6-CLEAN-REBUILD-V1` | Alignment gap | Audit evidence needed |
| --- | --- | --- | --- | --- |
| Release identity | Current release reported as `fba3c17`. | V6 build identity must report `AI-OS-V6-CLEAN-REBUILD-V1`. | Need version endpoint or runtime banner alignment. | Capture `/health`, `/health/runtime`, `/api/health`, commit hash, image tags. |
| Entry experience | Existing `ai.vafox.com` enterprise AI entry likely mixes auth, Dify, workbench, bot, and automation routes. | Gateway identity routes users into role-specific workspaces; `ai.vafox.com` serves Digital Workforce OS. | Need coexistence map before moving routes. | nginx `-T`, service inventory, route probes. |
| Auth | `vafox-auth :5010` is active. | Identity intelligence routes by role with legacy app picker removed. | Role/session claims must map to V6 roles without breaking current users. | Auth DB/session schema, login redirects, RBAC/ABAC policy export. |
| Agent UX | Current runtime may expose Dify apps, agents, or manual controls. | Universal conversation selects agents automatically. | Need agent inventory and mapping rules. | Dify app list, prompts, tools, provider configs, current UI paths. |
| Workflow automation | n8n active on `:5678`. | Automation health and workflow health are part of V6 control center. | Existing webhook URLs and credentials must be preserved. | n8n export, webhook route list, credential dependency matrix. |
| Knowledge | Dify datasets, Milvus vectors, MinIO files, and PostgreSQL metadata exist. | Core AI context/memory layer and knowledge assets must remain usable. | Need schema/collection/bucket compatibility plan. | PostgreSQL schemas, Milvus collections, MinIO buckets, embedding model metadata. |
| WeCom | WeCom bot active on `:5679`. | WeCom should remain an enterprise interaction channel, not be cut over destructively. | Callback compatibility and auth signatures must be validated. | callback URLs, event type inventory, token/secret location. |
| Nginx | Current nginx controls production routing. | V6 adds/keeps `ai.vafox.com` routes while preserving existing `/api`, `/console`, `/v1`, `/wecom`, and `/n8n` routes. | Need staged route overlay with rollback config. | Full nginx config backup, route diff, test config output. |

## 5. Assets Inventory Checklist

### 5.1 Must-preserve assets

- PostgreSQL databases, schemas, roles, extensions, app metadata, n8n metadata, Dify metadata, and backup snapshots.
- Milvus collections, partitions, vector indexes, embedding dimensions, aliases, and collection-level metadata.
- MinIO buckets, object prefixes, uploaded documents, generated files, policies, credentials, and lifecycle configuration.
- n8n workflows, credentials, webhook IDs, execution retention settings, and environment variables.
- WeCom bot configuration, callback endpoints, event subscriptions, tokens/secrets, and downstream workflow bindings.
- Dify app definitions, datasets, prompt templates, tool/provider credentials, API keys, and knowledge-to-vector mappings.
- nginx server blocks, TLS certificate paths, upstream definitions, and route-level proxy headers.
- systemd units, Docker Compose files, image tags, `.env` files, and secrets-management references.

### 5.2 Inventory commands for controlled audit windows

These commands are documentation for operators and must be run only in an approved audit window on the production host. They are read-only unless the local service tooling itself writes logs.

```bash
cd /opt/ai-vafox
git rev-parse HEAD
git status --short
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}'
nginx -T > /tmp/ai-vafox-nginx.audit.conf
systemctl list-units --type=service --all | egrep -i 'vafox|ai|dify|n8n|milvus|minio|postgres|wecom|nginx|docker'
ss -tulpen
```

## 6. Migration Analysis

### 6.1 Nginx migration

**Goal:** introduce Genesis-compatible routes without breaking current Dify, WeCom, n8n, or auth paths.

**Approach:**
1. Back up the full live nginx config and certificate references.
2. Produce a route table for `ai.vafox.com` including exact `location` precedence.
3. Keep existing `/api`, `/console`, `/v1`, `/wecom`, and `/n8n` routes unchanged during alignment.
4. Add V6 routes only behind a non-production host, internal header, or staging server block first.
5. Validate `nginx -t`, route probes, auth redirects, websocket behavior, upload limits, and callback signatures.
6. Prepare a single-file rollback by restoring the previous server block and reloading nginx.

**Key risk:** nginx location precedence can silently reroute Dify or WeCom callbacks. Any regex route must be reviewed against existing exact and prefix routes before activation.

### 6.2 Auth migration

**Goal:** preserve `vafox-auth :5010` while mapping current users to V6 identity routes.

**Approach:**
1. Inventory user roles, session claims, login redirects, token TTLs, and admin accounts.
2. Map existing roles to V6 roles: CEO, employee, procurement, store manager, supplier.
3. Run V6 route logic in shadow mode: log intended destination but keep current destination.
4. Verify RBAC/ABAC and audit logs for Dify, n8n, WeCom, and internal admin routes.
5. Only after approval, enable route-level changes in a canary path; this plan does not perform that step.

**Key risk:** breaking login or admin access would block operational recovery. Preserve a tested direct admin path and console access before any future cutover.

### 6.3 Agent migration

**Goal:** align current Dify/agent capabilities with V6 AI Workforce agents.

**Approach:**
1. Inventory Dify applications, prompts, tools, API keys, and model/provider settings.
2. Map existing apps to V6 agent groups: Risk, Supply, Store, Growth, Finance, and Enterprise fallback.
3. Convert manual app/agent selection into router metadata while leaving current apps operational.
4. Validate output format: conclusion, reason, data source, recommendation, next action, and task draft.
5. Preserve human approval for task creation.

**Key risk:** losing prompt/tool configuration or changing embeddings without compatibility testing. Keep Dify exports and provider settings versioned before transformation.

### 6.4 Workflow migration

**Goal:** preserve n8n workflows and WeCom/Dify integrations while exposing workflow health to V6 operations.

**Approach:**
1. Export workflow definitions with IDs, tags, webhook paths, cron schedules, and dependency credentials.
2. Identify workflows triggered by WeCom, Dify, auth events, or scheduled jobs.
3. Build a workflow dependency graph: trigger → credentials → external API → database/vector/object storage.
4. Run duplicate workflows disabled in staging for schema and credential validation.
5. Keep original webhook URLs active until signed callback and retry behavior is proven equivalent.

**Key risk:** changing webhook URLs can break WeCom callbacks or third-party automation. Use aliasing or proxy preservation before any future endpoint change.

### 6.5 Knowledge migration

**Goal:** preserve all knowledge assets and prove they can be queried from Genesis without re-ingestion loss.

**Approach:**
1. Inventory Dify datasets and map each dataset to PostgreSQL metadata, Milvus collection, and MinIO object prefixes.
2. Record embedding model name, dimension, tokenizer assumptions, and chunking rules.
3. Take logical backups or snapshots according to the existing production backup policy.
4. Validate read-only queries from a staging Genesis runtime against copied data.
5. Only re-embed in a separate collection/bucket prefix if model dimensions differ; never overwrite existing vectors.

**Key risk:** vector dimension mismatch or object-prefix drift can make knowledge retrieval fail while data still appears present. Keep old and new collections side by side.

## 7. Migration Stages

| Stage | Name | Actions | Exit criteria | Production change? |
| --- | --- | --- | --- | --- |
| 0 | Freeze and baseline | Record release `fba3c17`, service list, route list, backups, and owners. | Baseline report reviewed. | No |
| 1 | Discovery | Run read-only inventory for nginx, Docker/systemd, PostgreSQL, Milvus, MinIO, Dify, n8n, and WeCom. | Complete asset register with unknowns flagged. | No |
| 2 | Preservation backup | Produce approved config and data backups using existing backup procedures. | Restore procedure documented and sampled in non-prod. | No destructive change |
| 3 | Shadow Genesis | Deploy Genesis runtime in staging or isolated host using copied configs/data references. | V6 health/version and route contracts pass in staging. | No |
| 4 | Compatibility mapping | Map auth roles, agents, workflows, routes, and knowledge datasets. | Gap matrix approved by owners. | No |
| 5 | Coexistence rehearsal | Test nginx route overlay and workflow aliases in non-prod; validate WeCom/Dify/n8n behavior. | Route and callback tests pass; rollback tested. | No production cutover |
| 6 | Readiness review | Security, data, workflow, and operations sign-off. | Go/no-go package prepared for a future separate cutover plan. | No |

## 8. Risk Assessment

| Risk | Probability | Impact | Mitigation |
| --- | --- | --- | --- |
| nginx route precedence breaks Dify, WeCom, or auth paths. | Medium | High | Full `nginx -T` backup, route diff, staging overlay, exact path tests, instant rollback file. |
| Auth role mapping locks out administrators or misroutes users. | Medium | High | Preserve direct admin route, map roles in shadow mode, test session claims, maintain break-glass access. |
| n8n webhook URL drift breaks WeCom or external callbacks. | Medium | High | Preserve webhook paths, use aliases, validate signatures and retries before changes. |
| Dify app or provider credentials lost during export/import. | Medium | High | Export app metadata, securely back up `.env`/credential stores, validate provider calls in staging. |
| Milvus vector dimension mismatch after model changes. | Medium | Medium/High | Record dimensions and model metadata; create parallel collections only; never overwrite existing vectors. |
| MinIO object prefix or policy mismatch breaks document retrieval. | Medium | Medium | Inventory buckets/policies, validate signed URL and object reads, preserve prefixes. |
| PostgreSQL migrations mutate production metadata. | Low under this plan | High | Audit-only mode; run migrations only on restored copy; no production schema writes. |
| Hidden cron/systemd jobs bypass documented workflows. | Medium | Medium | Inventory systemd timers, crontab, containers, and app schedulers. |
| Current release `fba3c17` cannot be reproduced. | Medium | Medium | Record image digests, commit hash, config files, package versions, and backup artifacts. |

## 9. Rollback Plan

Rollback is mandatory for any future production alignment step. For this audit plan, rollback means returning to the documented `fba3c17` baseline because no production change should be executed.

### 9.1 Rollback assets to capture before future changes

- Git commit hash and image digests for current release `fba3c17`.
- Full nginx config from `nginx -T` and certificate/key path inventory.
- Docker Compose files, systemd unit files, env files, and secrets references.
- PostgreSQL logical backup or approved snapshot plus restore command.
- Milvus backup/snapshot procedure and collection inventory.
- MinIO bucket/object inventory and replication/snapshot state.
- n8n workflow/credential export or database backup according to approved secure process.
- Dify app/dataset export and database/vector/object-store backup references.
- WeCom bot callback configuration and token/secret recovery process.

### 9.2 Rollback sequence for future route-level changes

1. Restore previous nginx server block from the captured baseline.
2. Run `nginx -t`.
3. Reload nginx only after successful syntax validation.
4. Confirm `ai.vafox.com` login, Dify API/Web, WeCom callback route, and n8n route are back to baseline.
5. Confirm PostgreSQL, Milvus, MinIO, n8n, Dify, and WeCom services are healthy.
6. Record incident notes and block further migration until root cause is resolved.

### 9.3 Rollback sequence for future app/runtime changes

1. Stop only the newly introduced Genesis runtime components.
2. Restart or keep current `fba3c17` components using recorded systemd/Docker definitions.
3. Do not restore databases over production unless data owners approve; prefer forward fix if data was not modified.
4. Verify health endpoints and user login.
5. Verify a sample Dify query, n8n workflow, WeCom callback, Milvus retrieval, MinIO object read, and PostgreSQL read.

## 10. Immediate Next Actions

1. Approve an audit window for read-only discovery on `/opt/ai-vafox`.
2. Generate a current architecture evidence bundle: nginx, Docker/systemd, ports, health endpoints, app configs, and backup references.
3. Build the asset register for PostgreSQL, Milvus, MinIO, n8n, WeCom, Dify, and knowledge datasets.
4. Produce the route and auth mapping matrix from current Enterprise AI to Genesis roles/workspaces.
5. Stand up a non-production Genesis shadow environment using copied configuration and non-production data snapshots.
6. Review findings before any separate cutover proposal. This plan intentionally does not authorize production cutover.
