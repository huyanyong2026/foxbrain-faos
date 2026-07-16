# Runtime Version Report

Generated: 2026-07-16 12:36 UTC  
Scope: `gateway.vafox.com`, `huyan.vafox.com`, `ai.vafox.com`, `core.vafox.com`  
Verification package: `AI-OS-V4-RUNTIME-CHECK-V1`

## Executive Result

Production runtime version state is **UNVERIFIED** for all four services from this execution environment.

The repository defines V4 health/version endpoints and expected metadata fields, but live production evidence could not be retrieved because outbound HTTPS attempts to each production host were blocked by the execution environment's network proxy with `CONNECT tunnel failed, response 403`. DNS resolution via `getent ahosts` also returned no address rows for the requested hosts.

## Expected Health Contract

The documented V4 runtime contract expects these endpoints:

- `https://gateway.vafox.com/health/version`
- `https://huyan.vafox.com/health/version`
- `https://ai.vafox.com/health/version`
- `https://core.vafox.com/health/version`

Expected fields: `system`, `version`, `service`, `commit`, `build_time`, `deploy_time`, `environment`, `status`.

## Service Version Matrix

| Service Name | Host | Current Version | Git Commit | Build Time | Deploy Time | Runtime Status | Evidence |
|---|---|---:|---:|---:|---:|---|---|
| Gateway | `gateway.vafox.com` | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | HTTPS blocked by proxy 403; DNS returned no rows. |
| Huyan | `huyan.vafox.com` | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | HTTPS blocked by proxy 403; DNS returned no rows. |
| AI Workforce | `ai.vafox.com` | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | HTTPS blocked by proxy 403; DNS returned no rows. |
| Core | `core.vafox.com` | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | UNVERIFIED | HTTPS blocked by proxy 403; DNS returned no rows. |

## Local Repository Evidence Only

- Current local Git commit: `eac6e6eb2a6c0f480d6b43f1c972e342996db00c`.
- Current branch: `work`.
- Local source includes AI OS V4 version constant `AI-OS-V4.0`.
- Local source includes `/health/version` handlers for gateway, AI, and core code paths.
- Local tests for V4, observability, foundation routing, and security boundaries passed locally.

## Commands Run

```bash
getent ahosts gateway.vafox.com
curl -k -I -L --max-time 15 https://gateway.vafox.com
curl -k -sS -o /tmp/curlbody -w '%{http_code}' --max-time 10 https://gateway.vafox.com/health/version
```

The same DNS, HTTPS, and health/version checks were repeated for `huyan.vafox.com`, `ai.vafox.com`, and `core.vafox.com`.
