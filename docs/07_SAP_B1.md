# 07 SAP B1 / SAP 接口规范

## 原则

- 不破坏现有 `sync_sap_b1.py`。
- 不在代码提交真实数据库密码。
- 生产环境使用只读账号。
- AI 回答必须说明数据更新时间。

## 已有同步范围

- 客户
- 商品
- 仓库
- 业务员
- 分仓库存
- 销售发票
- 销售明细
- 采购订单
- 每日销售汇总
- 门店销售汇总

## API 占位

- `/api/sap/business-analysis`
- `/api/sap/profit-analysis`
- `/api/sap/inventory-analysis`
- `/api/sap/sales-trend`
- `/api/sap/ai-analysis`

