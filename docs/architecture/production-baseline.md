# Production Baseline

| Component | Baseline |
| --- | --- |
| Python | 3.12 |
| Node.js | 22 LTS |
| Docker | Docker Engine with Compose v2 |
| PostgreSQL | 16 |
| Redis | 7 |
| Milvus | 2.4-compatible deployment (managed separately) |
| MinIO | RELEASE.2025-01-20T14-49-07Z |

Pin image and package versions during release preparation. Upgrade one platform component at a time in test before promotion.
