# VAFOX Memory Factory

VAFOX Memory Factory is the backend-only enterprise-memory service. It receives files and API text, stores objects in MinIO, records file, owner, source, tags, free-form metadata, and timestamps in PostgreSQL, and provides filename and metadata search.

## Phase 1A Foundation Layer

Phase 1A has a deliberately narrow deployment scope. Docker Compose runs exactly these services:

| Service | Responsibility | Host exposure |
| --- | --- | --- |
| `memory-api` | Memory ingestion, metadata, object download, and lexical search | `${MEMORY_API_PORT:-8080}` |
| `postgres` | Memory metadata persistence | internal |
| `redis` | Foundation cache/queue dependency | internal |
| `minio` | S3-compatible memory object storage | internal |

Phase 1A does **not** deploy Qdrant, any vector database, embedding generation, AI retrieval, a gateway, or business-domain services. Search is lexical only, against filenames and metadata.

The PostgreSQL initialization migration [`infrastructure/postgres/002-memory-factory.sql`](infrastructure/postgres/002-memory-factory.sql) creates `memory_items`, `storage_objects`, and `memory_tags` for a fresh volume.

## Quick start

```bash
cp .env.example .env
# Replace all change_me values in .env.
docker compose up --build -d
docker compose ps
curl -fsS http://localhost:8080/health
```

Send a file to the Memory API:

```bash
curl -X POST http://localhost:8080/api/v1/memory/receive \
  -F file=@./example.txt -F source=manual -F owner=engineering \
  -F 'metadata={"project":"memory-factory"}' -F 'tags=["example"]'
```

Run the deployment health check:

```bash
APP_DIR="$PWD" bash healthcheck.sh
```

Stop the stack while retaining data with `docker compose down`; remove local persistent data with `docker compose down -v`.

## Backup and rollback

```bash
APP_DIR="$PWD" bash backup.sh
APP_DIR="$PWD" bash rollback.sh "$PWD/backups/YYYY-MM-DD_HH-MM-SS"
```

See [README_BACKUP_RESTORE.md](README_BACKUP_RESTORE.md) for details.

## Phase 1B AI Retrieval Layer

Phase 1B is reserved for AI retrieval capabilities, including embedding generation and a vector database. It is not part of this Compose deployment and must be designed, deployed, and operated as a separate phase.

The non-deployment architecture proposal—embedding provider abstraction and selection, Qdrant collection/payload schema, chunk pipeline, Retrieval API contracts, Dify boundary, staging guidance, and risks—is in [`docs/MEMORY_FACTORY_PHASE_1B_ARCHITECTURE.md`](docs/MEMORY_FACTORY_PHASE_1B_ARCHITECTURE.md). It deliberately does not modify Dify, SAP, Core, or production infrastructure.

## API

The API contract is in [`docs/openapi-memory-v1.yaml`](docs/openapi-memory-v1.yaml). The available endpoints are documented in [`docs/API.md`](docs/API.md).

For Phase 1A validation coverage and results, see [`docs/MEMORY_FACTORY_PHASE_1A_TEST_REPORT.md`](docs/MEMORY_FACTORY_PHASE_1A_TEST_REPORT.md). This repository does not connect to production SAP or Dify and does not modify servers.
