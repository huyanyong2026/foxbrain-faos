# VAFOX Enterprise OS V1.8 Workflow Automation Engine

V1.8 continues from V1.7 without rebuilding the system. It upgrades VAFOX from AI business analysis into AI workflow automation.

## Goal

AI discovers a problem, analyzes it, creates a task, notifies the responsible person, waits for human approval, tracks execution feedback and improves future advice.

## New Center

- Page: `/workflow-automation`
- API: `/api/workflow-automation`
- Run inventory risk workflow: `/api/workflow/run-inventory-risk`

## Workflow Builder

Supported node types:

- Start
- Condition
- AI Analysis
- Database Query
- Generate Report
- Send Notification
- Human Approval
- Execute Action
- End

## New Database Tables

- `workflows`
- `workflow_nodes`
- `task_logs`
- `approvals`
- `ai_memory`
- `decision_feedback`
- `business_cases`

Existing V1 tables reused:

- `tasks`
- `notifications`
- `ai_agents`

## Digital Employees

- AI General Manager
- AI Purchase Manager
- AI Sales Manager
- AI Content Operator

Every digital employee has responsibilities, tool scope, approval rules and performance metrics.

## Guardrails

- SAP production writeback remains disabled.
- AI can create tasks, notifications and approvals.
- High-risk execution waits for human approval.
- All workflow outputs are persisted.
- Mobile access uses the existing responsive portal layout.

