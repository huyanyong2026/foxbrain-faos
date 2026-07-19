# VAFOX Control Plane Phase 3 Agent Hub 实际建设执行计划

> **文档性质：执行计划（Plan Only）。** 本文件用于规划 `control.vafox.com` 的 Phase 3 Agent Hub 建设、验收与回滚准备；**不构成服务器操作指令的实际执行记录**，不执行部署、不启动服务、不变更配置、不接入任何生产数据。

| 项目 | 计划值 |
| --- | --- |
| 目标服务器 | `control.vafox.com` |
| 当前前置状态 | Phase 1 Security Completed；Phase 2A Foundation Completed；Phase 2B Service Framework Completed |
| 已有基础 | Docker、Compose、`/opt/vafox-control`、services framework、logs、backups |
| Phase 3 范围 | Agent Hub、Registry、Runtime、Reports，以及五个 VAFOX Agent 的受控注册与管理 |
| 初始数据边界 | 仅允许审批后的本地、离线、非生产、合成、脱敏或聚合样本 |
| 计划原则 | 默认拒绝、最小权限、先审批后激活、全链路审计、可验证回滚 |

## 一、Phase 3 目标

Phase 3 的上线目标是在 `control.vafox.com` 建立 VAFOX Control Plane 的第一代机器人管理中心（Agent Hub），使五个指定 Agent 可被统一登记、审批、调度、监控、审计、暂停及回滚。

上线后的 Agent Hub 必须做到：

1. Hub 是 Agent 任务进入 Runtime 的唯一受控入口；未注册、未批准、版本不一致或权限不满足的请求必须拒绝。
2. Registry 是 Agent 身份、版本、状态、责任人、审批、权限与能力的唯一权威目录。
3. Runtime 仅运行 Registry 中精确批准的 Agent 版本，并采用隔离、非 root、最小网络与资源限制基线。
4. Reports 仅保存受策略过滤的结构化结果、证据引用和人工可读报告，并可追溯到 Agent、版本、请求与审批记录。
5. 初始上线范围仅为 L0/L1 的观察、分析、建议与受控报告生成；不产生自动业务动作。

## 二、部署架构

### 2.1 目标链路

```text
经认证的内部调用方 / 已批准调度器
                  |
                  v
             Agent Hub
                  |
                  v
              Registry
                  |
                  v
              Runtime
                  |
                  v
              Reports
```

### 2.2 组件部署职责

| 组件 | 部署职责 | 运行边界 | 计划交付物 |
| --- | --- | --- | --- |
| Agent Hub | 统一入口、请求校验、策略判定、任务编排与审计关联。 | 不绕过 Registry；不直接扩大 Agent 权限；不代替审批。 | 版本化服务定义、访问策略、健康检查、审计事件 schema。 |
| Registry | 保存 Agent ID、版本、状态、负责人、权限、能力、审批和审计索引。 | 不执行任务；不保存 Secret、原始敏感 payload 或生产数据。 | Schema、迁移记录、状态转换规则、备份与恢复验证材料。 |
| Runtime | 为每个已批准 Agent 版本提供隔离执行环境。 | 禁止 privileged、Docker socket、host network、宿主机 shell 与未批准外连。 | 固定镜像 digest、运行配置、资源限制、健康检查与停止策略。 |
| Reports | 保存结构化结果、脱敏摘要、证据引用和读取审计。 | 不作为审批唯一存储；不得存储 Secret 或绕过来源校验。 | 报告 schema、访问控制、保留/轮转和导出限制。 |

### 2.3 网络与存储原则

- 在既有 `/opt/vafox-control` 服务框架内维护 Compose、版本化配置、日志与备份引用；运行时配置与密钥引用分离保存。
- 仅允许经批准的内部入口访问 Agent Hub；Registry、Runtime 与 Reports 不对公网直接暴露。
- Runtime 默认位于隔离内部网络并禁止公网出站；新增网络依赖必须以独立变更重新审批。
- 所有组件请求、审计和报告均使用 UTC 时间、关联 ID、Agent ID 与精确版本。
- 容器使用固定镜像 digest、非 root 用户、只读根文件系统（可行时）、最小挂载、最小 Linux capability、CPU/内存/进程/超时限制。

## 三、部署顺序

每个步骤均须在批准的变更窗口内执行；步骤完成不自动授予生产数据、外部系统或业务执行权限。

### Step 1：Registry 部署

**目的：** 先建立唯一可信的 Agent 治理目录，避免 Hub 或 Runtime 在无权威注册信息时运行。

| 计划活动 | 完成标准 |
| --- | --- |
| 在既有服务框架中定义 Registry 服务、持久化卷、内部网络、版本化 schema 和健康检查。 | 服务定义经审查；无公网暴露；持久化与备份位置明确。 |
| 建立 Agent 注册字段与状态模型：`Draft`、`Registered`、`Approved`、`Active`、`Suspended`、`Deprecated`。 | 状态切换记录前后值、操作者、时间、原因与审批引用。 |
| 导入五个 Agent 的 `Draft` 注册包，仅登记元数据与工件摘要。 | Agent ID 唯一；无 Agent 获得运行授权或数据访问权。 |
| 验证 Registry schema、审计写入、读取控制、备份和恢复路径。 | 验证结果留存，失败时不进入 Step 2。 |

### Step 2：Agent Hub Core 部署

**目的：** 建立所有 Agent 请求的受控入口和策略执行点。

| 计划活动 | 完成标准 |
| --- | --- |
| 部署 Hub Core，配置认证、请求 schema 校验、关联 ID、限流、超时和结构化审计。 | 无认证、无关联 ID、schema 不合法或超出限额的请求均被拒绝并审计。 |
| 接入 Registry 实时查询，校验 Agent ID、精确版本、状态、审批、权限和 capability。 | Hub 无法取得有效 Registry 结论时默认拒绝，不使用过期授权绕过。 |
| 配置 RBAC、ABAC 与 Capability 联合策略。 | 三项策略任一不满足均拒绝；管理角色不自动获得执行权限。 |
| 验证 Hub 到 Registry、Runtime、Reports 的内部接口边界。 | 仅批准内部服务身份可调用；未开放直达 Runtime/Registry/Reports 的外部路径。 |

### Step 3：Runtime 部署

**目的：** 为批准的 Agent 版本提供受限、可观察、可停止的执行环境。

| 计划活动 | 完成标准 |
| --- | --- |
| 创建通用 Runtime 安全基线和 Agent 专属服务定义。 | 镜像固定、非 root、非特权、无 Docker socket、无 host network、资源限制生效。 |
| 为每个 Agent 准备版本化配置、最小只读输入路径、受控临时空间和 Reports 输出契约。 | 配置不含明文 Secret；输入/输出范围与注册权限一致。 |
| 仅按本计划第四章顺序将通过审批的精确版本接入 Runtime。 | 每次只启用一个迁移阶段；发现异常即停止后续迁移并保留证据。 |
| 配置停止、暂停、限流、超时、失败隔离与报告脱敏策略。 | 任务无法自我扩权、重启其他服务、修改 Compose 或触发部署。 |

### Step 4：Health Check

**目的：** 在激活任何 Agent 前确认控制链、审计链、报告链和拒绝链完整可用。

| 检查域 | 验证内容 | 通过条件 |
| --- | --- | --- |
| Liveness | Hub、Registry、Runtime、Reports 进程/容器可用。 | 全部为 `healthy`；`unknown` 不视为健康。 |
| Readiness | 已加载精确批准版本、配置和策略，可接受受控请求。 | 所有组件返回就绪，版本/配置摘要一致。 |
| Dependency | Hub—Registry、Hub—Runtime、Runtime—Reports 的认证后依赖可达。 | 所有依赖使用受控身份；失败不得匿名降级。 |
| Policy | Agent 状态、审批、版本、权限、能力、数据边界一致。 | 越权、过期、未批准或不匹配请求被拒绝并审计。 |
| Reporting | 执行审计和报告可关联、脱敏、可读且受访问控制。 | 报告具有来源、版本、时间、请求 ID 与证据引用。 |

## 四、Agent 迁移顺序

迁移是 Agent 的治理与运行入口迁移，不是复制生产数据、凭据或历史运行环境。所有 Agent 先以 `Draft` 注册；只有逐项完成隔离验证与审批的精确版本才可进入 `Approved`，并在健康检查通过后进入 `Active`。

| 顺序 | Agent | 迁移理由 | 初始权限/能力边界 |
| --- | --- | --- | --- |
| 1 | `health-agent` | 只读健康快照与基础健康结论的风险最低，可最早验证 Hub、Registry、Runtime、审计和报告的端到端控制链。 | L1；仅观察、分析、建议；禁止 SSH、Docker 操作、服务重启与写入。 |
| 2 | `connectivity-agent` | 在已验证的基础链路上验证离线连接性分析与网络默认拒绝规则，不需要真实端点探测。 | L0；仅离线、非联网分析；禁止网络探测、远程命令和网络配置修改。 |
| 3 | `report-agent` | 依赖前两个 Agent 的稳定报告 schema 与审计来源，适合验证受控读取、汇总、脱敏和报告发布。 | L1；仅读取批准报告/元数据并生成固定 schema 输出；禁止修改源报告。 |
| 4 | `data-agent` | 数据输入分类、脱敏、范围和输出控制要求更高，应在报告与审计链路已经稳定后以合成/脱敏样本接入。 | L0；仅批准的离线、非生产、合成、脱敏或聚合样本；禁止数据库、Core、SAP 与数据修改。 |
| 5 | `ceo-agent` | 消费前序报告并形成高管摘要，依赖所有上游来源、版本和报告治理已稳定，因此最后接入。 | L1；仅分析批准报告与 Registry 元数据；禁止工作流触发和自动业务执行。 |

**顺序原则：** 先以最低风险的可观测能力验证平台控制，再验证离线网络分析、报告依赖与数据边界，最后接入汇总决策 Agent；任何一个阶段未通过均不得继续下一 Agent。

## 五、Agent 接入标准

每个 Agent 的每个可运行版本必须提交独立注册包，并满足以下强制项：

| 必需项 | 最低要求 |
| --- | --- |
| `agent.yaml` | 包含唯一 Agent ID、名称、所有者、环境、精确版本、镜像 digest/工件摘要、依赖、输入输出 schema、健康检查、资源限制与回滚版本。 |
| `SPEC.md` | 明确业务目的、允许/禁止能力、数据边界、工具边界、失败处理、报告格式、停止条件与责任人。 |
| approval 记录 | 绑定 Agent ID、精确版本、环境、权限、能力、数据范围、审批人、有效期、变更单与风险接受（如适用）。 |
| version | 使用语义版本并绑定不可变工件标识；禁止 `latest`、浮动标签和未登记工件。 |
| permission | 用“动作 + 资源 + 条件 + 时效”描述最小权限，包含数据、文件、网络、工具和报告读取/写入范围。 |
| capability | 明确允许任务类型、输入/输出 schema、调用配额、超时、并发、禁止动作与不可扩张的 capability 集。 |
| audit | 覆盖创建、修改、审批、状态变化、授权判定、调用、运行、拒绝、错误、暂停、回滚和报告读取。 |

接入校验不通过时，Agent 保持 `Draft` 或 `Registered`，不得获得任务调度、外部系统访问或自动执行能力。

## 六、权限设计

### 6.1 L0–L4 权限等级

| 等级 | 定义 | Phase 3 初始策略 |
| --- | --- | --- |
| L0 | 离线、非联网、非变更的设计、分析或样本处理。 | 可用于 connectivity-agent 与 data-agent；仅批准的非生产样本。 |
| L1 | 受控本地/内部只读分析与固定报告生成。 | 可用于 health-agent、report-agent、ceo-agent；无外部系统写入。 |
| L2 | 受控只读服务集成。 | Phase 3 初始不授予；需独立数据、网关、字段级策略与审批。 |
| L3 | 人工批准下的受限建议执行或任务编排。 | Phase 3 初始不启用；每次动作需审批、可逆性与强审计。 |
| L4 | 高风险或生产影响特权动作。 | 默认禁止；不属于五个 Agent 的初始接入范围。 |

### 6.2 RBAC、ABAC、Capability 联合控制

| 控制模型 | 定义 | 强制规则 |
| --- | --- | --- |
| RBAC | 基于角色分配职责，例如 Agent Runtime、Registry 管理员、审批人、报告读者。 | 管理 Registry 不等于可执行 Agent；执行者不等于审批者。 |
| ABAC | 基于主体、资源、环境、时间、数据分类、审批状态和请求上下文判定。 | 必须校验 `control.vafox.com` 环境、精确版本、`Active` 状态、审批有效期、来源、关联 ID 和数据分类。 |
| Capability | 对单个 Agent 授予短时、受众受限、资源受限、不可伪造的动作集合。 | `generate_report` 不得隐含 `network_probe`、`restart_service`、数据写入或业务执行。 |

允许一个请求的条件是三类控制均通过；任何缺失、过期、冲突或无法验证均拒绝并写入审计。

## 七、运行管理

| 管理项 | 计划要求 |
| --- | --- |
| 启动 | 仅 Hub 可调度 `Active`、审批有效且精确版本匹配的 Agent；启动前执行策略、配置摘要和健康前置校验。 |
| 停止 | 支持停止单个任务、停止单个 Agent、将 Agent 转为 `Suspended` 和紧急停止入口；停止后阻断新任务、会话、令牌与调度。 |
| 健康检查 | 持续执行 liveness、readiness、dependency、policy 和 reporting 检查；`degraded`/`unhealthy` 阻断新任务并告警。 |
| 日志 | Hub、Registry、Runtime、Reports 使用结构化日志，至少包含 UTC、关联 ID、Agent ID、版本、状态、授权结论、结果与错误分类；禁止记录 Secret 和真实敏感 payload。 |
| 版本管理 | Compose、服务配置、Agent manifest、策略与报告 schema 均版本控制；仅固定 digest 运行；变更权限、能力、数据范围、配置或镜像均视为新版本并重新审批。 |
| 监控与告警 | 监控可用性、错误率、拒绝率、审批失效、权限异常、资源超限、审计写入失败与报告失败；达到阈值时停止新增任务并升级人工处理。 |

## 八、备份设计

备份仅覆盖受控配置、治理元数据和报告/审计所需证据；备份不得包含明文 Secret、生产数据或未经批准的原始 payload。备份作业、保留期、访问控制、加密与恢复演练应遵循既有 backups 基础与更严格的数据治理要求。

| 备份域 | 备份对象 | 频率与保留计划 | 恢复验证 |
| --- | --- | --- | --- |
| Registry 备份 | Registry 数据、schema 版本、状态转换、审批引用、审计索引和工件摘要。 | 部署前完整备份；变更前备份；按既有备份策略执行周期性备份与保留。 | 在隔离环境恢复后验证记录完整性、schema 兼容性、审计可读性与权限默认拒绝。 |
| Agent 配置备份 | `agent.yaml`、`SPEC.md`、策略、批准记录引用、镜像 digest、报告 schema 与版本清单。 | 每个已批准版本发布前归档；配置变更前创建不可变快照。 | 验证版本、摘要、审批引用和禁止项与 Registry 一致。 |
| Runtime 配置备份 | Compose 服务定义、网络/卷定义、资源限制、健康检查、只读挂载与配置引用。 | 部署前、每次变更前及批准发布后归档。 | 在隔离环境验证可恢复配置不含 Secret，且不开放公网、host network 或 Docker socket。 |

## 九、回滚设计

回滚的优先目标是立即停止风险扩大、恢复最近一次批准且已验证的受控状态，并完整保留事件证据。触发条件包括健康检查失败、策略/审计失败、未授权变更、审批失效、异常资源行为、报告完整性失败或安全事件。

| 回滚域 | 计划动作 | 回滚完成标准 |
| --- | --- | --- |
| Agent 版本回滚 | 停止受影响任务；将 Agent 置为 `Suspended`；撤销当前版本调度；恢复到最近一次批准且已验证的镜像 digest、`agent.yaml`、策略和配置；重新执行健康与授权拒绝验证。 | 仅恢复批准的 L0/L1 范围；无新任务进入故障版本；审计关联事件、原因、操作者与恢复版本。 |
| Registry 恢复 | 冻结状态/权限变更与新激活；从最近可验证备份恢复 Registry 数据和 schema；校验记录、审批、审计索引及版本摘要；恢复前保持 Hub 默认拒绝。 | Registry 完整、一致、可审计；Hub 只读取已验证恢复结果；无未经审查的 `Active` 状态。 |
| Runtime 恢复 | 停止受影响 Runtime；恢复最近批准的 Compose、网络、卷、资源、健康检查和配置引用；验证容器安全基线与内部接口；逐一恢复已批准 Agent。 | Runtime 仅运行批准镜像和配置；无公网暴露、无宿主机特权、无自动业务执行。 |

任何回滚后必须完成原因分析、证据归档、影响评估、修复计划和重新审批；不得以回滚成功替代问题整改或审批。

## 十、验收标准

验收必须逐项留存证据，且所有必需项通过后才能宣布 Phase 3 完成。验收通过仅表示 Agent Hub 的受控管理能力就绪，不授予生产数据、SAP、Core 真实数据或自动业务执行权限。

| 验收项 | 通过标准 |
| --- | --- |
| Agent Hub 运行 | Hub 已部署于受控内部入口，认证、关联 ID、策略、限流、超时与审计可用；无绕过 Hub 的运行入口。 |
| Registry 正常 | Registry 可读取唯一 Agent 注册记录，状态/版本/权限/能力/审批变更可审计，默认拒绝生效。 |
| Agent 注册成功 | 五个 Agent 均具备完整注册包，精确版本、所有者、审批、permission、capability、audit 和禁止项可验证。 |
| Health Check 通过 | Hub、Registry、Runtime、Reports 的 liveness、readiness、dependency、policy、reporting 均通过；越权场景被拒绝并审计。 |
| Report 生成成功 | 使用批准的非生产/脱敏/合成输入，成功生成带 Agent ID、版本、时间、关联 ID、来源和证据引用的脱敏报告。 |
| 安全边界验证 | 生产数据、SAP、Core 真实数据、自动业务执行、审批绕过、未登记版本和 L2/L4 请求均被拒绝并审计。 |
| 回滚准备就绪 | Agent、Registry、Runtime 的备份、恢复顺序和隔离验证证据完整。 |

## 十一、安全边界

Phase 3 初始上线必须严格遵守以下禁止项：

- **禁止生产数据接入。** 不得将生产数据库、生产文件、生产日志原文或生产业务 payload 提供给任何 Agent。
- **禁止 SAP 访问。** 不得配置 SAP 连接器、账号、令牌、网络路径或间接代理访问。
- **禁止 Core 真实数据。** 不得读取、复制、缓存、导出或推断 Core 的真实业务数据。
- **禁止自动业务执行。** Agent 不得提交订单、修改记录、触发工作流、部署服务、变更网络、重启服务或执行其他业务/运维动作。
- **禁止绕过审批。** 不得通过管理员权限、直接 Runtime 调用、临时配置、缓存授权、共享令牌或未登记版本规避 Agent、版本、权限、能力及动作审批。

如未来需要扩大数据、网络、工具或执行范围，必须作为新的独立阶段完成设计、风险评估、审批、隔离测试、回滚演练与验收，不得在 Phase 3 内隐式启用。

## 十二、Phase 3 完成定义

Phase 3 在以下条件同时满足时完成：

1. `control.vafox.com` 上的 Agent Hub、Registry、Runtime 与 Reports 已按本计划部署并通过全部健康检查。
2. `health-agent`、`connectivity-agent`、`report-agent`、`data-agent`、`ceo-agent` 五个 Agent 已按既定顺序完成受控注册、审批、隔离验证与激活准备，并可由 Agent Hub 正式管理。
3. 每个 Agent 均可验证其 `agent.yaml`、`SPEC.md`、approval 记录、version、permission、capability 和 audit，且仅具有 L0/L1 的批准边界。
4. 结构化报告可成功生成并追溯至 Agent、版本、请求、审批和证据；健康、日志、备份与回滚机制均已验证。
5. 所有安全边界持续有效：无生产数据、SAP、Core 真实数据、自动业务执行或审批绕过。

**完成结论：** 满足上述定义后，VAFOX Control Plane 形成第一代机器人管理中心，能够以统一、可审计、可审批、可暂停和可回滚的方式正式管理五个 VAFOX Agent。
