# BA V2.0-C Employee AI Agent

## Goal
Create the employee digital assistant for Product Query, Inventory Query, Store Query, Procedure Query, and Knowledge Query.

## Response Contract
Every business answer must include Product, Store, Inventory or answer value, Data Source, and Update Time.

## Example
Question: `南山店 Osprey 26L库存？`

Response fields:
- Product: Osprey 26L
- Store: 南山店
- Inventory: Core read-only inventory result
- Data Source: `core.vafox.com`
- Update Time: Core snapshot time

## Agent Boundaries
The assistant recommends and explains. It does not write SAP or create duplicate business records.
