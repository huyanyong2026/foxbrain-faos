# Foundation operations and health checks

After `docker compose up --build -d`, validate the system with:

```bash
docker compose ps
curl -fsS http://localhost:8080/health
curl -fsS http://localhost:8080/api/v1/health
docker compose logs --tail=50 gateway auth core-data ai memory
```

Expected Compose health state: `gateway`, `auth`, `core-data`, `ai`, `memory`, `postgres`, `redis`, and `minio` are `healthy` or running after their health probes pass. PostgreSQL uses `pg_isready`; Redis uses `redis-cli ping`; MinIO uses its `/minio/health/live` endpoint.

To check protected routing, acquire a token from the login endpoint and send it as `Authorization: Bearer <token>` to one of the protected health endpoints listed in [API.md](API.md).
