# FoxBrain OS Enterprise V1.1 AI Knowledge Brain

V1.1 continues the Enterprise V1.0 architecture refactor. It does not rebuild the system. It integrates an AI Knowledge Brain module into the existing portal, SAP and knowledge-base workflows.

## Purpose

The AI Knowledge Brain connects:

- SAP data understanding.
- Enterprise knowledge base.
- SAP smart knowledge cards.
- Permission-aware retrieval.
- Query planning.
- Explainable and auditable AI answers.
- Human approval for high-risk actions.

## Delivered

- Module: `foxbrain_os/knowledge_brain.py`
- Page: `/knowledge/brain`
- API: `/api/knowledge/brain`
- API: `/api/knowledge/sap-understanding`
- API: `/api/knowledge/query-plan`
- Architecture registration: `knowledge_brain`

## SAP Data Understanding

The module evaluates whether SAP context is ready for AI reasoning:

- SAP freshness.
- Sales understanding.
- Inventory understanding.
- SAP knowledge card availability.
- Candidate coverage for brands, products, stores, employees, customers and suppliers.

When synced data is missing, the module reports limitations instead of inventing facts.

## Enterprise Knowledge Base

The module summarizes knowledge readiness:

- Total knowledge records.
- Knowledge chunks.
- Pending review count.
- Recent sources.
- Knowledge gaps.
- Retrieval flow.

## Guardrails

- SAP remains the source of truth.
- No SAP facts are invented.
- AI answers must cite SAP or knowledge sources.
- SAP writeback is disabled.
- High-risk actions require human approval.

## Next Stage

V1.2 should begin extracting the SAP and knowledge logic from `portal_v2.py` into service adapters while preserving all existing routes.

