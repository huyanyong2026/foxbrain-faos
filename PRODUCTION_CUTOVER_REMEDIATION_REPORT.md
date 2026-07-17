# VAFOX Outdoor LIFE Production Cutover Remediation Report

Date: 2026-07-17 UTC  
Scope: `gateway.vafox.com`, `ai.vafox.com`, `huyan.vafox.com`  
Constraint: SAP, Core data pipeline, and AI engine business logic were not changed.

## Before

- The audit could not prove public production was serving the current repository commit because DNS/HTTPS access from the audit environment was blocked.
- Gateway static Nginx could serve stale static assets for 30 days and did not explicitly proxy `/health/runtime` to the Gateway runtime API.
- AI production routing was documented as a partial Nginx snippet and did not explicitly own `/`, `/login`, `/home`, `/dashboard`, `/version`, or runtime health routes.
- Huyan exposed local `/login` when unauthenticated and did not expose `/health/runtime` from the main public service.
- Docker image tags still used `foxbrain-v4` / `0.20.5`, which obscured Genesis / AI OS V6 cutover verification.

## Problem

Production could drift from the approved Genesis experience even after `main` was merged because each hostname had separate routing, cache, and deployment pointers. Legacy login/dashboard surfaces could remain reachable through stale CDN/browser caches, partial Nginx route ownership, or ambiguous image tags.

## Fix

1. Confirm-current-commit support:
   - Runtime metadata endpoints now provide commit/build/environment evidence for all three scoped services.
   - Huyan now exposes `/health/version` and `/health/runtime` with the shared runtime metadata contract.
2. Deployment mismatch remediation:
   - Docker image references now use the Genesis release identity instead of the legacy `foxbrain-v4` label.
3. Route mismatch remediation:
   - Gateway Nginx explicitly routes `/health/runtime` and `/health/version` to the Gateway API.
   - AI Nginx explicitly routes `/`, `/login`, `/home`, `/dashboard`, `/version`, `/health/version`, and `/health/runtime` to the Workforce Home Flask app.
   - Huyan unauthenticated `/` and `/login` now redirect to Gateway login instead of rendering a local legacy login page; authenticated `/` remains CEO Home.
4. Cache remediation:
   - Gateway HTML and SPA fallbacks are `no-store`.
   - Gateway static assets now use short revalidating cache headers instead of long immutable caching to reduce stale cutover exposure.
   - Runtime/version routes are marked `no-store` in Nginx examples.
5. Legacy exposure remediation:
   - AI `/dashboard` remains only a compatibility redirect to `/home`.
   - Huyan local public login is no longer canonical.

## After

Expected production ownership after deploying these changes:

| Host | Root route | Login route | Dashboard route | Runtime verification |
| --- | --- | --- | --- | --- |
| `gateway.vafox.com` | Gateway Identity Center | Gateway Identity Center SPA / identity flow | Gateway SPA fallback, not old dashboard | `/health/runtime` via Gateway API |
| `ai.vafox.com` | Workforce Home redirect/login flow | Redirects to Gateway login | Redirects to `/home` | `/health/runtime` via AI Flask app |
| `huyan.vafox.com` | CEO Home after auth, Gateway login before auth | Redirects to Gateway login | Legacy dashboard endpoints remain non-canonical/auth-gated compatibility only | `/health/runtime` via Huyan service |

## Verification

Run after deployment from a network location that can reach production:

```bash
git rev-parse HEAD
for host in gateway.vafox.com ai.vafox.com huyan.vafox.com; do
  curl -fsS "https://$host/health/runtime" | python -m json.tool
  curl -I "https://$host/"
done
curl -I https://ai.vafox.com/login
curl -I https://ai.vafox.com/dashboard
curl -I https://huyan.vafox.com/login
```

Acceptance criteria:

- Each `/health/runtime` payload includes `service`, `version`, `commit`, `build_time`, and `environment`.
- Each runtime `commit` matches the approved `main` commit deployed to production.
- Gateway HTML returns `Cache-Control: no-store`.
- `ai.vafox.com/dashboard` redirects to `/home`.
- `ai.vafox.com/login` and `huyan.vafox.com/login` do not render old login pages and redirect to Gateway login.
