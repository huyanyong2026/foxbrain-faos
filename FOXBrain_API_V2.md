# VAFOX Foundation V2.0 API Contract

## Gateway APIs

- Identity center: CEO, Employee, Store Manager, Procurement, Supplier, Customer.
- Token management for service-to-service access.
- Routing to Huyan, AI, and Core.
- Rate limiting, audit logging, and security middleware.
- Health router checks Huyan, AI, and Core before release.

## Core Business APIs

Core exposes read-only business APIs for AI, Huyan, Gateway, and future applications:

- Master data: Product, Brand, Store, Supplier, Customer, Employee, Event.
- Events: Sales, Inventory, Purchase, Customer, Task, Approval.
- Business summary and data-health endpoints.
- SAP mirror status endpoints.

## AI APIs

- Agent registry with name, purpose, permission, knowledge source, version, and status.
- Workspace actions: chat, analysis, task, query, report generation.
- Knowledge connection and memory review APIs.

## API Safety

- No generic SAP write endpoint is introduced.
- Sensitive data requires scoped tokens and audited permissions.
- Customer and supplier access must use ABAC ownership constraints.
