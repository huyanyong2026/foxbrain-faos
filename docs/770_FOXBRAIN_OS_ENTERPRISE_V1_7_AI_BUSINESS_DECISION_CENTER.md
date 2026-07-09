# FoxBrain OS Enterprise V1.7 AI Business Decision Center

V1.7 continues from V1.6.6 without rebuilding the system. It upgrades FoxBrain from an AI knowledge assistant into an AI business management system.

## Scope

- AI Business Center page: `/ai-business-center`
- Daily AI business report: `/api/decision/today`
- Sales forecast: `/api/forecast/sales`
- AI Inventory Manager: `/api/inventory/risk`
- AI Purchase Manager: `/api/purchase/recommend`
- AI Profit Center: `/api/profit/analysis`
- Risk Engine: `/api/risk/list`
- AI task creation: `/api/ai/task/create`
- AI business memory: `/api/business-memory`

## Data Tables

- `sales_forecasts`
- `inventory_analysis`
- `risk_alerts`
- `business_memory`
- `ai_recommendation_history`

## Guardrails

- SAP remains the core business data source.
- SAP production writeback is disabled.
- AI advice is persisted and auditable.
- High-risk execution requires human approval.
- AI tasks create approval plans before execution.
- Mobile access is supported through the existing responsive portal layout.

## Automation Schedule

- 08:00 daily AI business report
- 09:00 inventory risk scan
- 10:00 sales forecast update
- 22:00 post-SAP-sync analysis
- Monday weekly business report
- 1st monthly business report

