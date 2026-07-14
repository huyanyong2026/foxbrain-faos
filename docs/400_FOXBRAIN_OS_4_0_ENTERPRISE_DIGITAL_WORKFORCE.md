# VAFOX OS 4.0 Enterprise Digital Workforce

## Purpose

VAFOX OS 4.0 builds the Enterprise Digital Workforce system on top of OS 1.0 release governance, OS 2.0 unified architecture and OS 3.0 AI Operations.

The goal is to turn AI agents into managed digital employees with clear roles, permission boundaries, tool scope, approval rules, audit logs and performance evaluation.

## Non-Negotiable Governance

Every AI digital employee must have:

- Role: business job, responsibilities and manager role.
- Permissions: role-based data and module scope.
- Tool scope: allowed tools, risk level and approval requirement.
- Approval rules: high-risk operations require human approval.
- Audit logs: agent runs, operation plans and activity logs remain traceable.
- Performance evaluation: quality, safety, completed tasks, feedback and blocked high-risk actions.

High-risk operations must retain human approval and must not auto execute.

## Core Routes and APIs

- `/digital-workforce`
- `GET /api/digital-workforce`
- `GET /api/digital-workforce/roles`
- `GET /api/digital-workforce/permissions`
- `GET /api/digital-workforce/tools`
- `GET /api/digital-workforce/approval-policy`
- `GET /api/digital-workforce/audit`
- `GET /api/digital-workforce/performance`
- `POST /api/digital-workforce/performance`

## Digital Employee Model

Digital employees reuse the existing `agent_roles` catalog and add:

- `digital_employee_id`
- `role_level`
- `approval_rule`
- `audit_policy`
- `performance_policy`
- `manager_role`

Performance records are stored in `digital_workforce_performance`.

## Safety Model

Digital employees may:

- Read permitted SAP summaries and business data.
- Search approved knowledge and memory.
- Draft reports, tasks, plans and recommendations.
- Request approval for higher-risk actions.
- Record feedback and performance results.

Digital employees may not:

- Write back to SAP automatically.
- Change prices, discounts or markdowns automatically.
- Execute finance payments automatically.
- Commit contracts automatically.
- Publish externally or mass-message customers automatically.
- Delete or bulk-change business data automatically.

## Performance Evaluation

Evaluation dimensions:

- Work output: planned tasks and completed tasks.
- Governance: approvals requested and high-risk actions blocked.
- Quality: manager review and quality score.
- Safety: safety score and policy compliance.
- Business feedback: feedback score and observed results.

Performance evaluation never grants business permissions automatically.

