# AI OS V4 Observability
FoxBrain AI OS V4 exposes runtime metadata through `/health/version` for gateway, huyan, ai, and core. Metadata includes system, version, service, commit, build time, deploy time, environment, and status.

Internal health dashboard data is provided by `control_tower_status()` with component status, version, commit, and last deployment.
