# Sprint014: Brand Intelligence｜品牌智能引擎

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint009 Knowledge Graph, Sprint010 Decision Engine, Sprint011 Business Rules, Sprint012 Business Health

---

## 1. Sprint Goal

Build VAFOX Brand Intelligence Engine.

Goal:

Transform brand data into strategic brand understanding.

```text
Brand Data
↓
Brand Analysis
↓
Brand Health
↓
Strategic Insight
↓
CEO Decision Support
```

---

## 2. Core Questions

VAFOX should answer:

- 哪个品牌贡献最大？
- 哪个品牌利润最好？
- 哪个品牌库存压力最大？
- 哪个品牌增长最快？
- 哪个品牌需要调整策略？
- 哪些品牌值得继续投入？

---

## 3. Brand Metrics

Create:

```text
brand_sales_amount
brand_sales_share
brand_gross_profit
brand_gross_margin
brand_inventory_amount
brand_inventory_pressure
brand_growth_rate
brand_health_score
```

---

## 4. Brand Analysis Model

Analyze each brand from:

### Sales

- sales amount
- sales quantity
- sales contribution

### Profit

- gross profit
- gross margin

### Inventory

- inventory amount
- inventory risk
- slow moving products

### Relationship

From Knowledge Graph:

```text
Brand
 ↓
Product
 ↓
Store
 ↓
Sales
 ↓
Inventory
```

---

## 5. Data Model

Create:

## brand_intelligence_snapshots

Fields:

```text
id
snapshot_date
brand_id
authority_score
sales_score
profit_score
inventory_score
growth_score
overall_score
summary
evidence_json
created_at
```

## brand_analysis_details

Fields:

```text
id
brand_id
metric_type
metric_value
status
summary
evidence_json
created_at
```

---

## 6. Decision Integration

Create Decision Insights when:

- brand inventory pressure is high
- brand margin declines
- brand dependency becomes risky
- brand growth opportunity appears

Every insight requires evidence.

---

## 7. Business Health Integration

Brand Health contributes to:

```text
Business Health
 ↓
Brand Health Dimension
```

---

## 8. UI Requirements

Add:

```text
/brand-intelligence
```

Display:

- brand ranking
- sales contribution
- profit contribution
- inventory pressure
- brand health
- risks
- opportunities

Brand detail page:

Show:

- products
- stores
- sales
- inventory
- decisions
- memory
- evidence

---

## 9. CEO Dashboard

Add small card:

```text
品牌健康
```

Display:

- top brands
- risky brands
- opportunity brands

Do not overload homepage.

---

## 10. QA Acceptance

Sprint014 passes when:

- brand intelligence page works.
- brand metrics calculated.
- brand health generated.
- Decision Insights include evidence.
- Knowledge Graph brand relationships displayed.
- Business Health brand dimension updated.
- Existing Sprint001-013 functions remain working.
- No production SAP connection.
- Smoke tests pass.

---

## 11. Codex Instruction

Incremental upgrade only.

Do not rewrite existing system.

Do not develop ai.vafox.com.

Do not make unsupported brand conclusions.

All strategic suggestions require evidence.

Deliver:

```text
SPRINT014_BRAND_INTELLIGENCE_SUMMARY.md
SPRINT014_BRAND_INTELLIGENCE_TEST_REPORT.md
```
