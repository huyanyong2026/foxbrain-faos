# AI Genesis Release Build Plan

## 1. Release Scope and Guardrails

- **Target host:** `ai.vafox.com`
- **Current production release:** `fba3c17`
- **Current production symlink:** `current-enterprise-ai -> releases/fba3c17`
- **Deployment model:** release based
- **Future release name:** `VAFOX AI Workforce / AI-OS-V6-CLEAN-REBUILD-V1`
- **Non-negotiable guardrail:** this plan prepares a future release only. It does **not** cut production over, repoint `current-enterprise-ai`, reload production NGINX, restart production services, or mutate production data.

## 2. New Release Directory Strategy

Create a new immutable release candidate directory beside the current production release:

```text
/opt/vafox/enterprise-ai/
├── current-enterprise-ai -> releases/fba3c17
├── releases/
│   ├── fba3c17/
│   └── AI-OS-V6-CLEAN-REBUILD-V1/
├── shared/
│   ├── env/
│   ├── logs/
│   ├── evidence/
│   ├── backups/
│   └── runtime-data/
└── staging-enterprise-ai -> releases/AI-OS-V6-CLEAN-REBUILD-V1
```

### Directory rules

1. `releases/fba3c17` remains untouched and is the rollback anchor.
2. `releases/AI-OS-V6-CLEAN-REBUILD-V1` is built as a complete, self-contained release candidate.
3. `staging-enterprise-ai` may point to the future release for staging-only validation.
4. `current-enterprise-ai` must continue pointing to `releases/fba3c17` until a separately approved production cutover window.
5. Shared assets must be referenced through explicit paths, not copied into release directories unless they are versioned build artifacts.
6. Each release must include a `RELEASE_MANIFEST.json` with commit SHA, build time, artifact checksums, service image tags, migration status, and validation evidence path.

## 3. Source Preparation

### 3.1 Branch and source freeze

1. Create or update a dedicated release branch:

   ```bash
   git checkout -b release/AI-OS-V6-CLEAN-REBUILD-V1
   ```

2. Confirm source provenance:

   ```bash
   git rev-parse HEAD
   git status --short
   ```

3. Record source state in:

   ```text
   /opt/vafox/enterprise-ai/shared/evidence/AI-OS-V6-CLEAN-REBUILD-V1/source_provenance.txt
   ```

### 3.2 Configuration preparation

Prepare staging-safe configuration files under shared environment storage:

```text
/opt/vafox/enterprise-ai/shared/env/AI-OS-V6-CLEAN-REBUILD-V1/
├── vafox-auth.env
├── agents.env
├── knowledge.env
├── workflows.env
├── wecom.env
├── dify-adapter.env
├── milvus.env
├── minio.env
└── postgres.env
```

Rules:

- Do not reuse production write credentials for staging validation.
- Use staging-only callback URLs, API keys, and service tokens.
- Store secrets outside Git and reference them through environment files or a secret manager.
- Verify every service has explicit `SERVICE_NAME`, `RELEASE_ID`, `ENVIRONMENT=staging`, `LOG_LEVEL`, and health check settings.
- Validate that any production read-only integration is explicitly marked read-only.

### 3.3 Data and migration preparation

- Export schema-only snapshots before any migration rehearsal.
- Rehearse migrations against staging PostgreSQL and staging Milvus collections only.
- Keep MinIO staging buckets separate from production buckets.
- Generate a migration report that includes applied revisions, rollback scripts, and destructive-operation review.

## 4. Service Mapping

| Service | Release role | Staging endpoint / binding | Data dependency | Validation owner |
| --- | --- | --- | --- | --- |
| `vafox-auth` | Identity, sessions, token validation, RBAC | Internal staging auth route; no production cookie domain cutover | PostgreSQL auth schema; external identity provider test credentials | Platform/Security |
| `agents` | AI workforce agent runtime and orchestration | Internal staging agent API | PostgreSQL agent state; knowledge API; Dify adapter as configured | AI Runtime |
| `knowledge` | Enterprise knowledge service and retrieval API | Internal staging knowledge API | Milvus staging collections; MinIO staging objects; PostgreSQL metadata | Knowledge Engineering |
| `workflows` | Business process automation and workflow execution | Internal staging workflow API | PostgreSQL workflow state; agents service | Automation |
| `WeCom` | Enterprise WeCom integration gateway | Staging callback URL only | WeCom sandbox/test app credentials; no production callback replacement | Integrations/Security |
| `Dify adapter` | Dify-compatible adapter for model/app integration | Internal staging adapter API | Dify staging app credentials; agents and knowledge services | AI Platform |
| `Milvus` | Vector database for retrieval | Staging Milvus instance/collection namespace | Staging vector collections only | Data Platform |
| `MinIO` | Object storage for documents, artifacts, and evidence | Staging MinIO buckets | Staging buckets and scoped access keys | Data Platform |
| `PostgreSQL` | Relational metadata, auth, workflow, and operational state | Staging PostgreSQL database/schema | Staging clone or clean seed, never production write target | DBA/Platform |

## 5. Build Process

### 5.1 Artifact assembly

1. Prepare the release directory:

   ```bash
   mkdir -p /opt/vafox/enterprise-ai/releases/AI-OS-V6-CLEAN-REBUILD-V1
   ```

2. Copy or checkout the approved source into the release directory.
3. Install dependencies using locked manifests only.
4. Build application artifacts and service images with deterministic tags:

   ```text
   vafox-auth:AI-OS-V6-CLEAN-REBUILD-V1
   agents:AI-OS-V6-CLEAN-REBUILD-V1
   knowledge:AI-OS-V6-CLEAN-REBUILD-V1
   workflows:AI-OS-V6-CLEAN-REBUILD-V1
   wecom:AI-OS-V6-CLEAN-REBUILD-V1
   dify-adapter:AI-OS-V6-CLEAN-REBUILD-V1
   milvus-config:AI-OS-V6-CLEAN-REBUILD-V1
   minio-config:AI-OS-V6-CLEAN-REBUILD-V1
   postgres-migrations:AI-OS-V6-CLEAN-REBUILD-V1
   ```

5. Generate checksums:

   ```bash
   find /opt/vafox/enterprise-ai/releases/AI-OS-V6-CLEAN-REBUILD-V1 -type f -print0 | sort -z | xargs -0 sha256sum > /opt/vafox/enterprise-ai/shared/evidence/AI-OS-V6-CLEAN-REBUILD-V1/checksums.sha256
   ```

### 5.2 Manifest requirements

Create `RELEASE_MANIFEST.json` inside the release directory with:

- release name and release ID
- source branch and commit SHA
- build host and build timestamp
- service image tags and digests
- dependency lockfile hashes
- database migration revision list
- Milvus collection namespace
- MinIO bucket names
- staging validation status
- health check summary
- rollback anchor: `fba3c17`
- explicit flag: `production_cutover=false`

## 6. Staging Validation

### 6.1 Staging activation

Staging validation may point `staging-enterprise-ai` to the future release:

```bash
ln -sfn releases/AI-OS-V6-CLEAN-REBUILD-V1 /opt/vafox/enterprise-ai/staging-enterprise-ai
```

Do **not** modify:

```text
/opt/vafox/enterprise-ai/current-enterprise-ai
```

### 6.2 Validation sequence

1. Start staging services on non-production ports or isolated staging hosts.
2. Confirm environment files load correctly and contain `ENVIRONMENT=staging`.
3. Run database migration rehearsal against staging PostgreSQL.
4. Run Milvus collection creation and vector indexing smoke tests.
5. Run MinIO bucket read/write smoke tests using staging buckets.
6. Validate `vafox-auth` login, token issue, token refresh, and RBAC denial paths.
7. Validate `agents` task execution with at least one deterministic test prompt.
8. Validate `knowledge` retrieval with seeded staging documents.
9. Validate `workflows` creation, execution, retry, and audit logging.
10. Validate WeCom sandbox callbacks without changing production callbacks.
11. Validate Dify adapter request/response compatibility using staging Dify credentials.
12. Capture logs, screenshots where applicable, response payloads, and command outputs.

## 7. Health Checks

Each service must expose or provide a health signal that is validated before release approval.

| Service | Required checks | Pass criteria |
| --- | --- | --- |
| `vafox-auth` | `/health`, database connection, token signing/verification, RBAC smoke test | HTTP 200, DB reachable, valid signed token, expected denial for unauthorized role |
| `agents` | `/health`, model/provider readiness, task execution smoke test | HTTP 200, provider configured, deterministic task completes |
| `knowledge` | `/health`, Milvus connectivity, MinIO connectivity, retrieval smoke test | HTTP 200, vector search succeeds, object fetch succeeds |
| `workflows` | `/health`, queue/worker status, workflow execution test | HTTP 200, worker online, test workflow completes |
| `WeCom` | callback verification endpoint, sandbox message receive/send test | callback validates, sandbox message path succeeds |
| `Dify adapter` | `/health`, adapter compatibility test, timeout/error mapping test | HTTP 200, compatible response schema, expected error mapping |
| `Milvus` | collection list, insert/search test, index status | staging collection exists, insert/search succeeds, index loaded |
| `MinIO` | bucket list, object put/get/delete test | staging bucket accessible and scoped credentials work |
| `PostgreSQL` | connection, migration status, read/write test on staging schema | DB reachable, migrations current, staging write/read succeeds |

Recommended command evidence pattern:

```bash
curl -fsS http://127.0.0.1:<service-port>/health | tee evidence/<service>-health.json
```

## 8. Rollback Strategy

Because this plan does not perform production cutover, rollback is primarily a release rejection path:

1. Keep `current-enterprise-ai -> releases/fba3c17` unchanged.
2. Stop or remove staging services for `AI-OS-V6-CLEAN-REBUILD-V1` if validation fails.
3. Preserve evidence and logs under:

   ```text
   /opt/vafox/enterprise-ai/shared/evidence/AI-OS-V6-CLEAN-REBUILD-V1/
   ```

4. Do not delete the failed release candidate until root cause review is complete.
5. If staging data migrations must be reverted, run only staging rollback scripts and attach the output to evidence.
6. If a later approved cutover occurs, the production rollback anchor remains `releases/fba3c17` until a newer release is formally certified.

Future production rollback after an approved cutover would require a separate cutover runbook and must include:

```bash
ln -sfn releases/fba3c17 /opt/vafox/enterprise-ai/current-enterprise-ai
```

That command is documented for rollback planning only and must not be executed during this preparation phase.

## 9. Release Evidence Requirements

Create a dedicated evidence directory:

```text
/opt/vafox/enterprise-ai/shared/evidence/AI-OS-V6-CLEAN-REBUILD-V1/
```

Required evidence files:

- `source_provenance.txt` — branch, commit SHA, working tree status, build operator, timestamp.
- `RELEASE_MANIFEST.json` — copied from the release directory after build.
- `checksums.sha256` — checksum list for release artifacts.
- `dependency_audit.txt` — dependency lockfile verification and vulnerability scan output where available.
- `migration_rehearsal_postgres.txt` — staging PostgreSQL migration output and rollback notes.
- `milvus_validation.txt` — collection, index, insert/search, and namespace evidence.
- `minio_validation.txt` — staging bucket and object operation evidence.
- `service_mapping.txt` — final service ports, internal routes, image tags, and environment files used.
- `healthchecks/` — one health response file per service.
- `staging_smoke_tests.txt` — end-to-end staging validation output.
- `wecom_sandbox_validation.txt` — callback and sandbox message evidence.
- `dify_adapter_validation.txt` — compatibility request/response evidence.
- `rollback_readiness.txt` — proof that `current-enterprise-ai` still points to `releases/fba3c17` and rollback anchor is available.
- `approval_record.md` — release owner, security owner, data owner, validation result, and explicit production cutover status.

## 10. Approval Gate

The release candidate can be marked build-ready only when all of the following are true:

- `current-enterprise-ai` still points to `releases/fba3c17`.
- `AI-OS-V6-CLEAN-REBUILD-V1` has a complete release directory and manifest.
- All services have passing staging health checks.
- PostgreSQL, Milvus, and MinIO validations are attached as evidence.
- WeCom and Dify adapter validations use staging or sandbox credentials only.
- Rollback anchor `fba3c17` is verified and documented.
- Approval record states `production_cutover=false`.

## 11. Explicit Non-Cutover Statement

This plan prepares the future `VAFOX AI Workforce / AI-OS-V6-CLEAN-REBUILD-V1` release for staging validation and evidence collection only. It must not change the production symlink, production routing, production credentials, production callbacks, or production data paths for `ai.vafox.com`.
