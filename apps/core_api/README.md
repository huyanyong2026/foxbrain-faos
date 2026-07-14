# Enterprise Data Core Read-Only API

This service is the only application-facing path to the SAP mirror.

- It loads credentials for the local `SAP_MIRROR` database only.
- It never loads or receives SAP production credentials.
- Only authenticated `GET` and `HEAD` requests are accepted.
- Raw SQL is not exposed. Table access is controlled by an allowlist.
- `gateway.vafox.com` receives only `public:read`; enterprise facts stay private.

Secrets belong in `/opt/foxbrain-core/api/core-api.env` on the server and must
never be committed.

## Business Object API

Applications consume normalized objects instead of SAP tables:

- `GET /api/v1/objects/stores`
- `GET /api/v1/objects/products`
- `GET /api/v1/objects/brands`
- `GET /api/v1/objects/suppliers`
- `GET /api/v1/objects/customers` (requires `customers:read`)
- `GET /api/v1/objects/customers/{customer_id}/purchases` (requires `customers:read`)
- `GET /api/v1/explorer/customer-match?phone_hash=...` (requires `explorer:match`; returns one match only)
- `GET /api/v1/business/summary`
- `GET /api/v1/data-health`
- `GET /api/v1/public/stores`
- `GET /api/v1/public/brands`

Recommended token scopes:

- Huyan CEO Brain: `facts:read`, `objects:read`, `customers:read`, `health:read`
- AI purchasing service: `objects:read`, `health:read`
- Store manager: `objects:read`, role `store_manager`, plus explicit `store_ids`
- Gateway: `public:read` only
- Core operator compatibility access: `raw:read` (never assign to Huyan, AI, or Gateway)

Public stores and brands are deny-by-default. Copy
`object-enrichment.example.json` to the server, confirm each public object, and
set `public` to `true`. The server file is operational configuration and is not
committed with real business values.

## Replenishment input

`GET /api/v1/replenishment/input` exposes normalized, read-only store inventory and two 30-day sales
windows from the SAP mirror. Configure the three approved warehouse mappings on the Core server only:

```text
CORE_STORE_MAP_JSON={"WH_NS":{"store_code":"nanshan","store_name":"南山店"},"WH_HY":{"store_code":"hangyuan","store_name":"航苑店"},"WH_ZX":{"store_code":"zhenxing","store_name":"振兴店"}}
```

Replace `WH_NS`, `WH_HY`, and `WH_ZX` with the actual SAP mirror warehouse codes. The endpoint remains
GET-only and never connects to SAP production.
