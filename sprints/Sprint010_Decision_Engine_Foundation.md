# Sprint010: Decision Engine Foundation｜经营决策引擎基础

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint008.5 Business Calibration, Sprint009 Business Knowledge Graph

---

## 1. Sprint Goal

Build the first version of VAFOX Decision Engine.

The goal is not to let AI make decisions automatically. The goal is to help the CEO understand:

```text
What happened?
Why did it happen?
What is risky?
What can be done next?
Which data supports the conclusion?
```

Sprint010 turns calibrated data, knowledge, memory, and graph context into structured decision support.

---

## 2. Core Principle

> Decision Engine must provide evidence-based suggestions, not unsupported AI opinions.

Every decision insight must be traceable to at least one of:

- calibrated business metrics
- Data Lake lineage
- Object Engine relationship
- Knowledge item
- Memory record
- Business rule
- Knowledge Graph edge

---

## 3. Decision Types

Support initial decision types:

```text
inventory_risk      库存风险
brand_performance   品牌表现
store_performance   门店表现
product_risk        商品风险
pricing_review      价格与折扣复盘
purchase_review     采购建议复盘
operation_alert     经营异常提醒
```

---

## 4. Data Model

Create:

## decision_insights

Fields:

```text
id
insight_type
title
summary
severity
status
entity_type
entity_id
metric_snapshot JSON
evidence JSON
suggestion
action_options JSON
created_by
created_at
updated_at
resolved_at
```

Severity:

```text
low
medium
high
critical
```

Status:

```text
new
reviewing
accepted
rejected
resolved
archived
```

## decision_evidence

Fields:

```text
id
insight_id
source_type
source_id
evidence_title
evidence_summary
confidence
created_at
```

## decision_actions

Fields:

```text
id
insight_id
action_title
action_description
action_type
status
owner
created_at
updated_at
```

---

## 5. Insight Generation Rules

Initial rule-based insights only. Do not require external AI API.

### 5.1 Inventory Risk

Generate when:

- inventory quantity is high and recent sales are low
- inventory cost quality is missing
- product exists in inventory but not in recent sales

### 5.2 Brand Performance

Generate when:

- brand sales share is unusually high
- brand gross margin is lower than expected
- brand inventory amount is high compared with sales

### 5.3 Store Performance

Generate when:

- store sales ranking changes
- store gross margin is lower than average
- store has high inventory but low sales

### 5.4 Product Risk

Generate when:

- product inventory exists but no sales record
- product has sales but negative or zero gross profit
- product has duplicate identity suggestions

---

## 6. UI Requirements

Add:

```text
/decision
/decision/insights
```

Page name:

```text
经营决策
```

UI sections:

- New risks
- High severity insights
- Inventory risks
- Brand insights
- Store insights
- Product insights
- Accepted / resolved decisions

Each insight detail page must show:

- Title
- Severity
- Summary
- Entity
- Evidence
- Suggested options
- Status update buttons

---

## 7. API Requirements

Add:

```text
GET  /api/decision/insights
GET  /api/decision/insights/:id
POST /api/decision/rebuild
PATCH /api/decision/insights/:id
POST /api/decision/insights/:id/actions
GET  /api/objects/:id/decisions
```

---

## 8. Dashboard Integration

CEO Dashboard should show:

- high severity decision insights count
- top 3 risks
- latest accepted decision
- link to Decision Engine

Do not overload homepage.

---

## 9. Memory Integration

When a decision insight is accepted or resolved, allow creating a Memory record.

This preserves:

- what was found
- what was decided
- why it was decided
- expected impact

---

## 10. Knowledge Graph Integration

Decision insights should attach to related graph nodes when possible.

Examples:

```text
KAILAS → brand_performance insight
南山店 → store_performance insight
Product SKU → inventory_risk insight
```

---

## 11. QA Acceptance

Sprint010 passes when:

- /decision page is accessible.
- decision_insights table exists.
- rule-based insights can be generated from existing sales/inventory/metrics data.
- each insight has evidence.
- Dashboard shows decision summary.
- Object detail can show related decisions.
- Accepted/resolved insight can create or prepare Memory record.
- No external AI API is required.
- No unsupported AI conclusion is generated.
- Sprint001-009 functions remain working.
- Smoke tests pass.

---

## 12. Codex Instruction

Incremental upgrade only.

Do not rewrite existing system.

Do not develop ai.vafox.com.

Do not connect production SAP.

Do not make unsupported AI claims.

All insights must include evidence.

Deliver:

```text
SPRINT010_DECISION_ENGINE_SUMMARY.md
SPRINT010_DECISION_ENGINE_TEST_REPORT.md
```
