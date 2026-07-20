# Memory Factory Phase 1A API

The public base URL is `http://localhost:${MEMORY_API_PORT:-8080}`. Only `memory-api` is published to the host; PostgreSQL, Redis, and MinIO remain on the Compose network.

| Method | Path | Authentication | Current behavior |
| --- | --- | --- | --- |
| GET | `/health` | No | Memory API liveness response. |

Requests for unlisted paths return `404`.

## Phase 1B-1 Qdrant foundation

These endpoints are intentionally unavailable (`503 phase1b_not_configured`) unless a Phase 1B Qdrant client is explicitly injected. They never use `QDRANT_URL` during normal Phase 1A startup and are for isolated development/staging only.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/health/vector` | Checks the injected Qdrant client's health. |
| GET | `/collections` | Lists Qdrant collections and reports the active logical alias. |
| POST | `/collections/init` | Creates the versioned physical collection and assigns the `memory_chunks_v1` alias. Body: `{"dimension":1024,"collection":"memory_chunks_v1__default","distance":"Cosine"}`; `collection` and `distance` are optional. |

The whitelisted Qdrant payload schema is `memory_id`, `chunk_id`, `owner`, `tags`, `source`, `created_at`, `content_hash`, and `embedding_profile`. `owner` is a mandatory server-side filter for every search. Alias switching is performed by creating and validating a separate physical collection (for example `memory_chunks_v2__default`) before moving the desired logical alias; existing vectors are never overwritten in place.

## Memory Factory V1

The service accepts both multipart file uploads and JSON API input. Every item records the file name and media type, required `source` and `owner`, a free-form metadata object, optional tags, and server-managed `created_at`/`updated_at` timestamps. In multipart requests, `metadata` and `tags` are JSON strings; in JSON requests they are an object and an array respectively. Phase 1A performs lexical matching on filename and metadata only; `owner` and exact `tag` are optional result filters. Embedding generation, vector storage, and AI retrieval are reserved for Phase 1B.

| Method | Path | Behavior |
| --- | --- | --- |
| POST | `/api/v1/memory/receive` | Stores an uploaded file or JSON text input and returns `memory_id` and `storage_path`. |
| GET | `/api/v1/memory/items/{memory_id}` | Reads active metadata. |
| GET | `/api/v1/memory/items/{memory_id}/content` | Downloads the object. |
| DELETE | `/api/v1/memory/items/{memory_id}` | Deletes the object and soft-deletes its metadata. |
| GET | `/api/v1/memory/search?q={query}&owner={owner}&tag={tag}` | Searches active filename and metadata; `owner` and exact `tag` are optional filters. |

### Receive examples

```bash
# File upload. `metadata` and `tags` must be valid JSON values.
curl -X POST http://localhost:8080/api/v1/memory/receive \
  -F file=@./brief.pdf -F source=manual -F owner=finance \
  -F 'metadata={"period":"2026-Q3"}' -F 'tags=["planning","quarterly"]'

# JSON text input.
curl -X POST http://localhost:8080/api/v1/memory/receive \
  -H 'Content-Type: application/json' \
  -d '{"name":"note.txt","content":"approved","source":"api","owner":"finance","metadata":{"project":"factory"},"tags":["approval"]}'
```

`tags` is optional and must be an array of non-empty strings. Successful item and search responses include `tags`, `created_at`, and `updated_at` alongside the stored metadata. Invalid JSON input returns `400 invalid_json`; invalid metadata and tag shapes return `400 metadata_must_be_object` and `400 tags_must_be_string_array`.

The machine-readable contract is [`openapi-memory-v1.yaml`](openapi-memory-v1.yaml).
