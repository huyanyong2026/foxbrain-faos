# VAFOX CEO Today Production Data Binding Report

## 结论

**目标状态：`CEO_Today_Real_Data_Ready`**

CEO Today 已固定使用 CEO API `GET /api/ceo/today`。浏览器不访问 SAP B1、SAP Mirror 或 Data Core；服务端只读转发 Data Core 提供的 CEO Today 合同，并且没有本地快照、mock、演示数据或静态业务数字回退。

## 生产数据链路

`SAP B1 → SAP Mirror → Data Core → CEO API → CEO Today 前端`

本次未修改 SAP B1、SAP Mirror、Data Core 表结构、Auth 或 AI Runtime。

## 绑定清单

| 页面字段 | CEO API 字段 | 规则 |
| --- | --- | --- |
| 今日销售额 | `sales` | 原值展示 |
| 今日订单 | `orders` | 原值展示 |
| 客单价 | `sales / orders` | 仅在订单数大于 0 时计算 |
| 有效库存 SKU | `effective_skus` | 不读取历史 SKU |
| 客户机会 | `customer_opportunities` | TOP5 仅由该数组产生，不读取供应商字段 |
| TOP 品牌销售 | `top_brands[].brand_name` | 不接受 `brand_code` 或 `item_code` 作为展示名称 |
| 数据状态 | `data_source`, `updated_at`, `confidence` | 页面独立展示数据血缘信息 |

## 门店边界

前后端采用双层只读白名单，仅展示 `zhenxing`（振兴）、`nanshan`（南山）、`hangyuan`（航苑）、`jinsha`（金沙）、`online`（网店）。武侯祠及其他历史门店即使出现在上游响应中也不会进入页面。

## 异常与真实性保证

- CEO API 不可用、非 2xx 或关键指标/血缘字段无效时，页面显示“数据暂不可用”。
- Data Core 客户端未配置或合同无效时，CEO API 返回 HTTP 503。
- 不使用本地快照填充 `/api/ceo/today`，不在失败时生成 AI 摘要、建议或数字。
- API 对外合同只复制客户机会的 `title` 与 `reason`，避免供应商结构混入。

## 验收状态

- 固定视觉区块保留：Header、六个指标、五店状态、AI 摘要、风险预警、TOP 品牌、客户机会 TOP5。
- 数据绑定符合生产只读边界。
- 最终状态：`CEO_Today_Real_Data_Ready`。
