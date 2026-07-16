# AI Workspace V5 Test Plan

Required checks:

1. AI Router Test: `pytest tests/test_ai_workspace_v5_migration.py tests/test_ai_os_v5.py`
2. UI Legacy Detection Test: `python scripts/verify_ai_workspace_v5.py`
3. Data Link Test: verify automatic `core.vafox.com` evidence links.
4. Permission Test: verify `authorize_ai_context` remains required.
5. Task Workflow Test: verify auto task draft is pending human approval.
6. Deployment Test: GitHub Actions workflow `AI Workspace V5 Protection`.
