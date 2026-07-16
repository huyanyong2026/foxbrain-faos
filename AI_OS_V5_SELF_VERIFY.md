# AI OS V5 Self Verification

Production verification flow: service runtime API → browser or verification script → PASS/FAIL confirmation.

Admin UI: `/internal/runtime-check` displays Gateway, Huyan, AI, and Core status as PASS when runtime metadata is available and version is `AI-OS-V5`.

Command-line verification:

```bash
python verify_runtime.py
```

Override endpoints with `GATEWAY_RUNTIME_URL`, `HUYAN_RUNTIME_URL`, `AI_RUNTIME_URL`, and `CORE_RUNTIME_URL`.
