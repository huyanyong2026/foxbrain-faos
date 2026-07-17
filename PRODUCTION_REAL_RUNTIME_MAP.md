# VAFOX Production Real Runtime Map

Date: 2026-07-17 UTC

## Executive conclusion

The exact running production source **could not be proven from this repository checkout** because this environment has no access to the live production server, Docker daemon, Nginx runtime, CDN control plane, or public HTTPS endpoints.

What can be proven locally:

- The repository expected production version is `AI-OS-V6-CLEAN-REBUILD-V1`.
- The current local branch commit is `bb9e17316836a6541ec12482c1c0132fe88bf55d` (`Clean up legacy Genesis governance (#147)`).
- The local deployment metadata still records commit `2f8ddedc0419` with build/deploy time `2026-07-16T12:54:07+00:00`.
- The local compose stack builds `foxbrain-web`, `foxbrain-api`, and `foxbrain-worker` from this repository and tags them as `vafox-genesis:${FOXBRAIN_VERSION:-AI-OS-V6-CLEAN-REBUILD-V1}`.
- Public checks from this environment are blocked: DNS queries to the configured resolver fail, and HTTPS CONNECT requests to all three domains return `403 Forbidden` from the environment proxy.

Therefore the user-facing legacy UI is most likely caused by one of these runtime mismatches, but the exact production source must be confirmed on the production host:

1. Production containers were not rebuilt/restarted from latest main.
2. Host Nginx or CDN still points to an older static root/upstream.
3. Static/CDN cache is serving old assets.
4. The production deployment path is not this repository checkout.
5. The live domains route to a different server/load balancer than the expected Docker/Nginx stack.

## Request path trace status

| Layer | gateway.vafox.com | ai.vafox.com | huyan.vafox.com | Evidence status |
|---|---|---|---|---|
| DNS | Unverified | Unverified | Unverified | `dig` failed in this environment because resolver `172.30.3.179` refused/timed out. |
| CDN | Unverified | Unverified | Unverified | No CDN API credentials or cache headers available. HTTPS blocked before origin response. |
| Load balancer | Unverified | Unverified | Unverified | No cloud/LB control-plane access available. |
| Host Nginx | Expected static/proxy config exists in repo | Expected proxy snippet exists in repo | Expected host-to-container route exists in repo | Live `/etc/nginx` cannot be inspected from this checkout. |
| Container proxy | Not defined in compose for gateway | Not defined in compose for ai | `foxbrain-nginx` expected from compose | Live Docker daemon unavailable here. |
| Application | Expected Gateway runtime API on `127.0.0.1:8091` by Nginx example | Expected AI runtime on `127.0.0.1:5010` by Nginx example | Expected `foxbrain-api:8000` and `foxbrain-web:3000` by compose Nginx | Live processes unavailable here. |

## Expected local runtime contracts

### gateway.vafox.com

- Expected user-facing version: Gateway Identity Center / Gateway Genesis under `AI-OS-V6-CLEAN-REBUILD-V1`.
- Expected Nginx shape: `/health/runtime`, `/health/version`, and `/api/public/` proxy to `127.0.0.1:8091`; static root is `/var/www/firefox-gateway/current`; `/assets/` may cache for one hour while `/index.html` is no-store.
- Expected serving process: **unverified in production**. The repo example expects a host process on port `8091`, not the main compose `foxbrain-api` container.
- Current user-facing version: **unverified from this environment**.
- Mismatch reason: **unverified**. If legacy UI is visible publicly, likely Nginx static root, CDN cache, or an older gateway process is still serving.
- Exact fix command after production confirmation:

```bash
ssh <prod-host> 'set -euo pipefail
cd ${PRODUCTION_DEPLOY_PATH:?}
git fetch --all --prune
git checkout main
git pull --ff-only
export FOXBRAIN_VERSION=AI-OS-V6-CLEAN-REBUILD-V1
export GIT_COMMIT=$(git rev-parse HEAD)
export BUILD_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
export DEPLOY_TIME=$BUILD_TIME
# Restart the actual gateway service discovered on port 8091, for example:
sudo systemctl restart vafox-gateway || sudo docker compose up -d --build gateway
sudo nginx -t && sudo systemctl reload nginx
curl -fsS https://gateway.vafox.com/health/runtime'
```

### ai.vafox.com

- Expected user-facing version: AI Workforce Home / VAFOX Digital Workforce OS V6 under `AI-OS-V6-CLEAN-REBUILD-V1`.
- Expected Nginx shape: workspace/home/runtime paths proxy to `127.0.0.1:5010`; `/static/` also proxies to `127.0.0.1:5010`.
- Expected serving process: **unverified in production**. The repo example expects a host process on port `5010`, not the main compose `foxbrain-api` container.
- Current user-facing version: **unverified from this environment**.
- Mismatch reason: **unverified**. If legacy UI is visible publicly, likely Nginx still routes to the old AI app/upstream, or static assets are cached.
- Exact fix command after production confirmation:

```bash
ssh <prod-host> 'set -euo pipefail
cd ${PRODUCTION_DEPLOY_PATH:?}
git fetch --all --prune
git checkout main
git pull --ff-only
export FOXBRAIN_VERSION=AI-OS-V6-CLEAN-REBUILD-V1
export GIT_COMMIT=$(git rev-parse HEAD)
export BUILD_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
export DEPLOY_TIME=$BUILD_TIME
# Restart the actual AI app discovered on port 5010, for example:
sudo systemctl restart vafox-ai || sudo docker compose up -d --build ai
sudo nginx -t && sudo systemctl reload nginx
curl -fsS https://ai.vafox.com/health/runtime'
```

### huyan.vafox.com

- Expected user-facing version: Huyan latest runtime / VAFOX Genesis V6 under `AI-OS-V6-CLEAN-REBUILD-V1`.
- Expected Nginx shape in compose: `foxbrain-nginx` listens on `${NGINX_LOOPBACK_PORT:-127.0.0.1:8088}:80`; `/health/runtime`, `/health/version`, and `/api/` proxy to `foxbrain-api:8000`; `/` proxies to `foxbrain-web:3000`.
- Expected serving process from this repo: `foxbrain-nginx` -> `foxbrain-web` / `foxbrain-api`, with image `vafox-genesis:${FOXBRAIN_VERSION:-AI-OS-V6-CLEAN-REBUILD-V1}`.
- Current user-facing version: **unverified from this environment**.
- Mismatch reason: **unverified**. If legacy UI is visible publicly, likely the server is running an image/container built before latest main, or host Nginx points away from `127.0.0.1:8088`.
- Exact fix command after production confirmation:

```bash
ssh <prod-host> 'set -euo pipefail
cd ${PRODUCTION_DEPLOY_PATH:?}
git fetch --all --prune
git checkout main
git pull --ff-only
export FOXBRAIN_VERSION=AI-OS-V6-CLEAN-REBUILD-V1
export GIT_COMMIT=$(git rev-parse HEAD)
export BUILD_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
export DEPLOY_TIME=$BUILD_TIME
docker compose up -d --build foxbrain-web foxbrain-api foxbrain-worker nginx
sudo nginx -t && sudo systemctl reload nginx
curl -fsS https://huyan.vafox.com/health/runtime'
```

## Running production commit vs latest main

| Item | Value | Status |
|---|---:|---|
| Latest local branch commit | `bb9e17316836a6541ec12482c1c0132fe88bf55d` | Proven by local `git rev-parse HEAD`. |
| Latest remote main commit | Unverified | No `origin` remote exists in this checkout. |
| Deployment metadata commit in repo | `2f8ddedc0419` | Proven by `deployment.json`; this is older/different than local HEAD. |
| Running production commit | Unverified | Requires live `/health/runtime` or `docker inspect` on production. |

Comparison result: **production-vs-main cannot be completed from this environment**. The repository itself already contains a commit mismatch signal: `deployment.json` records `2f8ddedc0419`, while the current checkout is `bb9e17316836a6541ec12482c1c0132fe88bf55d`.

## Verification of requested deployed features

| Feature | Expected version | Deployment status |
|---|---|---|
| gateway Identity Center | Gateway Genesis / `AI-OS-V6-CLEAN-REBUILD-V1` | Unverified in production. Repo has expected Nginx runtime route and Gateway docs, but live endpoint is blocked. |
| ai Workforce Home | VAFOX Digital Workforce OS V6 / `AI-OS-V6-CLEAN-REBUILD-V1` | Unverified in production. Repo tests expect Workforce OS V6 text, but live endpoint is blocked. |
| huyan latest runtime | Huyan Genesis V6 / `AI-OS-V6-CLEAN-REBUILD-V1` | Unverified in production. Repo compose and Nginx expect V6 runtime metadata, but live endpoint is blocked. |

## Production host commands required to identify exact serving process

Run these on the actual production server and paste the output into this report if live shell access is available:

```bash
set -euo pipefail

echo '## Host identity'
hostname -f || hostname
whoami
date -u +%Y-%m-%dT%H:%M:%SZ
pwd

echo '## Git checkout'
cd ${PRODUCTION_DEPLOY_PATH:?}
git remote -v || true
git branch --show-current || true
git rev-parse HEAD || true
git log -1 --format='%H %ci %s' || true
cat deployment.json || true

echo '## Docker containers'
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker compose ps || true

echo '## Docker image and container metadata'
for c in foxbrain-nginx foxbrain-web foxbrain-api foxbrain-worker; do
  echo "### $c"
  docker inspect "$c" --format 'name={{.Name}} image_config={{.Config.Image}} image_id={{.Image}} created={{.Created}} labels={{json .Config.Labels}} env={{json .Config.Env}}' || true
done
for img in $(docker ps --format '{{.Image}}' | sort -u); do
  echo "### image $img"
  docker image inspect "$img" --format 'id={{.Id}} created={{.Created}} repo_tags={{json .RepoTags}} labels={{json .Config.Labels}}' || true
done

echo '## Docker volumes'
docker volume ls
docker inspect foxbrain_foxbrain_portal foxbrain_foxbrain_postgres foxbrain_foxbrain_redis foxbrain_foxbrain_minio foxbrain_foxbrain_qdrant 2>/dev/null || true

echo '## Nginx enabled sites and full config'
sudo find /etc/nginx/sites-enabled /etc/nginx/conf.d -maxdepth 1 -type f -o -type l -print
sudo nginx -T | sed -n '/server_name gateway.vafox.com/,/server_name/p; /server_name ai.vafox.com/,/server_name/p; /server_name huyan.vafox.com/,/server_name/p'

echo '## Local origin checks through host Nginx/upstreams'
curl -fsS -D- http://127.0.0.1:8088/health/runtime || true
curl -fsS -D- http://127.0.0.1:8091/health/runtime || true
curl -fsS -D- http://127.0.0.1:5010/health/runtime || true

echo '## Public edge checks from production host'
for d in gateway.vafox.com ai.vafox.com huyan.vafox.com; do
  echo "### $d"
  getent ahosts "$d" || true
  curl -k -fsS -D- "https://$d/health/runtime" -o "/tmp/$d.runtime.json" || true
  cat "/tmp/$d.runtime.json" 2>/dev/null || true
  curl -k -fsS -D- -H 'Cache-Control: no-cache' -H 'Pragma: no-cache' "https://$d/" -o "/tmp/$d.index.html" || true
  head -80 "/tmp/$d.index.html" 2>/dev/null || true
done
```

## CDN and static cache checks required

Because no CDN account/API is available here, purge and validation must be run in the actual CDN provider console or CLI. Use the provider-specific equivalent of:

```bash
# Cloudflare example only; replace zone ID/token.
for d in gateway.vafox.com ai.vafox.com huyan.vafox.com; do
  curl -fsS -X POST "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/purge_cache" \
    -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
    -H 'Content-Type: application/json' \
    --data "{\"hosts\":[\"$d\"]}"
done
```

Also verify asset cache behavior:

```bash
for d in gateway.vafox.com ai.vafox.com huyan.vafox.com; do
  curl -k -I -H 'Cache-Control: no-cache' "https://$d/"
  curl -k -I -H 'Cache-Control: no-cache' "https://$d/health/runtime"
done
```

## Final runtime map placeholder pending production shell output

| Domain | Server | Container | Image | Image tag | Git commit | Build timestamp | Current user-facing version | Expected version | Mismatch reason | Exact fix command |
|---|---|---|---|---|---|---|---|---|---|---|
| gateway.vafox.com | Unverified | Unverified | Unverified | Unverified | Unverified | Unverified | Unverified | `AI-OS-V6-CLEAN-REBUILD-V1` Gateway Identity Center | Need production host/CDN access | Restart discovered gateway service and reload Nginx after updating main; see command above. |
| ai.vafox.com | Unverified | Unverified | Unverified | Unverified | Unverified | Unverified | Unverified | `AI-OS-V6-CLEAN-REBUILD-V1` AI Workforce Home | Need production host/CDN access | Restart discovered AI service and reload Nginx after updating main; see command above. |
| huyan.vafox.com | Unverified | Expected `foxbrain-nginx`, `foxbrain-web`, `foxbrain-api` if this compose stack is live | Expected `vafox-genesis` for app containers, `nginx` for proxy | Expected `AI-OS-V6-CLEAN-REBUILD-V1` for app containers | Unverified | Unverified | Unverified | `AI-OS-V6-CLEAN-REBUILD-V1` Huyan latest runtime | Need production Docker/Nginx access | `docker compose up -d --build foxbrain-web foxbrain-api foxbrain-worker nginx && sudo nginx -t && sudo systemctl reload nginx`. |

## Local commands run for this audit

```bash
find /workspace -name AGENTS.md -print
rg -n "gateway.vafox.com|ai.vafox.com|huyan.vafox.com|Identity Center|Workforce|huyan|nginx|docker|compose|vafox" -S . -g '!node_modules' -g '!vendor'
for d in gateway.vafox.com ai.vafox.com huyan.vafox.com; do dig +short A "$d"; dig +short CNAME "$d"; curl -k -I -L --max-time 20 "https://$d/"; curl -k -sS --max-time 20 "https://$d/health/runtime"; curl -k -sS --max-time 20 "https://$d/health/version"; done
sed -n '1,220p' docker-compose.yml
sed -n '1,220p' infra/nginx/huyan.vafox.com.conf
sed -n '1,160p' deploy/nginx/gateway.vafox.com.conf.example
sed -n '1,160p' deploy/nginx/ai.vafox.com-enterprise-ai.conf.example
sed -n '1,220p' foxbrain_os/platform_governance.py
git rev-parse HEAD
git log -1 --format='%H %ci %s'
git remote -v
git fetch origin main
git branch -a --verbose --no-abbrev
cat deployment.json
```
