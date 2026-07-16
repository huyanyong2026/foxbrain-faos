# BA V2.0-C WeCom Architecture

## Mission
Upgrade Enterprise WeCom into the FoxBrain Employee AI Workspace without redesigning infrastructure, modifying SAP business logic, or duplicating business data.

## Target Flow
Employee → Enterprise WeCom → `gateway.vafox.com` → Employee AI Agent → Core Enterprise Data (`core.vafox.com`) → Business Agents (`ai.vafox.com`, `huyan.vafox.com`).

## Gateway Integration
- WeCom authentication recognizes employee, store manager, purchaser, and CEO identities.
- WeCom UserID maps to FoxBrain Identity, role permissions, and data scope.
- Gateway remains the entrance; SAP remains business truth; Core remains enterprise data; AI provides assistant and recommendation only.

## Acceptance
PASS when a WeCom user can be recognized, mapped to FoxBrain identity, and routed to role-safe AI capability.
