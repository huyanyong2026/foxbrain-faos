# VAFOX Enterprise AI OS Foundation

VAFOX Foundation is the deployable infrastructure skeleton for the VAFOX Enterprise AI OS. It deliberately contains **no business domain, UI, SAP integration, or WeCom integration**.

## Repository layout

```text
apps/             Reserved application delivery surfaces (no pages in Foundation)
services/         Gateway, Auth, Core Data, AI, and Memory service processes
packages/         Shared HTTP, JSON logging, JWT, and authorization primitives
infrastructure/   PostgreSQL bootstrap assets and deployment infrastructure
docs/             API contract and operational documentation
```

## Included components

| Component | Role | Port exposure |
| --- | --- | --- |
| Gateway | Single external API entry point and upstream routing | `${GATEWAY_PORT:-8080}` |
| Auth Service | Bootstrap login and HS256 JWT issuance | internal |
| Core Data Service | Future enterprise-data boundary | internal |
| AI Service | Future AI-runtime boundary | internal |
| Memory Service | Future memory boundary | internal |
| PostgreSQL 16 | Relational persistence foundation | internal |
| Redis 7 | Cache/session/queue foundation | internal |
| MinIO | S3-compatible object-storage foundation | internal |

All application logs are structured JSON on stdout; Docker rotates JSON log files at 10 MB with three retained files per container. Every service provides `GET /health`, and Compose waits for dependency health checks before starting dependents.

## Quick start

```bash
cp .env.example .env
# Set non-default JWT_SECRET and BOOTSTRAP_ADMIN_PASSWORD in .env.
docker compose up --build -d
docker compose ps
curl -fsS http://localhost:8080/health
```

Stop the stack while retaining data:

```bash
docker compose down
```

Delete persistent development data as well:

```bash
docker compose down -v
```

## Authentication and authorization

`POST /api/v1/auth/login` receives a JSON `username` and `password`, validates the configured bootstrap administrator, and returns an expiring HS256 bearer token. The Gateway requires that bearer token for all non-auth upstream paths. The shared `require_roles()` middleware in `packages/vafox_foundation/auth.py` is the reusable service-level enforcement primitive. Role claims use strings such as `platform:admin`; no business permissions are defined in this foundation.

See [the API reference](docs/API.md) for the complete current API list and [the operations guide](docs/OPERATIONS.md) for health checks.
