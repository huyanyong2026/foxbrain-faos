# Production Deployment Evidence Report

Evidence collection date: 2026-07-17 UTC.

Scope: evidence only. No feature code or UI files were changed.

## Executive finding

The requested production-host inspection could not be completed from this container because the repository checkout has no GitHub remote, the GitHub CLI is not installed, no production SSH credentials or production secret values are present in the environment, and direct DNS/HTTPS from the shell is blocked or proxied. Public page retrieval through the browser/web fetch path does show legacy/public-facing UI content on the requested domains.

## 1. Latest `Production Deploy` workflow run

### Evidence collected

Command attempted:

```bash
gh run list --workflow "Production Deploy" --limit 5 --json databaseId,status,conclusion,headSha,createdAt,updatedAt,event,displayTitle,url 2>&1 || true
```

Observed output:

```text
/bin/bash: line 1: gh: command not found
```

Repository remote check:

```bash
git remote -v
```

Observed output: no remotes were configured in this checkout.

Current local commit:

```bash
git rev-parse HEAD
git log --oneline -5
```

Observed output:

```text
0c45b51e39ab866c6543be31849e063d65b59a39
0c45b51 Fix production deploy compose validation (#149)
ea5cf80 Document production runtime reality check (#148)
bb9e173 Clean up legacy Genesis governance (#147)
9d8b193 Add legacy governance cleanup audit (#146)
3686d76 Align governance tests with VAFOX Genesis (#145)
```

### Workflow definition evidence

The workflow is named `Production Deploy`, triggers on `push` to `main` and `workflow_dispatch`, and deploys with `FOXBRAIN_VERSION=AI-OS-V6-CLEAN-REBUILD-V1` and `GIT_COMMIT=${{ github.sha }}`.

The workflow order is:

1. checkout
2. release commit verification
3. workflow script validation
4. release tests
5. metadata generation
6. production secret validation
7. Docker Compose validation on CI runner
8. SSH setup
9. remote production deployment
10. public runtime verification

### Latest-run conclusion

Because the latest GitHub Actions run metadata could not be queried from this container, the actual latest workflow run status is **UNVERIFIED**.

| Requested item | Evidence status | Result |
|---|---:|---|
| Commit deployed | Not available from this environment | **UNVERIFIED** |
| Success/failure | Not available from this environment | **UNVERIFIED** |
| SSH deployment reached | Not available from this environment | **UNVERIFIED** |
| `docker compose` execution reached | Not available from this environment | **UNVERIFIED** |

Important workflow control point: if production secrets are missing, the workflow exits before SSH setup and before remote `docker compose` execution.

## 2. Production target

The workflow reads production target values from GitHub secrets:

| Target | Source in workflow | Actual value in this environment |
|---|---|---|
| `PRODUCTION_SSH_HOST` | `${{ secrets.PRODUCTION_SSH_HOST }}` | **Not exposed / unavailable** |
| `PRODUCTION_DEPLOY_PATH` | `${{ secrets.PRODUCTION_DEPLOY_PATH }}` | **Not exposed / unavailable** |

The local environment check found no `PRODUCTION_*`, SSH, VAFOX, or FoxBrain variables exposing the target values.

## 3. Production host verification

Requested production-host commands:

```bash
git rev-parse HEAD
docker ps
docker compose ps
docker images
# running container labels
# nginx upstream
```

Status: **NOT EXECUTED** from this environment.

Reason: no production SSH host/user/key/path values are available locally, and `PRODUCTION_SSH_HOST` / `PRODUCTION_DEPLOY_PATH` are GitHub Actions secrets that are not exposed to the repository checkout.

## 4. Public-domain evidence and mapping

### Public page retrieval evidence

The browser/web fetch path retrieved these public pages:

| Domain | Retrieved page evidence | Visible application identity |
|---|---|---|
| `gateway.vafox.com` | `https://gateway.vafox.com/` returned `VAFOX Gateway｜向外探索，向内成长` with outdoor-growth platform content and links to `ai.vafox.com` as “AI Outdoor ... 筹备中”. | Static/public VAFOX Gateway page, not proven to be the V6 application container. |
| `ai.vafox.com` | `https://ai.vafox.com/` redirected to `/auth/login` and returned `登录 | VAFOX 企业身份中心` / `真实身份，真实工作`. | Enterprise identity/login application. |
| `huyan.vafox.com` | `https://huyan.vafox.com/` returned `VAFOX 老板经营系统` login page. | Huyan owner/business system login application. |

### Shell network evidence

Direct shell DNS resolution failed against the container resolver:

```text
Temporary failure in name resolution
```

Direct `curl` over the configured proxy failed with:

```text
curl: (56) CONNECT tunnel failed, response 403
HTTP/1.1 403 Forbidden
server: envoy
```

Therefore shell-level IP/server mapping could not be verified.

### Repository nginx / compose mapping evidence

The repository deployment config maps the Docker Compose nginx service to `infra/nginx/huyan.vafox.com.conf` and publishes it on `${NGINX_LOOPBACK_PORT:-127.0.0.1:8088}:80`.

Repository nginx upstreams:

| Host/config | Upstream evidence in repo | Expected container / app |
|---|---|---|
| `huyan.vafox.com` | `/` proxies to `http://foxbrain-web:3000`; `/api/`, `/health/runtime`, and `/health/version` proxy to `http://foxbrain-api:8000`. | `foxbrain-nginx` -> `foxbrain-web` / `foxbrain-api`. |
| `gateway.vafox.com` example | Static root `/var/www/firefox-gateway/current`; `/health/runtime`, `/health/version`, and `/api/public/` proxy to `127.0.0.1:8091`; `/explorer` and `/api/explorer/` proxy to `127.0.0.1:8092`. | Host-level gateway static site plus local gateway/explorer processes, not the Compose `foxbrain-web` path. |
| `ai.vafox.com` example | Multiple routes including `/`, `/login`, `/home`, `/dashboard`, `/version`, `/health/version`, `/health/runtime`, `/ops-api/`, and `/static/` proxy to `127.0.0.1:5010`. | Host-level AI workspace process on port `5010`, not directly identified as a Compose service in `docker-compose.yml`. |

### Requested map

| Domain | Actual server | Actual container | Actual application | Evidence status |
|---|---|---|---|---|
| `gateway.vafox.com` | Not resolvable from shell; browser/web fetch reached a public server. | Not verifiable from this environment. Repo example suggests host static root and local ports `8091`/`8092`, not Compose service names. | Public VAFOX Gateway outdoor-growth/static site. | **PARTIAL / PUBLIC ONLY** |
| `ai.vafox.com` | Not resolvable from shell; browser/web fetch reached a public server. | Not verifiable from this environment. Repo example suggests host process on `127.0.0.1:5010`. | VAFOX enterprise identity/login app. | **PARTIAL / PUBLIC ONLY** |
| `huyan.vafox.com` | Not resolvable from shell; browser/web fetch reached a public server. | Not verifiable from this environment. Repo Compose suggests `foxbrain-nginx`, `foxbrain-web`, and `foxbrain-api`. | VAFOX 老板经营系统 login app. | **PARTIAL / PUBLIC ONLY** |

## 5. Expected vs running version

Expected release/version in repository and workflow:

```text
AI-OS-V6-CLEAN-REBUILD-V1
```

Evidence:

- `.github/workflows/production-deploy.yml` sets `FOXBRAIN_VERSION: AI-OS-V6-CLEAN-REBUILD-V1`.
- `docker-compose.yml` tags app images as `vafox-genesis:${FOXBRAIN_VERSION:-AI-OS-V6-CLEAN-REBUILD-V1}` and passes `FOXBRAIN_VERSION` into app containers.
- `deployment.json`, `foxbrain_os/platform_governance.py`, `foxbrain_os/ai_os_v6.py`, and `scripts/generate_deployment_metadata.py` all reference `AI-OS-V6-CLEAN-REBUILD-V1`.

Running production version:

```text
UNVERIFIED
```

Reason: production host commands and public `/health/version` JSON could not be verified from this shell. Public page evidence shows legacy/login/static UI surfaces, but it does not prove the running container image label or internal app version.

## Evidence gaps that require access outside this container

To finish the requested evidence without changing code, run these from an environment with GitHub Actions access and production SSH access:

```bash
# GitHub Actions latest run
gh run list --workflow "Production Deploy" --limit 1 --json databaseId,status,conclusion,headSha,createdAt,updatedAt,event,url
gh run view <RUN_ID> --log

# Production target values, without printing secrets publicly
printf 'PRODUCTION_SSH_HOST=%s\n' "$PRODUCTION_SSH_HOST"
printf 'PRODUCTION_DEPLOY_PATH=%s\n' "$PRODUCTION_DEPLOY_PATH"

# Production host verification
ssh "$PRODUCTION_SSH_USER@$PRODUCTION_SSH_HOST" 'cd "$PRODUCTION_DEPLOY_PATH" && git rev-parse HEAD && docker ps && docker compose ps && docker images && docker inspect $(docker ps -q) --format "{{.Name}} {{json .Config.Labels}}" && sudo nginx -T | sed -n "/server_name .*vafox.com/,/}/p"'
```

## Bottom line

- Expected production identity is `AI-OS-V6-CLEAN-REBUILD-V1`.
- Actual running production identity is **UNVERIFIED** from this container.
- Public pages reachable through the browser/web fetch path still display non-V6-specific legacy/login/static UI surfaces.
- The decisive evidence requested by the mission requires GitHub Actions run access plus SSH access to the production host.
