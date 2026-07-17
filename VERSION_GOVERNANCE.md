# Version Governance

Every deployment must declare aligned frontend, backend, API, database schema, deployment, and runtime versions for gateway, huyan, ai, and core.

Use `release_guard.py <manifest>` before deployment. The guard fails if any service does not equal the Genesis release `AI-OS-V6-CLEAN-REBUILD-V1`, or if a service advertises obsolete V4/V5/FoxBrain Enterprise OS governance identity.
