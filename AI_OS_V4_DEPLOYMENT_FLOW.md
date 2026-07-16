# FoxBrain AI OS V4 Production Activation

This document supports the production activation bridge without redesigning applications, changing SAP business logic, or changing AI workflows.

## Runtime Identity

Each runtime service exposes `/health/version` with system, version, release, service, commit, build time, deploy time, environment, and status.

## Health Console

Administrators use `/internal/health` to view Gateway, Huyan, AI, and Core status/version/commit. The console requires authenticated RBAC/ABAC authorization and writes a permission audit record.

## Verification

Run:

```bash
python production_activation_check.py
```

The script checks health API responses, route DNS/HTTPS reachability, service availability, and `deployment.json` metadata. Results are `PASS`, `FAIL`, or `UNVERIFIED`.

## Deployment Flow

Build generates `deployment.json`, deploys services, runs health checks, and fails deployment if production activation verification fails.

## Monitoring Foundation

Monitor service availability, API response status, version mismatch, and health status for Gateway, Huyan, AI, and Core.
