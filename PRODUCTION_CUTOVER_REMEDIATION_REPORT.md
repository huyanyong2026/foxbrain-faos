# VAFOX Outdoor LIFE Production Cutover Remediation Report

Date: 2026-07-17 UTC  
Scope: `gateway.vafox.com`, `ai.vafox.com`, `huyan.vafox.com`  
Constraint: SAP, Core data pipeline, and AI engine business logic were not changed.

## Current Environment Constraint

Codex execution environment cannot directly reach the production domains because the outbound proxy blocks HTTPS CONNECT to `gateway.vafox.com`, `ai.vafox.com`, and `huyan.vafox.com` with proxy `403 Forbidden`. This is an environment access limitation and must not be treated as an application failure.

## A. Verified Locally

- Runtime metadata endpoints are present in code for all scoped services and expose version, commit, build time, and environment metadata.
- Huyan Docker-side Nginx now routes `/health/runtime` and `/health/version` directly to `foxbrain-api:8000`, matching the runtime metadata service instead of falling through to the web UI.
- Host Nginx examples route Huyan runtime checks to the local FAOS proxy port and mark health/version responses `no-store`.
- Gateway Nginx example explicitly proxies `/health/runtime` and `/health/version` to the Gateway runtime API and marks SPA HTML/fallback responses `no-store`.
- AI Nginx example explicitly routes `/`, `/login`, `/home`, `/dashboard`, `/version`, `/health/version`, `/health/runtime`, `/supply`, and `/store` to the Workforce Home Flask app.
- Gateway deployment links now align with the AI OS V6 route contract: procurement uses `https://ai.vafox.com/supply` and store manager uses `https://ai.vafox.com/store`.
- AI local route aliases preserve compatibility by redirecting `/supply` to `/replenishment` and `/store` to `/operation` until the canonical V6 pages are fully separated.
- Docker Compose image references for FAOS services use the Genesis release identity `vafox-genesis:${FOXBRAIN_VERSION:-AI-OS-V6-CLEAN-REBUILD-V1}` rather than legacy `foxbrain-v4` / `0.20.5` runtime labels.

## B. Cannot Verify From Codex Environment

The following checks require network access to production domains and cannot be completed inside this Codex environment because the proxy blocks outbound HTTPS tunnels:

- Public DNS/TLS reachability for `gateway.vafox.com`, `ai.vafox.com`, and `huyan.vafox.com`.
- Production HTTP status, redirects, cache headers, and body payloads for `/`, `/login`, `/dashboard`, `/health/version`, and `/health/runtime`.
- Whether production is currently serving the exact approved `main` commit after deployment.
- Whether production Nginx has already reloaded the latest checked-in templates.

A proxy `403 Forbidden` from Codex is inconclusive and must be documented as `UNVERIFIED_FROM_CODEX`, not `FAIL`.

## C. Requires Production Server Verification

Run these commands on the production server or from an operator workstation that can reach the VAFOX production domains.

### 1. Capture deployed Git commit

```bash
cd /opt/foxbrain-faos || cd /opt/foxbrain || pwd
git rev-parse HEAD
git status --short
```

### 2. Verify runtime payloads for each domain

```bash
for host in gateway.vafox.com ai.vafox.com huyan.vafox.com; do
  echo "===== $host /health/runtime ====="
  curl -fsS "https://$host/health/runtime" | python -m json.tool
  echo
  echo "===== $host /health/version ====="
  curl -fsS "https://$host/health/version" | python -m json.tool
  echo
done
```

Each payload must include and operator must record:

- `service`
- `version`
- `commit`
- `build_time`
- `environment`
- route target / service owner evidence from Nginx mapping below

### 3. Verify route targets and redirects

```bash
for host in gateway.vafox.com ai.vafox.com huyan.vafox.com; do
  echo "===== $host root headers ====="
  curl -k -sS -D - "https://$host/" -o /tmp/${host}.root.html | sed -n '1,30p'
  echo
done

curl -k -sS -D - https://ai.vafox.com/login -o /tmp/ai.login.html | sed -n '1,30p'
curl -k -sS -D - https://ai.vafox.com/dashboard -o /tmp/ai.dashboard.html | sed -n '1,30p'
curl -k -sS -D - https://ai.vafox.com/supply -o /tmp/ai.supply.html | sed -n '1,30p'
curl -k -sS -D - https://ai.vafox.com/store -o /tmp/ai.store.html | sed -n '1,30p'
curl -k -sS -D - https://huyan.vafox.com/login -o /tmp/huyan.login.html | sed -n '1,30p'
```

Expected route targets:

| Host | Path | Expected production route target |
| --- | --- | --- |
| `gateway.vafox.com` | `/health/runtime`, `/health/version` | Gateway runtime API on port `8091` |
| `gateway.vafox.com` | `/` and SPA fallback | Gateway static SPA with `no-store` HTML |
| `ai.vafox.com` | `/`, `/login`, `/home`, `/dashboard`, `/version`, `/health/version`, `/health/runtime`, `/supply`, `/store` | Workforce Home Flask app on port `5010` |
| `huyan.vafox.com` | `/health/runtime`, `/health/version` | Huyan FAOS API/runtime service through local FAOS proxy/API |
| `huyan.vafox.com` | `/` | Huyan CEO Home after auth or Gateway login before auth |

### 4. Verify Nginx active configuration on production server

```bash
sudo nginx -T | sed -n '/server_name gateway.vafox.com/,/server_name/p'
sudo nginx -T | sed -n '/server_name ai.vafox.com/,/server_name/p'
sudo nginx -T | sed -n '/server_name huyan.vafox.com/,/server_name/p'
```

Confirm the active Nginx output contains the route targets listed above. If active production Nginx differs from the checked-in templates, update production or document the deliberate override before merge/deployment approval.

### 5. Verify Docker Compose deployment mapping

```bash
cd /opt/foxbrain-faos || cd /opt/foxbrain || pwd
docker compose config
docker compose ps
for svc in foxbrain-web foxbrain-api foxbrain-worker nginx; do
  docker compose images "$svc"
done
```

Confirm FAOS services use the Genesis image tag configured by `FOXBRAIN_VERSION` or the default `AI-OS-V6-CLEAN-REBUILD-V1`, and confirm the Huyan local proxy maps to loopback port `8088` for host Nginx.

## Merge / Deployment Gate

Do not merge or deploy unless all of the following are true:

- Config consistency checks pass locally.
- Local tests pass.
- Production-only checks above are either verified by an operator or explicitly recorded as unresolved production checks.
- Any Codex proxy `403 Forbidden` result is recorded as an environment limitation, not an application failure.
