# AI Genesis Implementation Plan

Target domain: `ai.vafox.com`  
Basis: `AI_GENESIS_ALIGNMENT_PLAN.md`  
Current runtime: `VAFOX Enterprise AI runtime`  
Current production app location: `/opt/ai-vafox`  
Current production baseline: release `fba3c17`  
Target runtime: `VAFOX AI Workforce` + `AI-OS-V6-CLEAN-REBUILD-V1`  
Plan type: implementation-level migration plan for a future approved migration window.

## 0. Non-Negotiable Safety Rules

1. **NO PRODUCTION CUTOVER is authorized by this plan.**
2. **NO DATA DELETE is authorized by this plan.**
3. Production `ai.vafox.com` remains on the documented baseline until a separately approved cutover plan exists.
4. All discovery against production must be read-only unless an owner explicitly approves a backup operation.
5. All schema migrations, vector rebuilds, object rewrites, workflow imports, and route overlays must be performed first against staging, restored copies, or isolated shadow infrastructure.
6. Rollback artifacts must exist before any future production route or runtime change.
7. Existing Dify, n8n, WeCom, PostgreSQL, Milvus, MinIO, and `vafox-auth` assets are preservation sources, not disposable legacy assets.

## 1. Implementation Scope

This plan converts the Genesis alignment direction into implementation work packages. It defines service mapping, keep/replace/wrap/migrate decisions, nginx target routing, data migration handling, deployment sequence, validation gates, and rollback requirements for moving toward `VAFOX AI Workforce` on `AI-OS-V6-CLEAN-REBUILD-V1`.

This plan intentionally stops before production cutover. It prepares a parallel deployment that can be validated without replacing the live production runtime.

## 2. Current-to-Target Service Mapping

### 2.1 Service decision matrix

| Current service | Current role | Target role in `VAFOX AI Workforce` / `AI-OS-V6-CLEAN-REBUILD-V1` | Decision | Implementation action | Production safety control |
| --- | --- | --- | --- | --- | --- |
| `vafox-auth` | Login, sessions, role checks, redirects, auth-protected routes. | Identity and role source for the AI Workforce entry experience; eventually routes employees into AI Workspace while preserving admin access. | **Wrap**, then **Migrate** selected routing logic. | Put V6 identity adapter behind `vafox-auth`; map current claims to V6 roles; run destination decisions in shadow logs before enabling any route change. | Keep current auth service and direct admin access unchanged; do not alter production sessions or role tables during planning. |
| WeCom bot | Enterprise chat callback endpoint and event bridge into workflows or AI apps. | External interaction channel for AI Workforce, task drafting, notifications, and callback-triggered automation. | **Keep** and **Wrap**. | Preserve callback URL, signature verification, tokens, and event payloads; add a compatibility adapter that forwards validated events to V6 services in staging. | Do not change WeCom callback configuration until staged signature and retry validation passes. |
| Dify API/Web | AI app runtime, console, datasets, prompts, tools, model/provider settings. | Knowledge/app capability source during transition; selected apps become agent skills or router targets in AI Workforce. | **Wrap** and **Migrate** app definitions gradually. | Export app/dataset metadata; expose existing Dify capabilities through a V6 agent router adapter; migrate prompts/tools to V6 format in staging. | Keep Dify API/Web available on existing routes; do not overwrite Dify apps or datasets. |
| n8n | Workflow automation, webhooks, credentials, schedules, execution history. | Workflow execution substrate or compatibility layer for V6 automation health and task orchestration. | **Keep** and **Wrap** initially; **Migrate** only workflows selected for native V6 orchestration. | Export workflows; map triggers and credentials; mirror selected workflows disabled in staging; expose workflow status to V6 operations. | Do not activate duplicate production workflows; preserve webhook URLs and credential stores. |
| Milvus | Vector database for knowledge retrieval and embeddings. | Vector memory/knowledge backend or source collection set for V6 knowledge retrieval. | **Keep** for existing collections; **Migrate** by parallel collection only when required. | Inventory collections, dimensions, indexes, aliases, partitions; attach V6 to copied collections in staging; create new collections only for incompatible embedding dimensions. | Never drop, compact destructively, or overwrite production collections. |
| MinIO | Object storage for documents, files, generated assets, dataset backing objects. | Object store for AI Workforce knowledge files and artifacts. | **Keep** and **Migrate** by prefix/bucket copy. | Inventory buckets, prefixes, policies, lifecycle rules, and object metadata; stage read-only object access; copy to new prefixes only if target naming requires it. | No object delete or rewrite; all migration writes must use new bucket/prefix names. |
| PostgreSQL | Relational metadata for apps, auth, workflows, datasets, and service state. | System metadata and compatibility data source for V6; source of truth for migrated app/workflow metadata snapshots. | **Keep** production unchanged; **Migrate** through restored copy and controlled scripts. | Take logical backups/snapshots; restore to staging; run V6 migrations only on restored copy; produce schema diff and data validation report. | No production schema migration under this plan; no data delete. |

### 2.2 Target service layout

| Target capability | Target component | Backing dependency during transition | Notes |
| --- | --- | --- | --- |
| AI Workforce web entry | `ai-workforce-web` or V6 frontend service | `vafox-auth`, nginx, existing Dify console links during coexistence | Served only on staging or internal preview route until cutover approval. |
| AI Workforce API | `ai-workforce-api` or V6 runtime API | PostgreSQL restored copy, Dify adapter, n8n adapter, Milvus, MinIO | Must expose version/health as `AI-OS-V6-CLEAN-REBUILD-V1`. |
| Identity adapter | `ai-identity-adapter` | `vafox-auth` claims/session validation | Performs role mapping and logs intended routing in shadow mode. |
| Agent router | `ai-agent-router` | Dify app catalog, V6 prompt registry, model provider configs | Replaces manual agent selection with inferred agent routing. |
| Knowledge adapter | `ai-knowledge-adapter` | Dify datasets, Milvus collections, MinIO objects, PostgreSQL metadata | Reads existing knowledge without changing existing vectors or objects. |
| Workflow adapter | `ai-workflow-adapter` | n8n workflows, webhook aliases, credential references | Preserves n8n while presenting workflow health and task draft hooks to V6. |
| WeCom adapter | `ai-wecom-adapter` | Current WeCom bot signature verification and event model | Runs in staging first; production callback remains unchanged. |

## 3. Migration Strategy: Keep, Replace, Wrap, Migrate

### 3.1 Keep

Keep means the service remains authoritative and operational during the first Genesis implementation phase.

- Keep PostgreSQL as the preservation source for all current relational data.
- Keep Milvus as the preservation source for current vectors.
- Keep MinIO as the preservation source for current objects.
- Keep n8n active for existing workflows and webhooks.
- Keep WeCom bot callbacks unchanged until a separate approved callback switch.
- Keep Dify API/Web available for existing operational users and console administration.
- Keep `vafox-auth` as the current production identity gate.

### 3.2 Replace

Replace means a target V6 component becomes the preferred implementation after staging validation and separate approval.

- Replace manual app/agent selection UI with AI Workforce natural-language routing.
- Replace manual workbench forms with a conversation-led interaction that infers object, source, and recommended action.
- Replace direct user dependence on Dify Web for employee-facing AI work with AI Workforce UI, while preserving Dify console for administrators during coexistence.
- Replace ad hoc route behavior with a documented nginx route map and route tests.

No production replacement is authorized in this plan.

### 3.3 Wrap

Wrap means a V6 adapter calls or proxies an existing service without mutating that service.

- Wrap `vafox-auth` with a V6 identity adapter that maps claims into Genesis roles.
- Wrap Dify apps through an agent-router adapter.
- Wrap n8n through a workflow adapter that preserves existing webhook IDs and credentials.
- Wrap WeCom through a callback compatibility adapter.
- Wrap Milvus and MinIO through a knowledge adapter that reads existing collections/objects and writes only to isolated staging resources.

### 3.4 Migrate

Migrate means data or behavior is copied or transformed into V6-compatible structures after backup and validation.

- Migrate PostgreSQL through backup restore into staging first; production migrations require separate approval.
- Migrate Milvus by collection copy or re-embedding into new collections only.
- Migrate MinIO by bucket/prefix copy only.
- Migrate Dify app metadata into the V6 agent registry after export verification.
- Migrate n8n workflows only after dependency and credential validation; leave source workflows active until a future cutover.
- Migrate WeCom callback processing by aliasing/proxying first, not by replacing the callback URL directly.

## 4. Nginx Transition Plan

### 4.1 Principles

1. Capture `nginx -T` before any future nginx edit.
2. Implement target routes first in staging or preview host, not on the live `ai.vafox.com` production server block.
3. Preserve current paths for Dify, n8n, auth, WeCom callbacks, and APIs during coexistence.
4. Avoid regex locations unless exact and prefix locations cannot meet the requirement.
5. Test route precedence, websocket upgrades, uploads, auth redirects, and callback signatures.
6. Keep a one-command rollback path: restore previous server block, run `nginx -t`, reload nginx.

### 4.2 Current route inventory and target mapping

| Current route | Current likely owner | Target route owner | Target behavior | Transition decision |
| --- | --- | --- | --- | --- |
| `/` | Current Enterprise AI entry or auth/workbench landing. | AI Workforce web entry. | Employee Digital Workforce OS home with natural-language AI entry. | **Wrap/Replace later**: serve V6 only in staging or preview; production `/` unchanged until cutover approval. |
| `/auth/` | `vafox-auth`. | `vafox-auth` plus V6 identity adapter. | Login/session/role mapping; shadow logs for V6 destination. | **Keep/Wrap**: keep route and upstream stable. |
| `/workbench` | Existing workbench UI. | AI Workforce workbench shell. | Conversation-led workbench; no manual agent/source controls. | **Replace later**: preview as `/preview/workbench` or staging host first. |
| `/agents` | Existing agent/Dify app surface. | AI Workforce agent router/admin mapping. | Admin-visible agent catalog and router diagnostics; employee UI should not require manual selection. | **Wrap/Migrate**: map Dify apps to V6 agent registry. |
| `/knowledge` | Dify datasets or current knowledge UI. | AI Workforce knowledge center. | Dataset visibility, source binding, retrieval diagnostics. | **Wrap/Migrate**: read current Dify/Milvus/MinIO assets; no overwrite. |
| `/tasks` | Current task/workflow UI if present. | V6 task draft and approval center. | AI creates draft recommendations/tasks requiring human approval. | **Migrate** task models in staging; no production writes. |
| `/api` | Current APIs, possibly Dify/backend APIs. | V6 API gateway plus compatibility routes. | Route `/api/ai-workforce/*` to V6; preserve existing `/api/*` behavior during coexistence. | **Wrap**: use namespaced V6 API first to avoid collisions. |
| `/console` | Dify Web console/admin. | Dify console retained for administrators; optional V6 admin links. | Keep admin console access stable. | **Keep** unchanged through transition. |
| `/n8n` | n8n UI/webhook route. | n8n retained; V6 workflow adapter reads health/status. | Preserve UI, webhooks, websocket behavior, and base path. | **Keep/Wrap** unchanged. |

### 4.3 Proposed target route table for staging/preview

| Route | Upstream | Purpose | Notes |
| --- | --- | --- | --- |
| `/` | `ai-workforce-web` | Target AI Workforce home. | Only on staging/preview before cutover. |
| `/auth/` | `vafox-auth` | Current auth plus V6 role mapping. | Existing production behavior must remain stable. |
| `/workbench` | `ai-workforce-web` | V6 workbench shell. | Backed by AI Workforce API. |
| `/agents` | `ai-workforce-web` | Agent registry/admin diagnostics. | Employee experience should not depend on manual selection. |
| `/knowledge` | `ai-workforce-web` | Knowledge catalog/retrieval diagnostics. | Uses knowledge adapter. |
| `/tasks` | `ai-workforce-web` | Task draft and approval center. | Draft-only until approved by human. |
| `/api/ai-workforce/` | `ai-workforce-api` | Namespaced V6 runtime API. | Avoids collision with current `/api`. |
| `/api/compat/dify/` | `ai-agent-router` or Dify API proxy | Dify compatibility. | For staged compatibility tests only. |
| `/api/compat/n8n/` | `ai-workflow-adapter` | n8n compatibility/health. | Must not trigger duplicate workflows. |
| `/api/compat/wecom/` | `ai-wecom-adapter` | WeCom callback rehearsal endpoint. | Validate signature and retry behavior before any callback change. |
| `/console` | Dify Web | Dify admin console. | Keep unchanged. |
| `/n8n` | n8n | n8n UI/webhook base path. | Keep unchanged. |

### 4.4 Nginx implementation gates

- Gate N1: `nginx -T` baseline captured and stored in the release evidence bundle.
- Gate N2: Route table reviewed for exact/prefix/regex precedence.
- Gate N3: Staging nginx config passes `nginx -t`.
- Gate N4: Staging probes pass for `/`, `/auth/`, `/workbench`, `/agents`, `/knowledge`, `/tasks`, `/api/ai-workforce/health`, `/console`, and `/n8n`.
- Gate N5: Websocket and upload tests pass for Dify/n8n paths where applicable.
- Gate N6: Rollback config tested in staging.

## 5. Data Migration Plan

### 5.1 PostgreSQL

**Objective:** preserve all current relational state and migrate only through restored copies until a separate production migration is approved.

Implementation steps:

1. Inventory databases, schemas, roles, extensions, table counts, approximate row counts, owners, and app bindings.
2. Capture logical backup with `pg_dump`/`pg_dumpall` or approved snapshot tooling.
3. Restore backup to staging PostgreSQL.
4. Run V6 schema migrations only against staging.
5. Build mapping tables for current entities: users, roles, Dify apps, Dify datasets, n8n workflow metadata, credentials references, task records, audit logs, and integration state.
6. Validate row counts and referential integrity after restore.
7. Generate a schema diff between restored current schema and target V6 schema.
8. Produce a migration script that is idempotent, reversible where possible, and non-destructive.
9. Mark any unsupported source tables as read-only compatibility tables rather than deleting them.

Validation checks:

- Backup restore completes successfully in staging.
- Critical table counts match source inventory.
- V6 runtime health can read expected metadata from the restored copy.
- No migration script contains `DROP TABLE`, `DROP DATABASE`, destructive `TRUNCATE`, or unscoped `DELETE`.

Rollback posture:

- Production rollback is to keep production PostgreSQL untouched.
- If a future production migration is approved, rollback must use transaction boundaries, pre-migration backup, and owner-approved restore steps.

### 5.2 Milvus collections

**Objective:** preserve existing vectors and make them queryable by Genesis without destructive rebuilds.

Implementation steps:

1. Inventory collections, aliases, partitions, fields, primary keys, vector dimensions, index types, metric types, row counts, and embedding model metadata.
2. Identify which Dify datasets map to each collection.
3. Snapshot or back up Milvus according to the deployed Milvus version and storage backend.
4. Restore or clone collections to staging.
5. Point the V6 knowledge adapter at staging collections for retrieval tests.
6. If V6 embedding dimensions differ, create new collections with a V6-specific suffix; do not overwrite current collections.
7. Re-embed only from copied source documents and only into new staging collections.
8. Compare retrieval quality between current and V6 collections using a fixed query set.

Validation checks:

- Collection counts and dimensions match inventory.
- Indexes load successfully in staging.
- Top-k retrieval returns expected documents for known queries.
- No collection drop, alias replacement, or destructive compaction is required.

Rollback posture:

- Keep current production collections and aliases unchanged.
- Remove only staging-created collections if cleanup is needed, never production collections.

### 5.3 MinIO objects

**Objective:** preserve object data and policies while allowing V6 to read files through compatible prefixes.

Implementation steps:

1. Inventory buckets, prefixes, object counts, object sizes, policies, lifecycle rules, encryption settings, and access keys.
2. Capture bucket configuration and policy exports.
3. Mirror required objects to staging MinIO or a new staging prefix.
4. Preserve original object keys in a mapping table if target prefixes differ.
5. Validate signed URL generation, direct object reads, Dify dataset file references, and V6 knowledge adapter reads.
6. For migrated objects, write only to new buckets or prefixes such as `genesis-staging/` or `ai-os-v6/`.

Validation checks:

- Object count and sampled checksums match source inventory.
- Required buckets/prefixes are readable by staging services.
- V6 does not require rewriting existing production object keys.
- No object delete lifecycle is introduced by the migration.

Rollback posture:

- Production objects remain untouched.
- Staging prefixes can be abandoned without affecting production assets.

### 5.4 n8n workflows

**Objective:** preserve current automation behavior while preparing workflow compatibility for V6.

Implementation steps:

1. Export all workflows with IDs, names, tags, active flags, webhook paths, schedules, node types, and dependency credentials.
2. Export credential metadata using the approved secure process; do not expose secrets in planning documents.
3. Inventory execution retention policy and active queue/worker settings.
4. Classify workflows by trigger: WeCom callback, Dify event, webhook, cron, manual, database, external API.
5. Import workflows into staging with active flags disabled by default.
6. Replace production credentials with staging-safe credentials or secret references.
7. Run manual test executions for selected workflows.
8. Define alias/proxy strategy for any webhook path that must remain stable.
9. Map successful workflows into V6 workflow health and task draft integration.

Validation checks:

- Workflow export count matches n8n inventory.
- Disabled staging imports do not trigger external side effects.
- Manual workflow tests pass with staging credentials.
- Webhook path preservation strategy is documented for each callback workflow.

Rollback posture:

- Production n8n workflows remain active and unchanged.
- Future failed migration rolls back by disabling V6 workflow adapter and keeping original n8n webhooks live.

### 5.5 WeCom callbacks

**Objective:** preserve callback compatibility and enterprise chat behavior.

Implementation steps:

1. Inventory callback URLs, event types, message types, token/encoding secret locations, IP allowlists, retry behavior, and downstream workflow triggers.
2. Reproduce signature verification in staging using non-production callback samples.
3. Build a WeCom adapter that validates signature first, then forwards normalized events to V6 runtime or n8n staging workflows.
4. Configure a preview callback path such as `/api/compat/wecom/callback` for rehearsal.
5. Test text message, file event, menu action, retry, duplicate delivery, and error response handling.
6. Preserve current production callback URL until a separate approved switch.

Validation checks:

- Signature validation matches current bot behavior.
- Event normalization preserves required fields.
- Duplicate events are idempotent.
- Failed downstream calls return safe retry behavior.

Rollback posture:

- Since production callback is not changed under this plan, rollback is to disable the staging adapter.
- For any future callback switch, rollback must reset WeCom configuration to the captured original callback URL and secret set.

## 6. Deployment Sequence

### 6.1 Phase 0: Freeze, ownership, and evidence bundle

1. Confirm migration owners for auth, Dify, n8n, WeCom, database, vector, object storage, and nginx.
2. Freeze production migration activity except approved read-only discovery and backups.
3. Capture release baseline: commit hash, image tags/digests, service definitions, env file paths, and nginx config.
4. Record open issues, unknown dependencies, and rollback owners.

Exit criteria:

- Evidence bundle exists.
- Owners acknowledge safety rules: no cutover and no delete.

### 6.2 Phase 1: Backup

1. Back up nginx config and TLS path inventory.
2. Back up Docker Compose/systemd units and environment references.
3. Back up PostgreSQL by logical dump or approved snapshot.
4. Back up Milvus through collection snapshot or approved Milvus backup tooling.
5. Back up MinIO bucket policies and objects through approved replication/snapshot tooling.
6. Export Dify metadata and confirm its PostgreSQL/Milvus/MinIO bindings.
7. Export n8n workflows and credential metadata using the approved secure process.
8. Capture WeCom callback configuration and recovery steps.

Exit criteria:

- Backups are present, named, timestamped, access-controlled, and tied to release `fba3c17`.
- At least one representative restore is tested in non-production.

### 6.3 Phase 2: Parallel deployment

1. Provision isolated Genesis staging infrastructure.
2. Deploy `AI-OS-V6-CLEAN-REBUILD-V1` services: web, API, identity adapter, agent router, knowledge adapter, workflow adapter, and WeCom adapter.
3. Restore PostgreSQL backup into staging.
4. Restore or clone Milvus collections into staging.
5. Mirror MinIO objects to staging or staging prefixes.
6. Import Dify/n8n metadata into staging-compatible stores without activating external side effects.
7. Configure staging nginx or preview server block for target route map.
8. Configure V6 to report target release identity and health.

Exit criteria:

- Parallel deployment is reachable only through staging/preview access.
- Production traffic and callbacks remain unchanged.

### 6.4 Phase 3: Validation

Validation must cover service health, route behavior, auth, data integrity, retrieval quality, workflows, WeCom callbacks, and rollback rehearsal.

Required checks:

1. V6 health/version reports `AI-OS-V6-CLEAN-REBUILD-V1`.
2. Staging route probes pass for every target route.
3. Current production routes remain unchanged during validation.
4. Auth role mapping works in shadow mode and does not alter current sessions.
5. Dify app mapping produces expected agent-router selections.
6. PostgreSQL restored row counts and critical records match source inventory.
7. Milvus retrieval returns expected documents for test queries.
8. MinIO object reads and sampled checksums pass.
9. n8n staging workflows remain disabled unless manually tested.
10. WeCom staging callbacks validate signatures and idempotency.
11. Task creation remains draft-only and requires human approval.
12. nginx rollback procedure is tested in staging.

Exit criteria:

- Validation report has no open Sev-1 or Sev-2 issues.
- Data owners sign off on non-destructive migration behavior.
- Operations signs off on rollback evidence.

### 6.5 Phase 4: DNS/nginx switch preparation only

This plan does **not** perform a production DNS or nginx switch. It only prepares the switch package for a future separately approved cutover.

Preparation tasks:

1. Produce final route diff between current production nginx and target nginx.
2. Define exact switch scope: route-level nginx switch, upstream change, DNS CNAME/A record change, or weighted traffic policy.
3. Define expected propagation behavior and TTL handling if DNS is involved.
4. Define smoke tests to run immediately after a future switch.
5. Define rollback command sequence and maximum rollback time objective.
6. Obtain explicit approval checklist for any future cutover.

Exit criteria:

- A future cutover runbook exists but is not executed.
- Approval gates are documented and pending.

### 6.6 Phase 5: Rollback plan

Rollback must be executable before any future production route or runtime change.

Route-level rollback:

1. Restore previous nginx server block from the baseline artifact.
2. Run `nginx -t`.
3. Reload nginx.
4. Probe `/`, `/auth/`, `/api`, `/console`, `/n8n`, and any WeCom callback path.
5. Confirm production upstreams match baseline.

Runtime rollback:

1. Disable new V6 upstreams or remove them from nginx routing.
2. Keep current `fba3c17` services serving production traffic.
3. Stop V6 services only if they are causing load, credential, or callback risk.
4. Do not restore over production databases unless data owners authorize it.
5. Verify Dify API/Web, n8n, WeCom bot, Milvus, MinIO, PostgreSQL, and auth health.

Data rollback:

1. Prefer no-op because production data is untouched by this plan.
2. If future approved writes occur, use pre-change backups and transaction logs according to the relevant data owner runbook.
3. Never use rollback as a reason to delete production collections, buckets, or schemas without separate authorization.

Exit criteria:

- Rollback has been rehearsed in staging.
- Rollback owner and communication channel are assigned.

## 7. Validation Matrix

| Area | Validation item | Method | Pass condition |
| --- | --- | --- | --- |
| Release identity | V6 version endpoint | HTTP probe | Reports `AI-OS-V6-CLEAN-REBUILD-V1`. |
| nginx | Route map | Automated route probes | Expected upstream responds for all staging routes. |
| Auth | Role mapping | Shadow login tests | Current login remains stable; V6 intended role is logged correctly. |
| Dify | App compatibility | Agent-router test set | Known prompts route to expected app/agent mapping. |
| PostgreSQL | Restore integrity | Counts, checksums where practical, schema diff | Restored critical data matches source inventory. |
| Milvus | Retrieval integrity | Fixed top-k query set | Expected documents appear in results. |
| MinIO | Object integrity | Sample checksums and signed URL tests | Objects are readable and match sampled checksums. |
| n8n | Workflow safety | Disabled import and manual tests | No duplicate production side effects; selected manual runs pass. |
| WeCom | Callback compatibility | Signature and retry tests | Valid callbacks pass; duplicates are idempotent. |
| Task governance | Human approval | Draft-task test | AI produces draft only; no unapproved final task creation. |
| Rollback | Route rollback | Staging rollback rehearsal | Baseline route behavior restored within rollback objective. |

## 8. Implementation Work Packages

| Work package | Owner role | Deliverables | Dependencies |
| --- | --- | --- | --- |
| WP1 Baseline and backup | Operations | Evidence bundle, backup manifest, restore notes | Production read-only access and backup permissions. |
| WP2 Service inventory | Platform | Service map, port map, env reference map | Docker/systemd/nginx inventory. |
| WP3 V6 parallel deployment | Platform | Staging V6 stack and health endpoints | Infrastructure, secrets, container images. |
| WP4 Identity adapter | Auth owner | Claim mapping, role matrix, shadow logs | `vafox-auth` behavior inventory. |
| WP5 Agent/Dify adapter | AI owner | Dify app export, V6 agent registry, router tests | Dify metadata and provider config access. |
| WP6 Knowledge migration | Data/AI owner | Dataset-to-Milvus/MinIO map, retrieval validation | PostgreSQL, Milvus, MinIO backups. |
| WP7 Workflow adapter | Automation owner | n8n workflow export, dependency graph, staging tests | n8n workflow/credential inventory. |
| WP8 WeCom adapter | Integration owner | Callback inventory, staging callback tests | WeCom configuration and sample events. |
| WP9 nginx transition | Operations | Staging route map, route probes, rollback file | WP3 services and current nginx baseline. |
| WP10 Readiness review | Migration lead | Validation report, gap list, future cutover package | WP1-WP9 outputs. |

## 9. Explicit Out-of-Scope Items

- Production cutover of `ai.vafox.com`.
- Production DNS changes.
- Production nginx route switch.
- Deleting PostgreSQL schemas, records, roles, or databases.
- Dropping Milvus collections, partitions, indexes, or aliases.
- Deleting or rewriting MinIO objects or lifecycle policies.
- Replacing WeCom callback URLs in production.
- Activating duplicate n8n workflows against production triggers.
- Removing Dify API/Web or console access.

## 10. Readiness Checklist for a Separate Future Cutover Plan

A separate production cutover plan may be drafted only after all of the following are true:

- [ ] Current baseline and backups are complete.
- [ ] Restore has been tested in non-production.
- [ ] Parallel V6 deployment is healthy.
- [ ] nginx target route map passes in staging.
- [ ] Auth role mapping passes in shadow mode.
- [ ] Dify app-to-agent migration is validated.
- [ ] PostgreSQL migration scripts are non-destructive and tested on restored data.
- [ ] Milvus retrieval quality is validated side by side.
- [ ] MinIO object reads and checksums are validated.
- [ ] n8n workflows are imported disabled and manually tested.
- [ ] WeCom callback adapter passes signature, retry, and idempotency tests.
- [ ] Human approval is enforced for task creation.
- [ ] Rollback is rehearsed and timed.
- [ ] Business, security, data, and operations owners approve the future cutover runbook.

## 11. Operator Command Appendix

The following commands are examples for controlled operator runbooks. They must be adapted to the actual production host and run only during approved windows. They are included to support implementation planning, not to authorize production mutation.

```bash
# Baseline evidence
cd /opt/ai-vafox
git rev-parse HEAD
git status --short
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}'
nginx -T > /tmp/ai-vafox-nginx.baseline.conf
nginx -t
ss -tulpen

# PostgreSQL logical backup examples; use actual container/service names and secure paths.
pg_dumpall --globals-only > /secure-backups/ai-vafox-postgres-globals.sql
pg_dump --format=custom --file=/secure-backups/ai-vafox-app.dump <database_name>

# MinIO inventory examples; use configured alias and secure output location.
mc ls <alias>
mc ls --recursive <alias>/<bucket> > /secure-backups/minio-object-inventory.txt
mc admin policy info <alias> <policy_name> > /secure-backups/minio-policy.json

# n8n export examples; use the deployed n8n-supported export mechanism.
n8n export:workflow --all --output=/secure-backups/n8n-workflows.json
```
