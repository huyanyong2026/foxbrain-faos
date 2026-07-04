# 27 Multi-Agent Collaboration / 多智能体协同

## 目标

Multi-Agent Collaboration Engine 让 FoxBrain 的 AI 智能体以企业角色方式协同工作。AI CEO 接收问题后，可以把子问题分配给 CFO、库存经理、品牌经理、研究员、门店经理等角色，再由 AI CEO 汇总，并交给人审核。

当前版本是协同框架，不做无监督自主执行。

## 页面与 API

- `/agents/collaboration`
- `GET /api/agents/collaboration`
- `GET /api/agents/roles`
- `POST /api/agents/roles`
- `GET /api/agents/tasks`
- `POST /api/agents/tasks`
- `POST /api/agents/tasks/{id}/approve`
- `POST /api/agents/tasks/{id}/reject`
- `GET /api/agents/discussions`
- `POST /api/agents/discussions`
- `GET /api/agents/tools`
- `POST /api/agents/tools`
- `POST /api/agents/scenarios/osprey-pricing`

## Default Agents

- AI CEO
- AI CFO
- AI COO
- AI Store Manager
- AI Brand Manager
- AI Inventory Manager
- AI Purchasing Manager
- AI Marketing Manager
- AI Training Manager
- AI Customer Service
- AI Secretary
- AI Risk Officer

## Agent Output Standard

Every agent recommendation should include:

- Summary
- Evidence
- Assumptions
- Risks
- Recommended action
- Confidence
- Related objects
- Need human decision
- Next task suggestion

If data is missing, the agent must say: 缺少数据，无法得出结论。

## Human Approval Gate

Any agent action that changes business state must require human approval:

- Create task assigned to employee
- Approve external knowledge
- Change memory
- Change pricing rule
- Create workflow approval
- Send notification
- Generate official report
- Publish content

## Osprey Scenario

The Osprey pricing scenario is a template only. It does not create real business conclusions unless supported by actual data and human review.
