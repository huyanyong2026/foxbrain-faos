# Enterprise Data Core Read-Only API

This service is the only application-facing path to the SAP mirror.

- It loads credentials for the local `SAP_MIRROR` database only.
- It never loads or receives SAP production credentials.
- Only authenticated `GET` and `HEAD` requests are accepted.
- Raw SQL is not exposed. Table access is controlled by an allowlist.
- `gateway.vafox.com` receives only `public:read`; enterprise facts stay private.

Secrets belong in `/opt/foxbrain-core/api/core-api.env` on the server and must
never be committed.

## Replenishment input

`GET /api/v1/replenishment/input` exposes normalized, read-only store inventory and two 30-day sales
windows from the SAP mirror. Configure the three approved warehouse mappings on the Core server only:

```text
CORE_STORE_MAP_JSON={"WH_NS":{"store_code":"nanshan","store_name":"南山店"},"WH_HY":{"store_code":"hangyuan","store_name":"航苑店"},"WH_ZX":{"store_code":"zhenxing","store_name":"振兴店"}}
```

Replace `WH_NS`, `WH_HY`, and `WH_ZX` with the actual SAP mirror warehouse codes. The endpoint remains
GET-only and never connects to SAP production.
