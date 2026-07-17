# VAFOX Identity Center Architecture

Version: Genesis-Construction-002  
Domain: `gateway.vafox.com`  
Purpose: one identity, one login, automatic routing into the correct VAFOX Home.

## 1. Foundation Rule

`gateway.vafox.com` is the only front door for VAFOX Outdoor LIFE identities. It must not replace SAP, bypass Core, or create a duplicate login surface inside Workforce Home, CEO Home, or future ecosystem homes.

Identity flow must preserve the enterprise chain:

```text
SAP
  ↓
Enterprise Data Hub
  ↓
Enterprise Digital Twin
  ↓
FoxBrain Intelligence Engine
  ↓
Mission Engine
  ↓
Home Experience
```

## 2. VID Model

A VID is the stable VAFOX identity key for a real person.

| Concept | Definition | Rule |
| --- | --- | --- |
| VID | Permanent VAFOX identity identifier | One person has one VID. |
| Relationship | A business relationship attached to the VID | One VID can have many relationships. |
| Role | Operational capability in a context | Roles are resolved after VID. |
| Home Route | The primary experience selected for the session | Route is derived from role, permission, and context. |

Example:

```text
VID-10086
  ├─ Employee
  ├─ Club Member
  ├─ Creator
  └─ Leader
```

The VID does not equal employee number, customer number, supplier number, mobile number, email, or SAP user. Those identifiers are credentials or relationship references linked to the VID.

## 3. Credential Model

Credentials prove control of an access channel; they do not define identity by themselves.

Supported credential categories:

- Mobile number / OTP.
- Email / magic link or passwordless sign-in.
- Enterprise SSO.
- WeCom or future enterprise social login.
- Hardware or passkey authentication when required.
- Service credential for system-to-system access, never used as a human VID.

Credential binding rules:

1. Each credential maps to exactly one VID after verification.
2. Multiple credentials may bind to the same VID.
3. Credential changes require audit logging and risk review.
4. Privileged roles require stronger authentication policy.
5. No downstream home may authenticate independently.

## 4. Role Model

Gateway resolves roles from enterprise relationships, not from UI choices.

Initial role families:

- Employee.
- Customer.
- Supplier.
- Brand Partner.
- Club Member.
- Leader.
- Creator.

Role resolution inputs:

- VID relationship records.
- HR / organization context from Core where available.
- Contract, partner, or membership status from Core.
- Runtime governance policy.
- Temporary mission delegation.

Role output:

```json
{
  "vid": "VID-10086",
  "roles": ["Employee", "Leader"],
  "primary_home": "ai.vafox.com",
  "eligible_homes": ["ai.vafox.com", "huyan.vafox.com"],
  "context_scope": ["org", "mission", "permission", "locale"]
}
```

## 5. Permission Model

Permissions are loaded after VID and role resolution. Gateway only brokers permission context; Core and runtime governance remain the authoritative enforcement layers for enterprise data access.

Permission dimensions:

- Identity permission: who the person is.
- Relationship permission: why the person is connected to VAFOX.
- Role permission: what the person may do.
- Data permission: which enterprise data can be seen.
- Mission permission: which actions can be created or approved.
- AI permission: what the AI Companion may retrieve, reason over, or draft.

Permission principles:

1. Default deny.
2. Least privilege.
3. Session-scoped permission snapshot.
4. Sensitive actions require approval workflow.
5. AI answers must cite allowed context and avoid leaking restricted data.

## 6. Login Flow

```text
User opens gateway.vafox.com
  ↓
Credential verification
  ↓
VID resolution
  ↓
Relationship and role resolution
  ↓
Permission snapshot loading
  ↓
Context loading from Core / Memory / Mission Engine
  ↓
Home route decision
  ↓
Session token issued
  ↓
User lands in the correct Home
```

Route examples:

| User context | Route |
| --- | --- |
| Employee | `ai.vafox.com` Workforce Home |
| Founder / CEO | `huyan.vafox.com` CEO Home |
| Future customer | Reserved Customer Home route |
| Future supplier | Reserved Supplier Home route |

## 7. Session Management

Gateway session responsibilities:

- Issue short-lived session tokens.
- Maintain refresh lifecycle.
- Attach VID, active role, permission version, and context version.
- Revoke sessions when credentials, roles, or permissions change.
- Record security events.
- Provide route handoff to homes without exposing raw credentials.

Session payload must avoid embedding full enterprise data. Homes request data through Core-backed APIs using the session permission snapshot.

## 8. Future Ecosystem Extension

Gateway reserves identity interfaces for:

- Customer Home.
- Supplier Home.
- Brand Home.
- Club Home.
- Community Home.

Extension interface contract:

```text
VID + Relationship + Role + Permission Snapshot + Context Scope → Home Route
```

No future home may introduce a separate identity silo. All ecosystem expansion must reuse VID, Gateway login, Core data boundaries, and runtime governance.
