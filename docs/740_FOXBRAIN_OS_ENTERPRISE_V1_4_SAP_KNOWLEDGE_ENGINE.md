# VAFOX Enterprise OS V1.4 SAP Knowledge Engine

## Objective

Continue from VAFOX Enterprise OS V1.0 to V1.3 without rebuilding the system. V1.4 focuses on SAP Knowledge Engine rather than new pages.

## Scope

- Read-only SAP sync layer.
- AI data warehouse as a downstream copy.
- Product knowledge model.
- Sales knowledge model.
- Inventory knowledge model.
- Member knowledge model.

## SAP Production Boundary

- Do not directly connect to modify the SAP production database.
- Do not write back to SAP.
- Do not change SAP production schema.
- SAP credentials remain on the server environment or secret store.
- AI reads downstream warehouse tables, snapshots or generated knowledge cards.

## APIs

- `/api/sap-knowledge-engine`
- `/api/sap-knowledge-engine/contract`
- `/api/sap-knowledge-engine/read-only-sync`
- `/api/sap-knowledge-engine/warehouse`
- `/api/sap-knowledge-engine/models`
- `/api/sap-knowledge-engine/models/product`
- `/api/sap-knowledge-engine/models/sales`
- `/api/sap-knowledge-engine/models/inventory`
- `/api/sap-knowledge-engine/models/member`

Compatibility aliases:

- `/api/knowledge/sap-engine`
- `/api/knowledge/sap-engine/warehouse`
- `/api/knowledge/sap-engine/models/{model}`

## Knowledge Models

Product model:
SKU, brand, category, season, price band, sales context and inventory context.

Sales model:
Sales amount, gross profit, margin, store, brand, product and period.

Inventory model:
On-hand, committed, available, average price, inventory amount, aging and risk level.

Member model:
Member ID, level, purchase history, preferences, points, last purchase and privacy boundary.

## Approval Rule

The engine can recommend, retrieve and explain. It must not write SAP or execute high-risk actions. Price, markdown, purchase, mass notification, export and SAP writeback decisions require human approval.
