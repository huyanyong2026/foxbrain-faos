# VAFOX Huyan V2.0.2 CEO AI 经营日报 API 实施报告

## 1. 交付结论

已在 Business Application Layer 新增独立的 CEO AI 经营日报编排与只读查询能力。实现严格消费注入的六域只读合同与 AI Runtime 客户端，不修改 SAP B1、SAP Mirror、Data Core、Auth 或 AI Runtime 核心配置，也不向这些系统提供写路径。

日报只有在来源合同、更新时间、鲜度、可信度、证据引用和四板块输出全部通过确定性门禁后才可发布。依赖不可用、有效数据域不足或 Runtime 输出无法闭合引用时，系统持久化 `failed` 状态，四个内容板块保持为空，不生成替代数字或通用日报。

## 2. API 合同

| 方法 | 路径 | 用途 | 成功结果 |
| --- | --- | --- | --- |
| `POST` | `/api/ceo/daily-report/generate` | 按 `report_date` 生成日报 | `201 published/degraded`；数据不足返回 `422 failed` |
| `GET` | `/api/ceo/daily-report?report_date=YYYY-MM-DD` | 查询指定日期及其状态 | 完整报告或 `404` |
| `GET` | `/api/ceo/daily-report/latest` | 查询最近一份已发布或有限发布日报 | 完整报告或 `404` |
| `GET` | `/api/ceo/daily-report/history?limit=30&offset=0` | 分页查询组织内历史及状态 | 历史摘要列表 |

生成请求体：

```json
{"report_date":"YYYY-MM-DD"}
```

日期必须是 ISO 日期且不得晚于当前 UTC 日期。报告以 `organization_id + report_date + Asia/Shanghai + v2.0.2` 形成幂等键；已发布版本重复触发时直接返回原报告，防止历史事实被覆盖。

## 3. 数据、输出与质量门禁

编排器逐一请求 `sales`、`product`、`inventory`、`customer`、`employee`、`supply_chain`。每个域必须提供非空真实 `data_source`、可解析 `updated_at`、合法 `freshness_status`、合法 `confidence` 及具备内部追踪引用的 evidence。默认最低覆盖为六域，可由经治理的 `CEO_DAILY_REPORT_MINIMUM_DOMAINS` 运维配置调整。

Runtime 仅接收标准化 evidence，并须返回以下固定板块：

- `business_summary`（经营总结）；
- `business_opportunities`（经营机会）；
- `business_risks`（经营风险）；
- `ceo_actions`（CEO 行动建议）。

每个 Runtime 条目必须引用已提供的 `evidence_id`。服务端根据引用重新附加 evidence，并确定性计算条目和报告的 `data_source`、`updated_at`、`freshness_status`、`confidence`；Runtime 无权提高可信度或引入无来源事实。

## 4. 权限与隔离

读取接口仅接受 CEO、管理员或现有 Auth 明确授予 `ceo_daily_report:read` 的授权管理层。生成接口仅接受 CEO、管理员或 `ceo_daily_report:generate`，且要求网关验证后的 `ALL_DATA` 数据范围。所有身份信息只来自 Gateway 的可信请求头；查询参数和请求体不能扩大权限。

持久层按 `organization_id` 隔离指定日期、最新报告及历史列表。每次读取、生成和拒绝均进入现有 Business 审计链。Gateway 只对已验证的 Huyan `VAFOX_CEO + ALL_DATA` 身份追加内部 `ceo` 角色；未认证和未授权请求继续由现有边界分别返回 `401` 和 `403`。

## 5. 失败策略

- 六域合同缺失、字段非法、来源不可用或有效域低于门槛：`failed / insufficient_verified_domains`；
- 只读来源客户端或 Runtime 客户端未配置：`failed / report_dependencies_unavailable`；
- Runtime 缺少板块、总结为空、无证据引用或引用不存在：`failed / runtime_output_rejected`；
- 失败报告的 `confidence.level` 为 `unavailable`、`freshness_status` 为 `missing`，所有 section 数组为空；
- `latest` 只返回 `published` 或 `degraded`，不会把失败记录或上一日内容伪装为当日报告。

## 6. 运维配置

- `CEO_DAILY_REPORT_DB`：日报自身 SQLite 读模型位置，默认 `/var/lib/vafox/daily-report.db`；
- `CEO_DAILY_REPORT_MINIMUM_DOMAINS`：最低有效域数，默认 `6`。

生产接入需向 `BusinessStore` 提供只读 `core_client.get_daily_report_domain(domain, report_date)` 及 `ai_runtime_client.generate_daily_report(report_date, evidence)`。若任一依赖未提供，系统按上述策略失败关闭。

## 7. 验证覆盖

自动化测试覆盖六域成功发布、四板块与统一溯源字段、数据不足显式失败、空内容保护、同日幂等以及组织级历史隔离。现有 Huyan CEO 授权测试同步覆盖日报路由映射。
