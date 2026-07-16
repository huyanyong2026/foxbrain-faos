# AI OS V5 Verification Guide

1. Deploy Gateway, Huyan, AI, and Core.
2. Open each `/health/runtime` endpoint and confirm `version` is `AI-OS-V5` and `status` is `running`.
3. Run `python verify_runtime.py` from CI/CD or an operator workstation.
4. Admins can open `/internal/runtime-check` to view all services in one page.
5. Deployment passes only when Gateway, Huyan, AI, and Core all report PASS.
