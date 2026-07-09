# FoxBrain OS 2.0 Master Upgrade

## Positioning

FoxBrain OS 2.0 is the compatibility-first upgrade target for the current FoxBrain system. It absorbs the V5 progress package and the Pack 18 to Pack 20 foundation, then turns them into one maintainable operating system plan.

The upgrade must not delete existing capabilities. All changes should preserve current login, permissions, SAP sync, knowledge, Jarvis, dashboard, automation, memory, reporting, growth, command center, deployment and backup behavior unless a replacement has been reviewed, tested and documented.

## Primary Goals

1. Unified architecture: reduce scattered duplicate logic, clarify module boundaries, and move toward shared services without big-bang rewrites.
2. Maintainability: keep the current portal stable while gradually extracting data, AI, workflow, permission and UI contracts into reusable layers.
3. AI collaboration: make Jarvis, AI CEO, specialist agents and command workflows share the same context, evidence, tool policy, audit trail and approval rules.
4. Unified data service: treat SAP B1, local archives, documents, knowledge, memory, tasks and reports as governed data sources exposed through stable APIs.
5. Production stability: every upgrade must keep health checks, backup, rollback, deployment notes and smoke tests current.
6. Evidence-based management: dashboards and AI recommendations must cite SAP records, documents, knowledge, memory or workflow data instead of inventing business facts.

## Compatibility Rules

- Preserve existing routes and APIs whenever possible.
- New APIs should be additive; old endpoints should return compatible payloads.
- High-risk actions such as SAP write-back, price changes, finance operations, bulk changes and external publishing remain blocked until explicit approval gates exist.
- If a feature is not fully wired to real data, the UI and API must say so clearly and expose the missing dependency.
- Any refactor touching shared behavior needs a smoke test and an architecture note.

## Target Architecture

```text
User / Mobile / Role Desktop
  -> Portal Shell and Command Center
  -> Jarvis and AI Agent Orchestration
  -> Unified Data Service
  -> SAP B1 / Archives / Knowledge / Memory / Tasks / Reports / External Research
  -> Governance: RBAC, audit, approvals, backup, observability
```

## Upgrade Tracks

### Track A: Architecture Integration

- Identify duplicate page/API definitions and converge them carefully.
- Introduce service-style helpers for data, permissions, AI context, audit and rendering.
- Keep single-file compatibility while preparing safe modular extraction.

### Track B: Unified Data Service

- Make SAP B1 synced tables queryable through stable read-only APIs.
- Normalize business metrics for sales, gross profit, inventory risk, store ranking and customer/member data.
- Add data freshness, source lineage and quality warnings to every management payload.

### Track C: AI Collaboration

- Connect Jarvis, AI CEO and specialist agents to the same context builder.
- Require cited sources and limitations in all AI management answers.
- Route suggested actions through human confirmation and audit logs.

### Track D: Command Center and Growth Engine

- Preserve Pack 18 Growth Engine and Pack 19 Executive Command Center as management surfaces.
- Connect growth scorecards, risk center, AI command and system health to real data services over time.

### Track E: Production Stability

- Maintain deployment runbooks, rollback steps, backup policy and health checks.
- Add smoke tests for critical routes, data contracts and 2.0 governance documents.
- Produce architecture review notes after each major upgrade batch.

## Delivery Cadence

Every 2.0 implementation batch should produce:

- Code changes that are backward compatible.
- Documentation updates under `docs/`.
- Smoke or contract tests under `tests/`.
- Architecture review notes covering risks, compatibility and rollback.
- A short release note explaining what changed and what remains limited.

## Non-Goals

- Do not rewrite the entire system from scratch.
- Do not remove current modules just because they are imperfect.
- Do not enable SAP write-back or external publishing without explicit approval controls.
- Do not let AI answers present unsourced assumptions as business facts.

