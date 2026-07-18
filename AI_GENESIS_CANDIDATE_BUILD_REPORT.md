# AI Genesis Candidate Build Report

Target: `ai.vafox.com`  
Current production pointer: `current-enterprise-ai -> releases/fba3c17`  
Future candidate: `AI Workforce Genesis Candidate`  
Release mode: **Release Candidate only**  
Production cutover status: **Not authorized / not performed**

## 0. Non-Production Guardrails

This build report defines the execution record for an isolated AI Genesis release candidate. It must not be used as a production cutover runbook.

Hard rules:

- Do not modify `current-enterprise-ai`.
- Do not repoint production from `releases/fba3c17`.
- Do not reload production nginx for live traffic changes.
- Do not write to production databases, production object storage, production vector indexes, production queues, or production WeCom recipients.
- Do not reuse production ports unless they are explicitly bound to an isolated preview listener.
- Stop the candidate immediately if any validation writes to an unauthorized production target.

## 1. Candidate Identity

| Field | Value |
|---|---|
| Candidate name | `AI Workforce Genesis Candidate` |
| Candidate version | `AI-OS-V6-CLEAN-REBUILD-V1-RC` |
| Candidate ID | `ai-genesis-rc-YYYYMMDD-HHMM-<short_commit>` |
| Target domain | `ai.vafox.com` |
| Preview URL | `https://ai.vafox.com/__preview/ai-genesis/<candidate_id>` or approved staging host |
| Current production release | `releases/fba3c17` |
| Current production symlink | `current-enterprise-ai -> releases/fba3c17` |
| Build owner | TBD |
| Validation owner | TBD |
| Security owner | TBD |
| Operations owner | TBD |

## 2. Execution Plan

### 2.1 Create Candidate Release Directory

Create a new immutable release directory. The directory name must include the UTC build timestamp and short commit.

```bash
cd /opt/ai-vafox
export GIT_COMMIT="$(git rev-parse HEAD)"
export SHORT_COMMIT="$(git rev-parse --short HEAD)"
export BUILD_TIME_UTC="$(date -u +%Y%m%d-%H%M)"
export CANDIDATE_ID="ai-genesis-rc-${BUILD_TIME_UTC}-${SHORT_COMMIT}"
export RELEASE_DIR="/opt/ai-vafox/releases/${CANDIDATE_ID}"

# Guardrail: prove production pointer before any candidate work.
readlink current-enterprise-ai
# Expected: releases/fba3c17

test "$(readlink current-enterprise-ai)" = "releases/fba3c17"
mkdir -p "${RELEASE_DIR}"
mkdir -p "${RELEASE_DIR}/logs" "${RELEASE_DIR}/evidence" "${RELEASE_DIR}/nginx-preview"
```

Acceptance evidence:

- `readlink current-enterprise-ai` returns `releases/fba3c17`.
- `${RELEASE_DIR}` exists.
- No existing release directory was overwritten.

### 2.2 Prepare Source

Prepare source from the approved release-candidate commit only.

```bash
cd /opt/ai-vafox/source/foxbrain-faos
git status --short
git rev-parse HEAD
git branch --show-current

git archive --format=tar HEAD | tar -x -C "${RELEASE_DIR}"
```

Source rules:

- `git status --short` must be empty before packaging.
- The manifest commit must match `git rev-parse HEAD`.
- Secrets, `.env` production files, live volumes, and production database dumps must not be copied into the candidate directory.

Acceptance evidence:

- Clean working tree output.
- Commit SHA recorded.
- Source extracted under `${RELEASE_DIR}`.

### 2.3 Build Services

Build all candidate services inside the candidate directory or into candidate-scoped artifacts.

Required services:

| Service | Build requirement | Runtime isolation |
|---|---|---|
| `auth` | Build login/session/RBAC service artifacts. | Candidate-only env and port/socket. |
| `agents` | Build AI Workforce agent orchestration artifacts. | Mutating tools disabled or dry-run. |
| `knowledge` | Build retrieval/index service artifacts. | Staging index, read-only replica, or sandbox. |
| `workflows` | Build workflow orchestration artifacts. | Dry-run workflow execution only. |
| `wecom` | Build WeCom integration artifacts. | Sandbox, dry-run, or allowlisted preview channel only. |
| `api` | Build public/internal API artifacts. | Candidate-only auth and rate limits. |
| `nginx-preview` | Generate preview server/location config. | Preview route only; no production route replacement. |

Suggested build skeleton:

```bash
cd "${RELEASE_DIR}"

# Use repository-specific build commands from lockfiles and service definitions.
# Examples only; replace with approved commands for the actual service layout.
python -m compileall foxbrain_os
python scripts/generate_deployment_metadata.py > "${RELEASE_DIR}/deployment_metadata.json"

# If frontend/package services exist, install/build from lockfiles only.
# npm ci && npm run build
# docker compose -f docker-compose.rc.yml build
```

Acceptance evidence:

- Build commands and output logs saved in `${RELEASE_DIR}/evidence/build.log`.
- Service artifact paths exist.
- Runtime ports/sockets are candidate-specific.

### 2.4 Generate Release Manifest

Create `${RELEASE_DIR}/RELEASE_MANIFEST.json` after build artifacts are finalized.

Required manifest fields:

```json
{
  "version": "AI-OS-V6-CLEAN-REBUILD-V1-RC",
  "candidate_id": "<candidate_id>",
  "target": "ai.vafox.com",
  "current_production": "current-enterprise-ai -> releases/fba3c17",
  "commit": "<git_commit_sha>",
  "build_time_utc": "<iso_8601_timestamp>",
  "services": [
    {"name": "auth", "artifact": "<path>", "port_or_socket": "<candidate-only>"},
    {"name": "agents", "artifact": "<path>", "port_or_socket": "<candidate-only>"},
    {"name": "knowledge", "artifact": "<path>", "port_or_socket": "<candidate-only>"},
    {"name": "workflows", "artifact": "<path>", "port_or_socket": "<candidate-only>"},
    {"name": "wecom", "artifact": "<path>", "port_or_socket": "<candidate-only>"},
    {"name": "api", "artifact": "<path>", "port_or_socket": "<candidate-only>"},
    {"name": "nginx-preview", "artifact": "<path>", "port_or_socket": "<preview-only>"}
  ],
  "checksum": "sha256:<release_tree_hash>",
  "checksums": {
    "release_tree": "sha256:<hash>",
    "service_bundle": "sha256:<hash>",
    "static_assets": "sha256:<hash>",
    "nginx_preview_config": "sha256:<hash>",
    "manifest": "sha256:<hash>"
  }
}
```

Suggested checksum commands:

```bash
cd "${RELEASE_DIR}"
find . -type f \
  ! -path './logs/*' \
  ! -path './evidence/*' \
  ! -name 'checksums.sha256' \
  -print0 | sort -z | xargs -0 sha256sum > checksums.sha256
sha256sum RELEASE_MANIFEST.json > RELEASE_MANIFEST.json.sha256
python -m json.tool RELEASE_MANIFEST.json > /dev/null
```

Acceptance evidence:

- `RELEASE_MANIFEST.json` exists and parses as JSON.
- Manifest includes version, commit, build time, services, and checksum data.
- `checksums.sha256` exists and verifies candidate artifacts.

### 2.5 Start Isolated Staging Runtime

Start the candidate runtime without changing production process definitions.

```bash
cd "${RELEASE_DIR}"
cp .env.rc.example .env.rc
# Fill .env.rc with staging/sandbox/read-only values only.

# Candidate runtime examples; use whichever is approved for this repo/host.
# docker compose --env-file .env.rc -f docker-compose.rc.yml up -d
# systemctl --user start "ai-genesis-${CANDIDATE_ID}.target"
# ./scripts/start_candidate_runtime.sh "${CANDIDATE_ID}"
```

Runtime isolation requirements:

- `APP_ENV=release_candidate` or `APP_ENV=staging`.
- `RELEASE_ID=${CANDIDATE_ID}`.
- Candidate services bind to candidate-only ports or sockets.
- Logs write to `${RELEASE_DIR}/logs`.
- WeCom mode is `sandbox`, `dry_run`, or allowlisted preview channel.
- Any database or knowledge target is staging, read-only replica, or approved sandbox.

Acceptance evidence:

- Candidate service status output saved.
- Candidate health endpoint returns candidate version and commit.
- Production pointer still resolves to `releases/fba3c17`.

## 3. Validation Matrix

All validation must target the isolated candidate runtime or preview route only.

| Area | Validation | Required result | Evidence |
|---|---|---|---|
| Login | Staging user logs in through preview route. | Login succeeds; session scoped to candidate. | Sanitized request IDs and status codes. |
| Auth | Invalid login and cross-role access tests. | Invalid access rejected; RBAC enforced. | Negative test output. |
| Agents | AI Workforce routes prompts to correct agents without manual selection. | CEO, finance, supply, store, growth, and fallback routes behave safely. | Prompt summaries and routing logs. |
| Knowledge | Approved staging queries retrieve relevant knowledge. | Results respect tenant/role boundaries and show source context. | Retrieval logs and dataset/index version. |
| Workflows | Dry-run task or approval workflow is created. | No production mutation; approval chain is auditable. | Dry-run workflow ID and audit summary. |
| WeCom | Sandbox/dry-run notification is rendered and validated. | No production recipient receives a message. | Payload summary and allowlist proof. |
| API | Health, protected route, schema, and negative auth tests. | Candidate metadata returned; protected routes enforce auth. | Contract/smoke output. |
| Nginx preview | Preview route reaches candidate services only. | Production route unchanged; nginx config validates. | `nginx -t`, route diff, preview response headers. |

Suggested validation commands:

```bash
readlink /opt/ai-vafox/current-enterprise-ai
curl -fsS "${PREVIEW_URL}/health"
curl -fsS "${PREVIEW_URL}/api/health"
python -m json.tool "${RELEASE_DIR}/RELEASE_MANIFEST.json"
sha256sum -c "${RELEASE_DIR}/RELEASE_MANIFEST.json.sha256"
nginx -t
```

## 4. Candidate Build Results

| Check | Status | Evidence path / notes |
|---|---|---|
| Production pointer unchanged | Pending | TBD |
| Candidate directory created | Pending | TBD |
| Source prepared from clean commit | Pending | TBD |
| Services built | Pending | TBD |
| Release manifest generated | Pending | TBD |
| Checksums generated | Pending | TBD |
| Isolated staging runtime started | Pending | TBD |
| Login validation | Pending | TBD |
| Auth validation | Pending | TBD |
| Agents validation | Pending | TBD |
| Knowledge validation | Pending | TBD |
| Workflows validation | Pending | TBD |
| WeCom validation | Pending | TBD |
| API validation | Pending | TBD |
| Nginx preview validation | Pending | TBD |

## 5. Promotion Approval Gate

This report does not approve promotion. It defines the gate that must be satisfied before a separate production promotion plan can be requested.

Promotion may be considered only when every item below is true:

- Production remained on `current-enterprise-ai -> releases/fba3c17` for the full RC build and validation window.
- `RELEASE_MANIFEST.json` is complete and checksum verification passes.
- Login, auth, agents, knowledge, workflows, WeCom, API, and nginx preview validations all pass with attached evidence.
- No production data, production WeCom recipient, production workflow, or production nginx live route was modified.
- Candidate logs contain no secrets and no unauthorized mutation evidence.
- Security owner signs off on auth, secret handling, and exposed preview routes.
- Data owner signs off on database, vector, object storage, and knowledge isolation.
- Business owner signs off on AI Workforce behavior.
- Operations owner signs off on runtime health, monitoring, rollback readiness, and preview isolation.
- A separate production cutover plan is written and approved.

Approval record:

| Role | Name | Decision | Timestamp UTC | Notes |
|---|---|---|---|---|
| Business owner | TBD | Pending | TBD | TBD |
| Engineering owner | TBD | Pending | TBD | TBD |
| Security owner | TBD | Pending | TBD | TBD |
| Data owner | TBD | Pending | TBD | TBD |
| Operations owner | TBD | Pending | TBD | TBD |

## 6. Final Candidate Decision

| Field | Value |
|---|---|
| Candidate result | Pending |
| Promotion eligible | No, pending validation and approvals |
| Production cutover performed | No |
| Production symlink changed | No |
| `current-enterprise-ai` final expected value | `releases/fba3c17` |

Final statement: this execution is a release-candidate build and validation process only. It must not modify production or change the `current-enterprise-ai` symlink.
