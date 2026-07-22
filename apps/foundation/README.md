# FoxBrain V1 Foundation — Sprint 1

`apps/foundation/app.py` exposes the first protected service boundary:

- **Identity:** human, AI employee, and system identity contexts; the canonical roles are CEO, Manager, Store Manager, Employee, Buyer, and Product Manager.
- **Gateway:** `POST /gateway/v1/login` issues a signed bearer token, session identifier, context, and role-directed destination (CEO → Huyan, Employee → AI, System → Control).
- **Core:** `GET /core/v1/{product|sales|inventory|store}` is token- and RBAC-protected and declares SAP-mirror, read-only lineage. There are deliberately no SAP credentials, mutating endpoints, or generic SQL endpoints.
- **Runtime:** `POST /runtime/v1/query` performs identity extraction, permission checks, read-only knowledge routing, citation generation, and append-only audit recording.

Run locally:

```bash
FOXBRAIN_TOKEN_SECRET=replace-me POSTGRES_PASSWORD=replace-me docker compose -f docker-compose.sprint1.yml up --build
```

The development seed credentials are `ceo` / `change-me`, `employee` / `change-me`, and `system` / `change-me`; replace the in-memory seed repository with a PostgreSQL/IdP implementation before production.
