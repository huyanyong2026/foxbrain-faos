# Deployment

## Environment contract

| Environment | `NEXT_PUBLIC_API_BASE_URL` |
| --- | --- |
| development | local API Gateway URL |
| test | test API Gateway URL |
| production | production API Gateway URL |

Environment variables are supplied by the deployment platform; `.env` files and credentials are never committed. Validate compose topology with:

```bash
docker compose --env-file test.env.example config --quiet
```

Frontend images are built with `infrastructure/docker/frontend.Dockerfile` and `APP=ai-web` or `APP=huyan-web`.
