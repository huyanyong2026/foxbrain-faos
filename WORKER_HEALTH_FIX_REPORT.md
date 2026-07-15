# Worker Health Fix Report V1.0

## Root cause

The `foxbrain-worker` service uses the shared `foxbrain-v4:cloud` image. That image defines an HTTP Docker `HEALTHCHECK` that calls `/api/health` on `${PORT:-8088}`. The worker container runs `python infra/scripts/cloud_worker.py` and does not start an HTTP server, so the inherited image health check reports the worker as unhealthy even when the scheduler process is running.

## Files changed

- `docker-compose.yml`
  - Added a service-level health check for `foxbrain-worker` so Docker Compose overrides the image-level HTTP health check.
  - The new health check runs `python /app/infra/scripts/worker_healthcheck.py`.
- `infra/scripts/worker_healthcheck.py`
  - Added a process-based health check that scans `/proc` and returns success only when the Python `infra/scripts/cloud_worker.py` scheduler process is running.

## Validation result

- `python -m py_compile infra/scripts/cloud_worker.py infra/scripts/worker_healthcheck.py`: passed.
- `python infra/scripts/worker_healthcheck.py` with no worker process running: returned exit code `1` as expected.
- `python infra/scripts/cloud_worker.py` started in the background, then `python infra/scripts/worker_healthcheck.py`: returned exit code `0` as expected.
- `docker compose config`: not run successfully in this execution environment because the `docker` CLI is not installed (`docker: command not found`).
- `docker compose build foxbrain-worker`: blocked in this execution environment because the `docker` CLI is not installed.
- `docker compose up -d`: blocked in this execution environment because the `docker` CLI is not installed.
- Production confirmation for `foxbrain-worker` healthy must be completed on a Docker host after deploying this commit.

## Scope control

No changes were made to portal business logic, frontend code, database schema, SAP logic, or AI logic.
