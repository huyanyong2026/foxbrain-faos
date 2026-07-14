# VAFOX V7.1 Enterprise Kernel + MCP Runbook

## Scope

V7.1 establishes the enterprise kernel and MCP foundation without replacing existing business modules.

## Pages

- `/enterprise-kernel`: configuration, organization, RBAC, API gateway and event overview.
- `/mcp-gateway`: connector registry for future integrations.

## APIs

- `GET /api/v7.1/status`
- `GET /api/v7.1/kernel`
- `GET /api/v7.1/mcp/connectors`
- `GET /api/v7.1/events`
- `POST /api/v7.1/events`
- `GET /api/v7.1/observability`

## Tables

- `kernel_settings`
- `org_units`
- `mcp_connectors`
- `api_gateway_routes`
- `event_bus_events`
- `observability_metrics`

## Initial MCP Connectors

- SAP Business One
- PostgreSQL
- Redis
- Neo4j
- Qdrant
- MinIO
- Dify
- n8n
- Wiki.js

## Safety Rules

- Credentials must come from environment variables or a future secret store.
- Connectors are registered first; live external calls are added gradually.
- High-risk business operations still require approval.
- Existing functions must remain stable.

