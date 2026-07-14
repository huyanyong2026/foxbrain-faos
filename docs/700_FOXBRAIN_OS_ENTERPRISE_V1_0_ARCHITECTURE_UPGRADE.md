# VAFOX Enterprise OS V1.0 Architecture Upgrade

This upgrade package moves VAFOX from page-level feature growth toward an enterprise AI operating system architecture.

## Current V6 Structure Check

The current system is stable but concentrated:

- `portal_v2.py`: one large compatibility portal containing routing, pages, database schema, APIs, AI flows, knowledge, SAP, approvals, digital workforce and platform payloads.
- `sync_sap_b1.py`: SAP B1 sync job and PostgreSQL snapshot writer.
- `tests/v6_smoke_check.py`: structural smoke tests for V6 packs and OS upgrades.
- `apps/api`, `apps/web`, `apps/worker`: target directories exist but are mostly placeholders.
- `docs/`: extensive product, architecture, runbook and task records.
- `docker-compose.yml`: production-oriented runtime for web, API, worker, PostgreSQL, Redis, MinIO, Qdrant and Nginx.

## Enterprise V1.0 Target

The target architecture is compatibility-first modularization:

- Kernel: identity, RBAC, module registry and global settings.
- Data: SAP DataHub, unified metrics, quality and lineage.
- Knowledge: ingestion, SAP smart knowledge, retrieval, citations and knowledge graph.
- AI: Jarvis, AI Operations, Digital Workforce and Enterprise Digital Brain.
- Governance: approvals, audit, security, API policies and risk gates.
- Platform: plugins, Integration Hub, developer docs and multi-company readiness.
- Operations: monitoring, jobs, backup, deployment and release gates.

## Refactor Rule

Do not delete existing capabilities. Existing routes and APIs stay compatible while services move behind stable contracts.

## Stage Plan

1. Stage 0: V6 structure audit.
2. Stage 1: Enterprise V1.0 architecture baseline.
3. Stage 2: Data and knowledge services extraction.
4. Stage 3: AI operations, approvals and digital workforce services extraction.
5. Stage 4: Platform monitoring, developer docs and release hardening.

## Safety

- SAP remains the core business system of record.
- High-risk operations require human approval.
- AI outputs must be explainable, traceable and auditable.
- Page changes alone are not sufficient; every stage must include architecture, docs and tests.

