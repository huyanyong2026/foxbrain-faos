# VAFOX Foundation V2.0 Security

## Identity Center

Supported role families:

- CEO
- Employee
- Store Manager
- Procurement
- Supplier
- Customer

## Permission Engine

VAFOX V2 uses both RBAC and ABAC.

### RBAC Examples

- CEO: full enterprise visibility.
- Procurement: supply chain, supplier, inventory, and purchase visibility.
- Store Manager: own-store data.
- Supplier: own-brand and supplier portal data.
- Customer: own account and own order data.

### ABAC Examples

- Store scope limits store managers to assigned stores.
- Brand scope limits suppliers to approved brands.
- Self scope limits customers and employees to their verified identity context.

## Audit and Middleware

- Authentication events are audited.
- Permission decisions are audited.
- API tokens are scoped by service and capability.
- Security middleware must reject mutating calls where the service is read-only.

## SAP Protection

AI and Huyan consume Core APIs. They do not write directly to SAP or bypass SAP accounting workflows.
