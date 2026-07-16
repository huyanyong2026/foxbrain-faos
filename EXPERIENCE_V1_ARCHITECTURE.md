# FoxBrain Experience Upgrade V1.0 Architecture

## Mission
Upgrade FoxBrain from multiple applications into one enterprise operating system experience without rebuilding the existing Foundation V2 services or duplicating SAP/data logic.

## Foundation Reuse
- Gateway V2 remains the unified identity, permission, and portal entry.
- Huyan V2 remains the CEO operating surface.
- AI Platform V2 remains the digital employee and agent platform.
- Core V2 remains the enterprise data platform and read-only SAP mirror UI/API layer.

## Target Flow
Users authenticate at `gateway.vafox.com`, pass through identity and permission checks, and are routed to role-specific operating workspaces:

- CEO → `huyan.vafox.com`
- Employee / Supplier / Customer → `ai.vafox.com`
- Procurement → Supply Chain Workspace
- Store Manager → Store Intelligence
- Data and governance workflows → `core.vafox.com`

## Implemented Experience Routes
- `/experience`, `/portal-v2`, `/gateway-v2`: FoxBrain Portal V2.
- `/huyan-v2`, `/ceo-os-v2`: CEO Operating System V2.
- `/ai-workforce-v2`, `/digital-employee`: AI Workforce OS V2.
- `/core-v2`, `/data-platform-v2`: Enterprise Data Platform UI V2.
- `/design-system-v1`, `/design-system`: FoxBrain Design System V1.

## Acceptance Summary
Gateway, unified login, smart routing, CEO dashboard, risk radar, decision center, agent center, task center, knowledge center, master data, event center, data governance, deployment, health, and rollback are represented as V1.0 operating surfaces while preserving foundation boundaries.
