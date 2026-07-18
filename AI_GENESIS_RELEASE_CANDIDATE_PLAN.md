# AI Genesis Release Candidate Plan

Target: `ai.vafox.com`  
Current production: `releases/fba3c17`  
Future release line: `VAFOX AI Workforce / AI-OS-V6-CLEAN-REBUILD-V1`  
Release type: **Release Candidate only**

## Non-Cutover Rule

This plan does **not** authorize a production cutover.

The release candidate must be built, staged, validated, and reviewed without changing production traffic for `ai.vafox.com`. Production must remain pinned to `releases/fba3c17` until a separate promotion decision is approved and executed.

## 1. Candidate Release Directory

Each release candidate must be placed in an immutable directory using a unique candidate identifier:

```text
/opt/ai-vafox/releases/<candidate_id>
```

Candidate identifier format:

```text
ai-genesis-rc-YYYYMMDD-HHMM-<short_commit>
```

Example:

```text
/opt/ai-vafox/releases/ai-genesis-rc-20260718-1200-a1b2c3d
```

Directory requirements:

- The candidate directory must be newly created for each RC.
- The directory must not overwrite `releases/fba3c17` or any previous release.
- Runtime assets, compiled outputs, static assets, service definitions, and release metadata must be self-contained under the candidate directory.
- Shared state, secrets, databases, and production symlinks must not be copied into the candidate directory.
- Any `current`, `production`, or live nginx symlink must remain unchanged during RC creation.

## 2. Build Inputs

### Source

Required source inputs:

- Git repository: `foxbrain-faos`.
- Branch: current release-candidate branch.
- Commit: exact Git commit used for the candidate build.
- Target release line: `AI-OS-V6-CLEAN-REBUILD-V1`.
- Target domain for preview validation: `ai.vafox.com` through a non-production preview route.

Source rules:

- Build from a clean Git working tree.
- Record `git rev-parse HEAD` in the release manifest.
- Record branch name and remote tracking reference when available.
- Do not build from uncommitted local changes.

### Dependencies

Required dependency inputs:

- Lockfiles committed in the repository, such as package, Python, or service-specific lockfiles.
- Base runtime versions for Node.js, Python, system packages, nginx, process manager, and any worker runtime.
- Internal service contracts for auth, agents, knowledge, workflows, WeCom, and API routes.
- Build-time tool versions used to compile or package the candidate.

Dependency rules:

- Install dependencies from lockfiles where lockfiles exist.
- Do not upgrade dependencies as part of RC packaging unless the upgrade is explicitly part of the candidate scope.
- Record dependency installer command output or dependency snapshot hashes as build evidence.
- Separate development-only dependencies from runtime dependencies.

### Environment Isolation

The RC must be isolated from production:

- Use a candidate-specific environment file, for example:

```text
/opt/ai-vafox/releases/<candidate_id>/.env.rc
```

- Use staging or preview credentials only.
- Use staging database schemas, read-only production replicas, mocked external integrations, or explicitly approved sandbox endpoints.
- Do not write to production databases, production queues, production object storage, or production WeCom channels.
- Bind RC services to candidate-specific ports or sockets.
- Expose RC through an nginx preview location or preview hostname only.
- Ensure logs are written to candidate-specific log paths.

Minimum isolation variables to define:

| Variable | Requirement |
|---|---|
| `APP_ENV` | `release_candidate` or `staging` |
| `RELEASE_ID` | `<candidate_id>` |
| `PUBLIC_BASE_URL` | Preview URL, not live production route |
| `DATABASE_URL` | Staging, read-only replica, or sandbox only |
| `REDIS_URL` | Staging or candidate namespace only |
| `WECOM_MODE` | `sandbox`, `dry_run`, or preview channel only |
| `LOG_DIR` | `/opt/ai-vafox/releases/<candidate_id>/logs` |

## 3. Release Manifest

Create a manifest at:

```text
/opt/ai-vafox/releases/<candidate_id>/RELEASE_MANIFEST.json
```

Required manifest fields:

```json
{
  "version": "AI-OS-V6-CLEAN-REBUILD-V1-RC",
  "candidate_id": "<candidate_id>",
  "target": "ai.vafox.com",
  "current_production": "releases/fba3c17",
  "commit": "<git_commit_sha>",
  "branch": "<git_branch>",
  "build_time_utc": "<iso_8601_timestamp>",
  "builder": "<build_actor_or_system>",
  "services": [
    {
      "name": "auth",
      "artifact": "<path>",
      "runtime": "<runtime_version>",
      "port_or_socket": "<candidate_port_or_socket>"
    },
    {
      "name": "agents",
      "artifact": "<path>",
      "runtime": "<runtime_version>",
      "port_or_socket": "<candidate_port_or_socket>"
    },
    {
      "name": "knowledge",
      "artifact": "<path>",
      "runtime": "<runtime_version>",
      "port_or_socket": "<candidate_port_or_socket>"
    },
    {
      "name": "workflows",
      "artifact": "<path>",
      "runtime": "<runtime_version>",
      "port_or_socket": "<candidate_port_or_socket>"
    },
    {
      "name": "wecom",
      "artifact": "<path>",
      "runtime": "<runtime_version>",
      "port_or_socket": "<candidate_port_or_socket>"
    },
    {
      "name": "api",
      "artifact": "<path>",
      "runtime": "<runtime_version>",
      "port_or_socket": "<candidate_port_or_socket>"
    },
    {
      "name": "nginx-preview",
      "artifact": "<path>",
      "runtime": "nginx <version>",
      "port_or_socket": "<preview_listener>"
    }
  ],
  "checksums": {
    "artifact_archive": "sha256:<hash>",
    "static_assets": "sha256:<hash>",
    "service_bundle": "sha256:<hash>",
    "nginx_preview_config": "sha256:<hash>"
  }
}
```

Checksum rules:

- Use SHA-256 for all release artifacts.
- Store generated checksum files in the candidate directory.
- Include checksums for compiled assets, backend bundles, service configs, migration files, and nginx preview config.
- Recompute checksums after any rebuild.

## 4. Staging Validation

All validation must run against the RC preview environment only.

### Auth

Validation requirements:

- Login succeeds for approved staging users.
- Invalid credentials are rejected.
- Session expiration and refresh behavior match policy.
- Role-based access control prevents cross-role access.
- Store-scoped users cannot access other store data.
- Admin-only actions are blocked for non-admin users.

Required evidence:

- Auth test command output.
- Sample sanitized request IDs.
- No secrets, passwords, tokens, or session cookies in evidence.

### Agents

Validation requirements:

- AI workforce routing works without manual agent selection.
- CEO, finance, commerce, supply, store, and workflow agents respond under expected scopes.
- Agent responses cite or identify the data source used where applicable.
- Agent fallback behavior is safe when data is unavailable.
- Agent actions that would mutate production data remain disabled in RC.

Required evidence:

- Prompt/response summaries.
- Agent routing logs.
- Safety-denial examples for unauthorized or production-mutating actions.

### Knowledge

Validation requirements:

- Knowledge retrieval returns relevant documents for approved staging queries.
- Tenant, role, and confidentiality boundaries are enforced.
- Stale, missing, or low-confidence knowledge is surfaced as such.
- Knowledge updates are restricted to staging indexes or dry-run mode.

Required evidence:

- Retrieval test output.
- Index version or dataset timestamp.
- Access-control test results.

### Workflows

Validation requirements:

- Workflow creation works in staging or dry-run mode.
- Approval chains are generated correctly.
- Task assignment follows role and store rules.
- Workflow status transitions are auditable.
- Failed workflow steps retry or fail safely.

Required evidence:

- Workflow dry-run IDs.
- Approval route summaries.
- Audit log references.

### WeCom

Validation requirements:

- WeCom integration runs in sandbox, dry-run, or preview-channel mode only.
- Message templates render correctly.
- User mapping resolves approved staging identities.
- No production WeCom recipients receive RC messages.
- Webhook signatures and callback validation are verified where applicable.

Required evidence:

- Dry-run message payload summaries.
- Preview channel delivery confirmation if enabled.
- Recipient allowlist used for validation.

### API

Validation requirements:

- Health endpoints return candidate release metadata.
- API route contracts match expected schemas.
- Authentication and authorization are enforced on protected endpoints.
- Rate limits and request size limits are active.
- Error responses do not leak secrets or stack traces.

Required evidence:

- API contract test results.
- Health endpoint response showing candidate ID.
- Negative authorization test results.

### Nginx Preview

Validation requirements:

- Preview route points to `/opt/ai-vafox/releases/<candidate_id>` services only.
- Production `ai.vafox.com` routing remains unchanged.
- TLS configuration remains valid.
- Preview route blocks indexing and includes appropriate no-cache headers.
- Static assets load from candidate artifact paths.

Required evidence:

- `nginx -t` output.
- Diff or listing proving production config was not changed.
- Preview request headers and response status.

## 5. Smoke Tests

Minimum RC smoke-test checklist:

| Area | Smoke Test | Expected Result |
|---|---|---|
| Release directory | Verify `/opt/ai-vafox/releases/<candidate_id>` exists | Directory exists and contains manifest |
| Manifest | Parse `RELEASE_MANIFEST.json` | Required fields are present and valid |
| Health | Call RC health endpoint | Returns `candidate_id`, version, and commit |
| Auth | Login with staging user | Login succeeds and token/session is scoped to RC |
| Auth negative | Login with invalid user | Request is rejected |
| Agents | Ask business-risk question | Correct agent routing and safe answer |
| Knowledge | Run approved retrieval query | Relevant staging knowledge returned |
| Workflows | Create dry-run approval task | Task generated without production mutation |
| WeCom | Send dry-run notification | Payload renders and targets allowlist only |
| API | Run contract test suite | Protected routes enforce auth and schema |
| Nginx preview | Request preview URL | Preview serves RC; production route unchanged |
| Logs | Inspect candidate logs | No secrets or production mutations present |

Suggested smoke commands:

```bash
git status --short
git rev-parse HEAD
sha256sum /opt/ai-vafox/releases/<candidate_id>/RELEASE_MANIFEST.json
python -m json.tool /opt/ai-vafox/releases/<candidate_id>/RELEASE_MANIFEST.json
curl -fsS <preview_url>/health
curl -fsS <preview_url>/api/health
nginx -t
```

## 6. Promotion Criteria: Candidate to Production

A release candidate can be promoted only after all criteria below are met:

- Production remains on `releases/fba3c17` throughout RC validation.
- Release manifest is complete and checksum verification passes.
- Staging validation passes for auth, agents, knowledge, workflows, WeCom, API, and nginx preview.
- Smoke tests pass with evidence attached to the release review.
- No high or critical security findings remain open.
- No production data mutation occurred during RC validation.
- Performance is within approved thresholds for startup, response latency, and error rate.
- Rollback path is documented and tested in staging.
- Business owner, engineering owner, and operations owner approve promotion.
- A separate production cutover plan is created and approved.

Promotion output, when separately approved, must create or update the production pointer only after the RC has been accepted. This RC plan itself must not perform that action.

## 7. Rollback Rules

Rollback must preserve the known-good production release:

- The production fallback release is `releases/fba3c17`.
- Do not delete, modify, or repack `releases/fba3c17` during RC work.
- If an RC validation failure occurs, stop promotion consideration and keep production unchanged.
- If a preview issue affects shared infrastructure, disable only the preview route or candidate services.
- If a candidate service writes to an unauthorized target, immediately stop the candidate services, revoke candidate credentials, preserve logs, and open an incident review.
- If promotion is later approved and fails during cutover, restore the production pointer to `releases/fba3c17`, reload services, verify health, and record rollback evidence.

Rollback verification checklist:

- Production pointer resolves to `releases/fba3c17`.
- Production health endpoint is healthy.
- Production nginx config validates.
- Production auth, API, and core user journeys pass smoke tests.
- Candidate services are stopped or isolated.
- Incident notes include root cause, timestamps, and owner.

## Release Candidate Approval Record

Before promotion can be considered, complete this record:

| Field | Value |
|---|---|
| Candidate ID | TBD |
| Git commit | TBD |
| Build time UTC | TBD |
| Builder | TBD |
| Preview URL | TBD |
| Validation owner | TBD |
| Security reviewer | TBD |
| Business approver | TBD |
| Operations approver | TBD |
| RC result | Pending |

## Final Guardrail

The only allowed outcome of this plan is a validated release candidate. Any production cutover, production symlink change, production nginx route change, or live traffic migration requires a separate approved production promotion plan.
