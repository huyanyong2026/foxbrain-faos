# VAFOX Identity Model

Version: Genesis-Construction-003-1

## VID Structure

The VAFOX Identity ID (VID) is the permanent identity key for VAFOX Outdoor LIFE.

Format: `VID-VAFOX-{20 character HMAC digest}`.

Principles:

- One person has one VID.
- VID is permanent even when role, phone, WeChat, employee status, supplier status, or membership changes.
- Credential is not identity. Credential only proves or locates a VID.
- Gateway resolves credentials to VID and never creates a duplicate login system outside Core identity governance.

## Identity Lifecycle

1. Credential presented at `gateway.vafox.com`.
2. Gateway verifies the credential through approved identity providers or Core contracts.
3. Gateway resolves or creates the VID according to identity governance.
4. Roles, relationships, permissions, mission context, and memory pointers are loaded.
5. Gateway issues a short-lived session token and routes the person home.
6. Credential changes update mappings only; the VID remains unchanged.
7. Offboarding removes active permissions and sessions but preserves audit history and VID lineage.

## Role Relationship

A VID may hold multiple roles at the same time:

- Employee
- Customer
- Supplier Partner
- Brand Partner
- Club Member
- Leader
- Creator
- Administrator
- Founder / CEO

Roles are attributes of the VID. Roles can change without changing the VID.

## Credential Mapping

Supported credential classes:

- Mobile phone
- WeChat
- Enterprise WeChat
- ERP Employee ID
- Membership ID
- Supplier ID
- Brand ID

Each credential maps to one VID through verified matching. A credential cannot be treated as the source identity.

## Permission Mapping

Permissions are derived from VID + roles + relationships + mission context:

- Founder / CEO: enterprise read, decision approval, memory read, private home routing.
- Employee: mission read, workflow contribution, governed memory contribution.
- Administrator: identity read, permission validation, audit read, Core administration routing.
- Future roles: customer, supplier, brand, club, and creator home scopes.

Permission checks must run server-side before context or routing responses are returned.
