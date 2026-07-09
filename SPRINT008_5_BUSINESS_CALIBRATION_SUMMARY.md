# Sprint008.5 Business Calibration Summary

## Scope

Sprint008.5 adds a business calibration layer on top of Sprint008 Data Lake and Business Object Pipeline.

It is an incremental upgrade:

- No production SAP connection.
- No SAP server installation.
- No ai.vafox.com work.
- Sprint001-008 features remain available.
- Raw SAP imports remain in Data Lake and are not overwritten.

## Database Changes

New and extended tables:

- `store_aliases`: canonical store name and source aliases.
- `brand_aliases`: canonical brand name and source aliases.
- `business_calibration_rules`: active calibration rule registry.
- `business_metric_quality`: metric-level quality warnings.
- `business_object_suggestions.canonical_key`: stable dedup key for object suggestions.

New indexes:

- `idx_business_object_suggestions_canonical`
- `idx_store_aliases_alias`
- `idx_brand_aliases_alias`
- `idx_metric_quality_lookup`

## Calibration Rules

Store normalization now maps SAP customer/store aliases to canonical stores, including:

- 南山店零售客户 / 南山店批发客户 / 南山店分销客户 -> 南山店
- 振兴店零售客户 / 振兴店批发客户 / 振兴店分销客户 / 振兴店会员客户 -> 振兴店
- 航苑店零售客户 / 航苑店批发客户 / 航苑店分销客户 -> 航苑店
- 金沙店零售客户 -> 金沙店
- 微店零售客户 -> 微店
- 网店零售客户 -> 网店

Brand normalization now maps aliases to canonical brands:

- Kailas / 凯乐石 -> Kailas
- Osprey -> Osprey
- Mammut / 猛犸象 -> Mammut
- VAFOX / 火狐狸 -> VAFOX
- VauDe / 沃德 -> VauDe

Product calibration uses a stable product identity:

1. `product_code`
2. `barcode`
3. normalized product name

## Pipeline Changes

Data Lake rebuild now:

- Preserves raw row data.
- Adds canonical store names.
- Adds canonical brand names.
- Adds `product_key` into normalized row data.
- Deduplicates object suggestions by `canonical_key`.
- Keeps object links per Data Lake record for traceability.

Object Match Center now receives fewer repeated suggestions while still preserving row-level evidence.

## API Changes

New APIs:

- `GET /api/business-calibration/summary`
- `GET /api/business-calibration/store-aliases`
- `GET /api/business-calibration/brand-aliases`
- `GET /api/business-calibration/quality`
- `POST /api/business-calibration/rebuild`

Existing APIs remain:

- `POST /api/data-lake/rebuild`
- `GET /api/business-metrics/summary`
- `GET /api/object-links`
- `GET /api/object-suggestions`

## UI Changes

New page:

- `/business-calibration`

Updated pages:

- `/data-lake`: adds gross margin, calibration warning count, and Business Calibration link.
- `/object-links` and `/object-suggestions`: continue to serve Object Match Center.
- `/search`: adds Store Alias, Brand Alias, Calibration Rule, and Metric Quality search types.
- CEO Dashboard: adds gross margin, inventory cost basis, calibration reminders, and Business Calibration entry.

## Dashboard Changes

CEO Dashboard now shows:

- Sales amount
- Gross profit
- Gross margin
- Inventory retail amount
- Inventory cost amount
- Object suggestion count
- Metric quality warning count
- Store and brand calibration reminder

Detailed calibration data stays behind `/business-calibration` instead of expanding on the homepage.

## Safety

No production SAP connection was made. Sprint008.5 only works with uploaded/exported SAP Excel/CSV-like files and the local FoxBrain database.

