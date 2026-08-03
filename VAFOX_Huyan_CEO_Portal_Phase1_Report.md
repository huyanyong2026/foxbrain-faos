# VAFOX Huyan CEO Portal Phase 1 Report

## 1. 交付结论

`huyan.vafox.com` 的 Phase 1 首页已按 **CEO 专用经营驾驶舱** 完成实现。默认页面为 `CEO Today`，受众明确为 CEO、董事和授权管理层；页面维持只读，并继续通过 Gateway 调用 CEO API，不建立前端数据库连接、本地快照、模拟数据或第二套事实数据。

本次代码范围仅包含：

- `apps/huyan-web/app/page.tsx`
- `apps/huyan-web/app/globals.css`
- 本交付报告

未修改 `ai portal`、`gateway portal`、API、认证、Data Core 或任何共享底层服务。

## 2. 页面实现

### 2.1 CEO Today 首页

- 使用白色内容卡、浅灰页面、黑灰文字及 VAFOX 橙色强调。
- 顶部标识“管理层专用”，页脚再次明确董事、CEO 与授权管理层边界。
- 默认展示经营全景、五店范围及 API 只读状态。
- 提供经营分析、商品分析、库存分析、客户分析、组织分析、供应链分析、AI 顾问七个深度模块入口。

### 2.2 AI 经营摘要

摘要按“结论 / 依据 / 建议”三段呈现，并同时显示：

- `data_source`：数据来源；
- `updated_at`：更新时间；
- `confidence`：可信状态。

AI 内容只读取 API 响应。页面明确说明 AI 不覆盖事实数据；API 失败时不生成替代摘要或建议。如果 API 提供 `ai_evidence`，页面逐条展示；当前合同未提供时，依据区域只声明本次分析使用的 API 数据域，不生成业务结论。

### 2.3 六个核心指标

| 指标 | 取值规则 |
| --- | --- |
| 销售额 | API `sales` |
| 订单数 | API `orders` |
| 客单价 | 仅使用 `sales / orders` 的确定性计算 |
| 库存金额 | API 可选字段 `inventory_amount`；缺失即显示“数据暂不可用” |
| 客户机会 | API `customer_opportunities.length` |
| 经营风险 | API `risks.length` |

既有 `effective_skus` 仍参与 API 合同有效性检查，但不再以 SKU 数量冒充需求明确指定的“库存金额”。

### 2.4 五店经营状态

前端白名单只允许：

1. 振兴（`zhenxing`）
2. 南山（`nanshan`）
3. 航苑（`hangyuan`）
4. 金沙（`jinsha`）
5. 网店（`online`）

其他历史门店即使出现在 API 响应内也不会显示。

### 2.5 风险、品牌与客户机会

- 风险区固定呈现库存风险、销售异常、客户风险、供应链风险、数据异常五类概览，并展示 API 返回的风险详情。
- TOP 品牌仅展示 `brand_name`、销售额与趋势；代码没有展示 `brand_code`。API 未返回趋势时明确显示“数据暂不可用”。
- 客户机会 TOP5 展示客户、机会类型、原因和建议动作。当前必选合同中的 `title` 和 `reason` 正常展示；可选 `opportunity_type` 与 `recommended_action` 未返回时明确显示“数据暂不可用”，不使用前端推断或模拟值。

## 3. 数据与权限边界

浏览器唯一业务数据请求为：

```text
GET /api/ceo/today
```

请求通过共享 `gatewayFetch` 发往已配置的 `NEXT_PUBLIC_API_BASE_URL`。Huyan 前端不包含数据库地址、数据库凭据或数据库 SDK。既有服务端 CEO 角色校验保持不变，前端没有新增扩大权限的请求，也没有为 AI 创建额外查询入口。

失败策略为 fail closed：HTTP 非成功响应、关键数字无效或血缘字段缺失时，页面展示“数据暂不可用”，不回退到静态业务数据。

## 4. API 合同差距

在不修改共享服务的代码边界下，Phase 1 UI 已为下列字段预留兼容读取能力；生产 API 应在后续合同升级中提供这些字段，页面才能完整显示事实值：

- `inventory_amount`
- `ai_evidence[]`
- `top_brands[].trend`
- `customer_opportunities[].opportunity_type`
- `customer_opportunities[].recommended_action`

在这些字段上线前，页面不会创建占位数字、虚构趋势、猜测机会类型或自动生成建议动作。

## 5. 验收结果

- [x] 首页默认 CEO Today。
- [x] AI 摘要包含结论、依据、建议、数据来源、更新时间和可信状态。
- [x] 六个核心指标名称与需求一致。
- [x] 只展示五个指定经营主体。
- [x] 风险覆盖五类经营预警视图。
- [x] TOP 品牌不展示 `brand_code`。
- [x] 客户机会 TOP5 使用 API 数据且不混入供应商信息。
- [x] 七个深度模块入口齐备。
- [x] 无数据库直连、无模拟业务数据、无第二套事实数据。
- [x] 修改范围限定在 Huyan Portal 与交付报告。

**Phase 1 状态：`HUYAN_CEO_PORTAL_PHASE1_UI_READY`。**
