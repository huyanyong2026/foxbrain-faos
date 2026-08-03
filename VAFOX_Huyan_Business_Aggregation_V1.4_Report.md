# VAFOX Huyan Portal V1.4 Business Aggregation Layer 交付报告

## 1. 交付结论

本次在既有 Business Application Layer 中新增只读业务聚合边界。聚合层只消费注入的真实 Data Core 客户端响应，不修改 SAP B1、SAP Mirror、Data Core、Auth 或 AI Runtime，也不提供本地数据回退。上游不可用或未配置时返回 `503`，不会生成替代经营事实。

## 2. API 合同

| API | 真实上游 | 聚合输出 |
| --- | --- | --- |
| `GET /api/business/sales-analysis` | Core sales | `summary`、固定五店 `stores[]`、按日期 `trend_series[]` |
| `GET /api/business/member-analysis` | Core members + sales | `members[]` 员工销售、`coverage_rate`、`pending_rows`、`completion_status` |
| `GET /api/business/customer-analysis` | Core customers + sales | 消费金额、购买次数、价值分层、经营机会 |
| `GET /api/business/supplier-analysis` | Core suppliers | 独立 `supply_chain` 域中的供应商采购与交付字段 |

四个接口沿用 Business Layer 的 CEO/Auth 上下文检查和审计记录。所有响应标记 `read_only: true`，并保留数据来源、更新时间及鲜度状态。

## 3. 数据与安全边界

- **不改变原始服务：** 聚合函数只处理 Core 返回对象，不向 Core 或其数据库写入。
- **无伪造数据：** 生产请求没有 mock、fixture、faker 或本地快照回退；缺少真实 Core 方法即明确返回 `503`。
- **客户域：** 仅以已授权客户主数据关联销售事实，输出客户价值与机会。
- **供应链域：** 使用独立 suppliers 输入，并以字段白名单输出；客户标识和客户属性不能进入供应商响应。
- **待补齐语义：** 未归属员工的销售进入 `pending_rows`；没有销售事实的员工标记 `pending_sales`；缺失门店事实标记 `pending`。

## 4. 页面接入

Huyan V1.4 经营分析页面已从 Core 原始接口切换到四个 `/api/business/*-analysis` 真实接口。销售、门店、员工、客户和供应商模块分别消费聚合合同；加载、无权限、空数据和错误状态继续显式展示，不使用浏览器端模拟数据。

## 5. 验收范围

自动化检查覆盖销售汇总/五店/趋势、员工覆盖率与待补齐、客户价值分层，以及供应商字段白名单隔离。前端静态合同检查确保页面不再直接加载 `/api/core/*`，且四个业务聚合接口均已声明。
