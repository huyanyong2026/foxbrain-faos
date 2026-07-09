# 03 Database Design / 数据库设计

当前门户使用 SQLite，生产同步数据使用 PostgreSQL。

## SQLite 表

- `users`：用户、角色、状态、登录安全。
- `records`：统一档案记录。
- `knowledge_items`：知识库条目。
- `uploaded_files`：上传文件元数据。
- `activity_log`：操作日志。
- `timeline_events`：时间轴。
- `relations`：对象关联关系。

## PostgreSQL 同步表

由 `sync_sap_b1.py` 维护：

- `sap_customers`
- `sap_items`
- `sap_warehouses`
- `sap_salespersons`
- `sap_stock_by_whs`
- `sap_sales_invoices`
- `sap_sales_invoice_lines`
- `sap_purchase_orders`
- `sap_daily_sales_summary`
- `sap_store_sales_summary`
- `sap_sync_runs`

## 迁移原则

- 使用 `create table if not exists` 保持兼容。
- 不删除旧字段。
- 新表新字段必须兼容已有数据。

