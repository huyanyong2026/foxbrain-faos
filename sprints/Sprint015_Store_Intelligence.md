# Sprint015: Store Intelligence｜门店智能引擎

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint012 Business Health, Sprint013 Inventory Intelligence, Sprint014 Brand Intelligence

---

## 1. Sprint Goal

Build FoxBrain Store Intelligence Engine.

Goal:

Create digital operating profiles for every store.

```text
Store Data
↓
Store Analysis
↓
Store Health
↓
Store Decision Support
↓
Store Improvement
```

---

## 2. Core Questions

FoxBrain should answer:

- 哪个门店经营最好？
- 哪个门店利润最高？
- 哪个门店需要改善？
- 哪个门店库存结构不健康？
- 哪个门店适合扩大？
- 哪个门店需要调整定位？

---

## 3. Store Intelligence Metrics

Create:

```text
store_sales_amount
store_sales_share
store_gross_profit
store_gross_margin
store_inventory_amount
store_inventory_pressure
store_health_score
store_growth_rate
store_efficiency
```

---

## 4. Store Digital Twin

Each store should connect:

```text
Store
 ↓
Sales
 ↓
Inventory
 ↓
Brand
 ↓
Product
 ↓
Employee
 ↓
Expense
 ↓
Contract
 ↓
Memory
 ↓
Decision
```

---

## 5. Data Model

Create:

## store_intelligence_snapshots

Fields:

```text
id
snapshot_date
store_id
sales_score
margin_score
inventory_score
efficiency_score
overall_score
summary
evidence_json
created_at
```

## store_analysis_details

Fields:

```text
id
store_id
metric_type
metric_value
status
summary
evidence_json
created_at
```

---

## 6. Analysis Model

### Sales

Analyze:

- sales contribution
- trend
- ranking

### Profit

Analyze:

- gross profit
- gross margin

### Inventory

Analyze:

- inventory pressure
- slow stock
- product mix

### Efficiency

Prepare foundation for:

- sales per employee
- sales per square meter
- expense ratio

---

## 7. Decision Integration

Create Decision Insights when:

- store performance declines
- inventory pressure is high
- margin drops
- improvement opportunity appears

Every insight requires evidence.

---

## 8. Knowledge Graph Integration

Connect:

```text
Store
 ↓
Brand
 ↓
Product
 ↓
Sales
 ↓
Inventory
 ↓
Decision
```

---

## 9. UI Requirements

Add:

```text
/store-intelligence
```

Display:

- store ranking
- health score
- sales
- margin
- inventory
- brands
- risks
- opportunities

Store detail:

Show digital twin information.

---

## 10. CEO Dashboard

Add small card:

```text
门店健康
```

Display:

- top stores
- risky stores
- opportunity stores

---

## 11. QA Acceptance

Sprint015 passes when:

- store intelligence page works.
- store metrics calculated.
- store health generated.
- Decision Insights contain evidence.
- Store graph relationships displayed.
- Existing Sprint001-014 functions remain working.
- No production SAP connection.
- Smoke tests pass.

---

## 12. Codex Instruction

Incremental upgrade only.

Do not rewrite existing system.

Do not develop ai.vafox.com.

All store recommendations require evidence.

Deliver:

```text
SPRINT015_STORE_INTELLIGENCE_SUMMARY.md
SPRINT015_STORE_INTELLIGENCE_TEST_REPORT.md
```
