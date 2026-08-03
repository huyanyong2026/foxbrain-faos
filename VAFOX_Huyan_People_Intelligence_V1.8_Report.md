# VAFOX Huyan Portal V1.8 People Intelligence 交付报告

## 交付范围

本次以 V1.7 为稳定基线，仅新增“组织分析”。CEO Today、经营分析、商品分析、库存分析、客户分析、SAP B1、SAP Mirror、Data Core、Auth 与 AI Runtime 的既有业务行为保持不变。

## 页面与能力

- **员工总览**：员工数量、有销售员工数量、销售覆盖率、订单数量、已归属销售贡献。
- **员工销售分析**：员工、门店、销售额、订单、客单价和逐日趋势；表头支持升降序切换。
- **员工能力分析**：以真实销售金额/订单、销售商品去重数、关联客户去重数呈现销售、商品和客户能力，不生成评分。
- **团队分析**：固定展示振兴、南山、航苑、金沙、网店的团队销售、人效和趋势。
- **成长建议**：严格采用“结论 / 依据 / 建议”结构，依据中明确已归属与待归属金额。

## API 与数据治理

新增只读 `GET /api/business/organization-analysis`。接口要求 Huyan CEO 身份及 `ALL_DATA` 范围，通过现有 Business API 读取 Data Core 的 `get_members()` 与 `get_sales()`；连接缺失或数据不可用时返回 503，不降级到 mock、fixture 或 faker。

员工或销售归属缺失时展示“销售归属待补齐。”。待归属订单和金额保留在独立治理桶中，不计入员工或团队，不进行平均分配，也不推测贡献。接口响应显式返回 `average_allocation: false` 与 `estimated_contribution: false`。

## 验证

覆盖聚合口径、待归属隔离、真实 API 不可用响应、前端 API 路径、五个模块、五个团队和治理文案。前端沿用 V1.7 的留白、橙色强调、描边卡片、数据溯源、响应式表格和移动端单列规范。
