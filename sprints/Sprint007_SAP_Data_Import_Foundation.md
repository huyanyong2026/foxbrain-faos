# Sprint007: SAP Data Import Foundation｜SAP 数据导入基础

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint001-006

---

## 1. Sprint Goal

建立安全的 SAP 数据导入基础，让 FoxBrain 可以从 SAP 导出的 Excel / CSV 文件中导入经营数据。

本 Sprint 不直接连接生产 SAP 数据库，不安装任何会影响 SAP 生产服务器的程序。

目标是先实现：

```text
SAP 导出 Excel/CSV
↓
上传到 FoxBrain Drive
↓
识别为 SAP 数据
↓
导入到经营数据表
↓
形成可查询、可搜索、可关联对象的基础经营数据
```

---

## 2. Safety Principle

> Production SAP must remain untouched.

严禁直接连接生产 SAP 服务器。

严禁要求在 SAP 生产服务器安装 AI、Python、Dify、n8n 或实验程序。

Sprint007 只做文件导入基础。

未来如需自动同步，也必须通过独立只读副本或夜间导出实现。

---

## 3. Supported Import Types

先支持以下 SAP 导出类型：

```text
sales          销售数据
inventory      库存数据
employee_sales 员工销售
brand_sales    品牌销售
category_sales 品类销售
purchase       采购数据
```

如果无法自动判断类型，允许用户手动选择。

---

## 4. Data Model

### 4.1 sap_import_batches 表

新增：

```text
sap_import_batches
```

字段建议：

```text
id
document_id
import_type
filename
status
row_count
success_count
failed_count
error_message
mapping JSON
created_by
created_at
updated_at
```

status 支持：

```text
pending
processing
completed
failed
```

### 4.2 sap_sales 表

字段建议：

```text
id
batch_id
sale_date
store_name
store_code
employee_name
employee_code
brand_name
category_name
product_code
product_name
barcode
quantity
amount
cost
gross_profit
raw_data JSON
created_at
```

### 4.3 sap_inventory 表

字段建议：

```text
id
batch_id
snapshot_date
store_name
store_code
brand_name
category_name
product_code
product_name
barcode
quantity
cost_amount
retail_amount
age_days
raw_data JSON
created_at
```

### 4.4 Flexible Import

不同 SAP 导出字段可能不一致，因此必须保存 raw_data JSON。

即使字段映射不完整，也不能丢失原始行数据。

---

## 5. UI Requirements

新增或升级页面：

```text
/sap-import
/data-import
```

页面名称：

```text
SAP 数据导入
```

### 5.1 Import Home

显示：

- 上传 SAP Excel / CSV
- 选择导入类型
- 最近导入批次
- 导入状态
- 成功/失败行数
- 错误信息

### 5.2 Mapping Preview

如果实现成本可控，提供字段映射预览：

- 原始字段名
- 系统字段名
- 示例值

如果暂时不做复杂映射，至少要显示读取到的列名和前 5 行预览。

---

## 6. API Requirements

新增或升级：

```text
POST /api/sap/import
GET  /api/sap/import-batches
GET  /api/sap/import-batches/:id
GET  /api/sap/sales
GET  /api/sap/inventory
GET  /api/sap/summary
```

---

## 7. Drive Integration

当用户上传 Excel / CSV 到 Drive 时，如果分类为 SAP数据，允许：

```text
导入为 SAP 数据
```

文件详情页显示：

- 是否已导入
- 导入批次
- 导入类型
- 行数
- 状态

---

## 8. Object Integration

导入数据时，尽量将 store_name、brand_name、employee_name、product_name 与 enterprise_objects 匹配。

如果找不到对象，不要自动乱建。

先记录为未匹配，并为未来提供“建议创建对象”的基础。

---

## 9. Dashboard Integration

CEO Dashboard 增加基础经营数据摘要：

- 最近 SAP 导入批次
- 销售数据行数
- 库存数据行数
- 最近导入时间

---

## 10. Search Integration

Global Search 可搜索 SAP 导入批次名称和基础 sales/inventory 数据。

搜索结果类型新增：

```text
sap_batch
sap_sales
sap_inventory
```

如性能有限，可先只搜索 batch 和产品/品牌/门店字段。

---

## 11. QA Acceptance

Sprint007 验收标准：

- /sap-import 或 /data-import 页面可访问。
- 能上传或选择一个 Excel/CSV 文件导入。
- 能选择导入类型。
- 能创建 sap_import_batches。
- 能导入销售数据到 sap_sales。
- 能导入库存数据到 sap_inventory。
- 能保存 raw_data JSON。
- 能查看导入批次状态。
- Drive 文件详情能看到导入状态。
- Dashboard 显示 SAP 导入摘要。
- 不连接生产 SAP。
- 不破坏 Sprint001-006 功能。
- 烟测通过。

---

## 12. Codex Implementation Instruction

Codex 必须从 main 拉取最新代码。

严禁推倒重写。

只做增量升级。

不要开发 ai.vafox.com。

不要直接连接生产 SAP。

不要要求安装任何程序到 SAP 生产服务器。

完成后提交代码并生成：

```text
SPRINT007_SAP_DATA_IMPORT_FOUNDATION_SUMMARY.md
```

总结必须包括：

- 新增数据表
- 新增 API
- 新增 UI
- 支持的导入类型
- 字段映射策略
- Dashboard 集成
- Search 集成
- 测试结果
- 已知限制
- 下一步建议
