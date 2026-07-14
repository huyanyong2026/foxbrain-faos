# VAFOX OS 2.0 AI Orchestration

## Purpose

VAFOX OS 2.0 AI orchestration defines how Jarvis, AI CEO and specialist agents collaborate without creating conflicting answers or unsafe actions.

## Shared Context Contract

Every AI response should be built from a shared context object:

- `user_context`: role, store, permissions and current workspace.
- `business_context`: SAP metrics, store ranking, inventory risk and data freshness.
- `knowledge_context`: approved documents, SOPs, policies and citations.
- `memory_context`: approved decisions, preferences and historical management notes.
- `task_context`: pending work, approvals, automation status and follow-up items.
- `risk_context`: active risks, approval gates and blocked high-risk actions.
- `limitations`: missing data, stale sync status or unsupported action types.

## Agent Roles

- Jarvis: unified question and action entrance.
- AI CEO: daily management judgment, risk focus and executive recommendation.
- AI CFO: finance, profit, cash flow and payment review.
- AI Inventory Manager: stock, replenishment, transfer and markdown suggestions.
- AI Store Manager: store execution, staff follow-up and customer/member actions.
- AI Brand/Product Manager: brand growth, product portfolio and pricing risk.
- AI Operations Agent: workflow, automation, deployment and system health.

## Safety Rules

- AI can recommend but must not directly execute high-risk operations.
- Every recommendation must expose evidence, source type and limitation.
- Conflicting agent outputs should be escalated to AI CEO or human review.
- Actions that affect price, finance, contract, SAP write-back, bulk data or external publishing require approval.
- Generated reports and content remain drafts until reviewed.

## Implementation Direction

1. Build one context builder used by Jarvis, AI CEO and dashboards.
2. Standardize tool results with `success`, `data`, `sources`, `limitations` and `next_actions`.
3. Record AI-suggested actions as pending confirmations before execution.
4. Add tests for no-source behavior and high-risk action blocking.

