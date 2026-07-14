# Sprint012: Business Health Engine｜企业健康度引擎

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint010 Decision Engine, Sprint011 Business Rule Engine

---

## 1. Sprint Goal

Build VAFOX Business Health Engine.

The goal is to provide a high-level view of enterprise health:

```text
Business Data
↓
Rules
↓
Metrics
↓
Health Score
↓
CEO Understanding
```

The CEO should answer one question quickly:

> 今天企业整体健康吗？

---

## 2. Health Dimensions

Initial dimensions:

```text
sales_health        销售健康
margin_health       毛利健康
inventory_health    库存健康
brand_health        品牌健康
store_health        门店健康
operation_health    运营健康
data_health         数据健康
```

---

## 3. Health Score Model

Create configurable health scoring foundation.

Example:

```text
Health Score = weighted dimensions
```

Do not hard-code final weights.

Weights must be configurable later through Business Rule Engine.

---

## 4. Data Model

Create:

## business_health_snapshots

Fields:

```text
id
snapshot_date
overall_score
sales_score
margin_score
inventory_score
brand_score
store_score
operation_score
data_score
status
calculation_version
created_at
```

## business_health_details

Fields:

```text
id
snapshot_id
dimension
entity_type
entity_id
score
status
summary
evidence_json
created_at
```

---

## 5. Health Calculation

Initial rule-based calculation.

Examples:

### Sales Health

Based on:

- sales amount
- growth trend
- target comparison when available

### Margin Health

Based on:

- gross margin
- negative profit alerts
- low margin rules

### Inventory Health

Based on:

- inventory amount
- inventory age
- slow-moving products

### Brand Health

Based on:

- sales contribution
- margin contribution
- inventory pressure

### Store Health

Based on:

- sales
- margin
- inventory
- trend

Every score must have evidence.

---

## 6. UI Requirements

Add:

```text
/business-health
```

Page name:

```text
企业健康
```

Display:

- overall health score
- dimension scores
- top risks
- top opportunities
- evidence
- historical trend

---

## 7. CEO Dashboard Integration

Add simple card:

```text
企业健康度
86/100
```

Click enters detail page.

Do not overload homepage.

---

## 8. Decision Integration

Health Engine should create Decision Insights when:

- health score falls significantly
- dimension reaches critical state
- risk rules trigger

All insights require evidence.

---

## 9. Timeline Integration

Record health snapshots as enterprise timeline events.

Example:

```text
Business Health Snapshot Created
```

---

## 10. QA Acceptance

Sprint012 passes when:

- /business-health works.
- Health snapshot tables exist.
- Health scores can be calculated from existing data.
- Every score has evidence.
- Dashboard shows health summary.
- Critical health changes can create Decision Insights.
- Existing Sprint001-011 functions remain working.
- No production SAP connection.
- Smoke tests pass.

---

## 11. Codex Instruction

Incremental upgrade only.

Do not rewrite existing architecture.

Do not develop ai.vafox.com.

Do not create unsupported health conclusions.

Deliver:

```text
SPRINT012_BUSINESS_HEALTH_ENGINE_SUMMARY.md
SPRINT012_BUSINESS_HEALTH_ENGINE_TEST_REPORT.md
```
