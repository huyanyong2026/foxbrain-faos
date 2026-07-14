# Sprint008 Real SAP Data Validation Report

## Safety

- Original `sap数据.zip` was not deleted or modified.
- Validation used a temporary local VAFOX database only.
- No production SAP connection was made.
- No program was installed on the SAP server.

## Test Files

| File | Type | Rows | Encoding | Delimiter | Batch | Document | File Hash Prefix |
| --- | --- | ---: | --- | --- | ---: | ---: | --- |
| 库存7.9.xls | inventory | 9,081 | gb18030 | tab | 1 | 1 | 529001acf1ec |
| 南山店库存7.9.xls | inventory | 3,704 | gb18030 | tab | 2 | 2 | 1c4456e24bdf |
| 总销售261.1-7.9.xls | sales | 24,741 | gb18030 | tab | 3 | 3 | 453c9084fd60 |
| 2501销售.xls | sales | 4,388 | gb18030 | tab | 4 | 4 | d7d158536424 |
| 25kailas销售.xls | sales | 13,543 | gb18030 | tab | 5 | 5 | ad1067381d7c |
| 26kailas销售.xls | sales | 0 | gb18030 | tab | 6 | 6 | f3b3b3c33b0f |

## Acceptance Results

| Check | Result |
| --- | --- |
| Files entered Data Lake | 6 data_lake_sources created; 6 sources have file hash |
| Import batches created | 6 sap_import_batches created |
| Raw data preserved | 55,457 data_lake_records contain raw_data |
| Inventory table imported | 12,785 sap_inventory rows |
| Sales table imported | 42,672 sap_sales rows |
| Product/brand/store suggestions created | 141,116 object links and 27,169 object suggestions |
| Dashboard sales amount | 34,746,796.27 |
| Dashboard gross profit | 10,226,406.24 |
| Dashboard inventory amount | 16,829,795.15 |
| Dashboard product quantity | 50,978.00 |

## Data Lake Summary

- documents: 6
- batches: 6
- inventory_rows: 12,785
- sales_rows: 42,672
- data_lake_sources: 6
- data_lake_records: 55,457
- raw_rows: 55,457
- object_links: 141,116
- object_suggestions: 27,169
- metric_snapshots: 53
- sources_with_hash: 6

## CEO Dashboard V2 Metrics

- Sales amount: 34,746,796.27
- Gross profit: 10,226,406.24
- Inventory retail amount: 16,829,795.15
- Inventory quantity: 50,978.00
- Quality alerts: 3

## Store Sales Ranking

| Store | Sales Amount |
| --- | ---: |
| 振兴店 | 15,535,646.09 |
| 航苑店 | 8,023,220.10 |
| 南山店 | 7,462,033.54 |
| 网店 | 1,676,009.86 |
| 金沙店 | 1,130,970.40 |
| 武侯祠店零售客户 | 668,175.80 |
| 员工仓零售客户 | 219,196.88 |
| 微店 | 31,543.60 |

## Brand Sales Ranking

| Brand | Sales Amount |
| --- | ---: |
| Kailas | 23,091,676.09 |
| Osprey | 2,037,858.97 |
| VauDe | 1,251,333.09 |
| Mammut | 41,575.96 |
| VAFOX | 0.00 |

## Inventory Summary

| Store | Metric | Value |
| --- | --- | ---: |
| 全部库存 | inventory_cost_amount | 0.00 |
| 全部库存 | inventory_quantity | 42,747.00 |
| 全部库存 | inventory_retail_amount | 10,582,619.07 |
| 南山店 | inventory_cost_amount | 3,080,742.45 |
| 南山店 | inventory_quantity | 8,231.00 |
| 南山店 | inventory_retail_amount | 6,247,176.08 |

## Notes

- `26kailas销售.xls` was included and produced 0 data rows from the provided export content.
- `object_suggestions` are intentionally pending for human confirmation; Sprint008 does not auto-create business objects.
- The temporary validation database was used only for verification and can be discarded after reporting.
