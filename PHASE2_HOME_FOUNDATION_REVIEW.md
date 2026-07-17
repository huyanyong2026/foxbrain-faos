# Phase 2 Home Foundation Review

Version: Genesis-Construction-002  
Scope: VAFOX Home Foundation architecture for `gateway.vafox.com`, `core.vafox.com`, `ai.vafox.com`, and `huyan.vafox.com`.

## 1. Validation Checks

### Consistency Check

Passed at architecture level.

- All Homes use one Gateway identity model.
- All enterprise data access flows through Core.
- All AI reasoning depends on FoxBrain Intelligence Engine and permission-filtered context.
- Mission Engine remains the bridge between intelligence and action.
- Mobile Home replaces dashboard-first interaction.

### Dependency Check

Passed at architecture level.

Required dependency order:

```text
Gateway Identity
  ↓
Core Data Hub
  ↓
Digital Twin / FoxBrain Context
  ↓
Mission Engine
  ↓
Workforce Home / CEO Home
```

No architecture document introduces a dependency that bypasses SAP, Core, Gateway, Permission, Workflow, Memory, Automation, or Runtime Governance AI-OS-V5.1.

### Route Check

Passed at architecture level.

Defined routes:

| Domain | Role in foundation |
| --- | --- |
| `gateway.vafox.com` | Identity Center and automatic Home routing |
| `core.vafox.com` | Enterprise Data Hub and nervous system |
| `ai.vafox.com` | Workforce Home |
| `huyan.vafox.com` | CEO Home |

Reserved future routes:

- Customer Home.
- Supplier Home.
- Brand Home.
- Club Home.
- Community Home.

### Architecture Review

Passed with open questions.

The package defines Home Foundation architecture only. It does not implement large features, dashboards, ERP portals, duplicate login, direct SAP writes, or isolated applications.

## 2. A. Completed Architecture

Completed deliverables:

- `IDENTITY_ARCHITECTURE.md` for Gateway Identity Center.
- `CORE_DATA_HUB_ARCHITECTURE.md` for Core Data Hub.
- `WORKFORCE_HOME_ARCHITECTURE.md` for Workforce Home.
- `CEO_HOME_ARCHITECTURE.md` for CEO Home.
- `MOBILE_HOME_EXPERIENCE.md` for mobile-first Home rules.
- `VAFOX_DESIGN_LANGUAGE.md` for unified VAFOX / 火狐狸 design language.
- `PHASE2_HOME_FOUNDATION_REVIEW.md` for validation and next-step review.

## 3. B. Open Questions

1. What is the authoritative VID issuing service: existing identity table, new Gateway identity service, or migration from current login users?
2. Which enterprise SSO and WeCom identity bindings are required first?
3. What are the exact freshness thresholds by entity type: order, inventory, finance, HR, mission, and risk?
4. Which CEO metrics are approved for the first read-only Enterprise Today briefing?
5. What audit retention and data classification policy should apply to AI answers and mission drafts?
6. Which roles are launch roles for Phase 3: Employee only, Employee + Leader, or Employee + CEO?

## 4. C. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Duplicate login appears in a Home | Identity fragmentation | Enforce Gateway-only authentication. |
| Home queries raw SAP or source data | Foundation bypass | Require Core API boundary for all enterprise context. |
| AI overexposes restricted data | Security breach | Enforce VID, role, permission snapshot, and field-level masking. |
| Dashboard patterns return | Product confusion | Use Home / Today / Mission architecture as acceptance criteria. |
| Freshness is invisible | Bad decisions | Attach freshness metadata to Core and AI responses. |
| Future ecosystem expands too early | Platform instability | Reserve interfaces only until Home Foundation is stable. |

## 5. D. Recommended Implementation Order

1. Gateway VID and session contract.
2. Core context API boundary and freshness metadata.
3. Permission snapshot integration across Gateway, Core, and AI.
4. Workforce Home first-screen read-only prototype.
5. AI Companion read-only question flow through Core.
6. CEO Home read-only Enterprise Today briefing.
7. Mission creation drafts with workflow approval.
8. Future ecosystem route interface definitions.

## 6. E. Next Construction Package

Recommended next package: `Genesis-Construction-003: Home Foundation Contracts`.

Suggested scope:

- Define VID schema and session token claims.
- Define Gateway route resolution contract.
- Define Core context API request / response envelopes.
- Define permission snapshot format.
- Define freshness metadata standard.
- Define AI Companion read-only retrieval contract.
- Define Workforce Home and CEO Home first-screen wire contracts.

Out of scope for the next package:

- SAP production writes.
- Customer / Supplier / Brand / Club / Community Home implementation.
- Large dashboard features.
- Autonomous business execution without workflow approval.
