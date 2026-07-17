# Version Alignment Report

Version: AI-OS-V6-CLEAN-REBUILD-V1-LEGACY-CLEANUP

## Result

PASS — Gateway, Huyan, VAFOX Enterprise AI Center, and Core are governed by the same Genesis release contract.

| Service | Current version | Git commit | Build version | Deployment version | Runtime version | Status |
| --- | --- | --- | --- | --- | --- | --- |
| gateway | AI-OS-V6-CLEAN-REBUILD-V1 | `runtime` | AI-OS-V6-CLEAN-REBUILD-V1 | AI-OS-V6-CLEAN-REBUILD-V1 | AI-OS-V6-CLEAN-REBUILD-V1 | PASS |
| huyan | AI-OS-V6-CLEAN-REBUILD-V1 | `runtime` | AI-OS-V6-CLEAN-REBUILD-V1 | AI-OS-V6-CLEAN-REBUILD-V1 | AI-OS-V6-CLEAN-REBUILD-V1 | PASS |
| ai | AI-OS-V6-CLEAN-REBUILD-V1 | `runtime` | AI-OS-V6-CLEAN-REBUILD-V1 | AI-OS-V6-CLEAN-REBUILD-V1 | AI-OS-V6-CLEAN-REBUILD-V1 | PASS |
| core | AI-OS-V6-CLEAN-REBUILD-V1 | `runtime` | AI-OS-V6-CLEAN-REBUILD-V1 | AI-OS-V6-CLEAN-REBUILD-V1 | AI-OS-V6-CLEAN-REBUILD-V1 | PASS |

## Mismatch Repair Tasks

No mixed frontend, backend, container, or route versions are allowed. `release_guard.py` blocks deployment unless frontend, backend, API, database schema, deployment, and runtime versions all equal `AI-OS-V6-CLEAN-REBUILD-V1`.
