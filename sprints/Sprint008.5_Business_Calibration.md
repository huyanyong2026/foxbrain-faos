# Sprint008.5: Business Calibration｜经营口径校准

Status: Ready for Codex  
Target: huyan.vafox.com  
Priority: P0.5  
Depends on: Sprint008

---

## 1. Sprint Goal

Sprint008 has proven the technical pipeline:

```text
SAP exported files
↓
Data Lake
↓
Sales / Inventory database
↓
Object Match Center
↓
Business Metrics
↓
CEO Dashboard V2
```

Sprint008.5 calibrates business meaning and reporting accuracy before building more AI analysis.

The goal is:

```text
Raw SAP rows
↓
Normalized business dimensions
↓
Trusted operating metrics
↓
CEO-ready dashboard
```

---

## 2. Why This Sprint Exists

Real SAP validation exposed several necessary calibration items:

- Store names can appear as `南山店`, `南山店零售客户`, `南山店批发客户`, or other SAP customer names.
- Brand fields are often missing and must be inferred from product names conservatively.
- Product/object suggestions can explode if generated per row.
- Total inventory files may lack usable cost values.
- Dashboard rankings must merge the same business entity before showing CEO metrics.
- `26kailas销售.xls` exists but currently contains 0 data rows.

Sprint008.5 fixes these operating-caliber issues without changing the safety boundary.

---

## 3. Safety Rules

Must follow:

- Do not connect to production SAP.
- Do not install anything on the SAP production server.
- Do not modify SAP source data.
- Do not delete original uploaded files.
- Do not auto-create business objects without human approval.
- Keep Sprint001-008 features working.
- Do not build ai.vafox.com.

---

## 4. Calibration Scope

### 4.1 Store Calibration

Create a store alias layer:

```text
store_aliases
```

Required fields:

```text
id
canonical_store_name
alias_name
alias_type
source
confidence
status
created_at
updated_at
```

Initial aliases:

```text
南山店零售客户 → 南山店
南山店批发客户 → 南山店
南山店分销客户 → 南山店

振兴店零售客户 → 振兴店
振兴店批发客户 → 振兴店
振兴店分销客户 → 振兴店
振兴店会员客户 → 振兴店

航苑店零售客户 → 航苑店
航苑店批发客户 → 航苑店
航苑店分销客户 → 航苑店

金沙店零售客户 → 金沙店
微店零售客户 → 微店
网店零售客户 → 网店
```

Dashboard and metrics must use canonical store name.

### 4.2 Brand Calibration

Create a brand alias layer:

```text
brand_aliases
```

Required fields:

```text
id
canonical_brand_name
alias_name
source
confidence
status
created_at
updated_at
```

Initial aliases:

```text
Kailas / 凯乐石 → Kailas
Osprey → Osprey
Mammut / 猛犸象 → Mammut
VAFOX / 火狐狸 → VAFOX
VauDe / 沃德 → VauDe
```

Brand inference must be conservative. If uncertain, leave blank and create a data-quality note rather than fabricating a brand.

### 4.3 Product Identity Calibration

Product identity priority:

1. `product_code`
2. `barcode`
3. `product_name`

Create product suggestions by unique product identity, not by every row.

Target behavior:

```text
same product_code
↓
one product suggestion
↓
many Data Lake rows linked to the same suggestion context
```

### 4.4 Object Suggestion Deduplication

Object suggestions must be deduplicated by:

```text
object_type
object_name
canonical_key
```

Do not create one suggestion per SAP row.

### 4.5 Inventory Cost Calibration

For inventory files:

- If `成本金额` exists, use it.
- If `成本金额` is blank and `库存量 × 成本价` is available, calculate it.
- If total inventory file lacks cost values, mark `cost_quality = missing_cost`.
- Do not invent cost.

Dashboard should show:

```text
inventory_retail_amount
inventory_cost_amount
inventory_cost_quality
```

### 4.6 Sales Metric Calibration

Sales metrics:

```text
sales_amount
gross_profit
gross_margin
sales_quantity
```

Gross margin:

```text
gross_profit / sales_amount
```

If sales amount is 0, gross margin must be 0 and quality warning should be recorded.

---

## 5. New Tables

Add:

```text
store_aliases
brand_aliases
business_calibration_rules
business_metric_quality
```

### 5.1 `business_calibration_rules`

Fields:

```text
id
rule_key
rule_type
rule_name
rule_json
status
created_by
created_at
updated_at
```

### 5.2 `business_metric_quality`

Fields:

```text
id
metric_key
dimension_type
dimension_value
quality_status
quality_message
source_batch_ids JSON
created_at
```

---

## 6. UI Requirements

Add:

```text
/business-calibration
/business-calibration/stores
/business-calibration/brands
/business-calibration/quality
```

The UI should support:

- View store aliases.
- View brand aliases.
- View metric quality warnings.
- Approve/edit aliases later.
- Show calibration status on Data Lake pages.

---

## 7. API Requirements

Add:

```text
GET  /api/business-calibration/summary
GET  /api/business-calibration/store-aliases
GET  /api/business-calibration/brand-aliases
GET  /api/business-calibration/quality
POST /api/business-calibration/rebuild
```

Optional later:

```text
POST /api/business-calibration/store-aliases
POST /api/business-calibration/brand-aliases
```

---

## 8. Dashboard Requirements

CEO Dashboard V2 must display calibrated values:

- Sales amount
- Gross profit
- Gross margin
- Inventory retail amount
- Inventory cost amount
- Inventory quantity
- Store sales ranking by canonical store
- Brand sales ranking by canonical brand
- Data quality warnings

Do not expand into detailed radar analysis on the homepage.

---

## 9. Search Requirements

Global Search should include:

```text
store_alias
brand_alias
calibration_rule
metric_quality
```

---

## 10. QA Acceptance

Acceptance checks:

- Sprint001-008 smoke tests pass.
- Real SAP validation files still import.
- Store ranking merges retail/wholesale/distribution aliases into canonical store names.
- Brand ranking uses canonical brand names.
- Object suggestions are deduplicated.
- Missing inventory cost is recorded as quality warning, not invented.
- Dashboard shows calibrated metrics.
- No production SAP connection.
- No SAP server installation.
- Original files are preserved.

---

## 11. Deliverables

Generate:

```text
SPRINT008_5_BUSINESS_CALIBRATION_SUMMARY.md
SPRINT008_5_BUSINESS_CALIBRATION_TEST_REPORT.md
```

Summary must include:

- New database tables
- Calibration rules
- API changes
- UI changes
- Dashboard changes
- Real SAP validation result
- Known limitations
- Sprint009 recommendation

---

## 12. Sprint009 Recommendation

After calibration, Sprint009 should implement:

```text
Business Knowledge Generation + CEO Query Layer
```

AI should only answer from calibrated metrics, Data Lake lineage, object links, and approved knowledge.
