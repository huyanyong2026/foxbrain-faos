# VAFOX Enterprise Memory Permission Model

## Scope and compatibility

This change applies only to `services/memory` and the additive Memory Factory
schema migration.  It does not modify Dify, SAP, Core, or the Phase 1A startup
topology.  Phase 1B remains dependency-injected and opt-in.

## Data model

`memory_items` now records the following server-bound ACL fields:

| Field | Meaning |
| --- | --- |
| `organization_id` | Tenant boundary; every permission decision requires an exact match. |
| `department_id` | Department boundary for department-visible memories. |
| `owner_id` | Uploading authenticated user; private-memory owner. |
| `role_scope` | Server-derived upload scope retained for audit and indexing. |
| `visibility` | `private`, `department`, or `organization`. |

The same fields are copied to every Qdrant chunk payload and indexed as keyword
payload fields.  This makes vector search enforce the same tenant and audience
boundary as metadata and content reads.

## Trusted authorization flow

The gateway supplies `X-VAFOX-ORGANIZATION-ID`, `X-VAFOX-DEPARTMENT-ID`,
`X-VAFOX-USER-ID`, and `X-VAFOX-ROLE-SCOPE`.  The Memory API builds an
`AuthContext` only from those trusted headers; request body `owner`,
`organization_id`, `department_id`, `role_scope`, and `visibility` fields do
not grant or expand access.

On upload, the authenticated user is always bound as `owner_id`.  Visibility is
derived server-side: `admin` or `organization` scope becomes organization
visibility; `department` scope becomes department visibility; all other uploads
remain private.

## Access rules

1. A caller must be in the memory's organization.
2. The owner may access their memory.
3. A department user may access department-visible memory in the same department.
4. Any user in the organization may access organization-visible memory.
5. An `admin` scope may access all memory in its organization, but never another
   organization.

These checks protect memory metadata, binary content, deletion, re-indexing,
index job inspection, related-memory requests, and lexical search results.

## Retrieval enforcement

`AuthContext -> permission scope -> Qdrant filter` is mandatory.  The Qdrant
filter first requires `organization_id`; non-admin callers receive a `should`
filter limited to their own `owner_id`, same-department `department` visibility,
or organization visibility.  Client-supplied owner filters are ignored, so a
caller cannot request another owner's vectors.

## Verification

The automated tests cover User A and User B isolation, denied cross-owner GET,
server-bound upload ACL, organization/department rules, admin access in its
organization, and Qdrant permission-filter construction.
