# VAFOX OS 6.1 SAP Smart Knowledge Base

VAFOX OS 6.1 upgrades the knowledge base so SAP and synced business data can be turned into AI-queryable knowledge cards.

## Goal

- Enrich the knowledge base from SAP-synced data.
- Match and generate knowledge for brands, products, stores, employees, customers and suppliers.
- Keep every generated item traceable to its source table and source key.
- Make generated knowledge searchable by Jarvis, AI Query and future agents.
- Keep SAP as the core business data source.

## Implemented Surface

- Page: `/knowledge/sap`
- API: `/api/knowledge/sap-intelligence`
- API: `/api/knowledge/sap-mappings`
- API: `/api/knowledge/sap-snapshots`
- API: `POST /api/knowledge/sap-generate`
- Compatibility API: `/api/sap/knowledge-snapshot`

## Safety

The 6.1 knowledge upgrade is read-only. It generates knowledge records from synced data and never writes back to SAP.

High-risk operations, including SAP writeback, external publication, finance changes, pricing changes and permission expansion, still require human approval.

## Generated Knowledge Card

Each SAP knowledge card includes:

- Source table.
- Entity type.
- Entity key.
- Display name.
- Selected business fields.
- Summary.
- Tags and keywords.
- Knowledge chunks.
- Source snapshot.
- Audit log entry.

## Page Intelligence

The knowledge page now has a clear SAP knowledge entry. The home page remains minimal; detailed knowledge hierarchy appears only after entering the knowledge section.

