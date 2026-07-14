# Sprint011: Business Rule Engine｜企业经营规则引擎

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint010 Decision Engine

---

## 1. Sprint Goal

Build the first version of VAFOX Business Rule Engine.

VAFOX already has:

```text
Drive
Data Lake
Object Engine
Knowledge Engine
Memory Engine
Knowledge Graph
Decision Engine
```

Sprint011 adds the rule layer that tells VAFOX how Huohu Fox interprets business situations.

The goal is:

```text
Business data
↓
Business rules
↓
Evidence-based decision insights
↓
Memory and execution
```

Rules must be structured, auditable, editable, and connected to decisions.

---

## 2. Core Principle

> AI may analyze, but business rules define the company’s operating logic.

Business Rule Engine must not replace Decision Engine. It must guide it.

Every rule must have:

- rule type
- condition
- expected action
- severity
- explanation
- source
- version
- status

No rule should be hidden in code only.

---

## 3. Rule Categories

Initial categories:

```text
inventory_rule       库存规则
pricing_rule         定价规则
discount_rule        折扣规则
margin_rule          毛利规则
brand_rule           品牌规则
store_rule           门店规则
purchase_rule        采购规则
risk_rule            风险规则
decision_rule        决策规则
calibration_rule     经营口径规则
```

---

## 4. Initial Huohu Fox Rules

Seed initial rules as editable rules.

### 4.1 Inventory Risk

```text
IF inventory_days > 180 AND inventory_amount > 50000
THEN severity = high
ACTION create inventory risk insight
```

### 4.2 Critical Inventory Risk

```text
IF inventory_days > 365 AND inventory_amount > 100000
THEN severity = critical
ACTION create decision insight and dashboard alert
```

### 4.3 Low Margin Warning

```text
IF gross_margin < 0.25
THEN severity = medium
ACTION create margin review insight
```

### 4.4 Negative Gross Profit

```text
IF gross_profit < 0
THEN severity = high
ACTION create product risk insight
```

### 4.5 Missing Cost Quality

```text
IF inventory_cost_quality = missing_cost
THEN severity = medium
ACTION create data quality warning
```

### 4.6 Brand Concentration

```text
IF brand_sales_share > 0.60
THEN severity = medium
ACTION create brand dependency insight
```

### 4.7 Store Margin Decline Placeholder

```text
IF store_margin_decline_months >= 3
THEN severity = high
ACTION create store review insight
```

If time-series comparison is not yet available, keep this rule inactive but visible.

---

## 5. Data Model

Create or extend:

## business_rules

Fields:

```text
id
rule_key
rule_name
rule_type
description
condition_json
action_json
severity
priority
status
version
source
created_by
created_at
updated_at
archived_at
```

Status:

```text
active
inactive
draft
archived
```

## business_rule_runs

Fields:

```text
id
run_type
status
rules_evaluated
rules_triggered
insights_created
started_at
finished_at
error_message
created_at
```

## business_rule_results

Fields:

```text
id
run_id
rule_id
entity_type
entity_id
matched
severity
result_summary
evidence_json
created_insight_id
created_at
```

---

## 6. Rule Evaluation

Initial evaluator should be rule-based only.

No external AI API required.

Rule evaluator should read from:

- calibrated business metrics
- sap_sales
- sap_inventory
- business_metric_quality
- decision_insights
- knowledge_graph_nodes / edges when available

It should create Decision Engine insights when rules match.

All generated insights must include evidence.

---

## 7. UI Requirements

Add:

```text
/business-rules
/business-rules/:id
/business-rules/runs
```

Page name:

```text
经营规则
```

UI sections:

- Active rules
- Draft rules
- Inactive rules
- Rule run history
- Triggered results
- Rules connected to decisions

Rule detail page should show:

- rule name
- category
- condition
- action
- severity
- status
- source
- latest results

Do not build complex visual DSL yet. A structured form/table view is enough.

---

## 8. API Requirements

Add:

```text
GET  /api/business-rules
GET  /api/business-rules/:id
POST /api/business-rules
PATCH /api/business-rules/:id
POST /api/business-rules/rebuild
GET  /api/business-rules/runs
GET  /api/business-rules/results
```

---

## 9. Decision Engine Integration

Business Rule Engine must integrate with Sprint010:

- Rule match can create decision_insights.
- Rule result becomes decision_evidence.
- Insight should reference rule_id and rule_run_id in evidence.
- Decision page should show which rule triggered the insight.

---

## 10. Dashboard Integration

CEO Dashboard should show:

- active rule count
- latest rule run
- triggered high-risk rules
- link to Business Rule Center

Do not overload homepage.

---

## 11. Memory Integration

When a rule-triggered insight is accepted/resolved, Memory record should preserve:

- rule that triggered it
- evidence
- decision
- expected impact

---

## 12. QA Acceptance

Sprint011 passes when:

- /business-rules page is accessible.
- business_rules table exists.
- initial Huohu Fox rules are seeded.
- rule evaluator runs without external AI API.
- rule run creates business_rule_results.
- matched high-risk rules create Decision Engine insights with evidence.
- Dashboard displays rule summary.
- Existing Sprint001-010 functions remain working.
- No production SAP connection.
- No ai.vafox.com development.
- Smoke tests pass.

---

## 13. Codex Instruction

Incremental upgrade only.

Do not rewrite existing system.

Do not develop ai.vafox.com.

Do not connect production SAP.

Do not hide rules only inside code.

All rule-triggered decisions must include evidence.

Deliver:

```text
SPRINT011_BUSINESS_RULE_ENGINE_SUMMARY.md
SPRINT011_BUSINESS_RULE_ENGINE_TEST_REPORT.md
```

Summary must include:

- new tables
- seeded rules
- APIs
- UI routes
- Decision Engine integration
- Dashboard integration
- test results
- known limitations
