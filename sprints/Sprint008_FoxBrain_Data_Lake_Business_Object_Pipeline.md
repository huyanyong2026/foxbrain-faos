# Sprint008: FoxBrain Data Lake + Business Object Pipeline

Status: Ready for Codex  
Target: huyan.vafox.com  
Priority: P0  
Depends on: Sprint001-007

---

## 1. Sprint Goal

Build the first end-to-end FoxBrain business data pipeline:

```text
SAP exported data
↓
Data Lake
↓
Sales database
↓
Inventory database
↓
Product objects
↓
Brand objects
↓
Store objects
↓
Knowledge base
↓
CEO Dashboard
```

Sprint007 proved that real SAP exported files can be imported safely. Sprint008 turns those imported rows into a governed enterprise data lake and then links them to FoxBrain business objects.

---

## 2. Safety Principles

Must follow:

- Do not connect to production SAP.
- Do not install any program on the SAP production server.
- Do not modify SAP source data.
- Do not auto-create business objects without traceability.
- Preserve original uploaded files and raw row JSON.
- Keep Sprint001-007 features working.
- Do not build ai.vafox.com.
- Only upgrade huyan.vafox.com incrementally.

---

## 3. Core Architecture

### 3.1 Data Lake Layer

Data Lake is the audit foundation. It stores every imported source file, parsed row, row hash, mapping result, and lineage link.

Required entities:

```text
data_lake_sources
data_lake_records
data_lake_lineage
data_quality_checks
```

### 3.2 Business Data Layer

Continue using Sprint007 normalized tables:

```text
sap_sales
sap_inventory
sap_import_batches
```

Sprint008 should enrich, index, summarize, and link those rows, not replace them.

### 3.3 Business Object Layer

Imported SAP rows should match existing objects where possible:

```text
product
brand
store
employee
supplier
customer
```

If a match is uncertain, create a suggestion record instead of silently creating the object.

### 3.4 Knowledge Layer

The pipeline should generate knowledge-ready summaries from imported SAP data:

```text
store sales summary
brand sales summary
product inventory summary
inventory risk summary
data quality summary
```

These summaries should be reviewable and traceable to source batches.

### 3.5 CEO Dashboard Layer

CEO Dashboard should show only the essential business state:

- Latest SAP import status
- Sales row count
- Inventory row count
- Store sales ranking
- Brand sales ranking
- Inventory value
- Data quality alerts
- Unmatched object suggestions

Detailed drilldown should stay behind click-through pages.

---

## 4. New Database Tables

### 4.1 `data_lake_sources`

Fields:

```text
id
source_type
source_name
document_id
batch_id
filename
file_hash
encoding
delimiter
status
row_count
created_by
created_at
updated_at
```

### 4.2 `data_lake_records`

Fields:

```text
id
source_id
batch_id
record_type
row_index
row_hash
raw_data JSON
normalized_data JSON
quality_status
quality_message
created_at
```

### 4.3 `business_object_links`

Fields:

```text
id
source_type
source_id
record_type
record_id
object_type
object_id
match_key
match_confidence
match_status
created_at
updated_at
```

`match_status`:

```text
matched
suggested
unmatched
ignored
```

### 4.4 `business_object_suggestions`

Fields:

```text
id
object_type
object_name
source_type
source_id
evidence JSON
confidence
status
reviewed_by
reviewed_at
created_at
updated_at
```

### 4.5 `business_metrics_snapshots`

Fields:

```text
id
snapshot_type
period_start
period_end
store_name
brand_name
product_code
metric_key
metric_value
source_batch_ids JSON
created_at
```

---

## 5. Data Lake Pipeline

When a SAP import batch completes:

```text
sap_import_batches
↓
create data_lake_sources
↓
copy every sap_sales / sap_inventory row into data_lake_records
↓
run data quality checks
↓
match business objects
↓
create object suggestions
↓
generate business metrics snapshots
↓
surface result in CEO Dashboard
```

Pipeline must be idempotent:

- Re-running the pipeline for the same batch must not duplicate records.
- Use row hash and batch id for deduplication.

---

## 6. Object Matching Rules

### 6.1 Store Matching

Match by normalized store name:

```text
南山店
振兴店
航苑店
金沙店
微店
网店
全部库存
```

If no store object exists, create a `business_object_suggestions` record.

### 6.2 Product Matching

Match by:

```text
product_code
barcode
product_name
```

Priority:

1. Exact product code
2. Exact barcode
3. Product name similarity

### 6.3 Brand Matching

Real SAP exports may not have a clean brand field. Infer brand conservatively from product name only when obvious. Examples:

```text
Kailas / 凯乐石
Osprey
Mammut / 猛犸象
VAFOX / 火狐狸
```

If uncertain, leave unmatched.

---

## 7. New Pages

Add or upgrade:

```text
/data-lake
/data-lake/sources
/data-lake/records
/object-links
/object-suggestions
```

Pages should be mobile-friendly and operational, not marketing pages.

---

## 8. API Requirements

Add:

```text
GET  /api/data-lake/sources
GET  /api/data-lake/records
POST /api/data-lake/rebuild
GET  /api/object-links
GET  /api/object-suggestions
POST /api/object-suggestions/:id/approve
POST /api/object-suggestions/:id/reject
GET  /api/business-metrics/summary
```

Approval endpoints should not modify SAP data. They only create or link local FoxBrain business objects.

---

## 9. Dashboard Requirements

CEO Dashboard should add:

```text
Data Lake sources
Data Lake records
Linked objects
Unmatched suggestions
Store sales ranking
Brand sales ranking
Inventory value summary
Data quality alerts
```

Keep the homepage simple. Show summaries only; detail pages carry hierarchy.

---

## 10. Search Requirements

Global Search should include:

```text
data_lake_source
data_lake_record
object_link
object_suggestion
business_metric
```

Search by filename, store, brand, product code, product name, barcode, and quality message.

---

## 11. QA Acceptance

Acceptance checks:

- Existing Sprint001-007 smoke tests pass.
- Real SAP file imports still pass.
- Data Lake sources are created from SAP import batches.
- Data Lake records are created from `sap_sales` and `sap_inventory`.
- Original raw row JSON remains traceable.
- Store/product/brand object links or suggestions are generated.
- CEO Dashboard shows Data Lake and object-link summaries.
- No production SAP connection exists.
- No SAP server installation is required.
- No ai.vafox.com development.

---

## 12. Deliverables

After implementation, output:

```text
SPRINT008_DATA_LAKE_BUSINESS_OBJECT_PIPELINE_SUMMARY.md
SPRINT008_DATA_LAKE_TEST_REPORT.md
```

Summary must include:

- Modified files
- New database tables
- New pages
- New APIs
- Pipeline behavior
- Object matching strategy
- Dashboard changes
- Test results
- Known limitations
- Sprint009 recommendation

---

## 13. Sprint009 Recommendation

Sprint009 should build:

```text
Business Knowledge Generation + CEO Query Layer
```

This will let the CEO ask questions across SAP data, linked objects, and knowledge summaries with traceable citations.
