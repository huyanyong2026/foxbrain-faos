# VAFOX Huyan CEO OS UI V1.0 交付报告

## 1. 交付结论

`huyan.vafox.com` 首页已完成 **VAFOX Huyan CEO Portal UI V1.0**：以 `CEO Today` 为默认经营入口，在一个克制、只读的管理层界面中集中呈现 AI 经营摘要、六项核心指标、五店状态、风险预警、TOP 品牌和客户机会 TOP5。

本次交付只修改 Huyan 前端页面及其交付文档。没有修改 SAP B1、Data Core、CEO API、Auth 或 AI Runtime。

## 2. 首页信息架构

### 2.1 CEO Today

页面由以下经营区块组成：

1. AI 经营摘要：结论、依据、建议、数据来源、更新时间与可信状态；
2. 六核心指标：销售额、订单数、客单价、库存金额、有效 SKU、客户机会；
3. 五店经营状态：振兴、南山、航苑、金沙、网店；
4. 风险预警：风险总量、分类统计和风险明细；
5. TOP 品牌：品牌、销售额和趋势；
6. 客户机会 TOP5：机会名称、类型、原因与建议动作。

### 2.2 导航

主导航完整提供：`CEO Today`、`经营分析`、`商品分析`、`库存分析`、`客户分析`、`组织分析`、`供应链分析`、`AI顾问`。桌面端和移动端均可横向访问，当前页使用 VAFOX 橙色进行轻量强调。

## 3. 数据接入与失败策略

页面唯一经营数据请求为：

```text
GET /api/ceo/today
```

请求继续通过共享 `gatewayFetch` 访问现有 CEO API。前端不连接数据库、不保存经营快照、不包含模拟数据，也不创建第二套事实源。

前端会校验核心数值、数据血缘字段和所有列表字段。HTTP 请求失败、必要字段缺失或字段类型不符合合同时，整体进入 fail-closed 状态并显示“数据暂不可用。”。可选字段或局部记录缺失时，仅对应位置显示“数据暂不可用。”，不会猜测、补齐或生成替代业务数据。

## 4. 数据映射

| UI 区域 | CEO API 字段 / 规则 |
| --- | --- |
| AI 结论 | `ai_summary` |
| AI 依据 | `ai_evidence[]`；缺失时显示不可用 |
| AI 建议 | `ai_recommendations[]` |
| 销售额 | `sales` |
| 订单数 | `orders` |
| 客单价 | 仅由 `sales / orders` 确定性计算 |
| 库存金额 | `inventory_amount`；API 未提供时显示不可用 |
| 有效 SKU | `effective_skus` |
| 客户机会数 | `customer_opportunities.length` |
| 五店状态 | `operating_stores[]`，按五个经营主体白名单排序 |
| 风险预警 | `risks[]` |
| TOP 品牌 | `top_brands[]`，最多五条 |
| 客户机会 TOP5 | `customer_opportunities[]`，最多五条 |
| 数据血缘 | `data_source`、`updated_at`、`confidence` |

当前 CEO API 未返回的可选字段包括 `inventory_amount`、`ai_evidence[]`、品牌趋势、机会类型及建议动作；UI 对这些字段统一展示“数据暂不可用。”，不使用 mock 数据。

## 5. 视觉与交互

- 白色内容卡与浅灰页面画布形成清晰但低对比的层次；
- 黑灰文字承担主要信息表达，仅用 VAFOX 橙色标记品牌、选中状态和需关注内容；
- 圆角、细描边、充足留白和紧凑排版形成 Apple / ChatGPT 式产品感；
- 无 ERP 表单堆叠、无大屏发光效果、无复杂色谱；
- 响应式布局覆盖桌面、平板和手机，移动端保持信息优先级与可读性；
- 页面明确标注“管理层专用”“只读”和数据同步状态。

## 6. 边界确认

- [x] 只调用现有 CEO API；
- [x] 不含 mock、静态经营数字或兜底业务结论；
- [x] 不修改 SAP B1；
- [x] 不修改 Data Core；
- [x] 不修改 CEO API；
- [x] 不修改 Auth；
- [x] 不修改 AI Runtime；
- [x] 业务数据不可用时明确显示“数据暂不可用。”。

**交付状态：`VAFOX_HUYAN_CEO_OS_UI_V1_READY`**
