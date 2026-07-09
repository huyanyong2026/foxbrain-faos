# FoxBrain OS 6.0 Enterprise AI Platform

FoxBrain OS 6.0 builds the Enterprise AI Platform on top of OS 1.0 to OS 5.0. It keeps the existing portal, SAP sync, Jarvis, AI Operations, Digital Workforce and Enterprise Digital Brain stable, then adds a platform layer for plugins, integrations, API governance, multi-company and multi-brand readiness, developer documentation and monitoring.

## Platform Scope

- Plugin system: governed plugin registry, SDK contracts, marketplace lifecycle and permission declarations.
- Integration Hub: unified connector registry for SAP B1, PostgreSQL, Redis, MinIO, Qdrant, Dify, n8n, Wiki.js and future services.
- API governance: route registry, policy registry, authentication, rate limit, audit and backward compatibility rules.
- Multi-company and multi-brand readiness: tenant registry, company scope, brand scope and SAP read-only data boundaries.
- Developer documentation: extension standards, API standards and platform entrypoints.
- Platform monitoring: health, SAP sync status, observability metrics, approval queue and audit visibility.

## Non-Negotiable Rules

- SAP B1 remains the core business data source.
- High-risk platform operations require human approval.
- Plugins cannot auto execute SAP writeback, external publishing, finance, pricing, contract or tenant data changes.
- AI recommendations must stay explainable, traceable and auditable.
- New platform APIs are additive and must not remove existing capabilities.

## Routes and APIs

- Page: `/enterprise-ai-platform`
- Page alias: `/integration-hub`
- Page alias: `/developer-platform`
- Page alias: `/platform-monitoring`
- API: `/api/enterprise-ai-platform`
- API: `/api/enterprise-ai-platform/plugins`
- API: `/api/enterprise-ai-platform/integration-hub`
- API: `/api/enterprise-ai-platform/api-governance`
- API: `/api/enterprise-ai-platform/tenants`
- API: `/api/enterprise-ai-platform/developer-docs`
- API: `/api/enterprise-ai-platform/monitoring`

## Home Page Rule

The public portal home should stay minimal. It should show only the main entrances. Business detail, platform hierarchy, SAP detail, AI governance detail and operational drill-downs belong inside the target pages after the user clicks in.

