# Production Final Verification Report

Verification date: 2026-07-17 13:07 UTC

Mission rule: verify production truth only. No production code, feature behavior, or deployment configuration was changed.

## Executive Result

Production cannot be fully certified from this runtime verifier because direct `/health/runtime` probes from the execution shell did not reach the VAFOX origins.

Observed truth:

- Direct shell HTTPS probes to all required `/health/runtime` endpoints were blocked by the environment outbound proxy with `HTTP/1.1 403 Forbidden` / `CONNECT tunnel failed, response 403`.
- Direct non-proxy DNS resolution from the execution shell failed for `gateway.vafox.com`, `ai.vafox.com`, and `huyan.vafox.com`.
- External page fetch did reach the public root pages and confirmed the currently visible unauthenticated surfaces:
  - `gateway.vafox.com` serves the VAFOX Outdoor Growth Platform / Genesis-style public gateway page, not the previously described legacy enterprise dashboard.
  - `ai.vafox.com` redirects to an enterprise identity login page.
  - `huyan.vafox.com` serves the FireFox AI Operating System login page.
- Because `/health/runtime` payloads were not retrievable from this environment, live `version`, `commit`, `build_time`, `deploy_time`, `environment`, and `running` status remain **UNVERIFIED** for all three required production hosts.

## Scope

Required production hosts:

| Host | Required endpoint |
| --- | --- |
| `gateway.vafox.com` | `https://gateway.vafox.com/health/runtime` |
| `ai.vafox.com` | `https://ai.vafox.com/health/runtime` |
| `huyan.vafox.com` | `https://huyan.vafox.com/health/runtime` |

Required fields:

- `version`
- `commit`
- `build_time`
- `deploy_time`
- `environment`
- `status` / `runtime_status` showing `running`

## Direct Runtime Probe Evidence

Command executed:

```bash
for h in gateway.vafox.com ai.vafox.com huyan.vafox.com; do echo '###' $h; curl -fsS --max-time 20 -i https://$h/health/runtime || true; echo; done
```

Observed output summary:

| Host | `/health/runtime` result | Runtime metadata result |
| --- | --- | --- |
| `gateway.vafox.com` | `HTTP/1.1 403 Forbidden` from `server: envoy`; curl reported requested URL returned error 403 | UNVERIFIED |
| `ai.vafox.com` | `HTTP/1.1 403 Forbidden` from `server: envoy`; curl reported requested URL returned error 403 | UNVERIFIED |
| `huyan.vafox.com` | `HTTP/1.1 403 Forbidden` from `server: envoy`; curl reported requested URL returned error 403 | UNVERIFIED |

Second command executed against `/health/runtime`, `/`, `/version`, and `/health`:

```bash
for h in gateway.vafox.com ai.vafox.com huyan.vafox.com; do for p in /health/runtime / /version /health; do echo "### https://$h$p"; curl -sS --max-time 20 -D - "https://$h$p" -o /tmp/resp.$$; done; done
```

Observed output summary:

- All tested paths returned `HTTP/1.1 403 Forbidden` from `server: envoy` before a response body was saved.
- curl reported `CONNECT tunnel failed, response 403`.

Non-proxy DNS/runtime command executed:

```bash
for h in gateway.vafox.com ai.vafox.com huyan.vafox.com; do echo '###' $h; curl --noproxy '*' -sS --max-time 20 -D - https://$h/health/runtime -o /tmp/${h}.health || true; done
```

Observed output summary:

| Host | Non-proxy result |
| --- | --- |
| `gateway.vafox.com` | `curl: (6) Could not resolve host: gateway.vafox.com` |
| `ai.vafox.com` | `curl: (6) Could not resolve host: ai.vafox.com` |
| `huyan.vafox.com` | `curl: (6) Could not resolve host: huyan.vafox.com` |

## Public Root Page Evidence

An external fetch path was able to read unauthenticated root pages.

| Host | Public page observed | Production UI finding |
| --- | --- | --- |
| `gateway.vafox.com` | `VAFOX Outdoor Growth Platform`, `向外探索 / 向内成长`, VAFOX Story, Adventure, Brand Universe, Explorer, Store | New public Gateway / Genesis-style experience is visible on the unauthenticated root page. Legacy enterprise dashboard was not observed on this page. |
| `ai.vafox.com` | Redirected to `/auth/login`; page title/content is `登录 | VAFOX 企业身份中心` and `真实身份，真实工作` | Enterprise identity login is active on unauthenticated access. Authenticated AI experience was not verified. |
| `huyan.vafox.com` | `火狐狸 AI 企业经营系统`, `FireFox AI Operating System：AI + ERP + CRM + OA + 知识库 + BI + 智能体平台的统一入口。` | Huyan login surface is active on unauthenticated access. Authenticated Genesis experience was not verified. |

## Runtime Metadata Matrix

| Host | version | commit | build_time | deploy_time | environment | status / runtime_status |
| --- | --- | --- | --- | --- | --- | --- |
| `gateway.vafox.com` | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED |
| `ai.vafox.com` | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED |
| `huyan.vafox.com` | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED |

Reason: required `/health/runtime` JSON responses could not be retrieved from this execution shell.

## Requested Confirmations

### 1. Production no longer serves legacy UI

Status: **PARTIALLY VERIFIED / AUTHENTICATED AREAS UNVERIFIED**

- `gateway.vafox.com` root page is not the previously reported legacy enterprise dashboard; it shows the VAFOX Outdoor Growth Platform / Genesis-style public gateway.
- `ai.vafox.com` and `huyan.vafox.com` unauthenticated roots show login surfaces, not enough authenticated content to prove no legacy UI exists after login.
- Full confirmation requires browser/session access for authenticated routes or production-side screenshots after login.

### 2. New Genesis experience is active

Status: **PARTIALLY VERIFIED**

- Gateway public root visibly presents the new VAFOX Outdoor Growth Platform / Genesis-style experience.
- `ai.vafox.com` and `huyan.vafox.com` runtime/health metadata and authenticated application surfaces were not accessible from this verifier, so Genesis activation cannot be fully certified across all three domains.

### 3. Single deployment workflow is active

Status: **REPOSITORY VERIFIED / PRODUCTION RUNTIME UNVERIFIED**

Repository evidence shows the production cutover repair intended a single automatic production deployment bridge and a post-deploy `/health/runtime` gate. The checked workflow is `.github/workflows/production-deploy.yml`, and the release verifier is `scripts/verify_release_runtime.py`.

This confirms repository intent, not actual GitHub production run history. Full production truth requires checking the GitHub Actions run list and confirming no other workflow deployed the same production hosts after the final repair.

### 4. Rollback protection is available

Status: **REPOSITORY VERIFIED / PRODUCTION EXECUTION UNVERIFIED**

Repository evidence shows rollback logic in the production deployment workflow and a manual rollback path documented in the cutover repair report. Because no production deployment was executed in this verification, rollback execution was not rehearsed or proven live during this run.

## Final Certification

Overall status: **NOT CERTIFIED AS FULL PASS FROM THIS ENVIRONMENT**

Reason:

- The required `/health/runtime` production metadata for `gateway.vafox.com`, `ai.vafox.com`, and `huyan.vafox.com` was not retrievable from the execution shell.
- The visible public Gateway page supports that the legacy public gateway UI is no longer active, but authenticated AI/Huyan surfaces and runtime version identity remain unverified.

## Required Next Verification From a Network Path That Can Reach Production Origins

Run from the production host, trusted VPN, GitHub Actions runner, or another network path that can resolve and connect to the public origins:

```bash
python scripts/verify_release_runtime.py --expected-version AI-OS-V6-CLEAN-REBUILD-V1
```

Then capture:

```bash
for h in gateway.vafox.com ai.vafox.com huyan.vafox.com; do
  echo "### $h /health/runtime"
  curl -fsS "https://$h/health/runtime" | python -m json.tool
  echo "### $h root"
  curl -fsS -D - "https://$h/?runtime-final-verification=$(date +%s)" -o "/tmp/${h}.html"
done
```

Acceptance requires every `/health/runtime` response to include current `version`, `commit`, `build_time`, `deploy_time`, `environment=production`, and `status`/`runtime_status=running`, plus visual/root evidence that no legacy UI is served.
