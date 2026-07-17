# VAFOX Outdoor LIFE Production Experience Cutover Audit Report

Date: 2026-07-17 UTC
Scope: audit only. No production fixes, route changes, or feature changes were made.

## Executive conclusion

The repository contains the Genesis / AI OS V6 experience contracts and runtime metadata endpoints, but this audit could not verify that the public production hosts are running the current `main` commit because outbound DNS and HTTPS from this execution environment are blocked. The strongest code-level mismatch risk is deployment/routing drift: `gateway.vafox.com` is configured as a static Nginx site rooted at `/var/www/firefox-gateway/current`, `huyan.vafox.com` is served by the Docker/Nginx FoxBrain stack, and `ai.vafox.com` is documented only as an Nginx snippet to be added to an existing server. These are separate production surfaces and can remain on legacy content if any one of the DNS/CDN/Nginx/service pointers has not been cut over.

## Evidence collected

### Local Git version

- Current local branch: `work`.
- Current repository commit: `ae393eb12956bbb570501e6e532a0171a5c3c60b`.
- Latest commit message: `Add Workforce Home pilot verification report (#137)`.
- Commit date: 2026-07-17 12:12:14 +0000.

### Production reachability from audit environment

Commands attempted:

```bash
for d in gateway.vafox.com ai.vafox.com huyan.vafox.com; do dig +short $d; curl -k -I --max-time 15 https://$d/; done
```

Observed results:

- DNS resolution failed for all three hosts because the configured resolver `172.30.5.35` refused or timed out.
- HTTPS requests to all three hosts failed before reaching origin with `CONNECT tunnel failed, response 403` from the environment proxy (`server: envoy`).
- Therefore public DNS records, CDN headers, origin headers, production HTML, production `/version`, production `/health/runtime`, and live frontend asset hashes are **UNVERIFIED** in this run.

## A. Current production version

| Host | DNS | CDN | Nginx/proxy | Container/service | Production commit | Version/build evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `gateway.vafox.com` | UNVERIFIED from this environment | UNVERIFIED | Expected static Nginx root `/var/www/firefox-gateway/current` per repo config | Static gateway files plus optional local APIs on `127.0.0.1:8091` and `127.0.0.1:8092` | UNVERIFIED | UNVERIFIED; no live `/version` response captured |
| `ai.vafox.com` | UNVERIFIED from this environment | UNVERIFIED | Expected existing HTTPS server with selected paths proxied to `127.0.0.1:5010` | Flask app in `apps/ai`, if snippet is installed | UNVERIFIED | UNVERIFIED; app exposes `/version`, `/health/version`, `/health/runtime` when routed to this service |
| `huyan.vafox.com` | UNVERIFIED from this environment | UNVERIFIED | Expected host Nginx to loopback Docker Nginx on `127.0.0.1:8088`; Docker Nginx routes `/api/` to `foxbrain-api:8000` and `/` to `foxbrain-web:3000` | `foxbrain-web`, `foxbrain-api`, `foxbrain-worker` images built as `foxbrain-v4:${FOXBRAIN_VERSION:-0.20.5}` | UNVERIFIED | UNVERIFIED; local code runtime defaults to `AI-OS-V6-CLEAN-REBUILD-V1` if no deployment metadata/env overrides exist |

## B. Current Git version

Current audited code is at commit `ae393eb12956bbb570501e6e532a0171a5c3c60b` on branch `work`. The runtime metadata code defaults to release version `AI-OS-V6-CLEAN-REBUILD-V1` and can read `GIT_COMMIT`, `COMMIT_SHA`, `BUILD_TIME`, `DEPLOY_TIME`, `FOXBRAIN_VERSION`, and `deployment.json` when present.

Important code-level version points:

- `foxbrain_os/platform_governance.py` defines the default release as `AI-OS-V6-CLEAN-REBUILD-V1`.
- `apps/ai/app.py` exposes `/version`, `/health/version`, `/health/runtime`, and `/control-tower` for runtime self-verification.
- `apps/ai/templates/base.html` renders runtime build time and commit in the footer for AI pages using that base template.
- Gateway static assets currently use query-string bundle markers `assets/styles.css?v=7462ff3` and `assets/app.js?v=917c659`.

## C. Deployment mismatch

Likely mismatch class: **production pointer mismatch**, not missing code.

Findings:

1. `huyan.vafox.com` Docker image name still uses `foxbrain-v4:${FOXBRAIN_VERSION:-0.20.5}` in `docker-compose.yml`, while runtime code declares `AI-OS-V6-CLEAN-REBUILD-V1`. This can make production operators believe the running image is still V4/0.20.5 even when source code contains V6 contracts, and it makes image-tag-based cutover audits ambiguous.
2. `gateway.vafox.com` is not a container route in the main compose file. It is a static Nginx root at `/var/www/firefox-gateway/current`, so merging GitHub `main` does not update production unless the gateway static release directory or symlink is redeployed.
3. `ai.vafox.com` is represented by an Nginx snippet, not a full authoritative server config. If the snippet was not installed, or if a broader legacy `location /` takes precedence, `ai.vafox.com` can continue serving legacy content.
4. The audit environment has no Docker binary, so no local production container/image labels or running image digests could be inspected from this workspace.

## D. Route mismatch

Expected route ownership from current repo:

| Host | `/` | `/login` | `/dashboard` | `/home` |
| --- | --- | --- | --- | --- |
| `gateway.vafox.com` | Static Gateway Identity Center via `index.html` | SPA fallback to `index.html` unless a separate identity service route exists in production | SPA fallback to `index.html` | SPA fallback to `index.html` |
| `ai.vafox.com` | Flask AI app redirects to `/home` if session exists, otherwise redirects to Gateway login | Redirects to Gateway login | Compatibility route redirects to `/home` after login | Workforce Home rendered by `dashboard.html` and guarded by `ai.use` permission |
| `huyan.vafox.com` | FoxBrain `portal_v2.py` CEO/home page if logged in, otherwise local login | FoxBrain local login | No single explicit audited `/dashboard` mapping found in dispatch excerpt; dashboard rendering is internal/authenticated | No explicit `/home` public route confirmed in audited dispatch excerpts |

Mismatch risk:

- Gateway and AI now intend Gateway-owned login, but Huyan still has local `/login` handling in `portal_v2.py`. If production routing sends users to Huyan for `/login`, users can see a legacy local login page.
- AI `/login` is correctly disabled as a local form in current code and redirects to Gateway, but production must route `ai.vafox.com/login` to the Flask AI app for this behavior to appear.
- Gateway Nginx `try_files $uri $uri/ /index.html` means `/login`, `/dashboard`, and `/home` on Gateway are static SPA fallbacks unless server-side identity routes are separately configured.

## E. Cache and legacy exposure issues

Potential legacy exposure found in repo/config:

1. Gateway static assets under `/assets/` are cached for 30 days with `immutable`. If `index.html` or CDN cache points users to old asset URLs, legacy JavaScript/CSS can remain visible until cache purge or filename/hash change.
2. Gateway `index.html` uses query-string versions instead of content-hashed filenames. Some CDNs cache query-string assets correctly, but others require explicit cache-key configuration; this must be verified on the live CDN.
3. AI app still contains legacy-compatible templates and routes (`login.html`, `operation_home.html`, `/dashboard` compatibility redirect, disabled legacy login implementation retained as a non-route function). These are acceptable for compatibility but must not be exposed as canonical entry points after cutover.
4. `portal_v2.py` contains older V2/V4/V5 labels, route contracts, and local login/dashboard code. If `huyan.vafox.com` is still pointed at old `portal_v2.py` behavior without Genesis route ownership, legacy pages will remain visible.
5. `ai.vafox.com` Nginx snippet only proxies selected exact routes and `/static/`; it does not define ownership for `/`, `/login`, or `/home`. Those routes depend on the existing production server config.

## F. Required fixes before cutover, not applied

Do not merge fixes automatically. Recommended next actions for the deployment owner:

1. From a network location that can reach production, capture DNS/CDN/origin evidence for each host:
   - `dig +trace gateway.vafox.com`, `dig +trace ai.vafox.com`, `dig +trace huyan.vafox.com`
   - `curl -I https://<host>/`
   - `curl -I https://<host>/version`, `curl -s https://<host>/health/runtime` where supported
   - `curl -s https://<host>/ | sha256sum`
2. On the production host, capture Nginx and service ownership:
   - `sudo nginx -T | sed -n '/server_name gateway.vafox.com/,/}/p'`
   - `sudo nginx -T | sed -n '/server_name ai.vafox.com/,/}/p'`
   - `sudo nginx -T | sed -n '/server_name huyan.vafox.com/,/}/p'`
   - `docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'`
   - `docker inspect <container> --format '{{json .Config.Image}} {{json .Config.Labels}} {{json .Config.Env}}'`
3. Stamp all production builds with `GIT_COMMIT`, `BUILD_TIME`, `DEPLOY_TIME`, and `FOXBRAIN_VERSION`, or generate `deployment.json` in the image/release directory.
4. Align image tags with release identity. Replace ambiguous `foxbrain-v4:${FOXBRAIN_VERSION:-0.20.5}` naming with a tag that includes the Genesis/V6 release and commit SHA.
5. Make `ai.vafox.com` route ownership explicit for `/`, `/login`, `/dashboard`, and `/home` in its production Nginx server block.
6. For Gateway static cutover, deploy to a new content-hashed release directory, update `/var/www/firefox-gateway/current`, reload Nginx, and purge CDN cache for `/`, `/index.html`, `/assets/app.js*`, and `/assets/styles.css*`.
7. Retain legacy templates only as compatibility fallbacks, but block them from canonical public routes after Gateway SSO cutover.

## Audit status

- Production commit vs latest Git commit: **UNVERIFIED** due blocked network and no production host access.
- Deployment status: **UNVERIFIED** live; repo deployment config reviewed.
- Container image version: **UNVERIFIED** live; repo image tag mismatch risk found.
- Build timestamp: **UNVERIFIED** live; code supports metadata but defaults to `unknown` without env/metadata.
- Frontend bundle version: **PARTIAL**; Gateway static query-string markers found locally, live bundle unverified.
- Backend release version: **PARTIAL**; local default is `AI-OS-V6-CLEAN-REBUILD-V1`, live backend unverified.
