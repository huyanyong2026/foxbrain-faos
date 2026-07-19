# VAFOX Phase 4A — Huyan CEO Control Plane 只读接入 Artifact

> **状态：Draft（草案）— 未审批不得执行。**
>
> 本 Artifact 定义 `huyan.vafox.com` 通过 Gateway 对 `control.vafox.com` 实施第一阶段安全只读接入的审批边界、控制要求、验证证据与回滚要求。它不是执行授权；不得据此部署、修改配置、签发凭据、连接生产数据或对 Agent 发起操作。

## 一、Artifact Metadata

| 字段 | 内容 |
| --- | --- |
| Artifact ID | `VAFOX-P4A-HUYAN-READONLY-001` |
| 标题 | VAFOX Phase 4A Huyan CEO Control Plane 只读接入 Artifact |
| 版本 | `v1.0.0-draft` |
| 创建日期 | `2026-07-19 UTC` |
| 生成工具 | Codex（文档生成；未连接目标环境） |
| 目标系统 | `huyan.vafox.com`、`control.vafox.com`（唯一入口：`gateway.vafox.com`） |
| 前置状态 | Phase 3 Agent Hub Completed；执行前须复核其审批、健康、审计与发布状态。 |
| 风险等级 | **High**：涉及 CEO 私有摘要、经营聚合信息、身份权限和跨系统读取边界。 |
| 审批状态 | **Draft — 未审批，不得执行。** |
| 执行窗口 | `{{APPROVED_CHANGE_WINDOW_UTC}}` |
| 回滚位置 | `{{APPROVED_CONFIG_RELEASE_REF}}`、`{{APPROVED_GATEWAY_POLICY_VERSION}}`、`{{APPROVED_DASHBOARD_RELEASE_REF}}`；证据归档：`{{APPROVED_EVIDENCE_URI}}`。 |
| 关联计划 | `VAFOX_PHASE4A_HUYAN_READONLY_INTEGRATION_PLAN.md` |
| 验收报告 | `VAFOX_PHASE4A_HUYAN_READONLY_ACCEPTANCE_REPORT.md` |

### 1.1 责任、审批与停止条件

| 角色 | 执行前必须确认 | 职责 |
| --- | --- | --- |
| 业务负责人 | `{{BUSINESS_OWNER}}` | 确认 CEO 使用范围、数据口径及灰度名单。 |
| 安全/权限审批人 | `{{SECURITY_APPROVER}}` | 批准 RBAC、ABAC、MFA、令牌、Secret 与审计控制。 |
| Control Plane 负责人 | `{{CONTROL_OWNER}}` | 确认只读投影、API 契约及无写路径。 |
| 执行负责人 | `{{EXECUTION_OWNER}}` | 仅于批准窗口执行已批准变更并记录脱敏证据。 |
| 回滚负责人 | `{{ROLLBACK_OWNER}}` | 验证 API、访问、配置和 Dashboard 的恢复路径。 |
| 独立复核人 | `{{REVIEWER}}` | 复核门禁、测试证据、审计与最终结论。 |

出现以下任一情况必须停止、维持默认拒绝并不得进入下一步：审批或窗口缺失/过期；目标域名、身份或版本不匹配；Gateway、MFA、审计或撤销验证失败；发现非 `GET`/`HEAD` 方法、Agent 控制路径或生产明细访问；CEO Private Brain、Employee AI 或 Core Data 隔离失效；无法完成已验证回滚。

## 二、Phase 4A 范围与不可变边界

### 2.1 允许范围

- 版本化 **Read Only API** 的受控读取。
- Dashboard 对已发布快照的数据读取与展示。
- 已发布 Agent 状态展示。
- 已审核、已发布 Report 展示。
- 符合 CEO 私有策略的 CEO Summary 展示。

### 2.2 明确禁止

- 写入、修改或删除 Control Plane 的配置、任务、状态、报告或策略。
- 修改、调度、启动、停止、重试、暂停、恢复或编排任何 Agent。
- 直接或间接接入生产 Core Data、原始表、生产明细或个人敏感信息。
- 绕过 Gateway，或直接访问 Agent Runtime、Agent Hub 内部端点、数据库和数据源。
- 因故障扩大角色、scope、属性范围，或使用共享帐号、管理员 Token、长期静态 Token 规避控制。

只读接入的唯一目标是展示经过发布、质量校验、脱敏和权限过滤的聚合事实；它不提供执行能力、行动入口、回调地址、Webhook、任意查询表达式或内部资源路径透传。

## 三、数据架构与来源

### 3.1 逻辑数据流

```text
Huyan（huyan.vafox.com）
            |
            | Gateway SSO / MFA / Token / Policy / Audit
            v
Read Only API（control.vafox.com/api/v1/readonly）
            |
            | 已发布、只读、脱敏的聚合快照
            v
Control Plane
            |
            | 仅消费已完成的受控输出；查询不得触发运行
            v
Agent Hub
```

`gateway.vafox.com` 是唯一身份与访问入口。Huyan 不直连 Agent Hub、Agent Runtime、数据库或 Core Data；Control Plane 也不得因本链路的读取请求启动 Agent、刷新生产数据或创建任何任务。

### 3.2 数据来源与发布控制

| 来源 | 可发布到只读视图的内容 | Huyan 展示形式 | 永不暴露 |
| --- | --- | --- | --- |
| `health-agent` | 匿名化服务状态、告警等级、最近检查时间。 | 健康卡片与趋势。 | 主机/内网拓扑、原始日志、凭据、修复命令。 |
| `connectivity-agent` | Gateway→Huyan→Control 的逻辑连通结果、延迟区间、检查时间。 | 链路状态与异常摘要。 | IP、端口、路由规则、网络诊断原文。 |
| `report-agent` | 已审核日/周/月报告、版本、数据截止时间与授权摘要。 | 报告目录、摘要及授权正文。 | 草稿、中间文件、未发布附件、个人数据明细。 |
| `data-agent` | 数据新鲜度、完整性、口径版本、质量异常及批准的聚合指标。 | 数据可信度与聚合经营指标。 | Core 原始记录、PII、访问凭据。 |
| `ceo-agent` | 已发布 CEO Summary、战略风险、关键异常和待关注事项。 | CEO 私有摘要或授权高管摘要。 | 推理链、提示词、私有笔记、未批准建议、行动指令。 |

每个响应必须带有 `as_of`、`snapshot_id`、`source`、`classification`、`policy_version` 和 `request_id`。未完成、过期、质量失败、未审核或分类不允许的数据不得进入 Read Only API、缓存、索引、导出或 Dashboard。

### 3.3 隔离要求

| 数据域 | 隔离控制 | Phase 4A 规则 |
| --- | --- | --- |
| CEO Private Brain | 独立分类、加密上下文、令牌 audience/scope、缓存命名空间与 ABAC 策略。 | 仅显式 CEO scope 且属性通过时读取已批准摘要；不得复制原文。 |
| Employee AI | 独立产品、会话、检索索引、服务身份及策略域。 | 不可读取、检索、推断或继承 CEO Private Brain 内容。 |
| Core Data | 既有企业核心数据治理、数据源身份与访问边界。 | 不直接接入；仅消费批准的脱敏聚合发布视图，不提供生产明细。 |

隔离必须在 Gateway、API、服务身份、数据视图、缓存、日志、索引、备份及导出层均有效；前端隐藏字段绝不能替代服务端授权。

## 四、Read Only API 设计

### 4.1 通用契约

| 项目 | 强制要求 |
| --- | --- |
| 版本控制 | 基础路径固定为 `https://control.vafox.com/api/v1/readonly`。破坏性变更仅能以新主版本发布；响应中返回 `meta.api_version`。 |
| 认证 | `Authorization: Bearer <access_token>`；Gateway 签发并由 Control Plane 再校验签名、发行方、受众、到期、撤销、主体、租户、角色、scope 与 ABAC 属性。 |
| 只读权限 | 仅允许 `GET`、`HEAD`；其他 HTTP 方法一律 `405 Method Not Allowed`，并产生审计事件。 |
| 最小查询 | 仅允许预定义枚举、筛选字段、分页上限和时间窗；禁止 SQL、任意表达式、Agent 参数与内部路径透传。 |
| 通用响应 | JSON：`data` 与 `meta.{api_version,as_of,snapshot_id,source,classification,policy_version,request_id}`。 |
| 错误处理 | 无 Token/无效 Token 为 `401`；策略拒绝为 `403`；不存在为 `404`；禁止方法为 `405`。错误不得泄露内部实现或敏感数据。 |

### 4.2 接口清单

| API | 路径与方法 | 最小只读 scope | 返回范围 | 明确排除 |
| --- | --- | --- | --- |
| Agent Status API | `GET /agent-status` | `agent:status:read` | 已发布 Agent 状态、最近成功时间、快照 ID、业务异常摘要。 | 配置、队列、任务参数、日志、控制操作。 |
| Health API | `GET /health` | `health:read` | API/发布快照的匿名化健康、依赖摘要、最后检查时间。 | 服务器、堆栈、配置、地址、凭据。 |
| Report API | `GET /reports?period={daily|weekly|monthly}&as_of={date}`；`GET /reports/{report_id}` | `report:read` | 经审核发布的元数据、摘要和按策略过滤的正文。 | 草稿、未当前版本、未授权附件、明细。 |
| CEO Summary API | `GET /ceo-summary?as_of={date}` | `ceo:summary:read` | 已发布经营概览、战略风险、关键异常、待关注事项。 | Private Brain 原文、推理过程、笔记、写入口。 |
| Decision Template API | `GET /decision-templates`；`GET /decision-templates/{template_id}` | `decision:template:read` | 已批准的只读决策模板、版本、适用范围与展示字段。 | 模板创建/修改/审批、执行参数、任务触发。 |

全部端点须通过 Gateway 路由；服务账户也仅有受众限定、短期、最小只读 scope。Dashboard 只能调用这些已批准路径，且不显示暗含写入或 Agent 操作的控件。

## 五、权限设计

RBAC 定义职能基线，ABAC 在每次请求中校验主体、资源、环境与数据属性；**两者均须满足**。Gateway 负责集中策略决策，Control Plane 必须二次校验关键 scope 并按策略过滤数据。

| 主体 | RBAC 基线 | 必须满足的 ABAC 条件 | 可读范围 |
| --- | --- | --- | --- |
| CEO | `ceo` | `tenant_id` 匹配、MFA 完成、受管设备/允许会话、`ceo_private_access=true`、分类和有效期允许。 | CEO Summary、全部已发布聚合报告、Agent 状态、Health、Decision Template。 |
| 高管 | `executive` | `tenant_id`、部门/区域/门店范围、报告分级、MFA、会话风险和有效期均通过。 | 职责范围内发布报告、授权经营摘要、Agent 状态、Health、Decision Template。 |
| 员工 | `employee` | 即使租户或组织属性匹配，也不签发本阶段 CEO Control Plane API scope。 | **无本阶段数据访问权。** |

CEO Private Brain 权限不得因角色继承赋予高管或员工；跨租户、跨组织范围、过期快照、未完成 MFA、异常会话与无授权字段均默认拒绝。策略变更必须经批准、版本化、审计并在回滚清单中登记。

## 六、安全设计

### 6.1 MFA、Token 与 Secret

- CEO 和高管必须使用 MFA；新设备、异常地理位置、会话风险升高、敏感 CEO Summary 读取或策略变化时应重新验证。
- 访问 Token 必须短期、受众限定为 Read Only API、包含最小 scope；禁止通用管理员 Token、长期静态 Token 和共享身份。
- Huyan 不持久化用户 Bearer Token。服务间身份必须独立、最小权限、可轮换、可撤销，并与用户 Token 分离。
- Secret 仅存放于批准的 Secret 管理系统，按服务和环境隔离访问；Artifact、代码、Dashboard、日志、报告与备份均不得记录 Secret 明文。

### 6.2 API 审计与访问日志

每个认证、授权、拒绝、Token 撤销、策略变更和 API 请求必须产生可关联、UTC 时间的审计事件，至少记录：`request_id`、主体/服务身份、角色、scope、ABAC 决策、MFA 结果、资源、分类、快照 ID、策略版本、状态码、返回记录数和时间。审计日志须防篡改、最小访问、受控保留；不得包含 Token 明文、CEO Private Brain 正文、PII 或 Core 原始数据。

### 6.3 技术强制控制

| 控制层 | 强制控制 |
| --- | --- |
| Gateway | SSO、MFA、令牌签发/撤销、路由 allowlist、方法限制、限流、WAF 与统一审计。 |
| Control Plane | 令牌与策略二次校验、只读路由、响应字段过滤、发布快照校验、默认拒绝。 |
| 数据层 | 仅受控只读投影；无数据库透传；独立读身份；无生产明细访问。 |
| Dashboard | 仅展示授权 API 响应、显示数据时间与分类、无写控件、无 Token 本地持久化。 |
| 监控 | 401/403/405 异常、速率异常、跨域/跨范围尝试、审计缺失与快照过期必须告警。 |

## 七、灰度接入流程

| 阶段 | 准入与操作范围 | 必须验证 | 放行门槛 |
| --- | --- | --- | --- |
| Step 1：内部测试 | 仅测试环境；仅合成或批准的脱敏数据；不连生产 Core Data。 | Gateway→Huyan→API 链路、MFA、Token、RBAC/ABAC、字段过滤、`405`、审计和数据口径。 | 全部测试通过，且无写路径、无 Agent Runtime 直连。 |
| Step 2：小范围灰度 | 仅明确批准的少量 CEO/高管账户；有限报告、Health 和状态快照；设限流和观察窗口。 | 快照一致性、拒绝日志、权限矩阵、缓存隔离、告警与回滚演练。 | 安全/业务负责人签字，异常已关闭或已批准处置。 |
| Step 3：CEO 正式使用 | 仅在前两步验收与变更审批完成后，按版本化配置逐步开放。 | 连续审计、MFA、数据时效、Dashboard 可用性、撤销和回滚可操作性。 | 正式验收报告完成且所有批准引用有效。 |

任一阶段失败均不得跳过验证直接扩大访问范围；应关闭 API 或撤销相应访问，并从 Step 1 的受控验证重新开始。

## 八、回滚方案

回滚触发条件包括越权、发现写路径、数据不一致、异常流量、审计缺失、Token 泄露、隔离失效、快照错误或严重漏洞。回滚负责人必须保留脱敏证据，并且不得通过放宽权限、关闭审计或接入生产数据来恢复服务。

| 顺序 | 回滚操作 | 最低验证 |
| ---: | --- | --- |
| 1 | **API 关闭**：在 Gateway 禁用 Huyan→Read Only API 路由/策略，或使 API 进入维护拒绝模式。 | 新增请求被拒绝；无绕过 Gateway 的有效路径。 |
| 2 | **访问撤销**：撤销用户会话、服务身份与 Token；移除灰度组成员；轮换可能暴露的凭据。 | 被撤销 Token 和会话无法访问；撤销事件可审计。 |
| 3 | **配置恢复**：恢复最近验证的 Gateway allowlist、RBAC/ABAC 策略、API 契约、数据视图与功能开关版本。 | 策略/配置版本与批准基线一致，默认拒绝仍有效。 |
| 4 | **Dashboard 恢复**：回退到不调用该 API 的已验证 Dashboard release，清除受控缓存并移除入口。 | 不显示受保护数据；无残留缓存、写控件或活跃连接。 |

回滚后须封存审计记录、确认无 Control 写入和 Agent 执行、评估数据暴露范围，并在修复后从内部测试重新验证。

## 九、验收标准与证据

| 验收项 | 通过标准 | 必备证据 |
| --- | --- | --- |
| API 读取成功 | 已授权 CEO/高管可经 Gateway 读取其允许的五类 API 数据。 | 脱敏请求/响应、`request_id`、快照 ID、审计引用。 |
| Dashboard 显示正常 | Dashboard 正确显示状态、报告、Health、授权摘要及数据时间/分类。 | UI 验证记录、版本引用、授权账户测试结果。 |
| 权限正确 | CEO、高管、员工、无 Token、错误 Token、跨范围请求均符合预期。 | RBAC/ABAC 测试矩阵、401/403 审计事件。 |
| 无写权限 | 所有公开路径的 `POST`/`PUT`/`PATCH`/`DELETE` 均被拒绝；无 UI/后台写入口。 | `405` 测试、路由清单、服务身份与 UI 复核。 |
| 审计正常 | MFA、Token、策略、访问结果、快照和撤销均可关联且不泄露敏感内容。 | 审计样本、日志脱敏复核、告警测试。 |
| 可回滚 | API 关闭、访问撤销、配置恢复、Dashboard 恢复已于非生产环境验证。 | 回滚演练记录、版本/证据引用、复核签字。 |

## 十、执行前门禁与报告要求

执行前须全部满足：Artifact 已批准；执行窗口、负责人和回滚负责人已确认；Phase 3 状态复核通过；API/OpenAPI 契约、Gateway 策略、RBAC/ABAC 矩阵与数据分类已获批准；合成/脱敏测试数据可用；审计、告警、Token 撤销和回滚演练可验证。

实际执行必须使用 `VAFOX_PHASE4A_HUYAN_READONLY_ACCEPTANCE_REPORT.md`，完整填写执行时间、执行人、Artifact 版本、接入内容、验证结果、异常和回滚。未获批准或未满足门禁时，报告只能标记“未执行”，不得伪造通过证据。

## 十一、禁止事项

1. **禁止绕过 Gateway**：浏览器、Huyan、脚本、服务或任何外部主体不得直连 Control 内部接口、Agent Hub、Agent Runtime、数据库或数据源。
2. **禁止直接访问 Agent Runtime**：Read Only API 不代理 Agent endpoint，查询不得触发 Agent 的运行、重试、停止或调度。
3. **禁止写入 Control**：不得创建、修改、删除或审批 Control Plane 资源、任务、报告、策略或配置。
4. **禁止生产数据访问**：不得读取生产 Core Data、原始表、个人敏感信息、未发布数据或生产明细。
5. **禁止权限扩大**：不得使用共享帐号、角色继承、前端隐藏、管理员/长效 Token 或临时宽松策略扩大访问。

## 结论

本 Artifact 将 Huyan CEO Control Plane 第一阶段限定为经 Gateway、经 MFA、经 RBAC+ABAC 的版本化只读访问。只有已发布的脱敏聚合快照可供展示；CEO Private Brain、Employee AI 与 Core Data 保持隔离；Control Plane、Agent Hub 和生产数据均不获得任何写入、调度或直连能力。**在 Draft 未获批准前，本 Artifact 不可执行。**
