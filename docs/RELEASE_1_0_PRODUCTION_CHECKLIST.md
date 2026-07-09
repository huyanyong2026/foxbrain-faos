# FoxBrain Release 1.0 Production Checklist

## Stability

- Local syntax check passes.
- Smoke tests pass.
- Existing login and role permissions remain unchanged.
- High-risk actions require approval.

## Deployability

- `Dockerfile` exists.
- `docker-compose.yml` exists.
- `.env.example` exists.
- `install.sh` exists.
- GitHub Actions deployment workflow exists.
- `restart: always` is configured for long-running services.

## Observability

- `/api/health` exists.
- `healthcheck.sh` exists.
- Logs directory is mounted.
- Operations endpoint exposes backup, restore and health status.

## Rollback

- `backup.sh` exists.
- `restore.sh` exists.
- Backup and restore documentation exists.
- Rollback checklist exists.

## Security

- Secrets remain in `.env`.
- No real passwords are committed.
- Role-based authorization is active.
- High-risk AI, automation and business actions require approval.

## Final Gate

Before live production rollout:

1. Pull latest `main` on the server.
2. Run deployment.
3. Confirm containers are healthy.
4. Open login page.
5. Open `/api/health`.
6. Test backup.
7. Test rollback on a maintenance window or staging copy.
