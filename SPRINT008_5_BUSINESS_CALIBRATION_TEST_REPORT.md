# Sprint008.5 Business Calibration Test Report

## Test Scope

Sprint008.5 was validated with the real SAP export package `sap数据.zip`.

Test files:

- 库存7.9.xls
- 南山店库存7.9.xls
- 总销售261.1-7.9.xls
- 2501销售.xls
- 25kailas销售.xls
- 26kailas销售.xls

No production SAP connection was made.

## Real Data Import Result

| File | Type | Rows | Encoding | Batch |
| --- | --- | ---: | --- | ---: |
| 库存7.9.xls | inventory | 9,081 | gb18030 | 1 |
| 南山店库存7.9.xls | inventory | 3,704 | gb18030 | 2 |
| 总销售261.1-7.9.xls | sales | 24,741 | gb18030 | 3 |
| 2501销售.xls | sales | 4,388 | gb18030 | 4 |
| 25kailas销售.xls | sales | 13,543 | gb18030 | 5 |
| 26kailas销售.xls | sales | 0 | gb18030 | 6 |

## Data Lake Validation

- Data Lake sources: 6
- Data Lake records: 55,457
- SAP inventory rows: 12,785
- SAP sales rows: 42,672
- Business object links: 141,116
- Business object suggestions: 20,822

## Store Normalization

Store normalization was validated against the real SAP sales rows.

Validated store ranking after calibration:

| Store | Sales Amount |
| --- | ---: |
| 振兴店 | 15,535,646.09 |
| 航苑店 | 8,023,220.10 |
| 南山店 | 7,462,033.54 |
| 网店 | 1,676,009.86 |
| 金沙店 | 1,130,970.40 |

Store aliases loaded: 21.

## Brand Normalization

Brand normalization was validated against the real SAP brand rows.

Validated brand ranking after calibration:

| Brand | Sales Amount |
| --- | ---: |
| Kailas | 23,091,676.09 |
| Osprey | 2,037,858.97 |
| VauDe | 1,251,333.09 |
| Mammut | 41,575.96 |
| VAFOX | 0.00 |

Brand aliases loaded: 9.

## Product Calibration

Product calibration uses stable identity priority:

1. product code
2. barcode
3. normalized product name

Validated product keys: 20,808.

This preserves SKU-level separation and avoids merging products that share the same display name.

## Object Suggestion Reduction

Object suggestion reduction was measured against the Sprint008 real-data baseline.

Sprint008 baseline object suggestions: 27,169.

Sprint008.5 calibrated object suggestions: 20,822.

Reduction: 6,347 fewer suggestions.

Reduction rate: 23.36%.

The reduction is mainly from canonical store and brand deduplication. Product suggestions remain SKU-aware to avoid incorrect auto-merge.

## Business Metrics

- Sales amount: 34,746,796.27
- Gross profit: 10,226,406.24
- Gross margin: 29.43%
- Inventory quantity: 42,749
- Metric quality warnings: 0

Note: inventory cost and retail amount depend on the exact exported inventory columns. Sprint008.5 records the metric-quality structure so future mapping issues can be reviewed without changing SAP.

## Dashboard Changes

Dashboard changes were validated through static smoke tests and the real-data metric payload.

CEO Dashboard validation:

- Sales amount visible.
- Gross profit visible.
- Gross margin added.
- Inventory amount/cost cards added.
- Object suggestion count visible.
- Calibration warning count visible.
- Business Calibration entry added.

Data Lake page validation:

- Gross margin added.
- Calibration warning count added.
- Business Calibration link added.

Search validation:

- Store Alias search type added.
- Brand Alias search type added.
- Calibration Rule search type added.
- Metric Quality search type added.

## Smoke Tests

Validated:

- `python -m py_compile portal_v2.py`
- `python -m py_compile tests/v6_smoke_check.py`
- Sprint008.5 schema strings present.
- Sprint008.5 routes and APIs present.
- Sprint008.5 Dashboard and Search integration present.

## Safety Result

No production SAP connection was made. The validation used only uploaded/exported SAP files from `sap数据.zip` and a temporary local SQLite database.
