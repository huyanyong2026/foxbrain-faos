# VAFOX Huyan Agent Hub Architecture

**文档状态：** Architecture Design / Draft  
**定位域名：** `huyan.vafox.com`  
**设计目标：** 设计 Huyan CEO Control Plane 的 Agent Hub；本文只定义目标架构、治理契约与安全边界，不实施任何服务器、腾讯云、Docker 或数据库操作。

## 0. 架构结论与范围

Huyan 是面向 CEO 的**控制面与决策呈现层**，不是 Agent 的自由执行环境、运维跳板或数据系统。Huyan 内的 Agent Hub 负责把经过 VAFOX-Control 治理批准的 Agent，以统一的身份、权限、状态、调用和报告契约提供给 CEO Dashboard。

目标逻辑链路如下：

```text
VAFOX-Control
  └─ Registry / Policy / Approval / Audit（治理权威）
           ↓ 已批准的 Agent 元数据、策略与脱敏结果
huyan.vafox.com
  └─ Huyan CEO Control Plane
       └─ Agent Hub（编排、授权校验、状态投影、报告汇总）
                ↓ 最小化、受策略约束的任务契约
             AI/Core
  └─ AI Workforce / Core Data Brain（受治理的数据与智能能力域）
```

**本设计不改变既有 Phase 1 Agent 边界。** 当前模板中的 Agent 均处于 `Draft`，其已声明的本机/离线、只读或设计范围仍然有效；在完成重新注册、隔离测试及正式审批前，本文的目标集成图不构成 Huyan、AI、Core、网络、数据或执行权限。

---

## 1. Agent Hub 定位

### 1.1 使命

Agent Hub 是 Huyan CEO Control Plane 的受治理 Agent 门面，向 CEO Dashboard 提供“企业健康、风险、机会、建议和证据”的统一视图。它必须：

- 隐藏具体 Agent 的选择与复杂性；CEO 只看到业务问题、结论、证据、建议与待审批事项。
- 以 VAFOX-Control 的 Registry、策略和审批为唯一治理依据。
- 对每一次 Agent 调用执行身份、状态、版本、权限、数据范围、审批与审计校验。
- 仅编排已批准的最小能力；不自行扩大 Agent 权限，也不把建议转换为执行指令。
- 将拒绝、超时、未知和数据过期明确呈现，绝不将它们折算为“正常”。

### 1.2 非职责

Agent Hub 不承担以下职责：

- 不替代 VAFOX-Control 的注册、审批、策略制定或审计权威。
- 不直接承担 AI/Core 的数据库、业务系统或原始数据访问职责。
- 不提供 SSH、远程 shell、服务器运维、腾讯云管理、Docker/容器修改、数据库修改、部署、回滚或自动修复能力。
- 不把 Agent 建议直接转成任务分派、审批、通知或生产工作流。

### 1.3 逻辑组件

| 组件 | 职责 | 关键约束 |
| --- | --- | --- |
| CEO Dashboard Adapter | 将 Dashboard 的业务问题转换为标准 Agent Hub 请求，并呈现已授权结果。 | 不携带凭据；不绕过 Hub 直连 Agent。 |
| Agent Gateway | 请求认证、限流、关联 ID、输入模式校验与标准响应。 | 默认拒绝；只接受已注册契约。 |
| Policy Decision Point | 根据 VAFOX-Control 投影的策略判定调用是否允许。 | 策略只读投影，不能在 Huyan 本地提权。 |
| Orchestrator | 选择允许的 Agent、编排依赖、管理超时与幂等。 | 只编排 `Active` 且审批有效的版本。 |
| Registry/Status Cache | 只读缓存 Agent 元数据、版本、状态、撤销与紧急停止标记。 | VAFOX-Control 是源头；撤销优先于缓存可用性。 |
| Report Aggregator | 合并带来源的 Agent 输出，形成 CEO 视图。 | 不篡改源结论；保留证据、新鲜度和不确定性。 |
| Audit Emitter | 输出不可抵赖的调用与策略判定事件。 | 仅记录最小必要元数据与脱敏摘要。 |

---

## 2. Agent 注册机制

### 2.1 注册权威与记录

VAFOX-Control Agent Registry 是唯一的注册权威。Huyan Agent Hub 仅消费经签名或可验证完整性的 Registry 投影，不允许通过 Dashboard 或 Huyan 本地配置创建“隐式 Agent”。

每个注册版本至少包含：

- 不可复用的 `agent_id`、名称、类型、版本、负责人和生命周期状态；
- 能力等级与允许/禁止动作；
- 权限等级、数据分类、允许来源/字段/输出和环境范围；
- 调用契约（输入/输出 schema、超时、幂等规则、报告 schema）；
- `approval_required`、审批引用、有效期、策略版本和紧急停止标记；
- 审计要求、保留策略以及变更/撤销记录。

任何能力、数据源、工具、输出目的地、系统边界或执行范围的扩大，都必须作为**新版本**重新走注册、风险评估、隔离测试和审批；不得覆盖既有版本记录。

### 2.2 注册门禁

```text
Draft
  ↓ 元数据完整、负责人已指定
Registered
  ↓ 安全 / 数据 / 技术 / 业务 / 权限审批与隔离测试通过
Approved
  ↓ 部署契约、审计、监控与紧急停止已验证
Active
  ↘ 异常、审批到期、撤销或策略不匹配 → Suspended
  ↘ 停用并撤销所有运行权限 → Deprecated
```

- `Draft`、`Registered`、`Approved` 不等于可由 Huyan 调用；Agent Hub 只允许 `Active` 版本接受生产性请求。
- `Suspended` 或 `Deprecated` 的 Agent 必须立即从调度候选集中移除；仅保留最小审计查询能力。
- Registry 不可用、签名/完整性无法验证或策略版本不一致时，Hub 必须拒绝新调用并返回可审计的 `POLICY_UNAVAILABLE` 或 `REGISTRY_INVALID`。

### 2.3 当前 Agent 注册映射

| 逻辑 Agent | 现有 Agent ID | 当前 Phase 1 角色 | Hub 的未来使用条件 |
| --- | --- | --- | --- |
| health-agent | `agt_ops_health_phase1_001` | 已批准健康快照的只读分析与人工建议。 | 新版本获准后，提供健康结论/证据，不提供修复。 |
| connectivity-agent | `agt_ops_connectivity_phase1_001` | 离线连接状态设计与样本分析。 | 新版本获准后，仅消费受控快照，不进行探测或网络操作。 |
| report-agent | `agt_ops_report_phase1_001` | 本机、已批准源报告的汇总。 | 新版本获准后，输出可追溯的管理层汇总。 |
| data-agent | `agt_ops_data_phase1_001` | 离线、非生产、脱敏或合成样本分析。 | 新版本获准后，以数据产品契约提供最小聚合指标。 |
| ceo-agent | `agt_ceo_decision_phase1_001` | 本机既有报告的离线决策分析。 | 新版本获准后，形成非执行性的 CEO 决策建议。 |

---

## 3. Agent 调用流程

### 3.1 标准调用链

```text
CEO Dashboard
  → Huyan Agent Gateway
  → 身份 / 目的 / 租户 / 关联 ID 校验
  → Registry、状态、版本、审批与紧急停止校验
  → VAFOX-Control Policy Decision
  → Orchestrator 选择最小 Agent 集
  → Agent / AI-Core 受策略的契约调用
  → 输出验证、脱敏、来源绑定、报告汇总
  → CEO Dashboard + 审计事件
```

### 3.2 单次调用的强制步骤

1. **发起：** Dashboard 请求必须声明业务目的、调用方身份、关联 ID、目标逻辑域、期望时效和最小数据分类；不得传递服务器地址、密钥或任意执行命令。
2. **认证与输入校验：** Gateway 验证身份、请求 schema、速率与大小限制，并拒绝未登记能力或模糊目的。
3. **运行时授权：** Hub 同时验证 Agent `Active` 状态、精确版本、批准范围、审批有效期、调用方权限、数据分类、允许来源与输出目的地。
4. **策略决策：** VAFOX-Control 策略返回 `allow`、`deny` 或 `require_human_approval`；无明确 `allow` 即为拒绝。
5. **最小编排：** Orchestrator 只调用完成问题所必需的 Agent；跨 Agent 只传递批准 schema 中的最小脱敏字段及同一关联 ID。
6. **结果封装：** 每项结果必须含 Agent/版本、生成时间、证据引用、数据新鲜度、置信度/不确定性和策略判定；缺失或冲突必须标为 `UNKNOWN` / `PARTIAL`。
7. **审计与呈现：** 写入调用摘要、授权判定、输入/输出摘要、拒绝/超时和相关审批引用；Dashboard 只展示已通过输出校验的结果。

### 3.3 失败处理

- 状态非 `Active`、审批失效、版本不匹配、策略不可验证、数据来源越界或输出含敏感字段：**拒绝，不调用下游**。
- 依赖 Agent 超时或不可用：返回 `UNKNOWN` 或 `PARTIAL`，列出缺失来源及人工复核建议；不得推断为 `PASS`。
- 非幂等请求不得自动重试；允许重试的只读调用必须复用关联 ID，并记录重试次数与原因。
- CEO Dashboard 不得提供绕过 Hub 的“直连 Agent”入口。

---

## 4. Agent 权限控制

### 4.1 权限模型

Hub 使用“**RBAC + ABAC + Capability**”三层决策：

- **RBAC：** CEO、授权管理者、审计员、平台管理员等角色决定可请求的业务域。
- **ABAC：** 依据调用目的、组织/租户、环境、数据分类、时间、审批引用、Agent 状态和风险等级动态收窄权限。
- **Capability：** Agent 注册能力是上限；调用令牌是一次性、短时、受众受限且不可转授的最小能力凭证。

最终授权为交集：

```text
允许调用 = 调用方角色 ∩ 属性策略 ∩ Agent 注册能力 ∩ 审批范围 ∩ 数据契约 ∩ 当前状态
```

### 4.2 权限矩阵

| Agent | 允许的目标能力 | 明确不允许 |
| --- | --- | --- |
| health-agent | 受控健康快照的 Observe / Analyze / Recommend。 | 修复、服务控制、Docker、部署、数据写入、SSH。 |
| connectivity-agent | 受控且脱敏的连接状态快照分析。 | 网络探测、DNS/HTTP 调用、远程连接、网络配置。 |
| report-agent | 已批准本机源报告的聚合与非执行性摘要。 | 源报告修改、远程访问、任务触发、生产操作。 |
| data-agent | 已批准数据产品或离线样本的最小聚合分析。 | 原始生产数据、数据库访问、导出、写入、Core/SAP 直连。 |
| ceo-agent | 已批准报告和聚合证据的决策辅助。 | 自动决策、审批、任务分派、外部发送或执行。 |

### 4.3 人工审批门

以下请求必须在 Hub 拒绝自动执行，或进入显式人工审批队列（且审批后仍仅限注册能力）：

- 涉及新数据分类、新来源、新环境、权限扩大或新 Agent 版本；
- 需要产生可执行任务、通知、外部通信或对业务状态造成影响的动作；
- 任何写入、部署、回滚、服务控制、云资源、网络或数据库相关操作。

当前 Agent 集合不授予 `Execute` 能力；人工批准不能将其隐式提升为执行权限。

---

## 5. Agent 状态管理

### 5.1 双层状态

Hub 将状态分为两个不可互相替代的维度：

1. **治理状态：** `Draft`、`Registered`、`Approved`、`Active`、`Suspended`、`Deprecated`，由 VAFOX-Control Registry 权威管理。
2. **运行状态：** `HEALTHY`、`DEGRADED`、`UNAVAILABLE`、`UNKNOWN`，只描述已批准的可观测性证据，不代表治理授权。

只有“治理状态为 `Active` 且运行状态可接受且策略有效”的 Agent 才可被编排。`UNKNOWN` 不能成为可用性证明。

### 5.2 状态投影与紧急停止

- VAFOX-Control 发布带版本和时间戳的状态投影；Hub 缓存只用于降低读取延迟，不能延迟撤销生效。
- `Suspended`、审批撤销和紧急停止事件具有最高优先级；Hub 立即撤销该 Agent 的会话、令牌、队列任务和下游调用资格。
- 状态变化必须包含操作者/系统身份、原因、关联审批、时间和审计引用。
- 恢复 `Suspended` Agent 必须由 VAFOX-Control 重新批准并验证，不能由 Huyan 本地开关恢复。

---

## 6. Agent 报告汇总

### 6.1 汇总原则

Report Aggregator 是证据汇总器而非事实重写器。它按统一 schema 汇总 health、connectivity、data 与 ceo 等 Agent 的已批准输出，并保留“谁在何时、基于什么数据、按什么策略得出该结论”。

### 6.2 统一报告信封

每个可展示结果都应包含：

```text
report_id, correlation_id, agent_id, agent_version, generated_at_utc,
policy_decision_id, approval_reference, source_evidence_refs,
data_freshness, classification, status, confidence, uncertainty,
findings, recommendations, limitations, audit_reference
```

汇总规则：

- **来源优先：** 每一条结论关联原始 Agent 输出与证据引用；不丢失版本和时间。
- **新鲜度优先：** 超出允许时间窗口的数据标记为过期，不用于生成“当前正常”结论。
- **冲突显式化：** 多 Agent 结果冲突时列出冲突与待核查项，不能由 Hub 静默选边。
- **最小披露：** 聚合输出只保留 CEO 决策所需的脱敏摘要；敏感明细不进入 Dashboard。
- **非执行性：** 建议必须标注为人工复核/决策材料，不可自动触发执行。

### 6.3 汇总视图

- **企业健康：** Health Agent 状态、数据新鲜度、影响和证据。
- **链路风险：** Connectivity Agent 的逻辑链路状态与不确定性。
- **经营洞察：** Data Agent 的已批准指标、口径、范围与局限。
- **CEO 简报：** CEO Agent 基于可追溯报告形成的风险、机会、方案与待决事项。
- **报告完整性：** 输入覆盖率、过期/缺失来源、拒绝和审计状态。

---

## 7. CEO Dashboard 数据来源

CEO Dashboard 只从 Huyan Agent Hub 的**受控只读查询 API**获取展示模型；不直接查询 VAFOX-Control、AI、Core、SAP、数据库、服务器、日志或云平台。

| Dashboard 模块 | 允许数据来源 | 必须展示的限定信息 |
| --- | --- | --- |
| Enterprise Health | 经 Hub 验证的 Health Agent 报告/快照摘要。 | 生成时间、状态、影响、新鲜度、证据引用。 |
| Connectivity/Risk | 经 Hub 验证的 Connectivity Agent 报告摘要。 | 逻辑链路、状态、不确定性、最后有效证据。 |
| AI Briefing / Opportunity | 经 Hub 验证的 Data/CEO Agent 已批准输出。 | 数据范围、指标口径、置信度、局限与待验证项。 |
| Decision Center | CEO Agent 的非执行性方案与人工审批引用。 | 事实/推断区分、风险、负责人建议与人工决定状态。 |
| Agent Governance | Registry 投影和审计摘要。 | Agent 版本、治理状态、审批状态、最近调用结果。 |

Dashboard 的读模型应按业务必要性预聚合和脱敏；任何钻取到更高敏感度或新数据域的能力，都必须通过新的数据契约和策略审批。

---

## 8. Huyan 与 VAFOX-Control 关系

```text
VAFOX-Control = Governance Plane（登记、策略、审批、审计权威）
Huyan          = CEO Control Plane（编排、呈现、受控请求入口）
Agent Hub      = Huyan 内的 Policy Enforcement / Orchestration Layer
```

- VAFOX-Control 决定“**什么 Agent、以什么版本、在什么范围、何时可以被使用**”。
- Huyan 决定“**如何把已批准能力组合成 CEO 可读的控制面体验**”，但不能扩大任何已注册范围。
- Hub 对 VAFOX-Control 的依赖是治理同步、策略判定、审批验证、状态/撤销投影与审计关联；这些交互使用最小只读/受控契约，而非管理平面直连或共享管理员凭据。
- Huyan 发生故障不得改变 VAFOX-Control 的 Registry 真相；VAFOX-Control 不可用时，Huyan 应降级为只读的已缓存、带“可能过期”标识的历史视图，或拒绝新 Agent 调用。

---

## 9. Huyan 与 AI/Core 关系

```text
Huyan Agent Hub --(目的受限、最小字段、短时凭证)--> AI Workforce / Core Data Brain
AI/Core        --(脱敏、可追溯、非执行性结果)--> Huyan Agent Hub
```

- AI 是受治理的智能能力域：负责在批准范围内执行模型推理、Agent 工具编排或知识处理；Huyan 不持有 AI 的高权限工具能力。
- Core 是受治理的数据/业务事实域：负责经数据产品契约提供最小、脱敏、聚合且可追溯的数据结果；Huyan 不直连 Core 数据库，也不读取原始业务数据。
- Hub 仅以 Agent 注册契约中的逻辑能力调用 AI/Core；请求必须绑定调用目的、数据分类、字段白名单、关联 ID、有效期与受众。
- AI/Core 返回的每项结果必须通过 Hub 的 schema、敏感信息、来源和策略校验后才可进入 Dashboard。
- 任何 AI/Core 的写入、动作执行或外部工具调用必须由独立执行平面和独立审批体系处理，不属于 CEO Agent Hub。

---

## 10. 安全边界

### 10.1 强制禁止项

本架构及当前 Phase 1 设计**不实施、也不授权**下列事项：

- SSH、SCP、SFTP、远程 shell、远程命令执行、端口扫描、DNS 查询或网络探测；
- 服务器操作、服务启动/停止/重启、部署、回滚、文件或配置修改；
- 腾讯云账号、网络、安全组、负载均衡或其他云资源修改；
- Docker、镜像、容器、Compose、Kubernetes 或运行时修改；
- 数据库连接、结构/数据修改、迁移、导入导出或原始数据复制；
- 自动修复、自动审批、自动任务分派、自动通知或自动业务执行。

### 10.2 技术控制

1. **默认拒绝与最小权限：** 未被 Registry、策略和审批同时明确允许的主体、动作、来源、字段、环境和输出一律拒绝。
2. **零信任服务身份：** 服务间使用独立工作负载身份、短期令牌、受众绑定和定期轮换；不共享长期管理员凭据，不在请求、报告或审计中记录密钥。
3. **数据最小化：** 优先消费脱敏、聚合的数据产品和报告；按字段白名单、目的限制、保留期和输出脱敏处理。
4. **分层隔离：** Dashboard、Hub、AI/Core、Registry/Policy 和审计域职责分离；Dashboard 不可绕过 Hub，Hub 不可绕过策略层。
5. **输出安全：** 对 Agent 输出执行 schema 验证、敏感信息检测、证据/新鲜度校验与提示注入防护；失败则阻断展示或降级为安全错误。
6. **可审计性：** 每次调用记录最小必要的身份、目的、版本、策略判定、审批引用、输入/输出摘要、时间、状态和拒绝原因；审计记录与业务数据分离保管。
7. **韧性与熔断：** 限流、配额、超时、并发限制、熔断和紧急停止；下游不确定时优先返回 `UNKNOWN` / `PARTIAL`。
8. **变更治理：** Agent、策略、schema、数据源和 Dashboard 读模型的变化均走版本化评审、测试与审批；生产发布与运行权不得由单一主体同时决定。

### 10.3 上线前验收条件

目标架构进入任何联网或生产运行阶段前，至少应完成：Registry 完整性与签名验证、策略默认拒绝测试、权限越权测试、数据脱敏测试、审计可追溯测试、状态撤销/紧急停止测试、超时/降级测试、输出安全测试，以及业务/安全/数据/技术责任方的正式审批。未满足任一条件时，保持 Draft 或受控离线状态。

---

## 11. 目标实现阶段（仅架构路线）

1. **治理先行：** 固化 VAFOX-Control Registry、生命周期、策略、审批和审计契约；当前 Agent 维持各自 Phase 1 禁止边界。
2. **Hub 骨架：** 建立 Huyan 内的 Gateway、Policy Enforcement、状态投影、报告 schema 和只读 Dashboard 读模型；不接入执行能力。
3. **受控观察：** 为每个 Agent 以新版本引入获批准的最小只读数据契约、隔离测试与人工审批。
4. **CEO 编排：** 在所有输入可追溯、状态可撤销、输出可解释的前提下，提供健康、风险、经营洞察和决策材料的统一体验。
5. **独立执行平面（未来另案）：** 如确有执行需求，必须单独设计执行平面、人工审批、职责分离、回滚与审计；不得复用或暗中扩张 Agent Hub 权限。
