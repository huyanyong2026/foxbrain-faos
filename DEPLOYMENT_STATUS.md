# FoxBrain Production UI Deployment Verification

Verification date: 2026-07-16 11:36 UTC

## Executive Status

The repository branch contains the UX-V3.0 merge commit, but this diagnostic environment cannot directly verify the live production server state because:

- `docker` is not installed in the current shell, so local/remote running container metadata cannot be queried from here.
- HTTPS requests to `https://huyan.vafox.com` are blocked by the execution environment's outbound proxy with `403 Forbidden` / `CONNECT tunnel failed`.

Based on repository evidence, there is also a build/version mismatch risk: the current commit message is UX V3, but the application health/version metadata and UX information architecture contract still report older product versions (`0.20.5`, `VAFOX V6 Autonomous Cloud Framework`, and `VAFOX OS UX 2.0`).

## Required Fields

| Field | Observed value | Evidence |
| --- | --- | --- |
| Current Git Commit | `07b931b99fc04696ed4661321b1c22f51249289b` (`feat: add UX V3 AI-native workspace routing (#110)`) | `git rev-parse HEAD`; `git log -1 --oneline --decorate --date=iso --format='%h %H %ad %D %s'` |
| Production Commit | Unknown from this environment | Production HTTPS probe was blocked by outbound proxy; Docker is unavailable locally. |
| Running Containers | Unknown from this environment | `docker ps` failed because `docker` command is not installed. Compose definitions expect `foxbrain-web`, `foxbrain-api`, `foxbrain-worker`, `postgres`, `redis`, `minio`, `qdrant`, and `nginx`. |
| Frontend Version | Repository runtime health returns `VAFOX V6 Autonomous Cloud Framework`; platform manifest version is `0.20.5`; UX contract still returns `VAFOX OS UX 2.0`. | `portal_v2.py` health payload and `foxbrain_os/platform_alignment.py` / `foxbrain_os/ux_information_architecture.py` inspection. |
| Huyan Version | Configured Huyan release unit is `portal_v2.py + infra/nginx/huyan*.conf`; version metadata is not UX-V3.0 in code. | `foxbrain_os/platform_alignment.py` inspection. |
| AI Version | Configured AI release unit is `apps/ai`; no live AI container/version could be read here. | `foxbrain_os/platform_alignment.py` inspection. |
| Gateway Route | Nginx routes `/api/` to `foxbrain-api:8000` and all other paths `/` to `foxbrain-web:3000`; application role routing maps CEO/admin to `/huyan-v2`, employees/suppliers/customers to `/ai-workforce-v2`. | `infra/nginx/huyan.vafox.com.conf`; `portal_v2.py` inspection. |
| Deployment Time | Unknown from this environment | Requires production host/container inspect, image labels, CI deployment logs, or server access. |

## Checks Performed

### 1. Git branch status

- Branch: `work`
- HEAD: `07b931b99fc04696ed4661321b1c22f51249289b`
- Commit subject: `feat: add UX V3 AI-native workspace routing (#110)`
- Working tree before this report: clean.

### 2. Current deployed commit

Could not be verified from this environment. `curl` to production failed before reaching the origin:

```text
curl: (56) CONNECT tunnel failed, response 403
HTTP/1.1 403 Forbidden
server: envoy
```

No production endpoint response body or headers were available for commit/version extraction.

### 3. Running container image

Could not be verified from this environment because Docker is unavailable:

```text
/bin/bash: line 1: docker: command not found
```

Repository compose configuration builds the web/API/worker services from the local `Dockerfile` and tags all three as `foxbrain-v4:${FOXBRAIN_VERSION:-0.20.5}`.

### 4. Docker services

Repository compose configuration defines these core services:

- `foxbrain-web`
- `foxbrain-api`
- `foxbrain-worker`
- `postgres`
- `redis`
- `minio`
- `qdrant`
- `nginx`

Optional/profile services are also present, including `n8n`, `dify`, `ollama`, and `wikijs`.

### 5. Nginx routing

The Huyan nginx config routes:

- `/api/` → `http://foxbrain-api:8000`
- `/` → `http://foxbrain-web:3000`

This is a potential route split: if `foxbrain-api` and `foxbrain-web` are not rebuilt from the same commit/image, API behavior and UI behavior can diverge.

### 6. Static assets version

No separately versioned static asset bundle was found in the checked paths. The UI appears to be server-rendered by `portal_v2.py`, which emits HTML/CSS/JS inline and sends `Cache-Control: no-store` and `Pragma: no-cache` on application responses.

### 7. Frontend build version

The current code does not expose UX-V3.0 as the runtime frontend/build version:

- Health payload reports `app_version: VAFOX V6 Autonomous Cloud Framework`.
- Platform manifest reports `ENTERPRISE_OS_VERSION = "0.20.5"`.
- UX information architecture contract reports `version: VAFOX OS UX 2.0`.

Therefore, even if the UX-V3.0 commit is deployed, production-visible version probes may still look old unless the page content itself changed visibly.

### 8. Browser cache headers

Application responses from `portal_v2.py` are configured with:

- `Cache-Control: no-store`
- `Pragma: no-cache`

This makes a browser-cache-only explanation less likely for application-rendered HTML. Nginx does not add cache-control headers itself in the inspected Huyan config.

## Expected UX-V3.0 vs Actual Production UI

| Area | Expected UX-V3.0 | Actual / observed from this environment |
| --- | --- | --- |
| Git source | HEAD contains UX-V3.0 merge commit and UX V3 docs. | Confirmed in repository. |
| Runtime production UI | Production should serve the UX-V3.0 UI from commit `07b931b`. | Not confirmable here because production HTTPS is blocked. |
| Version endpoint / metadata | Should expose or indicate UX-V3.0 if used as deployment verification signal. | Current code still exposes older metadata (`0.20.5`, `VAFOX OS UX 2.0`, `VAFOX V6 Autonomous Cloud Framework`). |
| Route | Huyan should route UI traffic to current `foxbrain-web`. | Config routes `/` to `foxbrain-web:3000`; live route not confirmable. |
| Cache behavior | Fresh HTML should be served. | Code sets `no-store`; cache issue is less likely for server-rendered HTML. |

## Mismatch Classification

Because live production commit/container state could not be read, the mismatch cannot be conclusively assigned to a single production cause from this environment.

Most likely categories, in order:

1. **Not deployed / wrong container**: likely if production is still running an image built before commit `07b931b`. This must be checked on the production host with `docker ps`, image digests, image creation time, and container labels.
2. **Build/version metadata issue**: confirmed in repository. UX-V3.0 code/docs are present, but runtime-visible version metadata still says older versions. This can make production verification look old even after deployment.
3. **Route issue**: possible if external traffic is not reaching the expected `foxbrain-nginx`/`foxbrain-web` stack. The repo nginx route is correct for `/`, but the live edge route could not be verified.
4. **Cache issue**: less likely for the Python-rendered UI because application responses set `Cache-Control: no-store` and `Pragma: no-cache`; still possible if a CDN/edge layer caches upstream responses outside this repo config.
5. **Build issue**: possible if the production image build context or Dockerfile did not include the intended updated files, but this cannot be proven without production image inspection.

## Recommended Production-Host Commands

Run these on the production host to close the remaining unknowns:

```bash
git -C /path/to/foxbrain-faos rev-parse HEAD
git -C /path/to/foxbrain-faos log -1 --oneline --decorate --date=iso

docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker inspect foxbrain-web --format '{{.Image}} {{.Config.Image}} {{.Created}}'
docker inspect foxbrain-api --format '{{.Image}} {{.Config.Image}} {{.Created}}'
docker image inspect foxbrain-v4:0.20.5 --format '{{.Id}} {{.Created}}'

docker exec foxbrain-web python - <<'PY'
import pathlib
print(pathlib.Path('/app/UX_V3_RELEASE.md').exists())
print(pathlib.Path('/app/portal_v2.py').read_text().find('/workspace'))
PY

curl -k -sS -D - https://huyan.vafox.com/api/health -o /tmp/huyan-health.json
cat /tmp/huyan-health.json
curl -k -sS -D - https://huyan.vafox.com/ -o /tmp/huyan-home.html
head -80 /tmp/huyan-home.html
```

## Conclusion

The UX-V3.0 commit is present in the current repository branch, but production state could not be verified from this environment. Repository evidence shows the deployment stack can still advertise old versions even when UX-V3.0 files exist, and live production verification requires production host/container access. If the production UI is visually old, first verify whether `foxbrain-web` and `foxbrain-api` containers were rebuilt/recreated from commit `07b931b`; if they were, then verify edge routing and CDN/cache behavior.
