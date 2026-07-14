# VAFOX Enterprise OS V1.2 Agent Orchestration

## Objective

Continue from VAFOX Enterprise OS V1.0 and V1.1 without rebuilding the system and without refactoring the database. V1.2 adds a governed AI agent orchestration layer on top of the existing Agent framework, SAP understanding and enterprise knowledge brain.

## Scope

- Business Operations Agent for operating review, sales, profit, task and risk analysis.
- Inventory Agent for stock pressure, brand/product inventory and purchasing support.
- Member Growth Agent for membership segments, follow-up planning and privacy-aware customer work.
- Content Agent for brand-safe draft content, campaign support and knowledge-based material generation.

## Architecture

- Contract module: `foxbrain_os/agent_orchestration.py`
- Portal page: `/agents/v1.2`
- Contract API: `/api/agents/v1.2`
- Domain APIs:
  - `/api/agents/v1.2/business`
  - `/api/agents/v1.2/inventory`
  - `/api/agents/v1.2/membership`
  - `/api/agents/v1.2/content`
- Plan request API: `/api/agents/v1.2/plan`
- Existing approval storage: `ai_operation_plans`

## Approval Rule

All AI execution requests must enter the approval flow first. V1.2 does not let AI agents execute tools directly.

Default plan state:

- `approval_required = 1`
- `approval_status = pending_review`
- `execution_mode = approval_then_execute`
- `execution_status = blocked_manual_required`
- `risk_level = high`

## Data Rule

SAP B1 remains the core business data source. Agents may reference SAP understanding and enterprise knowledge, but SAP writeback is disabled unless a future explicitly approved business rule allows it.

## Compatibility

V1.2 reuses existing tables, pages and approval services. It does not remove existing Agent, Digital Workforce, AI Operations, Knowledge Brain or Enterprise AI Platform capabilities.
