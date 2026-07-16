# BA-V2.0-D Store Security

Status: PASS

Store AI maintains RBAC, ABAC, and audit log behavior.

## Roles

- CEO: all stores.
- Regional Manager: assigned regions and stores.
- Store Manager: own store.
- Employee: authorized store data.

## Enforcement

`StoreAIContext` carries roles, permissions, stores, and regions. `authorize_store_ai` records permission checks with actor, action, permission, resource store, decision, reason, time, and source.
