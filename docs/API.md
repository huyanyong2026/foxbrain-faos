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
