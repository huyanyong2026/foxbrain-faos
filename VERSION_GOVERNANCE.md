# Version Governance

Every deployment must declare aligned frontend, backend, API, database schema, deployment, and runtime versions for gateway, huyan, ai, and core.

Use `release_guard.py <manifest>` before deployment. The guard fails if any service does not equal `AI-OS-V5.1`.
