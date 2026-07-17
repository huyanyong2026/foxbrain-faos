# VAFOX Genesis Legacy Governance Cleanup Report

Audit date: 2026-07-17
Scope: repository-only audit for legacy governance/test expectations after VAFOX Genesis migration.
Constraint: audit only; no product feature changes.

## A. Remaining legacy items

### 1. Legacy release names and version expectations

| Legacy item | File locations | Impact |
| --- | --- | --- |
| `AI-OS-V4.0` active in V4 architecture/design/runtime docs and code constants | `AI_OS_V4_ARCHITECTURE.md`, `AI_WORKFORCE_V4_DESIGN.md`, `DATA_ACTIVITY_V4.md`, `CORE_V4_DESIGN.md`, `GATEWAY_V4_DESIGN.md`, `HUYAN_V4_DESIGN.md`, `AI_OS_V4_RELEASE.md`, `AI_OS_V4_TEST.md`, `AI_OS_V4_VERSION_MANAGEMENT.md`, `AI_OS_V4_OBSERVABILITY.md`, `foxbrain_os/ai_os_v4.py`, `tests/test_ai_os_v4_observability.py` | Keeps V4 as an apparent valid release contract. Tests can continue to enforce pre-Genesis health/version payloads and observability metadata. |
| `AI-OS-V5` / `AI-OS-V5.0` / `AI-OS-V5.1` active in V5 release, architecture, runtime, and test material | `AI_OS_V5_ARCHITECTURE.md`, `AI_OS_V5_RELEASE.md`, `AI_OS_V5_RUNTIME_API.md`, `AI_OS_V5_SELF_VERIFY.md`, `AI_OS_V5_HEALTH_REPORT.md`, `AI_OS_V5_PRODUCTION_REPORT.md`, `AI_OS_V5_RUNTIME_REPORT.md`, `AI_OS_V5_USER_ACCEPTANCE.md`, `AI_WORKSPACE_V5_DESIGN.md`, `GATEWAY_V5_DESIGN.md`, `HUYAN_V5_DESIGN.md`, `release_guard.py`, `automation_health_check.py`, `foxbrain_os/ai_os_v5.py`, `tests/test_ai_os_v5.py`, `tests/test_ai_os_v5_runtime.py` | Creates mixed-version governance after Genesis. Release guards and tests may fail or pass against V5 instead of the Genesis baseline. |
| Prior audit explicitly records `FoxBrain Enterprise OS`, `AI-OS-V4.0`, and V5.1 test assertions | `TEST_GOVERNANCE_ALIGNMENT_REPORT.md` | Confirms legacy expectations existed in platform governance tests. This file is useful as evidence but should not be treated as a current acceptance target. |
| Deployment/runtime truth still warns that checked-in metadata can advertise `AI-OS-V5.1` | `PRODUCTION_RUNTIME_TRUTH_REPORT.md`, `deployment.json` | Production verification can report a stale pre-Genesis identity even when application code has changed. |

### 2. Legacy branding: old AI workspace and CEO agent names

| Legacy item | File locations | Impact |
| --- | --- | --- |
| `AI Workspace`, `AI Workforce`, `FoxBrain AI Workforce V5`, and `My AI Team` labels | `AI_WORKSPACE_V3_DESIGN.md`, `AI_WORKSPACE_V5_MIGRATION.md`, `AI_WORKSPACE_V5_DESIGN.md`, `AI_WORKSPACE_V6_DESIGN.md`, `AI_WORKFORCE_V2_GUIDE.md`, `AI_WORKFORCE_V4_DESIGN.md`, `UX_V2_PRODUCTION_REPORT.md`, `EXPERIENCE_V1_ARCHITECTURE.md`, `tests/test_ai_workspace_v5_migration.py`, `tests/test_ai_os_v4.py` | Keeps older workspace terminology in docs and tests. This can conflict with Genesis naming and can preserve legacy UI acceptance criteria. |
| `Huyan V2/V3/V4/V5`, `CEO Brain`, `CEO Agent`, and `CEO Autonomous Command Center` labels | `GATEWAY_V2_GUIDE.md`, `HUYAN_V3_DESIGN.md`, `HUYAN_V4_DESIGN.md`, `HUYAN_V5_DESIGN.md`, `HUYAN_V6_DESIGN.md`, `FOXBrain_OPERATION_V2.md`, `SPRINT015_5_VISIBLE_CEO_UI_TEST_REPORT.md`, `foxbrain_os/foundation_v2.py`, `foxbrain_os/multi_agent_system.py`, `foxbrain_os/enterprise_second_brain.py`, `foxbrain_os/knowledge_fusion.py`, `tests/test_foundation_v2.py`, `tests/test_ceo_strategy_snapshot.py`, `tests/v6_smoke_check.py` | Legacy CEO-facing surface names and agent names remain part of seed data, tests, and documentation. These may be compatibility labels, but they should be classified before cleanup. |
| Old multi-agent names including Supplier, Customer, Commerce, Member, Product, Inventory, Finance, HR, Marketing, Brand, Knowledge agents | `foxbrain_os/enterprise_second_brain.py`, `foxbrain_os/multi_agent_system.py`, `foxbrain_os/knowledge_fusion.py`, `tests/v6_smoke_check.py`, `UX_V3_TEST.md`, `AI_WORKFORCE_V2_GUIDE.md` | May reintroduce prohibited or pre-Genesis agent inventory expectations, especially where tests assert broad agent sets. |

### 3. Legacy observability expectations

| Legacy item | File locations | Impact |
| --- | --- | --- |
| V4 observability expects `/health/version` metadata with V4 release fields | `AI_OS_V4_OBSERVABILITY.md`, `AI_OS_V4_RUNTIME_GUIDE.md`, `AI_OS_V4_DEPLOYMENT_FLOW.md`, `AI_OS_V4_PRODUCTION_ACTIVATION.md`, `tests/test_ai_os_v4_observability.py` | Tests and runbooks can validate old payload shape/version instead of Genesis runtime identity. |
| V5 runtime checks expect `/health/runtime` or `/health/version` with V5 values | `AI_OS_V5_RUNTIME_API.md`, `AI_OS_V5_SELF_VERIFY.md`, `AI_OS_V5_VERIFICATION_GUIDE.md`, `tests/test_ai_os_v5_runtime.py` | Runtime verification may accept V5 identity and block Genesis version normalization. |
| Current release guards still use `AI-OS-V5.1` as the expected deployment/runtime governance version | `release_guard.py`, `automation_health_check.py`, `VERSION_GOVERNANCE.md`, `VERSION_ALIGNMENT_REPORT.md` | Deployment protection can enforce the wrong generation if Genesis has a new canonical release string. |
| Production reports describe health endpoints as blocked/unverified from this environment | `AI_OS_V4_HEALTH_REPORT.md`, `AI_OS_V5_HEALTH_REPORT.md`, `AI_OS_V5_RUNTIME_REPORT.md`, `V5_UI_RUNTIME_REPORT.md`, `PRODUCTION_RUNTIME_TRUTH_REPORT.md`, `PRODUCTION_FINAL_VERIFICATION_REPORT.md` | Legacy environment limitations are repeatedly documented; cleanup should separate real product failures from execution-environment network blocks. |

### 4. Gateway test environment issues

| Issue | File locations | Impact |
| --- | --- | --- |
| Gateway smoke tests require a local static server on port `4173` before running `node apps/gateway/smoke-test.cjs` | `GATEWAY_IMPLEMENTATION_REPORT.md`, `GENESIS_CONSTRUCTION_VALIDATION_REPORT.md`, `GENESIS_REMEDIATION_REPORT.md`, `apps/gateway/smoke-test.cjs` | Running the Gateway smoke test directly can fail with `ECONNREFUSED`; the required server setup should be standardized in test scripts/docs. |
| Production Gateway/Huyan/AI/Core health checks are blocked from this environment by proxy/tunnel restrictions | `GENESIS_PHASE1_STABILIZATION_REPORT.md`, `AI_OS_V5_HEALTH_REPORT.md`, `AI_OS_V5_RUNTIME_REPORT.md`, `V5_UI_RUNTIME_REPORT.md`, `PRODUCTION_FINAL_VERIFICATION_REPORT.md` | Production verification can remain `UNVERIFIED` even when local contracts pass. Reports should avoid marking production PASS from this environment alone. |
| Gateway identity tests require repository root on `PYTHONPATH` in some invocations | `GATEWAY_IMPLEMENTATION_REPORT.md`, `tests/test_gateway_identity_center.py` | Test commands without `PYTHONPATH=.` can fail due to import path setup rather than product behavior. |
| Gateway role routing still appears in legacy V2/V4/V5 docs | `GATEWAY_V2_GUIDE.md`, `GATEWAY_V4_DESIGN.md`, `GATEWAY_V5_DESIGN.md`, `GATEWAY_V6_DESIGN.md`, `tests/test_ai_os_v4.py`, `tests/test_ai_os_v5.py` | Mixed role-routing expectations can hide whether Genesis Gateway behavior is authoritative. |

## B. File locations by cleanup cluster

1. **Version/release governance:** `release_guard.py`, `automation_health_check.py`, `deployment.json`, `VERSION_GOVERNANCE.md`, `VERSION_ALIGNMENT_REPORT.md`, `PRODUCTION_RUNTIME_TRUTH_REPORT.md`, `tests/test_ai_os_v4_observability.py`, `tests/test_ai_os_v5_runtime.py`, `tests/test_ai_os_v5.py`.
2. **Legacy release documents:** `AI_OS_V4_*`, `AI_OS_V5_*`, `AI_WORKFORCE_V4_DESIGN.md`, `AI_WORKSPACE_V5_DESIGN.md`, `GATEWAY_V4_DESIGN.md`, `GATEWAY_V5_DESIGN.md`, `HUYAN_V4_DESIGN.md`, `HUYAN_V5_DESIGN.md`, `CORE_V4_DESIGN.md`, `AUTOMATION_ENGINE_V5.md`, `DATA_LINKING_V5.md`.
3. **Branding and agent inventory:** `AI_WORKSPACE_V3_DESIGN.md`, `AI_WORKSPACE_V5_MIGRATION.md`, `AI_WORKSPACE_V6_DESIGN.md`, `AI_WORKFORCE_V2_GUIDE.md`, `UX_V2_PRODUCTION_REPORT.md`, `foxbrain_os/foundation_v2.py`, `foxbrain_os/multi_agent_system.py`, `foxbrain_os/enterprise_second_brain.py`, `foxbrain_os/knowledge_fusion.py`, `tests/test_foundation_v2.py`, `tests/test_ceo_strategy_snapshot.py`, `tests/v6_smoke_check.py`.
4. **Observability and production verification:** `AI_OS_V4_OBSERVABILITY.md`, `AI_OS_V4_RUNTIME_GUIDE.md`, `AI_OS_V4_DEPLOYMENT_FLOW.md`, `AI_OS_V4_PRODUCTION_ACTIVATION.md`, `AI_OS_V5_RUNTIME_API.md`, `AI_OS_V5_SELF_VERIFY.md`, `AI_OS_V5_VERIFICATION_GUIDE.md`, `AI_OS_V5_HEALTH_REPORT.md`, `AI_OS_V5_RUNTIME_REPORT.md`, `V5_UI_RUNTIME_REPORT.md`, `PRODUCTION_FINAL_VERIFICATION_REPORT.md`.
5. **Gateway test setup:** `apps/gateway/smoke-test.cjs`, `GATEWAY_IMPLEMENTATION_REPORT.md`, `GENESIS_CONSTRUCTION_VALIDATION_REPORT.md`, `GENESIS_REMEDIATION_REPORT.md`, `tests/test_gateway_identity_center.py`.

## C. Impact summary

- **Highest governance risk:** V5.1 remains hard-coded in release guard, automation health check, and tests. This can make the repository enforce pre-Genesis runtime identity.
- **Highest test risk:** V4/V5 observability tests assert old versions and payload expectations. These can keep legacy health contracts alive even after Genesis migration.
- **Highest branding risk:** AI Workspace / AI Workforce and CEO Agent / CEO Brain labels appear across docs, tests, and seed data. Some may be historical documentation, but active tests and code should be reviewed first.
- **Highest environment risk:** Gateway and production checks have known setup/network constraints. Failures from missing local server, missing `PYTHONPATH`, or outbound proxy blocks should not be confused with product regressions.

## D. Recommended cleanup order

1. **Freeze this report for review.** Do not change product code until owners confirm the canonical Genesis release name, service names, and allowed compatibility labels.
2. **Classify files as active contract, historical record, or obsolete report.** Keep historical reports immutable where needed, but remove them from acceptance criteria.
3. **Normalize active runtime governance first.** Update active guards, deployment metadata generation, and runtime tests away from V4/V5 after the canonical Genesis version is approved.
4. **Replace active observability expectations.** Convert V4/V5 health/version tests to the Genesis runtime contract and mark old observability docs as archival.
5. **Clean active branding/test assertions.** Update tests and seed data that assert old AI workspace, CEO agent, or prohibited agent inventory names. Do not bulk-edit historical reports before active tests are clean.
6. **Standardize Gateway test commands.** Add or document a single smoke-test wrapper that starts the local server, sets required environment variables, and clearly labels production checks as network-dependent.
7. **Archive or relocate old release documents.** Move V4/V5 design and production verification reports into an archive area or add archival headers after active governance no longer depends on them.
