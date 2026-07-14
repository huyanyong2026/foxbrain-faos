# Sprint013: Inventory Intelligence｜库存智能引擎

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint008 Data Lake, Sprint010 Decision Engine, Sprint011 Business Rules, Sprint012 Business Health

---

## 1. Sprint Goal

Build VAFOX Inventory Intelligence Engine.

Goal:

Transform inventory data into actionable inventory understanding.

```text
Inventory Data
↓
Inventory Analysis
↓
Risk Detection
↓
Decision Insight
↓
Action Recommendation
```

---

## 2. Core Questions

VAFOX should answer:

- 哪些库存风险最高？
- 哪些 SKU 长时间没有销售？
- 哪些品牌库存压力最大？
- 哪些门店库存结构不健康？
- 哪些商品应该促销处理？
- 哪些商品值得继续补货？

---

## 3. Inventory Metrics

Create inventory intelligence metrics:

```text
inventory_amount
inventory_quantity
inventory_age_days
sales_velocity
turnover_rate
stock_risk_level
sell_through_rate
```

---

## 4. Inventory Risk Model

Initial rule-based model:

### High Risk

```text
inventory_days > 180
AND
sales_velocity low
```

### Critical Risk

```text
inventory_days > 365
AND
inventory_amount high
```

### Dead Stock

```text
inventory exists
AND
no sales history
```

### Fast Moving Opportunity

```text
sales velocity high
AND
inventory low
```

---

## 5. Data Model

Create:

## inventory_intelligence_snapshots

Fields:

```text
id
snapshot_date
total_inventory_amount
total_inventory_quantity
high_risk_count
critical_risk_count
slow_stock_count
calculation_version
created_at
```

## inventory_product_analysis

Fields:

```text
id
product_id
store_id
inventory_quantity
inventory_amount
sales_quantity
sales_amount
last_sale_date
inventory_days
risk_level
recommendation
evidence_json
created_at
```

---

## 6. Integration

### Decision Engine

Create insights:

- inventory risk
- slow stock
- replenishment opportunity

Every insight must include evidence.

### Business Rules

Use existing rules:

- inventory days
- inventory amount
- margin
- quality warnings

### Knowledge Graph

Connect:

```text
Product
 ↓
Brand
 ↓
Store
 ↓
Inventory Risk
```

---

## 7. UI Requirements

Add:

```text
/inventory-intelligence
```

Display:

- inventory health summary
- risk ranking
- brand inventory pressure
- store inventory pressure
- slow moving products
- opportunity products

Detail page:

Show:

- product
- brand
- store
- inventory
- sales history
- evidence
- recommendation

---

## 8. CEO Dashboard

Add small card:

```text
库存健康
```

Display:

- high risk items
- critical risks
- inventory trend

Do not overload homepage.

---

## 9. QA Acceptance

Sprint013 passes when:

- inventory intelligence page works.
- inventory metrics calculated.
- slow stock detection works.
- risk insights created with evidence.
- Decision Engine integration works.
- Business Health integration works.
- Existing Sprint001-012 functions remain working.
- No production SAP connection.
- Smoke tests pass.

---

## 10. Codex Instruction

Incremental upgrade only.

Do not rewrite existing system.

Do not develop ai.vafox.com.

Do not make unsupported inventory conclusions.

All recommendations require evidence.

Deliver:

```text
SPRINT013_INVENTORY_INTELLIGENCE_SUMMARY.md
SPRINT013_INVENTORY_INTELLIGENCE_TEST_REPORT.md
```
