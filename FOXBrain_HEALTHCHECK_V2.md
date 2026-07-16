# VAFOX Foundation V2.0 Health Check

## Gateway

- Authentication: PASS when login/token validation works.
- Routing: PASS when Huyan, AI, and Core routes respond.
- Permission: PASS when RBAC and ABAC deny out-of-scope access.

## Huyan

- CEO Dashboard: PASS when sales, margin, inventory, supply risk, health, and AI recommendations load.
- Risk Radar: PASS when sales, inventory, supply, and operation risk categories are evaluated.
- Daily Briefing: PASS when summary, cause, and recommended actions are generated.

## AI

- Agent Registry: PASS when required agents and metadata are present.
- Workspace: PASS when chat, analysis, task, query, and report workflows are available.
- Knowledge and Memory: PASS when evidence, source tracking, feedback, and memory review are enforced.

## Core

- Master Data: PASS when Product, Brand, Store, Supplier, Customer, Employee, and Event models are exposed.
- Event Engine: PASS when Sales, Inventory, Purchase, Customer, Task, and Approval events are represented.
- Business API: PASS when Gateway, Huyan, and AI can consume approved APIs.

## Release Gate

Security, CI/CD, and rollback checks must pass before release.
