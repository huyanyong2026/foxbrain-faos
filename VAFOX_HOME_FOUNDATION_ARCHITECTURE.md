# VAFOX Outdoor LIFE Genesis — Phase 2 Home Foundation Architecture

Generated: 2026-07-17

## Executive intent

Phase 2 establishes the Home Foundation Architecture for the four active VAFOX foundation homes. This document is an architecture boundary only: it defines the intended home surfaces, ownership lines, API responsibilities, security posture, and migration constraints without starting large feature implementation.

Phase 2 must continue the Genesis stabilization rule: no Customer or Supplier expansion, no Community buildout, and no new broad agent construction until the foundation homes are reviewed and approved.

## Architecture principles

1. **One identity gateway, multiple operating homes**: all user entry begins at `gateway.vafox.com`, then routes to the correct home by verified identity, role, permission, and mission context.
2. **Mobile-first, desktop-capable**: every home must support a compact primary journey first, then expand into richer desktop panels only when screen space allows.
3. **Bounded domains**: Gateway, Workforce Home, CEO Home, and Core Data Hub keep separate responsibilities and communicate through explicit APIs.
4. **Readiness before expansion**: Phase 2 validates foundation navigation, health, security, and data-readiness contracts before any Customer/Supplier or large functional expansion.
5. **AI assists, humans decide**: AI Companion and AI Briefing surfaces can summarize, suggest, and guide, but approval authority remains with authenticated users and their role permissions.

## 1. `gateway.vafox.com` — Identity Center

### Mission

`gateway.vafox.com` is the Identity Center and trusted front door for VAFOX Outdoor LIFE Genesis. It owns authentication, verified identity resolution, and secure routing into the remaining foundation homes.

### Core responsibilities

- **VID**
  - Assign and resolve the VAFOX Identity ID as the stable cross-home identity key.
  - Bind VID to login credentials, employee profile, leadership profile, and system-service identity where applicable.
  - Prevent downstream homes from creating alternate identity roots.
- **One Login**
  - Provide a single login entry for all active foundation homes.
  - Manage session establishment, session refresh, logout, and step-up authentication triggers.
  - Preserve a consistent login and recovery experience across mobile and desktop.
- **Role resolution**
  - Resolve effective roles after authentication, including CEO, executive, employee, store, finance, growth, supply chain, data, governance, and administrator roles where already supported by the foundation.
  - Keep role resolution separate from page rendering so downstream homes consume a normalized role context.
  - Support multi-role users through explicit active-role selection or policy-driven default role routing.
- **Permission routing**
  - Convert identity and role context into routing decisions for `ai.vafox.com`, `huyan.vafox.com`, and `core.vafox.com`.
  - Route users only to homes and modules that match their effective permissions.
  - Deny access safely with clear guidance and audit events when a requested route is outside the user boundary.

### Phase 2 non-goals

- No new Customer or Supplier portal routing.
- No public community identity expansion.
- No replacement of existing foundation authentication internals unless required for stability.

## 2. `ai.vafox.com` — Workforce Home

### Mission

`ai.vafox.com` is the Workforce Home for employees and active internal operating roles. It organizes daily work, mission context, AI assistance, learning, and growth into one mobile-first employee operating surface.

### Home areas

- **Today**
  - Presents the user's current operating day: tasks, priorities, reminders, assigned work, alerts, and relevant status.
  - Prioritizes a short mobile summary before deeper desktop work queues.
- **Mission**
  - Connects daily work to VAFOX business objectives, store execution, supply-chain activity, finance follow-up, growth initiatives, or other active internal missions.
  - Shows what matters now, why it matters, and what completion means.
- **AI Companion**
  - Provides contextual help, summarization, next-step suggestions, and guided task support.
  - Uses the user's role and permission context from Gateway and does not bypass authority boundaries.
- **Learning**
  - Surfaces role-relevant learning, operating guides, onboarding content, and recommended skill development.
  - Keeps learning linked to current missions instead of becoming a disconnected content library.
- **Growth**
  - Shows personal development, performance-support prompts, capability progress, and next recommended growth actions.
  - Growth guidance must remain supportive and transparent, not opaque scoring or hidden evaluation.

### Phase 2 non-goals

- No Customer workspace.
- No Supplier workspace.
- No large new AI-agent feature set.

## 3. `huyan.vafox.com` — CEO Home

### Mission

`huyan.vafox.com` is the CEO Home for executive command, enterprise awareness, decision preparation, and strategic AI briefing. It must remain focused on leadership visibility and decision support, not operational page duplication.

### Home areas

- **Enterprise Today**
  - Summarizes enterprise status across core operating domains using approved data feeds and health indicators.
  - Prioritizes exception visibility and executive-level context.
- **Decisions**
  - Shows pending, recommended, or recently made decisions requiring CEO or executive attention.
  - Preserves traceability from decision prompt to supporting data and source systems.
- **Risks**
  - Highlights operational, financial, data, security, supply-chain, or execution risks within existing foundation scope.
  - Requires clear severity, owner, and next-action metadata.
- **Opportunities**
  - Identifies growth, efficiency, margin, product, store, or operational opportunities when supported by approved data.
  - Separates evidence-based opportunities from speculative AI suggestions.
- **AI Briefing**
  - Provides executive summaries, scenario framing, and follow-up questions.
  - Must cite or link back to source data, health status, or decision artifacts wherever possible.

### Phase 2 non-goals

- No CEO-only rebuild of employee workflows.
- No direct write access to Core data from briefing cards without governed APIs.
- No Customer/Supplier executive expansion tracks.

## 4. `core.vafox.com` — Enterprise Data Hub

### Mission

`core.vafox.com` is the Enterprise Data Hub for trusted data visibility, data-health monitoring, runtime status, and Digital Twin readiness. It is the foundation home for data confidence before broader business expansion.

### Home areas

- **Data health**
  - Shows source freshness, validation status, schema/contract health, exception counts, and data-quality warnings.
  - Provides role-safe visibility into data issues that affect downstream homes.
- **Runtime status**
  - Presents service health, version alignment, integration availability, and operational readiness for the four foundation domains.
  - Distinguishes local readiness, production readiness, and environment-blocked verification.
- **Digital Twin readiness**
  - Tracks whether entities, events, master data, synchronization, and governance conditions are ready to support Digital Twin workflows.
  - Marks readiness as staged and evidence-based; readiness labels must not imply a fully built Digital Twin before implementation approval.

### Phase 2 non-goals

- No uncontrolled data write surface.
- No new Customer/Supplier data products.
- No Digital Twin feature implementation beyond readiness architecture.

## 5. Mobile-first experience model

Phase 2 homes must share a consistent mobile-first model:

1. **Home summary first**: each home opens to the most important status, action, or briefing for the user.
2. **Three-level depth**: summary card, focused detail, and full workspace view.
3. **Thumb-safe actions**: primary actions must be reachable and clearly separated from destructive or approval actions.
4. **Role-aware navigation**: navigation options come from Gateway role and permission context, not hard-coded assumptions.
5. **Offline-tolerant messaging**: when data or runtime status is unavailable, the UI should explain the limitation and avoid false certainty.
6. **Consistent language**: use VAFOX Outdoor LIFE Genesis naming for foundation homes while retaining internal service names where needed for operations.

## 6. API boundaries

### Gateway APIs

- Own authentication, VID resolution, session state, role context, permission context, and route authorization.
- Expose normalized identity and authorization claims to approved foundation homes.
- Do not expose raw credential or sensitive authentication internals to downstream homes.

### Workforce Home APIs

- Consume identity, role, permission, task, mission, learning, and AI-assistance context through governed interfaces.
- Request AI Companion responses only within the authenticated user's permission boundary.
- Do not directly mutate enterprise source data without approved domain APIs.

### CEO Home APIs

- Consume executive summaries, risk indicators, decision artifacts, opportunity signals, runtime health, and approved AI briefing context.
- Require source traceability for briefing and decision data.
- Do not bypass Core governance for data access or write operations.

### Core Data Hub APIs

- Own data-health, runtime-status, readiness, lineage, validation, and data-governance APIs.
- Provide read-only or governed write access according to existing foundation permissions.
- Publish machine-readable readiness/status contracts for Gateway, Workforce Home, and CEO Home.

## 7. Security model

Phase 2 uses a layered security model:

- **Identity**: VID is the primary identity key; all homes trust Gateway-issued identity context.
- **Authentication**: One Login establishes the user session and supports step-up authentication for sensitive actions.
- **Authorization**: role resolution and permission routing are evaluated before a home or module is presented.
- **Least privilege**: homes receive only the claims and data needed for the current role and workflow.
- **Auditability**: login events, route decisions, denied access, decision actions, AI briefing generation, and data-health changes must be auditable.
- **AI boundary**: AI Companion and AI Briefing cannot expand user access, invent authority, or hide uncertainty.
- **Data protection**: Core data exposure is role-scoped, source-traceable, and separated from authentication secrets.
- **Operational resilience**: unavailable services must fail closed for protected routes and fail transparent for status displays.

## 8. Migration boundary

Phase 2 migration remains architecture-first:

- Keep existing foundation services intact while documenting the home architecture.
- Align future routing and UI work to the four homes only: Identity Center, Workforce Home, CEO Home, and Enterprise Data Hub.
- Preserve current Phase 1 stabilization constraints until reviewed.
- Do not introduce Customer, Supplier, or Community expansion.
- Do not build large new features, Digital Twin implementation, or broad new AI-agent capabilities in this phase.
- Future implementation work must be proposed as smaller reviewed increments after this architecture document is accepted.

## Review checklist

- [ ] `gateway.vafox.com` identity responsibilities are accepted.
- [ ] `ai.vafox.com` workforce home areas are accepted.
- [ ] `huyan.vafox.com` CEO home areas are accepted.
- [ ] `core.vafox.com` data hub responsibilities are accepted.
- [ ] Mobile-first model is accepted.
- [ ] API boundaries are accepted.
- [ ] Security model is accepted.
- [ ] Migration boundary confirms no Customer/Supplier expansion.
