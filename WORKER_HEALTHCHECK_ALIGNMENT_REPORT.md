# Worker Healthcheck Alignment Report V2.0

## Scope

This change reviews and aligns the Docker healthcheck for `foxbrain-worker` with the actual worker runtime command in `infra/scripts/cloud_worker.py`.

## Runtime baseline

The worker service is started by Docker Compose with:

```yaml
command: ["python", "infra/scripts/cloud_worker.py"]
```

The worker itself is a long-running scheduler loop. It does not expose an HTTP port, so HTTP healthchecks from the shared application image are not suitable for this container.

## Root cause

The worker container can be running correctly while still being marked unhealthy if the healthcheck does not validate the actual scheduler process. The correct health signal for this container is process-based:

1. a Python worker process exists;
2. the process command includes `infra/scripts/cloud_worker.py`;
3. the process is in a running/sleeping kernel state rather than exited or zombie.

## Alignment implemented

`infra/scripts/worker_healthcheck.py` now scans `/proc` for a live Python process whose command line runs `infra/scripts/cloud_worker.py`. It accepts both relative and absolute script paths, excludes the healthcheck process itself, and verifies that the matched worker process is in an active Linux process state.

The Compose worker healthcheck continues to call the dedicated script:

```yaml
healthcheck:
  test: ["CMD", "python", "/app/infra/scripts/worker_healthcheck.py"]
```

## Expected validation

Inside a running `foxbrain-worker` container:

```bash
python infra/scripts/worker_healthcheck.py
```

Expected result: exit code `0`.

For Docker Compose:

```bash
docker compose ps
```

Expected result: `foxbrain-worker` reports `healthy` after the configured start period and retries.

## Non-goals

No worker business logic, scheduled jobs, database code, API code, or frontend code was changed.
