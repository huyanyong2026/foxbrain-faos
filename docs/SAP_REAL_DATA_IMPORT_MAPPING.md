# SAP Real Data Import Mapping

This document records the real SAP export format used by Sprint007. The import remains file-based only: no production SAP connection, no SAP database write, and no program installed on the SAP production server.

## File Format

The current `.xls` exports in `sap数据.zip` are mostly GB18030/GBK encoded tab-separated text files, not real Excel binary workbooks.

Importer behavior:

- `.csv`: decode as UTF-8 BOM, GB18030, GBK, UTF-16, or fallback UTF-8 ignore.
- `.xls`: if it is not OLE Excel binary, parse as delimited text.
- Delimiter detection prefers tab, comma, or semicolon.
- Raw row data is always preserved in `raw_data` JSON.

## Inventory Export Fields

Observed total inventory headers:

```text
物料编码, 物料名称, 条码, 库存量, 可用量2, 库存单位, 已承诺, 已订购, 可用量, 成本价, 成本金额, 规格, 默认供应商编码, 默认供应商, 件数, 散数, U_BPrice1...
```

Observed store inventory headers:

```text
商品编码, 商品名称, 条码, 目录规格, 位置编码, 位置名称, 仓库, 库存量, 单位, 成本价, 零售价, 库位
```

Mapping to `sap_inventory`:

- `snapshot_date`: empty for current exports unless provided later.
- `store_name`: `仓库`; if missing, infer from filename such as `南山店库存7.9.xls`.
- `store_code`: `位置编码` / `仓库代码`.
- `product_code`: `商品编码` / `物料编码`.
- `product_name`: `商品名称` / `物料名称`.
- `barcode`: `条码`.
- `quantity`: `库存量`.
- `cost_amount`: `成本金额`; if absent, `库存量 × 成本价`.
- `retail_amount`: `零售金额`; if absent, `库存量 × 零售价` or `库存量 × U_BPrice1`.
- `raw_data`: complete original row JSON.

## Sales Export Fields

Observed sales headers:

```text
客户编号, 客户名称, 日期, 单号, 物料编号, 物料名称, 规格, 数量, 金额, 毛利, 联系人, 参考编号, 单据折扣率, 备注, 销售代表, 条码, 销售单位, 颜色, 内部核算价, 内部核算成本, 核算毛利率(%), 客户采购单号, 总额, 总额(外币), 总额(系统币)
```

Mapping to `sap_sales`:

- `sale_date`: `日期`.
- `store_name`: infer from filename first for store files; otherwise use `客户名称`.
- `store_code`: `客户编号`.
- `employee_name`: `销售代表`.
- `product_code`: `物料编号`.
- `product_name`: `物料名称`.
- `barcode`: `条码`.
- `quantity`: `数量`.
- `amount`: `金额`.
- `cost`: `内部核算成本`.
- `gross_profit`: `毛利`.
- `raw_data`: complete original row JSON.

## Store Inference

When the filename contains a known store name, the importer writes that normalized store name:

- `南山店`
- `振兴店`
- `航苑店`
- `金沙店`
- `微店`
- `网店`

For total sales files, the importer keeps row-level `客户名称`.

## Initial Priority Files

- `库存7.9.xls`
- `南山店库存7.9.xls`
- `振兴店库存7.9.xls`
- `航苑店库存7.9.xls`
- `金沙店库存7.9.xls`
- `总销售261.1-7.9.xls`
- `南山店销售1.1-7.9.xls`
- `振兴店销售1.1-7.9.xls`
- `航苑店销售1.1-7.9.xls`
- `金沙店销售1.1-7.9.xls`

## Safety

This mapping is for uploaded/exported files only. It does not grant permission to connect to or modify production SAP.
