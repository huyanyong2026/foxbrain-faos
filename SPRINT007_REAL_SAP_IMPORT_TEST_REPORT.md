# Sprint007 Real SAP Import Test Report

## Scope

Test package: `sap数据.zip`

Priority files imported:

1. `库存7.9.xls`
2. `南山店库存7.9.xls`
3. `振兴店库存7.9.xls`
4. `航苑店库存7.9.xls`
5. `金沙店库存7.9.xls`
6. `总销售261.1-7.9.xls`
7. `南山店销售1.1-7.9.xls`
8. `振兴店销售1.1-7.9.xls`
9. `航苑店销售1.1-7.9.xls`
10. `金沙店销售1.1-7.9.xls`

Safety boundary: local file import only; no production SAP connection; no program installed on the SAP production server.

## Parser Result

The priority `.xls` files are GB18030/GBK encoded tab-separated text exports, not standard Excel binary files. The importer now detects this and parses them as delimited text.

## Import Result

| File | Type | Rows | Success | Failed | Status |
| --- | --- | ---: | ---: | ---: | --- |
| 库存7.9.xls | inventory | 9,081 | 9,081 | 0 | completed |
| 南山店库存7.9.xls | inventory | 3,704 | 3,704 | 0 | completed |
| 振兴店库存7.9.xls | inventory | 3,786 | 3,786 | 0 | completed |
| 航苑店库存7.9.xls | inventory | 3,850 | 3,850 | 0 | completed |
| 金沙店库存7.9.xls | inventory | 2,135 | 2,135 | 0 | completed |
| 总销售261.1-7.9.xls | sales | 24,741 | 24,741 | 0 | completed |
| 南山店销售1.1-7.9.xls | sales | 6,301 | 6,301 | 0 | completed |
| 振兴店销售1.1-7.9.xls | sales | 7,968 | 7,968 | 0 | completed |
| 航苑店销售1.1-7.9.xls | sales | 6,331 | 6,331 | 0 | completed |
| 金沙店销售1.1-7.9.xls | sales | 2,309 | 2,309 | 0 | completed |

Totals:

- Import batches: 10
- Inventory rows: 22,556
- Sales rows: 47,650
- Failed rows: 0

## Inventory Summary

| Store | Rows | Quantity | Cost Amount | Retail Amount |
| --- | ---: | ---: | ---: | ---: |
| 全部库存 | 9,081 | 42,747 | 0.00 | 10,582,619.07 |
| 航苑店 | 3,850 | 9,019 | 2,917,387.72 | 6,025,719.10 |
| 振兴店 | 3,786 | 20,753 | 3,459,565.37 | 7,343,632.00 |
| 南山店 | 3,704 | 8,231 | 3,080,742.45 | 6,247,176.08 |
| 金沙店 | 2,135 | 4,466 | 1,190,356.36 | 2,585,805.50 |

Note: the total inventory export has blank cost values in the sampled rows, so total cost amount remains 0 where SAP did not export usable cost data. Raw row JSON is preserved.

## Sales Summary

| Store / Customer | Rows | Quantity | Amount | Gross Profit |
| --- | ---: | ---: | ---: | ---: |
| 振兴店 | 7,968 | 9,363 | 8,348,728.03 | 2,316,763.01 |
| 振兴店零售客户 | 6,990 | 7,818 | 6,544,899.35 | 1,830,264.68 |
| 航苑店 | 6,331 | 6,872 | 4,684,947.60 | 1,182,727.91 |
| 南山店 | 6,301 | 6,549 | 4,710,608.02 | 1,416,559.37 |
| 南山店零售客户 | 6,297 | 6,545 | 4,704,728.02 | 1,414,879.37 |
| 航苑店零售客户 | 6,026 | 6,523 | 4,324,392.10 | 1,095,952.91 |
| 金沙店 | 2,309 | 2,806 | 918,469.00 | 367,630.20 |
| 金沙店零售客户 | 2,309 | 2,806 | 918,469.00 | 367,630.20 |

The total sales file keeps SAP row-level `客户名称`; store-specific files infer normalized store name from filename.

## Validation

- All 10 target files were parsed.
- All 10 import batches completed.
- Sales data landed in `sap_sales`.
- Inventory data landed in `sap_inventory`.
- `raw_data` JSON is preserved for every row.
- Production SAP remained untouched.
