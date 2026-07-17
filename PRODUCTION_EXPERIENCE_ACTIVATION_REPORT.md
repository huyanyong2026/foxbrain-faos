# VAFOX Production Experience Activation Report

Date: 2026-07-17
Branch: work
Local expected main commit: `d4158c17c660341d76197211614c9fefd94aa7ab`
Scope: production activation verification and cutover plan only; no feature development.

## Before

### Production runtime checks

| Domain | Check | Result | Evidence |
| --- | --- | --- | --- |
| `gateway.vafox.com` | `https://gateway.vafox.com/health/version` | Blocked from this execution environment | `curl` returned `CONNECT tunnel failed, response 403` from the outbound proxy before reaching origin. |
| `ai.vafox.com` | `https://ai.vafox.com/health/version` | Blocked from this execution environment | `curl` returned `CONNECT tunnel failed, response 403` from the outbound proxy before reaching origin. |
| `huyan.vafox.com` | `https://huyan.vafox.com/health/version` | Blocked from this execution environment | `curl` returned `CONNECT tunnel failed, response 403` from the outbound proxy before reaching origin. |

Because the production origins could not be reached from this container, the live running commit could not be compared directly against the expected main commit `d4158c17c660341d76197211614c9fefd94aa7ab` here.

### Docker service checks

| Service | Expected production role | Result from this environment |
| --- | --- | --- |
| `foxbrain-web` | Genesis web runtime serving `huyan.vafox.com` UI on port `3000` behind nginx | Not directly verifiable; Docker CLI is not installed in this container. |
| `foxbrain-api` | Genesis API/runtime metadata service on port `8000` behind nginx | Not directly verifiable; Docker CLI is not installed in this container. |
| `foxbrain-worker` | Background worker for controlled platform jobs | Not directly verifiable; Docker CLI is not installed in this container. |
| `nginx` | Container nginx routing Huyan traffic to `foxbrain-web` and `foxbrain-api` | Not directly verifiable; Docker CLI is not installed in this container. |

### Local approved Genesis route inventory

| Surface | Approved active route | Repository evidence |
| --- | --- | --- |
| Gateway | VAFOX Identity Center | `apps/gateway/index.html` declares the Identity Center and VAFOX Outdoor LIFE entry. |
| AI | Workforce Home | `apps/ai/templates/dashboard.html` declares `VAFOX Workforce Home`. |
| Huyan | CEO Home / Enterprise Brain | `portal_v2.py` routes `/` to `ceo_home_v11_page(user)` for authenticated users and exposes Huyan runtime metadata. |

## Root cause

The repository configuration indicates that the approved Genesis experience is present locally, but production verification was blocked before origin access. The most likely legacy-serving source remains a production routing/caching issue rather than missing Genesis code.

Priority root-cause candidates to validate on the production host:

1. Old nginx upstream or host-level nginx server block still routing public domains to a previous process/port instead of the Genesis services.
2. Old static volume or document root still mounted for `gateway.vafox.com`, especially if the host serves `/var/www/firefox-gateway/current` from a stale release path.
3. Old container exposure still published to host ports and selected by host nginx.
4. Stale browser/CDN/proxy asset cache serving previous HTML or JavaScript.
5. Old template inside a persistent mounted application directory overriding the image contents.

## Activation steps

These are the controlled cutover steps to execute on the production host when the latest deployment is present but public pages still show legacy UI.

### 1. Establish expected commit and running runtime

```bash
git -C /opt/foxbrain-faos fetch origin main
git -C /opt/foxbrain-faos rev-parse origin/main
curl -ksS https://gateway.vafox.com/health/version | jq .
curl -ksS https://ai.vafox.com/health/version | jq .
curl -ksS https://huyan.vafox.com/health/version | jq .
```

Expected: all runtime payloads report commit `d4158c17c660341d76197211614c9fefd94aa7ab` or the newer confirmed `origin/main` commit.

### 2. Verify Docker services

```bash
docker compose -f /opt/foxbrain-faos/docker-compose.yml -f /opt/foxbrain-faos/docker-compose.prod.yml ps
docker inspect foxbrain-web foxbrain-api foxbrain-worker foxbrain-nginx --format '{{.Name}} {{.Config.Image}} {{json .Config.Labels}} {{json .NetworkSettings.Ports}}'
```

Expected services: `foxbrain-web`, `foxbrain-api`, `foxbrain-worker`, and `foxbrain-nginx` are running and healthy.

### 3. Verify active routes from inside Docker network

```bash
docker compose -f /opt/foxbrain-faos/docker-compose.yml exec -T nginx wget -qO- http://foxbrain-api:8000/health/version
docker compose -f /opt/foxbrain-faos/docker-compose.yml exec -T nginx wget -qO- http://foxbrain-web:3000/ | head -c 1000
```

Expected: API metadata is Huyan/VAFOX Genesis runtime, and web HTML is not the legacy page.

### 4. Switch nginx upstream to Genesis services

For container nginx, the approved Huyan mapping is:

- `/health/runtime` and `/health/version` -> `http://foxbrain-api:8000`
- `/api/` -> `http://foxbrain-api:8000`
- `/` -> `http://foxbrain-web:3000`

For host-level nginx, ensure the public `huyan.vafox.com` server block forwards to the Docker nginx loopback port or directly to the same Genesis upstreams, not an old static root or old process.

```bash
nginx -T | sed -n '/server_name gateway.vafox.com/,/}/p'
nginx -T | sed -n '/server_name ai.vafox.com/,/}/p'
nginx -T | sed -n '/server_name huyan.vafox.com/,/}/p'
nginx -t && nginx -s reload
```

### 5. Remove stale exposure and invalidate stale assets

```bash
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
docker stop <legacy_container_name>
docker rm <legacy_container_name>
find /var/www -maxdepth 3 -type f \( -name 'index.html' -o -name '*.js' -o -name '*.css' \) -mtime +0 -print
```

Only remove files or containers after confirming they are not the active Genesis release. Invalidate CDN/browser-facing static assets by serving root HTML with `Cache-Control: no-store` and versioned/static assets with a short revalidation window.

## After verification

Run after cutover from a network path that can reach production origins:

```bash
for host in gateway.vafox.com ai.vafox.com huyan.vafox.com; do
  echo "=== $host version ==="
  curl -ksS "https://$host/health/version" | jq .
  echo "=== $host root markers ==="
  curl -kLsS "https://$host/" | python3 -c 'import sys; s=sys.stdin.read(); print([m for m in ["VAFOX Identity Center","VAFOX Workforce Home","CEO Home","VAFOX Enterprise Brain","VAFOX Outdoor LIFE"] if m in s])'
done
```

Expected route markers:

| Domain | Required marker |
| --- | --- |
| `gateway.vafox.com` | `VAFOX Identity Center` |
| `ai.vafox.com` | `VAFOX Workforce Home` |
| `huyan.vafox.com` | `CEO Home` or `VAFOX Enterprise Brain` |

## Rollback plan

1. Preserve the previous nginx configuration before reload:
   ```bash
   nginx -T > /root/nginx-before-vafox-genesis-cutover-$(date -u +%Y%m%dT%H%M%SZ).conf
   ```
2. Preserve current Docker image IDs and container list:
   ```bash
   docker ps --format '{{.Names}} {{.Image}} {{.ID}}' > /root/docker-before-vafox-genesis-cutover-$(date -u +%Y%m%dT%H%M%SZ).txt
   ```
3. If health checks fail after cutover, restore the saved nginx server block or point the public upstream back to the last known healthy container.
4. Reload nginx only after `nginx -t` passes.
5. Keep the failed Genesis containers running but not publicly exposed until logs are collected:
   ```bash
   docker compose logs --tail=200 foxbrain-web foxbrain-api foxbrain-worker nginx
   ```

## Status

Activation could not be completed from this container because direct production HTTP checks are blocked by the environment proxy and Docker is not available locally. The approved Genesis code and routing configuration are present in the repository; production host access is required to perform the final nginx/container cutover safely.
