# AI Companion Report

Version: Genesis-Construction-003-2

## Interface
The Ask AI panel is embedded directly in Workforce Home and supports natural questions such as:
- 今天应该做什么？
- 这个客户怎么服务？
- 这个产品怎么介绍？
- 库存怎么办？

## Governance
AI requests continue through the existing governed `/ops-api/runs` flow: CSRF, login permission, AI context authorization, Core evidence, task drafting, and review policy.

## Legacy Removal
Home does not expose manual Agent selector, source selector, object selector, or analysis configuration.

## Acceptance Status
- PASS: AI Companion can answer with business context through the V6 router.
- PASS: Optional tasks and evidence links remain governed.
