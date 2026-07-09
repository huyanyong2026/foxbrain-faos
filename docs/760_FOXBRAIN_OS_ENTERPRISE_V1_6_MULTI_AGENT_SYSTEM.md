# FoxBrain OS Enterprise V1.6 Multi-Agent System

## Goal

Continue from FoxBrain OS Enterprise V1.0-V1.5 without rebuilding the system. V1.6 adds a governed multi-agent collaboration layer so the CEO, business, inventory, product, member and content agents can share SAP Knowledge Engine context and work together.

## Scope

- New contract module: `foxbrain_os/multi_agent_system.py`
- Page route: `/agents/v1.6`
- Contract API: `/api/agents/v1.6`
- Shared SAP context API: `/api/agents/v1.6/shared-sap-knowledge`
- Collaboration plan API: `/api/agents/v1.6/collaboration-plan`

## Agent Roles

- CEO Agent: orchestrates objectives and consolidates agent findings.
- Business Agent: reviews sales, operating risks and task drafts.
- Inventory Agent: reviews stock risk, transfer drafts and replenishment drafts.
- Product Agent: maintains product knowledge, selling points and SKU context.
- Member Agent: reviews member segments, privacy boundaries and follow-up drafts.
- Content Agent: drafts content and publish requests from approved knowledge.

## Shared SAP Knowledge

All agents read the same governed SAP context:

- SAP Knowledge Engine
- AI data warehouse
- product, sales, inventory and member knowledge models
- knowledge quality score
- enterprise knowledge brain

SAP remains the source of truth. Agents read downstream SAP knowledge and must show limitations when SAP data is missing or stale.

No SAP writeback is allowed from V1.6 agent collaboration plans before explicit human approval.

## Approval Boundary

V1.6 does not execute high-risk work automatically. Collaboration requests create `ai_operation_plans` records with:

- `approval_status = pending_review`
- `execution_status = blocked_manual_required`
- `execution_mode = approval_then_execute`
- `risk_level = high`

High-risk actions such as SAP writeback, price changes, purchase orders, mass notifications and external publishing require human approval.
