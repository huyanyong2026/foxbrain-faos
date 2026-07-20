# Memory Factory Phase 1A API

The public base URL is `http://localhost:${MEMORY_API_PORT:-8080}`. Only `memory-api` is published to the host; PostgreSQL, Redis, and MinIO remain on the Compose network.

| Method | Path | Authentication | Current behavior |
| --- | --- | --- | --- |
| GET | `/health` | No | Memory API liveness response. |

Requests for unlisted paths return `404`.

## Memory Factory V1

The service accepts both multipart file uploads and JSON API input; `source` and `owner` are required, and multipart `metadata` is a JSON object string. Phase 1A performs lexical matching on filename and metadata only. Embedding generation, vector storage, and AI retrieval are reserved for Phase 1B.

| Method | Path | Behavior |
| --- | --- | --- |
| POST | `/api/v1/memory/receive` | Stores an uploaded file or JSON text input and returns `memory_id` and `storage_path`. |
| GET | `/api/v1/memory/items/{memory_id}` | Reads active metadata. |
| GET | `/api/v1/memory/items/{memory_id}/content` | Downloads the object. |
| DELETE | `/api/v1/memory/items/{memory_id}` | Deletes the object and soft-deletes its metadata. |
| GET | `/api/v1/memory/search?q={query}&owner={owner}` | Searches active filename and metadata; `owner` is optional. |

The machine-readable contract is [`openapi-memory-v1.yaml`](openapi-memory-v1.yaml).
