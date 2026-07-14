# SAP Real Data Import Mapping｜火狐狸真实 SAP 数据导入映射说明

Version: 2026-07-09
Target Sprint: Sprint007 SAP Data Import Foundation
Data package: sap数据.zip, 店铺费用202605.zip

---

## 1. Purpose

This document records the real SAP export files provided by Huohu Fox and defines the first import mapping for VAFOX Data Lake.

Sprint007 should use this mapping to import real SAP Excel/CSV-like files safely.

Important: Many `.xls` files are actually GBK-encoded tab-separated text files, not binary Excel workbooks. The importer must detect this format and parse it correctly.

---

## 2. Safety Rule

Do not connect to the production SAP server.

Do not install any software on the SAP production server.

Only import user-uploaded exported files.

Original files must be preserved in VAFOX Drive.

---

## 3. File Format Detection

For `.xls` files, do not assume binary Excel.

Detection order:

1. Try reading as text using GBK / GB18030.
2. If first line contains tab characters, parse as TSV.
3. If text parsing fails, then try Excel parser.
4. Always preserve raw file and raw row data.

---

## 4. First Priority Files

Import these first:

```text
sap数据/库存7.9.xls
sap数据/南山店库存7.9.xls
sap数据/振兴店库存7.9.xls
sap数据/航苑店库存7.9.xls
sap数据/金沙店库存7.9.xls
sap数据/总销售261.1-7.9.xls
sap数据/南山店销售1.1-7.9.xls
sap数据/振兴店销售1.1-7.9.xls
sap数据/航苑店销售1.1-7.9.xls
sap数据/金沙店销售1.1-7.9.xls
sap数据/微店销售1.1-7.9.xls
sap数据/网店销售1.1-7.9.xls
```

Then import monthly 2025 sales:

```text
2501销售.xls ... 2512销售.xls
```

Then import brand sales:

```text
25kailas销售.xls
26kailas销售.xls
25猛犸象销售.xls
26猛犸象销售.xls
```

---

## 5. Sales Files Mapping

Typical sales header:

```text
客户编号	客户名称	日期	单号	物料编号	物料名称	规格	数量	金额	毛利	联系人	参考编号	单据折扣率	备注	销售代表	条码	销售单位	颜色	内部核算价	内部核算成本	核算毛利率(%)	客户采购单号	总额	总额(外币)	总额(系统币)
```

Older 2025 monthly files may not include `物料编号`; they may start with:

```text
客户编号	客户名称	日期	单号	物料名称	数量	金额	毛利	备注	销售代表	条码	销售单位	颜色	内部核算价	内部核算成本	核算毛利率(%)...
```

### 5.1 sap_sales mapping

```text
客户编号 -> customer_code
客户名称 -> customer_name
日期 -> sale_date
单号 -> document_no
物料编号 -> product_code
物料名称 -> product_name
规格 -> specification
数量 -> quantity
金额 -> amount
毛利 -> gross_profit
销售代表 -> employee_name
条码 -> barcode
销售单位 -> sales_unit
颜色 -> color
内部核算价 -> internal_price
内部核算成本 -> internal_cost
核算毛利率(%) -> gross_margin_rate
备注 -> remark
总额 -> total_amount
```

Store inference:

- Filename contains 南山店 -> store_name = 南山店
- Filename contains 振兴店 -> store_name = 振兴店
- Filename contains 航苑店 -> store_name = 航苑店
- Filename contains 金沙店 -> store_name = 金沙店
- Filename contains 微店 -> store_name = 微店
- Filename contains 网店 -> store_name = 网店
- Filename contains 总销售 -> store_name can be inferred from 客户名称 when possible, otherwise blank or 总部

Brand inference:

- If filename contains kailas/KAILAS -> brand_name = KAILAS
- If filename contains 猛犸象 -> brand_name = Mammut / 猛犸象
- Otherwise leave blank for future product master matching.

All rows must save raw_data JSON.

---

## 6. Inventory Files Mapping

### 6.1 Total inventory file

File:

```text
sap数据/库存7.9.xls
```

Header:

```text
物料编码	物料名称	条码	库存量	可用量2	库存单位	已承诺	已订购	可用量	成本价	成本金额	规格	默认供应商编码	默认供应商	件数	散数	U_BPrice1...
```

Mapping:

```text
物料编码 -> product_code
物料名称 -> product_name
条码 -> barcode
库存量 -> quantity
可用量 -> available_quantity
库存单位 -> unit
成本价 -> cost_price
成本金额 -> cost_amount
规格 -> specification
默认供应商编码 -> supplier_code
默认供应商 -> supplier_name
```

### 6.2 Store inventory files

Files:

```text
南山店库存7.9.xls
振兴店库存7.9.xls
航苑店库存7.9.xls
金沙店库存7.9.xls
```

Header:

```text
商品编码	商品名称	条码	目录规格	位置编码	位置名称	仓库	库存量	单位	成本价	零售价	库位
```

Mapping:

```text
商品编码 -> product_code
商品名称 -> product_name
条码 -> barcode
目录规格 -> specification
位置编码 -> location_code
位置名称 -> location_name
仓库 -> warehouse
库存量 -> quantity
单位 -> unit
成本价 -> cost_price
零售价 -> retail_price
库位 -> bin_location
```

Store inference from filename:

```text
南山店库存7.9.xls -> 南山店
振兴店库存7.9.xls -> 振兴店
航苑店库存7.9.xls -> 航苑店
金沙店库存7.9.xls -> 金沙店
```

All rows must save raw_data JSON.

---

## 7. Suggested Enhancements for Sprint007

Sprint007 should add a real data package import mode:

```text
Import SAP ZIP
```

Workflow:

```text
Upload sap数据.zip
↓
Extract files safely
↓
Detect SAP file types by filename and header
↓
Create document records for each file
↓
Create sap_import_batches
↓
Parse TSV/Excel rows
↓
Import into sap_sales / sap_inventory
↓
Preserve raw_data
↓
Create summary
```

Do not import image files into SAP tables. Images should remain in Drive / Media and later be related to store objects.

---

## 8. Data Quality Rules

1. Empty rows should be skipped.
2. Invalid numeric fields should become null, not crash.
3. Invalid dates should be preserved in raw_data and counted as warnings.
4. Duplicate rows should not crash the import.
5. The importer should record success_count and failed_count.
6. Every imported row must preserve batch_id and raw_data.

---

## 9. Dashboard Summary for Imported Data

After import, CEO Dashboard should show:

- Last SAP import time
- Sales row count
- Inventory row count
- Import batch count
- Failed import count

---

## 10. Search Integration

Search should find:

- product_name
- product_code
- barcode
- store_name
- employee_name
- supplier_name
- imported file name

Search result types:

```text
sap_batch
sap_sales
sap_inventory
```

---

## 11. Acceptance Test With Real Files

Codex should test import with at least:

```text
库存7.9.xls
南山店库存7.9.xls
总销售261.1-7.9.xls
南山店销售1.1-7.9.xls
2501销售.xls
25kailas销售.xls
```

Acceptance:

- rows imported successfully
- batch summary created
- raw_data preserved
- Dashboard data updates
- Search can find at least one product from imported rows
- no production SAP connection
- smoke tests pass
