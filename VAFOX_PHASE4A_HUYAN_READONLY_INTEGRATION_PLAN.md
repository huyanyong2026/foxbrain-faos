# VAFOX Phase 4A：Huyan CEO Control Plane 只读接入计划

- **阶段名称**：Phase 4A — Huyan Read-Only Integration
- **目标定位**：形成 Huyan CEO Control Plane 第一阶段只读接入标准。
- **前置状态**：Phase 3 Agent Hub 已完成。
- **执行边界**：本文仅为设计计划；不包含服务器登录、部署、配置变更、数据迁移或 Agent 执行。

## 0. 范围与设计原则

当前目标链路如下：

```text
gateway.vafox.com
        |
huyan.vafox.com
        |
control.vafox.com
        |
Agent Hub
```

Phase 4A 仅在既有 Gateway 身份边界内，让 Huyan 以经授权、可审计、不可写的方式读取 Control Plane 已发布的聚合事实、报告与健康状态。Control Plane 和 Agent Hub 在本阶段均不得因 Huyan 请求触发写入、任务下发、Agent 运行或生产数据查询。

设计遵循以下原则：

1. **Gateway 优先**：所有用户和服务访问均经 `gateway.vafox.com` 完成身份验证、令牌签发和策略决策。
2. **默认拒绝**：未明确授予的角色、属性、数据域、接口、字段和请求方法一律拒绝。
3. **最小披露**：返回满足 CEO 经营决策所需的最小聚合数据；优先使用摘要、脱敏字段和时间窗数据。
4. **只读可验证**：仅提供 `GET`/`HEAD` 接口；服务端、令牌 scope、网关策略和审计规则共同保证无写路径。
5. **可追溯与可回退**：每次访问有可关联的身份、策略、数据版本和审计事件；任一异常可立即关闭 API 并撤销访问。

---

## 一、Phase 4A 目标

### 1.1 为什么先采用只读接入

先采用只读接入是为了在不改变 Control Plane、Agent Hub 或 Core Data 状态的前提下，验证 Huyan CEO Control Plane 的身份链路、权限边界、数据口径、性能和审计能力。该方式将风险限定为经过治理的“信息展示风险”，避免在数据质量、业务审批、执行授权和生产运维流程尚未完成验证前产生“操作执行风险”。

只读阶段应实现：

- Huyan CEO 页面可读取由 Control Plane 发布的 Agent 状态、经营报告、CEO Summary 和平台健康摘要。
- 每个响应可标明来源、数据更新时间、数据版本/快照标识与脱敏级别。
- CEO 和获授权高管获得与职责相符的可见范围；员工无权看到 CEO 私有内容和敏感经营数据。
- 所有非只读 HTTP 方法、未授权 scope、跨组织/跨部门/跨门店访问均被拒绝并产生审计记录。

### 1.2 非目标

Phase 4A 不包括：写入 Control Plane、修改 Core Data、创建/审批/执行任务、触发 Agent、访问生产明细数据、直接访问 Agent Hub，或以本计划实施任何服务器操作。

---

## 二、架构设计

### 2.1 逻辑数据流

```text
Huyan CEO UI
    |
    | Gateway SSO、MFA、短期访问令牌
    v
Read Only API（control.vafox.com）
    |
    | 仅查询已发布的只读视图、快照与摘要
    v
Control Plane
    |
    | 内部受控聚合；不接受来自本链路的写入或执行请求
    v
Agent Hub
```

### 2.2 组件职责

| 组件 | Phase 4A 职责 | 明确边界 |
| --- | --- | --- |
| `gateway.vafox.com` | SSO、MFA 强制、令牌签发、RBAC/ABAC 策略判定、速率限制与统一审计。 | 不将身份令牌绕过 Gateway 直接交给后端。 |
| `huyan.vafox.com` | CEO/高管只读展示层；仅调用允许的 Read Only API。 | 不保存长期特权凭据，不直连 Control Plane 内部组件。 |
| `control.vafox.com` | 发布版本化的只读 API、聚合快照和数据血缘；验证令牌与策略结果。 | 不提供写接口、任务接口或 Agent 控制接口。 |
| Agent Hub | 向 Control Plane 提供已完成任务的状态和经发布输出。 | 不被 Huyan 直接调用，不因查询启动、停止或重试 Agent。 |

### 2.3 Read Only API 边界

Read Only API 是 Huyan 与 Control Plane 的唯一业务数据边界。接口仅从经过发布和校验的只读投影（read model）读取；不得透传数据库连接、原始表、内部 Agent endpoint 或可执行命令。响应应包含 `as_of`、`snapshot_id`、`source`、`classification` 与 `request_id`，以支撑数据解释和审计关联。

---

## 三、数据来源

所有来源均通过 Control Plane 进行规范化、质量校验、权限过滤和只读快照发布后，才可由 Huyan 消费。

| 来源 Agent | 可发布只读内容 | Huyan 可见形式 | 禁止暴露内容 |
| --- | --- | --- | --- |
| Health Agent | 服务可用性、依赖状态、最近检查时间、告警等级。 | 红黄绿健康摘要和趋势。 | 主机凭据、内网拓扑、原始日志、修复命令。 |
| Connectivity Agent | Gateway→Huyan→Control 的逻辑连通结果、延迟区间、检查时间。 | 链路状态和异常摘要。 | IP、端口、路由规则、网络诊断原始输出。 |
| Report Agent | 已审核的日/周/月经营报告、报告版本、数据截止时间。 | 报告目录、摘要与授权正文。 | 未审核草稿、报告生成中间文件、个人数据明细。 |
| Data Agent | 数据新鲜度、完整性、口径版本、质量异常和聚合指标。 | 数据可信度卡片、聚合经营指标。 | Core 原始记录、可识别个人信息、访问凭据。 |
| CEO Agent | CEO Summary、战略事项、经营风险、待关注问题和建议。 | CEO 私有摘要、经授权的高管摘要。 | 推理链、提示词、私有笔记、未批准建议及行动指令。 |

每条数据应带来源 Agent、生成时间、发布状态、有效期、数据分级和快照 ID。未完成、过期、质量校验失败或标记为内部/私有的数据不得发布到 Huyan。

---

## 四、API 设计

### 4.1 通用约定

- 基础路径：`https://control.vafox.com/api/v1/readonly`；Huyan 只能经 Gateway 路由访问。
- 允许方法：`GET`、`HEAD`；`POST`、`PUT`、`PATCH`、`DELETE` 一律返回 `405 Method Not Allowed`。
- 身份：`Authorization: Bearer <access_token>`；令牌须包含受众、到期时间、主体、角色、scope、租户和必要 ABAC 属性。
- 响应：JSON，包含 `data`、`meta.as_of`、`meta.snapshot_id`、`meta.source`、`meta.classification`、`meta.request_id`。
- 分页和筛选：仅允许预定义字段、枚举和上限；不接受 SQL、任意查询表达式、内部资源路径或 Agent 参数透传。
- 错误：未认证返回 `401`，无权限返回 `403`，资源不存在返回 `404`，不允许方法返回 `405`；错误响应不得泄露资源是否存在以外的敏感细节。

### 4.2 Agent 状态接口

`GET /agent-status`

返回 Agent Hub 已发布的 Health、Connectivity、Report、Data、CEO Agent 状态（如 `healthy`、`degraded`、`unavailable`、`stale`）、最近成功时间、输出快照 ID 与面向业务的异常摘要。仅展示状态，不返回 Agent 配置、队列、任务参数、日志或控制能力。

### 4.3 Report 接口

`GET /reports?period={daily|weekly|monthly}&as_of={date}`  
`GET /reports/{report_id}`

返回经审核并发布的报告元数据及符合调用者权限的数据内容，包括报告标题、期间、口径版本、数据截止时间、发布状态、摘要和授权正文。报告必须以 `report_id` 的不可预测标识访问；不得暴露草稿、非当前版本或未授权附件。

### 4.4 CEO Summary 接口

`GET /ceo-summary?as_of={date}`

仅向具有 `ceo:summary:read` scope 且满足 CEO 私有空间属性策略的主体提供 CEO Summary。响应可包含已发布的经营概览、战略风险、关键异常和待关注事项；不得包含 CEO Private Brain 原文、个人笔记、推理过程、行动执行入口或任何可写链接。

### 4.5 Health 接口

`GET /health`

返回 Read Only API 自身、已发布数据快照、关键依赖的匿名化健康状态，以及最后成功检查时间。该接口用于 UI 状态展示与监控，不泄露具体服务器、网络、凭据、堆栈、配置或内部依赖地址。

---

## 五、权限设计

权限以 RBAC 定义职能基线，以 ABAC 在请求时校验主体、资源、环境和数据属性；两者必须同时满足。权限策略由 Gateway 集中执行，并由 Control Plane 再次校验关键 scope 与数据过滤结果。

| 访问主体 | RBAC 基线 | ABAC 限制 | 可读取内容 |
| --- | --- | --- | --- |
| CEO | `ceo` | `tenant_id` 匹配、已完成 MFA、受管设备/允许会话、`ceo_private_access=true`、数据分类和有效期满足策略。 | CEO Summary、所有已发布的聚合报告、Agent 状态、健康摘要。 |
| 高管 | `executive` | `tenant_id`、部门/区域/门店范围、报告分级、MFA 与会话风险满足策略。 | 本职责范围内已发布报告、授权经营摘要、Agent 状态与健康摘要。 |
| 员工 | `employee` | 即使 tenant、部门或门店匹配，也不授予 CEO/高管只读 API scope。 | 本阶段无 Huyan CEO Control Plane 数据访问权。 |

员工不可见内容至少包括 CEO Summary、CEO Private Brain、跨部门经营汇总、利润与战略风险、原始健康/连通性细节、Core Data 明细、客户或员工个人信息、Agent 配置和审计记录。高管也不得因角色继承自动获得 CEO Private Brain 权限；该权限必须显式授予并满足 ABAC 条件。

---

## 六、数据隔离

| 数据域 | 存储/访问定位 | Phase 4A 规则 |
| --- | --- | --- |
| CEO Private Brain | CEO 私有逻辑域，独立数据分类、加密上下文和访问策略。 | 仅 CEO 的显式 scope 与 ABAC 条件可读取经批准的摘要；不向 Employee AI 或通用报告复制原文。 |
| Employee AI | 面向员工的独立产品/会话/检索域。 | 不读取 CEO Private Brain，不获得 Control Plane CEO API scope，不可反向推断 CEO 内容。 |
| Core Data | 企业核心数据域，保持既有数据库与数据治理边界。 | Huyan 不直接访问；Read Only API 只消费经授权的、脱敏的、聚合的发布视图，且不提供生产明细访问。 |

隔离应覆盖身份、令牌 audience/scope、数据库或数据视图、缓存键、日志、索引、备份和导出。不得使用共享服务账户、共享缓存命名空间或前端隐藏字段替代服务端访问控制。

---

## 七、安全设计

### 7.1 Token

- Gateway 签发短期、受众限定为 Read Only API 的访问令牌；令牌包含最小 scope，禁止使用通用管理员或长期静态 token。
- Huyan 不持久化用户 Bearer token；服务间调用采用独立工作负载身份、轮换凭据和最小只读 scope。
- Control Plane 校验签名、发行方、受众、到期时间、撤销状态、主体、租户、角色、scope 和 ABAC 属性；失败即拒绝。

### 7.2 MFA

CEO 和高管访问必须完成 MFA；遇到新设备、异常地理位置、会话风险升高、敏感 CEO Summary 访问或策略变更时，要求重新验证。员工即使完成 MFA 也不因此获得本阶段访问权。

### 7.3 审计

记录认证、授权决策、MFA 状态、请求 ID、主体/角色、资源、scope、数据分类、快照 ID、结果码、返回记录数、策略版本和时间。审计日志应防篡改、限制访问、保留可追溯期限；日志不得记录 token 明文、CEO Private Brain 正文、个人敏感字段或 Core 原始数据。

### 7.4 只读权限保证

网关路由、WAF/API 策略、应用路由、服务账户、数据库只读视图和测试用例共同实行 deny-by-default。接口不得携带任务触发、回调 URL、命令、Webhook、执行标识或可变更参数；任何写方法和 Agent 执行入口都必须在该 API 域外且默认拒绝。

---

## 八、部署策略

本计划不执行部署；后续实施须按以下门槛推进，并在每一阶段保留审计和回退证据。

1. **测试环境**：使用合成或已批准的脱敏数据，验证 Gateway→Huyan→Read Only API 链路、令牌校验、RBAC/ABAC、字段脱敏、只读方法限制、审计事件和数据口径。不得连接生产 Core Data。
2. **灰度环境**：仅向少量明确授权的 CEO/高管账户开放，只发布有限报告和健康摘要；设置限流、观察窗口、访问告警和人工复核，持续比对快照一致性与拒绝日志。
3. **正式环境**：在测试与灰度验收全部通过、权限审批完成、回滚演练通过、监控告警就绪后，按版本化配置逐步开放。正式环境仍只允许已发布的只读视图，不改变 Agent Hub 或 Core Data 的运行状态。

每阶段升级前均需完成安全评审、数据分级确认、API 契约检查、权限矩阵评审和回滚负责人确认。

---

## 九、回滚方案

触发条件包括越权访问、数据不一致、异常流量、审计缺失、发现写路径、令牌泄露或高风险漏洞。回滚按以下顺序设计：

1. **API 关闭**：在 Gateway 中禁用 Huyan 到 Read Only API 的路由/策略或将 API 置为维护拒绝模式，阻断新增读取请求。
2. **配置恢复**：将 Gateway 路由、RBAC/ABAC 策略、API allowlist、数据视图版本和 Huyan 功能开关恢复到最近已验证版本；不通过临时放宽权限解决故障。
3. **访问撤销**：撤销相关用户会话、服务身份和 token；删除灰度授权组成员，轮换可能受影响的服务凭据，并保留证据。
4. **证据与复核**：封存审计记录、确认无写入和无 Agent 执行、评估影响范围；修复后必须从测试阶段重新验证，不直接恢复正式访问。

---

## 十、验收标准

| 验收项 | 通过标准 |
| --- | --- |
| Huyan 读取成功 | 已授权 CEO/高管可经 Gateway 在 Huyan 成功读取其允许的 Agent 状态、报告、CEO Summary（仅 CEO）和 Health 数据。 |
| 数据一致 | Huyan 响应的快照 ID、数据截止时间、口径版本和关键聚合指标与 Control Plane 发布视图一致；过期或失败数据清晰标识且不伪装为实时。 |
| 权限正确 | CEO、高管、员工及无 token/错误 token/跨范围属性请求均符合预期的允许或拒绝结果；CEO Private Brain 不发生角色继承泄露。 |
| 无写权限 | 对全部公开路径执行的 `POST`、`PUT`、`PATCH`、`DELETE` 均被拒绝；无接口、服务账户、UI 控件或后台任务可写入 Control Plane、Core Data 或触发 Agent。 |
| 安全可审计 | MFA、token 校验、策略版本、访问结果和快照引用均可在审计中关联；日志不含敏感 token 和受保护正文。 |
| 可回滚 | 已在非生产环境验证 API 关闭、配置恢复和访问撤销，且回滚后无缓存或有效会话继续访问受保护数据。 |

---

## 十一、禁止事项

Phase 4A 及其后续实现必须禁止以下事项：

- **绕过 Gateway**：不得从 Huyan、浏览器、脚本或任何服务直接访问 `control.vafox.com` 内部接口、Agent Hub 或数据源。
- **写入 Control**：不得通过 Read Only API 或任何关联流程创建、修改、删除 Control Plane 配置、任务、状态、报告或策略。
- **Agent 执行**：不得由 Huyan 页面、API 调用、报告读取或 CEO Summary 触发、重试、暂停、恢复或编排任何 Agent。
- **生产数据访问**：不得直接读取生产 Core Data、原始表、生产明细、个人敏感信息或未发布数据；仅可消费经批准的聚合只读视图。
- **权限降级**：不得以共享账号、前端隐藏、长效 token、管理员 token 或临时宽松策略替代 RBAC、ABAC、MFA 与服务端校验。
- **未审查扩展**：不得在未完成新的设计、审批、测试和验收前，将只读接口扩展为写入、执行、控制或生产明细访问能力。

## 结论

Phase 4A 以 Gateway 为唯一入口、以 Control Plane Read Only API 为唯一数据边界、以 RBAC+ABAC+MFA 为访问约束、以聚合发布视图为数据来源。该标准在保留 CEO 经营可见性的同时，明确隔离 CEO Private Brain、Employee AI 与 Core Data，并确保 Huyan 不获得写入、执行或生产数据直连能力。
