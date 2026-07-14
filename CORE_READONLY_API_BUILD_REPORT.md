# VAFOX Enterprise Data Core Read-Only API Build Report

## Completed

- Added an authenticated HTTPS API at `https://core.vafox.com`.
- Kept SQL Server bound to `127.0.0.1:11433`; the database port is not public.
- Created a dedicated local mirror login, `foxbrain_core_api`, with data-reader membership only.
- Verified `SELECT` succeeds and `INSERT`, `UPDATE`, `DELETE`, and DDL are denied.
- Added separate credentials for Huyan, AI, and Gateway without committing secrets.
- Gave Huyan and AI the `facts:read` scope.
- Gave Gateway only `public:read`; it cannot list or read enterprise tables.
- Added rate limiting, TLS, no-store responses, identifier validation, a table allowlist, and a 200-row response ceiling.
- Preserved the existing 22:00 Core mirror timer and made no SAP production changes.

## API

- `GET /api/health` - authenticated enterprise health.
- `GET /api/v1/status` - authenticated mirror freshness and reconciliation status.
- `GET /api/v1/tables` - approved table metadata for enterprise clients.
- `GET /api/v1/tables/{schema}/{table}/rows` - paged, allowlisted, read-only rows.
- `GET /api/v1/public/status` - restricted public operating status.

All `POST`, `PUT`, `PATCH`, and `DELETE` requests return `405 read_only_api`.

## Client Connections

- `huyan.vafox.com`: server-side Core URL and private token configured; production access test returned 200.
- `ai.vafox.com`: server-side Core URL and private token configured; production access test returned 200.
- `gateway.vafox.com`: `/api/core/status` proxies only the public status endpoint and keeps the token on the server.

## Production Safety

- Core backup: `/opt/foxbrain-core/backup/core-api-20260713-211500`
- Huyan backup: `/opt/backups/core-api-client-20260713-212000`
- AI/Gateway backup: `/opt/backups/core-api-client-20260713-212000`
- SAP production credentials are not loaded by the API.
- No SAP write permission was added.
- No SQL endpoint or user-supplied SQL is exposed.

## Verification

- Local unit and integration tests: 15 passed.
- Huyan to Core status: 200.
- AI to Core status: 200.
- Gateway public status: 200 JSON.
- Gateway token attempting enterprise table access: 401.
- Unauthenticated Core request: 401.
- Authenticated write request: 405.
- Approved mirror table row request: 200.
- Core API service: active.
- Core Nginx HTTPS service: active.
