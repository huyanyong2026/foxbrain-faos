# Foundation API list

The public base URL is `http://localhost:${GATEWAY_PORT:-8080}`. Only the Gateway is published to the host; all service ports remain on the Compose network.

| Method | Path | Authentication | Current behavior |
| --- | --- | --- | --- |
| GET | `/health` | No | Gateway liveness response: `{"status":"ok","service":"gateway"}`. |
| GET | `/healthz` | No | Gateway liveness alias. |
| GET | `/api/v1/health` | No | Gateway liveness alias. |
| POST | `/api/v1/auth/login` | No | Issues a JWT for the configured bootstrap administrator. |
| GET | `/api/v1/core/health` | Bearer JWT | Core Data Service liveness. |
| GET | `/api/v1/ai/health` | Bearer JWT | AI Service liveness. |
| GET | `/api/v1/memory/health` | Bearer JWT | Memory Service liveness. |

No business APIs are implemented. Requests for unlisted gateway paths return `404`; protected paths without a valid bearer token return `401`.

## Login example

```bash
curl -sS -X POST http://localhost:8080/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  --data '{"username":"admin","password":"replace-with-your-bootstrap-password"}'
```

## Memory Factory V1

All Memory Factory endpoints require a bearer JWT when called through the Gateway. The service accepts both multipart file uploads and JSON API input; `source` and `owner` are required, and multipart `metadata` is a JSON object string. V1 performs lexical matching on filename and metadata only; the embedding integration is intentionally reserved for a future version.

| Method | Path | Behavior |
| --- | --- | --- |
| POST | `/api/v1/memory/receive` | Stores an uploaded file or JSON text input and returns `memory_id` and `storage_path`. |
| GET | `/api/v1/memory/items/{memory_id}` | Reads active metadata. |
| GET | `/api/v1/memory/items/{memory_id}/content` | Downloads the object. |
| DELETE | `/api/v1/memory/items/{memory_id}` | Deletes the object and soft-deletes its metadata. |
| GET | `/api/v1/memory/search?q={query}&owner={owner}` | Searches active filename and metadata; `owner` is optional. |

The machine-readable contract is [`openapi-memory-v1.yaml`](openapi-memory-v1.yaml).
