# VAFOX Production Runtime Truth Report

Audit date: 2026-07-17 UTC  
Scope: `gateway.vafox.com`, `ai.vafox.com`, `huyan.vafox.com`  
Local repository branch: `work`  
Local repository HEAD: `8a03d18b7b58a9ac52c524c51232da29fafaadb4` (`Remediate production cutover routing verification (#140)`)  
Mission rule: runtime truth only; no production fix was attempted.

## Executive finding

This audit cannot prove that the production domains are running the Genesis experience because this execution environment cannot reach the live domains or production host. The runtime probes are blocked before reaching VAFOX infrastructure:

- DNS lookup for all scoped domains failed against the container resolver `172.30.0.179`.
- HTTPS `curl` to all scoped domains failed at the outbound CONNECT proxy with `HTTP/1.1 403 Forbidden`, `server: envoy`.
- The repository has no configured `origin`, so GitHub `main` could not be fetched from this checkout.
- The production Docker host, production Nginx config, production containers, image IDs, mounted volumes, and service process table are not accessible from this container.

Therefore the truthful production status is **UNVERIFIED / blocked from this environment**, not PASS. The repo does, however, show a likely deployment mismatch risk: checked-in runtime metadata still contains `AI-OS-V5.1` and commit `2f8ddedc0419`, while local HEAD is `8a03d18b7b58a9ac52c524c51232da29fafaadb4`. If production uses the checked-in `deployment.json` or an image built before metadata regeneration, users can see legacy version identity even after Genesis code was merged.

## Evidence collected

### Network/runtime probes from this environment

Commands run:

```bash
for h in gateway.vafox.com ai.vafox.com huyan.vafox.com; do
  dig +short "$h"
  curl -k -sS -L -D "/tmp/$h.h" -o "/tmp/$h.html" --max-time 20 "https://$h/"
done
```

Observed result for each scoped host:

| Domain | DNS from container | HTTPS from container | Runtime conclusion |
| --- | --- | --- | --- |
| `gateway.vafox.com` | `no servers could be reached` | `CONNECT tunnel failed, response 403`; headers from outbound `envoy` proxy | Live runtime cannot be inspected from here. |
| `ai.vafox.com` | `no servers could be reached` | `CONNECT tunnel failed, response 403`; headers from outbound `envoy` proxy | Live runtime cannot be inspected from here. |
| `huyan.vafox.com` | `no servers could be reached` | `CONNECT tunnel failed, response 403`; headers from outbound `envoy` proxy | Live runtime cannot be inspected from here. |

### GitHub/main comparison availability

Commands run:

```bash
git remote -v
git ls-remote origin refs/heads/main
git show -s --format='%H %ci %s' HEAD
```

Observed result:

- No `origin` remote is configured in this checkout.
- `git ls-remote origin refs/heads/main` failed because `origin` does not exist.
- Local HEAD is `8a03d18b7b58a9ac52c524c51232da29fafaadb4`, dated `2026-07-17 12:45:38 +0000`.

## Repository deployment architecture found

The checked-in architecture is:

```text
DNS
  -> public CDN / edge / proxy layer (not verifiable from this environment)
  -> host Nginx (expected, not verifiable from this environment)
  -> Docker-side Nginx on loopback 127.0.0.1:8088
  -> containers:
       foxbrain-nginx
       foxbrain-web  -> portal_v2.py, PORT=3000
       foxbrain-api  -> portal_v2.py, PORT=8000
       foxbrain-worker
       optional ai Workforce Home Flask app if separately deployed on PORT=5010
       gateway public API if separately deployed on PORT=8091
  -> services / source files:
       apps/gateway/index.html and apps/gateway/public_api.py
       apps/ai/app.py and apps/ai/templates/*
       portal_v2.py
  -> git commit / build metadata:
       deployment.json or generated metadata payloads
```

Important checked-in facts:

- `docker-compose.yml` builds `foxbrain-web`, `foxbrain-api`, and `foxbrain-worker` from the root `Dockerfile` and tags them as `vafox-genesis:${FOXBRAIN_VERSION:-AI-OS-V6-CLEAN-REBUILD-V1}`.
- Root `Dockerfile` copies `portal_v2.py`, `foxbrain_os`, `infra/scripts`, and `docs`, then starts `python portal_v2.py` by default.
- Docker-side Nginx exposes only loopback `${NGINX_LOOPBACK_PORT:-127.0.0.1:8088}:80` and mounts `infra/nginx/huyan.vafox.com.conf`.
- The checked-in Huyan Docker Nginx routes `/health/runtime` and `/health/version` to `foxbrain-api:8000`; `/api/` to `foxbrain-api:8000`; `/` to `foxbrain-web:3000`.
- The AI app default runtime port is `5010` when run directly.
- The gateway public data API default runtime port is `8091`.

## Per-domain runtime truth matrix

Because production cannot be reached from this environment, all live fields below are **UNVERIFIED**. The “expected from repo” column is the checked-in intent, not a live production observation.

| Domain | Current running service | Current running container/image | Current git commit | Current build time | Current frontend template source | Expected from repo |
| --- | --- | --- | --- | --- | --- | --- |
| `gateway.vafox.com` | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | Static Gateway Identity Center from `apps/gateway/index.html`; runtime API from `apps/gateway/public_api.py` on port `8091`. |
| `ai.vafox.com` | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | Workforce Home Flask app from `apps/ai/app.py` + `apps/ai/templates/*` on port `5010`; routes include `/`, `/login`, `/home`, `/dashboard`, `/health/version`, `/health/runtime`, `/supply`, `/store`. |
| `huyan.vafox.com` | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | FAOS/Huyan service from `portal_v2.py`; Docker-side Nginx should proxy `/` to `foxbrain-web:3000` and health/API paths to `foxbrain-api:8000`. |

## A. What users see now

Not verifiable from this environment. The audit cannot truthfully state the visual UI currently seen by users because HTTP(S) requests never reached VAFOX production. Any claim that users definitely see legacy UI would require one of the following production-side captures:

```bash
curl -k -sS -D - https://gateway.vafox.com/ -o /tmp/gateway.html
curl -k -sS -D - https://ai.vafox.com/ -o /tmp/ai.html
curl -k -sS -D - https://huyan.vafox.com/ -o /tmp/huyan.html
```

and/or browser screenshots from an unblocked network.

## B. What GitHub/main/latest contains, based on this checkout

GitHub `main` could not be fetched because no remote is configured. The latest available local commit contains Genesis-era deployment intent:

- Gateway links route CEO to `https://huyan.vafox.com`, Employee to `https://ai.vafox.com`, Procurement to `https://ai.vafox.com/supply`, and Store Manager to `https://ai.vafox.com/store`.
- AI app defines a Workforce Home / Digital Workforce OS V6 label and exposes `/health/version` and `/health/runtime`.
- Huyan/FAOS root image is tagged by default as `vafox-genesis:AI-OS-V6-CLEAN-REBUILD-V1`.
- Huyan Docker Nginx routes runtime health checks to `foxbrain-api:8000` and root UI to `foxbrain-web:3000`.
- `deployment.json` is stale relative to local HEAD: it says version `AI-OS-V5.1`, commit `2f8ddedc0419`, build time `2026-07-16T12:54:07+00:00`.

## C. Why mismatch likely exists

The confirmed root cause cannot be proven without host access, but the repository evidence points to these likely mismatch classes:

### 1. Old image / old container risk

If production containers were not rebuilt after the Genesis merge, `foxbrain-web` and `foxbrain-api` may still run an older root image even though the repo now expects `vafox-genesis:AI-OS-V6-CLEAN-REBUILD-V1`.

Production-side verification required:

```bash
docker compose ps
docker compose images foxbrain-web foxbrain-api foxbrain-worker nginx
docker inspect foxbrain-web --format '{{.Image}} {{.Config.Image}} {{.Created}}'
docker inspect foxbrain-api --format '{{.Image}} {{.Config.Image}} {{.Created}}'
```

### 2. Stale runtime metadata risk

`deployment.json` still reports `AI-OS-V5.1`, commit `2f8ddedc0419`, and build time `2026-07-16T12:54:07+00:00`, while the local repo HEAD is `8a03d18b7b58a9ac52c524c51232da29fafaadb4`. If runtime metadata is copied into the image or served by production, health endpoints can advertise an old commit/build even when some files are newer.

Production-side verification required:

```bash
curl -fsS https://gateway.vafox.com/health/version | python -m json.tool
curl -fsS https://ai.vafox.com/health/version | python -m json.tool
curl -fsS https://huyan.vafox.com/health/version | python -m json.tool
```

### 3. Old Nginx route risk

The repo expects host Nginx to route each public domain to the correct local service. If host Nginx still routes `ai.vafox.com` to the old portal or routes `gateway.vafox.com` only to a stale static directory, users will see legacy UI even with updated containers present.

Production-side verification required:

```bash
sudo nginx -T | sed -n '/server_name gateway.vafox.com/,/}/p'
sudo nginx -T | sed -n '/server_name ai.vafox.com/,/}/p'
sudo nginx -T | sed -n '/server_name huyan.vafox.com/,/}/p'
```

### 4. Old volume / stale static directory risk

The compose stack mounts `foxbrain_portal:/data/firefox-portal` and `./logs:/app/logs`. If production additionally binds old static directories for gateway or AI, or if host Nginx serves files directly from an old release directory, the UI can remain legacy while containers are updated.

Production-side verification required:

```bash
docker inspect foxbrain-web --format '{{json .Mounts}}' | python -m json.tool
docker inspect foxbrain-api --format '{{json .Mounts}}' | python -m json.tool
sudo nginx -T | grep -E 'root |alias |proxy_pass'
```

### 5. CDN / browser / Nginx cache risk

The repo includes `no-store` behavior for runtime/HTML paths, but production cache headers cannot be verified from here. If an upstream CDN or host Nginx cache keeps old HTML, users can see legacy UI after a successful backend deploy.

Production-side verification required:

```bash
for host in gateway.vafox.com ai.vafox.com huyan.vafox.com; do
  curl -k -sS -D - "https://$host/?runtime-audit=$(date +%s)" -o /tmp/${host}.html
  sed -n '1,40p' /tmp/${host}.html
 done
```

### 6. Missing deployment pipeline risk

This checkout has no GitHub remote configured and no live production deployment state available. There is no evidence in this environment that a merge to GitHub `main` automatically rebuilds images, regenerates deployment metadata, reloads Nginx, restarts containers, purges CDN cache, or verifies `/health/version` against the merged commit.

## D. Exact remediation steps

Do not change code until the following production-side truth capture is complete.

### Step 1 — Capture GitHub and production commit truth

```bash
cd /opt/foxbrain || cd /opt/foxbrain-faos || pwd
git remote -v
git fetch --all --prune
git rev-parse HEAD
git rev-parse origin/main
git log -1 --oneline --decorate
```

Expected acceptance condition: production checkout commit equals GitHub `origin/main` latest approved merge commit.

### Step 2 — Capture production DNS / CDN / edge truth

Run from an unrestricted network and from the server:

```bash
dig +short gateway.vafox.com
dig +short ai.vafox.com
dig +short huyan.vafox.com
curl -k -sS -D - https://gateway.vafox.com/health/version -o /tmp/gateway.version.json
curl -k -sS -D - https://ai.vafox.com/health/version -o /tmp/ai.version.json
curl -k -sS -D - https://huyan.vafox.com/health/version -o /tmp/huyan.version.json
```

Expected acceptance condition: headers and JSON identify the intended service, commit, build time, and `no-store` cache behavior.

### Step 3 — Capture Nginx routing truth

```bash
sudo nginx -T | tee /tmp/nginx.full.txt
grep -nE 'server_name (gateway|ai|huyan)\.vafox\.com|proxy_pass|root |alias |expires|Cache-Control' /tmp/nginx.full.txt
```

Expected acceptance condition:

- `gateway.vafox.com` routes `/health/version` and `/health/runtime` to the Gateway runtime API and serves the current Gateway HTML.
- `ai.vafox.com` routes Workforce Home paths to the AI Flask service on port `5010` or the intended container equivalent.
- `huyan.vafox.com` routes health/API paths to FAOS API and root UI to the current FAOS web service.

### Step 4 — Capture container/image truth

```bash
docker compose ps
docker compose images
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.CreatedAt}}\t{{.Status}}\t{{.Ports}}'
docker inspect foxbrain-web foxbrain-api foxbrain-worker foxbrain-nginx --format '{{.Name}} {{.Config.Image}} {{.Image}} {{.Created}}'
```

Expected acceptance condition: app containers use an image built from the latest approved commit and not an old `foxbrain-v4`, `0.20.5`, or pre-Genesis tag.

### Step 5 — Verify latest merged files are deployed

```bash
docker exec foxbrain-web sh -lc 'sha256sum /app/portal_v2.py; python - <<PY
import pathlib
print(pathlib.Path("/app/portal_v2.py").read_text()[:200])
PY'

docker exec foxbrain-api sh -lc 'sha256sum /app/portal_v2.py'

# For gateway and AI services, adjust container names if they are managed by systemd rather than compose:
sha256sum apps/gateway/index.html apps/gateway/public_api.py apps/ai/app.py
```

Expected acceptance condition: production file hashes match the latest approved GitHub files for `apps/gateway`, `apps/ai`, and `portal_v2.py`.

### Step 6 — Only after truth capture, redeploy if mismatch is confirmed

If any production commit/image/file hash differs from GitHub `main`:

```bash
git checkout main
git pull --ff-only
python scripts/generate_deployment_metadata.py
FOXBRAIN_VERSION=AI-OS-V6-CLEAN-REBUILD-V1 docker compose build --no-cache foxbrain-web foxbrain-api foxbrain-worker
docker compose up -d --remove-orphans
sudo nginx -t && sudo systemctl reload nginx
```

Then rerun all `/health/version`, `/health/runtime`, UI HTML, Nginx, and container checks. Purge CDN cache only after confirming origin is correct.

## Final truth status

| Question | Status | Truthful answer |
| --- | --- | --- |
| Are production users currently seeing legacy UI? | UNVERIFIED | This environment cannot reach production domains. |
| Are `apps/gateway` changes deployed? | UNVERIFIED | Must compare live Gateway HTML/API hash or runtime response on production. |
| Are `apps/ai` changes deployed? | UNVERIFIED | Must inspect AI service/container or live AI HTML/version endpoint. |
| Is `portal_v2.py` latest deployed? | UNVERIFIED | Must compare production container `/app/portal_v2.py` hash with GitHub. |
| Is an old container/image running? | UNVERIFIED / likely risk | Docker host access required. |
| Is an old volume/static directory involved? | UNVERIFIED / possible risk | Nginx and Docker mount inspection required. |
| Is an old Nginx route involved? | UNVERIFIED / likely risk | Host `nginx -T` required. |
| Is old CDN/cache involved? | UNVERIFIED / possible risk | Public headers and cache purge logs required. |
| Is deployment pipeline missing/incomplete? | UNVERIFIED / likely risk | No remote/pipeline evidence exists in this checkout; production automation must be audited. |
