# VAFOX Workforce Home Pilot Verification Report

Date: 2026-07-17  
Scope: First VAFOX Outdoor LIFE user space validation before expansion.  
Decision: **Pilot validation is conditionally blocked for live expansion until production SSO/mobile/role tests are completed with real Gateway sessions and test users. Do not start CEO Home expansion from this report alone.**

## A. Completed

### 1. Gateway SSO integration contract

| Check | Status | Evidence |
| --- | --- | --- |
| `gateway.vafox.com` is the identity front door | Completed in code contract | Gateway uses `GATEWAY_HOST = "gateway.vafox.com"` and issues a Gateway session cookie. |
| VID resolution exists before routing | Completed in code contract | Gateway resolves credentials into stable `VID-VAFOX-*` values before session creation. |
| Role-based route resolution exists | Completed in code contract | Employee role routes to `https://ai.vafox.com`; CEO routes to `https://huyan.vafox.com`; Admin routes to `https://core.vafox.com`. |
| AI Home redirects unauthenticated users to Gateway | Completed in code contract | AI app redirects missing sessions to `GATEWAY_LOGIN_URL`, defaulting to `https://gateway.vafox.com/login`. |
| Local login remains bypassed for user entry | Completed in current home flow | `/home` requires `ai.use` and `login_required` sends unauthenticated web users to Gateway. |

Verified intended chain:

```text
gateway.vafox.com
↓ Gateway login / session cookie / VID context
VID
↓ role route: employee → ai.vafox.com
ai.vafox.com Workforce Home
```

### 2. Workforce Home content

| Required content | Status | Evidence |
| --- | --- | --- |
| My Identity | Completed | Dashboard renders VID, role, department, store, team, and growth context. |
| Enterprise Today | Completed | Dashboard renders headline, enterprise events, Core/SAP status, and mobile performance note. |
| My Mission | Completed | Dashboard renders mission title, priority, reason, expected result, and execution steps. |
| Growth Profile | Completed | Dashboard renders learning, skills, contribution, completed task, and experience signals. |
| Ask AI | Completed | Dashboard embeds Ask AI form posting to `/ops-api/runs` with CSRF and no manual agent/source/object selector. |

### 3. Mobile experience

| Device class | Status | Evidence |
| --- | --- | --- |
| iPhone-width layouts | Code-level completed; live device verification missing | Responsive CSS collapses Workforce Home flow to one column below `780px`, uses grid actions, and preserves identity readability. |
| Android-width layouts | Code-level completed; live device verification missing | Same responsive rules cover common Android phone widths; no platform-specific browser evidence was captured in this environment. |
| Mobile first-screen intent | Completed in design/code | Hero and first card expose identity, mission entry, and Ask AI entry before deeper management content. |

### 4. Permission: Employee, Manager, Admin

| Role | Status | Evidence |
| --- | --- | --- |
| Employee | Completed in route contract | Gateway employee role routes to `https://ai.vafox.com`; AI Home requires `ai.use`. |
| Manager | Partially completed | Workforce mission logic recognizes `management` as a pilot/management role, but Gateway currently aliases `management` into the employee route profile rather than a distinct Manager permission profile. |
| Admin | Completed for identity/admin surfaces; not a Workforce Home pilot default | Gateway admin role routes to `https://core.vafox.com`; AI admin links render only with `identity.view` or wildcard permission. |
| Permission enforcement | Completed in AI app | AI routes use `permission_required`; denied permissions are audited. |

### 5. AI context

| Required AI context | Status | Evidence |
| --- | --- | --- |
| User identity | Completed | `/ops-api/runs` stores `permission_context["identity"]` in `context_json`. |
| Role | Completed through identity context | AI context uses `authorize_ai_context(user["identity"], ...)`, and identity context includes role data. |
| Permission | Completed | `authorize_ai_context` derives allowed AI context from the current identity permission snapshot before run creation. |
| Enterprise context | Completed | AI run context stores selected business objects, selected agents, required Core data sources, route evidence, and read-only Core access. |

## B. Issues

1. **Live SSO validation is not complete.** The repository verifies the Gateway identity/routing contract, but no real `gateway.vafox.com → VID → ai.vafox.com` browser session evidence was captured in this run.
2. **Manager is not a separate Gateway role profile.** `management` is accepted as an employee alias and later treated as management by Workforce Home mission logic, but the Gateway public role contract does not currently expose a first-class `manager` profile with explicit manager permissions.
3. **Admin is routed to Core by Gateway, not Workforce Home by default.** This may be correct for operations, but the pilot checklist asks for Admin permission verification in the Workforce Home context; that requires a defined admin test path into `ai.vafox.com` or a clear decision that Admin validates via Core only.
4. **AI context does not add a separate top-level `permission` field in `ai_agent_runs.context_json`.** Permission is present inside the authorized identity context; if downstream audit tooling expects a top-level `permission` or `permissions` key, that contract should be normalized before rollout.
5. **Live mobile proof is missing.** CSS and prior mobile reports support mobile readiness, but no fresh iPhone Safari or Android Chrome screenshots were generated in this environment.

## C. Missing data

- Production or staging Gateway test credentials for Employee, Manager, and Admin.
- Expected Manager permission set and whether Manager should route to `ai.vafox.com`, `core.vafox.com`, or both.
- Production SSO cookie/domain handoff evidence between `gateway.vafox.com` and `ai.vafox.com`.
- Real enterprise context payload expected from Core during the first pilot day.
- Real mobile device/browser screenshots or device-lab recordings for iPhone and Android.
- Acceptance owner for the final pilot gate.

## D. User experience problems

1. **Manager identity may be confusing.** A manager can enter through the employee route contract while seeing management-style mission content; the role label/permission model should be explicit before expanding.
2. **Admin journey is ambiguous.** Admin users route to Core, but the pilot asks to verify Admin against Workforce Home. This could create inconsistent expectations during UAT.
3. **Growth Profile is present but mostly descriptive.** The current profile explains learning/task/experience/skill/contribution signals, but real personal progress values are not yet populated.
4. **Ask AI context is invisible to the user.** The UI says permission and Core context are checked automatically, but it does not expose a concise “AI used your VID / role / permission / Core context” confirmation after submission.
5. **Pilot scope warning appears only for CEO/wildcard users.** Employee testers may not see enough indication that this is a limited pilot and not a full employee rollout.

## E. Next recommendations

1. **Do not start CEO Home expansion yet.** First complete live Workforce Home pilot validation with real Employee, Manager, and Admin identities.
2. **Create a first-class Manager contract.** Define Gateway role key, route, permissions, and AI data scope for Manager instead of relying on an employee alias.
3. **Run live SSO checks.** Capture evidence for `gateway.vafox.com` login, VID resolution, route handoff, and authenticated `ai.vafox.com/home` access.
4. **Run role-based UAT.** Validate Employee, Manager, and Admin journeys with expected allowed/denied pages and permission audit entries.
5. **Capture mobile screenshots.** Use iPhone Safari and Android Chrome, or Playwright device emulation if physical devices are not available.
6. **Normalize AI audit context.** If audit consumers require it, add explicit top-level `role`, `permissions`, and `enterprise_context` fields to AI run context in a later implementation task after pilot validation requirements are accepted.
7. **Keep SAP/Core untouched.** Continue using read-only Core retrieval and session permission snapshots for all AI answers.

## Pilot gate conclusion

**Status: BLOCKED FOR EXPANSION / READY FOR LIVE PILOT TESTING.**

The codebase contains the required Workforce Home surface, Gateway identity contract, permission checks, and governed AI context path. However, live SSO, device, and role-based production/staging evidence is missing. CEO Home work must remain on hold until those pilot validation checks pass with dated evidence.
