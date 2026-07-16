# AI OS V5 Runtime API

FoxBrain services expose `GET /health/runtime` for production self-verification.

Safe response fields: `system`, `service`, `service_key`, `version`, `commit`, `build_time`, `environment`, `status`, `runtime_status`, `timestamp`, and boolean/status capability checks.

No business, customer, financial, or SAP row-level data is returned.

Expected version: `AI-OS-V5`.

Endpoints:
- `https://gateway.vafox.com/health/runtime`
- `https://huyan.vafox.com/health/runtime`
- `https://ai.vafox.com/health/runtime`
- `https://core.vafox.com/health/runtime`
