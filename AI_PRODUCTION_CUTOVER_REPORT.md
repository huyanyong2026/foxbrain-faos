# AI Production Cutover Report

Target: `ai.vafox.com`  
Requested target runtime: `VAFOX AI Workforce` / `AI-OS-V6-CLEAN-REBUILD-V1`  
Report time: `2026-07-18T02:16:26Z`  
Repository baseline checked: `561d6d606d5eabcb22ecd28efdfe2d6d82132642` on branch `work`

## Before

The cutover did **not** proceed. The mandatory pre-cutover checklist did not pass from this execution environment, so execution stopped before any production change.

Important governing constraints found in the referenced cutover documents:

- `AI_PRE_CUTOVER_CHECKLIST.md` currently states **NO CUTOVER**, **do not modify production**, and prohibits changes to DNS, nginx production routing, WeCom production callbacks, n8n production workflow active states, PostgreSQL production schema/data, Milvus production collections, and MinIO production objects.
- `AI_GENESIS_ALIGNMENT_PLAN.md` identifies the existing production app location as `/opt/ai-vafox`, current release baseline as `fba3c17`, and the target as `VAFOX AI Workforce` plus `AI-OS-V6-CLEAN-REBUILD-V1`.
- `AI_GENESIS_IMPLEMENTATION_PLAN.md` states that no production cutover or production data delete is authorized by that plan and that production must remain on the documented baseline until a separately approved cutover plan exists.

Pre-change evidence collected from this repository/workspace:

| Check | Result | Evidence |
| --- | --- | --- |
| Git baseline | Captured | `git rev-parse HEAD` returned `561d6d606d5eabcb22ecd28efdfe2d6d82132642`. |
| Git working tree | Clean before report creation | `git status --short` returned no tracked/untracked changes before this report was written. |
| Docker Compose availability | **Critical fail** | `docker compose -f docker-compose.yml config` failed with `/bin/bash: line 4: docker: command not found`. |
| Production route probes | **Critical fail / blocked** | `curl -fsSI` to `https://ai.vafox.com/`, `/auth/`, `/console`, and `/n8n` each returned `HTTP/1.1 403 Forbidden` from `envoy`. |
| Destructive SQL scan | Findings require owner review | `rg -n --ignore-case '\b(DROP\s+TABLE\|DROP\s+DATABASE\|TRUNCATE\|DELETE\s+FROM)\b' . --glob '!node_modules' --glob '!.git'` found delete/drop statements in application/test/support files. No migration execution was performed. |
| Local V6 identity references | Present in repo | `docker-compose.yml` references `vafox-genesis:${FOXBRAIN_VERSION:-AI-OS-V6-CLEAN-REBUILD-V1}` and passes `FOXBRAIN_VERSION` into app containers. |

## Backup evidence

Required production backups were **not completed from this environment**. This is a hard stop for cutover.

| Required backup | Status | Reason |
| --- | --- | --- |
| PostgreSQL globals and application database | Not completed | No production PostgreSQL connection details, database name, credentials, or approved secure backup path were available in this environment. |
| Milvus | Not completed | `milvus-backup` was not available in this environment and no production Milvus backup configuration was provided. |
| MinIO | Not completed | `mc` was not available in this environment and no MinIO alias/bucket details were provided. |
| n8n workflows | Not completed | `n8n` CLI was not available in this environment and no production n8n export context was provided. |
| Current nginx config | Not completed | No production host nginx access was available; `nginx -T`/`nginx -t` could not be run against the live host configuration. |
| Current Docker compose state | Not completed | Docker CLI was unavailable in this environment, so container/image inventories and compose state could not be captured. |

No destructive commands were run. No production volume deletion, database reset, schema migration, object rewrite, vector rewrite, workflow activation change, nginx route switch, or DNS change was attempted.

## Changes

No runtime cutover changes were made.

Repository-only change created by this execution:

- Added `AI_PRODUCTION_CUTOVER_REPORT.md` to document the failed pre-cutover gate, missing backup evidence, validation blockers, and rollback posture.

Operational changes explicitly **not** performed:

- No PostgreSQL changes.
- No Milvus changes.
- No MinIO changes.
- No n8n workflow changes.
- No WeCom callback changes.
- No nginx production route changes.
- No Docker container/image/runtime changes.
- No migration scripts executed.

## Validation

Validation did not reach the new-runtime validation phase because the pre-cutover gate failed.

| Validation area | Status | Evidence / blocker |
| --- | --- | --- |
| Login | Not validated | Production `/auth/` returned 403 from this environment; no authenticated test session/cookie was provided. |
| Agents | Not validated | No validated staging `ai-workforce` runtime endpoint or test token was provided. |
| Knowledge retrieval | Not validated | No staging PostgreSQL/Milvus/MinIO restore endpoints or known query set were provided. |
| Workflows | Not validated | n8n CLI/context unavailable; no staging workflow adapter endpoint was provided. |
| WeCom callback | Not validated | No callback baseline evidence, sample signature data, token/secret location evidence, or staging adapter endpoint was provided. |
| API health | Not validated | No staging host for `/api/ai-workforce/health` was provided; production route probes were blocked with 403. |
| SSL/domain | Partially probed, blocked | HTTPS responded at `ai.vafox.com`, but all probed paths returned 403, so route behavior could not be validated. |

Critical blockers that stopped the cutover:

1. Mandatory production backups were not captured.
2. Docker/nginx/PostgreSQL/Milvus/MinIO/n8n production access or tooling was unavailable from this environment.
3. Production endpoint probes returned 403, preventing baseline route validation.
4. The checklist requires staging validation before nginx switch, but no staging host/test credentials were available.
5. The referenced checklist and implementation plan themselves explicitly stop before production cutover and require future owner-approved gates.

## Rollback status

Rollback remains a **no-op from this execution** because no production runtime, route, data, volume, callback, or workflow changes were made.

Future rollback readiness remains incomplete until operators capture and verify, at minimum:

- A rendered baseline nginx config (`nginx -T`) and syntax validation (`nginx -t`).
- Current Docker container/image/compose state.
- PostgreSQL globals and application database backups, with staging restore evidence.
- Milvus backup and staging restore/query evidence.
- MinIO bucket/object inventory and checksum evidence.
- n8n workflow export evidence and disabled staging import evidence.
- WeCom callback baseline evidence without exposing secrets.
- A tested one-command nginx route rollback procedure in staging.

## Decision

**Cutover status: STOPPED / NOT EXECUTED.**

The requested production cutover can proceed only after every critical pre-cutover item passes or has an explicit owner-approved exception, mandatory backups are completed and restore-tested, staging validation passes, and the governing plans/checklist are updated or superseded by an explicitly approved production cutover runbook.
