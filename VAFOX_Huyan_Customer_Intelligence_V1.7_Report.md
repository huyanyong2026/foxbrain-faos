# VAFOX Huyan Portal V1.7 Customer Intelligence 交付报告

## 1. 交付结论

在 V1.6 稳定版本上新增独立“客户分析”页面，沿用 VAFOX CEO OS 的侧栏、留白、橙色强调、卡片、表格和数据溯源规范。未修改 CEO Today、经营分析、商品分析、库存分析及 SAP B1、SAP Mirror、Data Core、Auth、AI Runtime。

## 2. 页面模块

1. **客户总览**：客户数量、活跃客户、消费金额、订单数量、平均消费、VIP 数量。
2. **客户价值分层**：VIP、高价值、成长、正常、流失风险；分层标签来自 Customer360，不在前端臆测。
3. **购买行为分析**：品牌偏好、品类偏好、消费周期、购买趋势。
4. **客户机会池**：读取 `customer_opportunities`，展示客户、机会类型、原因、依据、建议动作、负责人；仅接受复购、升级、召回、交叉销售四类合同值。

## 3. 真实数据链

页面只请求 `GET /api/business/customer-intelligence`。Business Layer 要求 Core 客户端同时提供 `get_customer360()` 与 `get_customer_opportunities()`；任一方法缺失、读取失败或合同异常均返回 `503`，不会退回本地快照，也不使用 mock、fixture、faker 或静态客户数据。

服务端仅规范 Customer360 已返回的客户事实、偏好、周期、趋势、价值标签和机会字段。可由事实行直接计算的汇总只做确定性聚合；没有数据时展示空态，不生成客户或机会。

## 4. 企业微信与只读边界

响应仅声明企业微信接口预留，`delivery_enabled = false`。页面明确显示“未启用推送、不自动执行”。新接口仅聚合读取并记录审计事件，不包含触达、任务派发、客户资料修改或任何 SAP/Core 写操作。

## 5. 权限

新路由沿用 Huyan Portal 的 `VAFOX_CEO + ALL_DATA` 映射及 Business Layer CEO 角色校验；数据范围不是 `ALL_DATA` 时返回 `403`。

## 6. 验证范围

- Python 单元测试验证六项总览、五层价值标签、购买行为、四类机会规范及企业微信关闭状态。
- Node 静态合同测试验证页面模块、字段、真实聚合 API 和禁止数据构造规则。
- TypeScript 检查验证页面类型与组件编译。
