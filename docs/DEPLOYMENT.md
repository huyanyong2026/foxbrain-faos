# Sprint 3 Pilot Deployment

## Prerequisites

- Docker Engine with the Docker Compose plugin.
- A private deployment environment and a secret manager (or a server-local
  `.env` file with restrictive permissions).
- No SAP credential is required by the Sprint 3 services. The Business API is
  read-only and must not be configured with SAP write credentials.

## Configure the environment

1. Copy `production.env.example` to a secret-managed deployment `.env`.
2. Replace every `change_me_*` value with an environment-specific secret.
3. Set `NEXT_PUBLIC_API_BASE_URL` to the externally reachable, TLS-protected
   gateway URL. This value is compiled into the frontend bundle, so rebuild the
   frontend after changing it.
4. Keep `.env`, SAP credentials, API keys, and production tokens out of Git.

The Compose stack needs `JWT_SECRET`, PostgreSQL (`POSTGRES_DB`,
`POSTGRES_USER`, `POSTGRES_PASSWORD`), Redis (`REDIS_URL`), MinIO
(`MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `MINIO_ENDPOINT`, `MINIO_BUCKET`),
and the public ports in the environment file. `DATABASE_URL` is available to
services which require direct PostgreSQL access.

## Start and validate

```bash
cp production.env.example .env
# edit .env through the deployment secret-management process
docker compose config
docker compose up -d --build postgres redis minio business-api gateway ai-web huyan-web
docker compose ps
curl -fsS http://localhost:${GATEWAY_PORT:-8088}/health
```

`gateway` is the API entry point; `business-api` is intentionally not exposed
on a host port. The stack includes PostgreSQL as its database service and both
Next.js frontends: `ai-web` (Employee/Store Manager workspace) and `huyan-web`
(CEO cockpit).

## API security and routing

Send API requests only through the gateway with `Authorization: Bearer <JWT>`.
The gateway validates the token and forwards only verified identity fields to
the internal Business API. The following endpoints enforce authentication,
RBAC, ACL/data scope, and append audit records for successful and denied
authorized requests:

- `GET /api/customer/profile/{customer_id}` and
  `GET /api/customer/equipment/{customer_id}`
- `GET /api/retail/store-insight`, `GET /api/retail/inventory-alerts`
- `GET /api/store/dashboard`, `POST /api/store/feedback`

Use a token with an organization, user, role scopes, and department/store scope
appropriate to the user. Customer access additionally needs `customers:read`
or `customer:read`; Store Manager access needs `store_manager` (or an allowed
retail/CEO/admin role). All Sprint 3 recommendations are advisory-only.
