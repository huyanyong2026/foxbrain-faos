# VAFOX Control Plane Phase 3 — Agent Hub 建设 Artifact

> **状态：Draft（未审批，不可执行）**
> 本 Artifact 是 `control.vafox.com` 第一代 Agent Hub 的建设、验证与回滚基线。它只定义受控的 Phase 3 准备工作；在完成全部审批门禁前，不得执行任何部署、注册激活、网络变更或真实数据访问。

## 1. Artifact Metadata

| 项目 | 内容 |
|---|---|
| Artifact ID | `VAFOX-CP-P3-AGENT-HUB-001` |
| 标题 | VAFOX Control Plane Phase 3 Agent Hub 建设 Artifact |
| 版本 | `0.1.0-draft` |
| 创建日期 | 2026-07-19 (UTC) |
| 生成工具 | Codex (GPT-5.6 Terra) |
| 目标环境 | `control.vafox.com`；公网 `114.132.55.178`；内网 `172.16.16.6` |
| 前置基线 | Phase 1 Security Completed；Phase 2A Foundation Completed；Phase 2B Service Framework Completed |
| 风险等级 | Medium（控制面新增组件；范围严格限定为无生产数据、无执行能力） |
| 审批状态 | **Draft / Not Approved / Not Executable** |
| 回滚位置 | 经批准的变更窗口工作目录中的 Phase 3 发布包、Registry 导出、Runtime/Compose 配置快照及本 Artifact 第 8 节恢复记录 |

**解释：** IP 地址仅用于已批准运行手册中的目标识别，不构成直连、SSH、端口开放或任何服务器操作授权。所有服务调用必须经受控 Gateway 与运行时策略校验。

## 2. Phase 3 范围与硬边界

### 2.1 允许范围

- Agent Hub 的受控部署与基础配置。
- Agent Registry 初始化及空/模板化登记结构验证。
- Agent Runtime 准备、隔离配置、身份与审计链路验证。
- Report Center 接口、报告 schema 与脱敏输出链路准备。

### 2.2 明确禁止范围

- 接入任何生产数据、生产数据副本或可反查的生产导出。
- 访问 SAP，或建立到 SAP 的凭据、网络路由、连接器或任务。
- 访问 Core 的真实数据、数据库、业务 API 或真实数据镜像。
- 自动业务执行、写入、审批、任务分派、外部发送、服务控制或修复动作。

以上禁止项在本 Phase 中没有例外；人工批准不得将其隐式转换为允许项。范围扩大必须创建新版本 Artifact、完成风险评估并重新审批。

## 3. Agent Hub 架构

```text
Agent Hub
    ↓  注册、版本、状态、策略引用
Agent Registry
    ↓  已核验的最小能力契约
Agent Runtime
    ↓  脱敏、只读、非执行性结果
Report Center
```

| 组件 | 职责 | 数据流 | 权限边界 |
|---|---|---|---|
| Agent Hub | 统一入口；认证、请求 schema 校验、策略决策、编排与审计关联。 | 接收受控请求；读取 Registry 决策；向 Runtime 下发最小任务；向 Report Center 提交已校验结果。 | 默认拒绝；不得直连 Agent、Core、SAP 或生产数据源；不得发放扩大权限。 |
| Agent Registry | 唯一的 Agent 身份、版本、能力、状态、审批及权限目录。 | 向 Hub/Runtime 发布可验证的注册与撤销状态；记录变更审计。 | 未注册、非 `Active`、版本不匹配或审批失效的 Agent 一律不可运行。 |
| Agent Runtime | 在隔离环境执行已登记的 Observe/Analyze/Recommend 能力；校验短时能力令牌。 | 仅接受 Hub 经 Gateway 授权的任务；输出契约化、脱敏结果。 | 不持有生产凭据；不允许 Execute；无直接外网、SAP/Core 或业务系统访问路径。 |
| Report Center | 接收、验证、保存并呈现具有证据引用的非执行性报告。 | 汇总 Runtime 输出，保留 Agent/版本/时间/策略/证据关联。 | 仅接受已注册来源；不触发任务或业务动作；不展示超出授权分类的字段。 |

**强制数据流：** 所有请求均为 `调用方 → Gateway → Agent Hub → Registry 校验 → Runtime → Report Center → 调用方`。Registry 状态、策略或审计任一项不可验证时必须拒绝请求。禁止绕过 Gateway、Hub 或资源侧权限校验。

## 4. 部署步骤（审批后执行）

> 每一步开始前确认执行窗口、负责人、变更单、备份与紧急停止路径；任一退出条件不满足即停止，不进入下一步。

| 步骤 | 工作内容 | 验证与退出条件 | 安全限制 |
|---|---|---|---|
| Step 1：Registry 初始化 | 部署/初始化 Registry schema、不可复用 ID 规则、版本记录、生命周期、审计字段及撤销状态；仅建立 Draft 模板记录。 | Registry 可用；Draft 记录可查询；审计事件可检索；无 Agent 为 Active。 | 不导入生产数据或生产凭据；不激活 Agent。 |
| Step 2：Agent Hub Core 部署 | 部署 Hub、Gateway 集成、认证、RBAC/ABAC 策略加载、关联 ID、限流、拒绝与审计处理。 | 未注册和未授权请求被拒绝并审计；Hub 无直连下游路径。 | 不配置 Core/SAP 连接器；不得绕过 Gateway。 |
| Step 3：Runtime 部署 | 部署隔离 Runtime、服务身份、短时能力令牌校验、输出 schema 校验、健康端点与紧急停止。 | Runtime 仅接受已授权模拟请求；无 Execute capability；默认网络拒绝策略生效。 | 不加载真实业务数据、密钥或执行工具。 |
| Step 4：Health Check | 验证 Hub、Registry、Runtime、Report Center 健康、证书/身份、策略拒绝、审计与告警。 | 所有健康检查通过；故障/策略不可用场景 fail-closed；报告输出可追溯。 | Health Check 只使用合成或脱敏测试数据。 |
| Step 5：第一个 Agent 接入 | 按第 5 节接入 `health-agent` 的 Draft/Registered 验证版本，完成能力、权限、输入输出及回滚验证。 | 注册成功；未获 Active 与审批前不得接收生产任务；验证报告生成成功。 | 仅 Observe/Analyze/Recommend 的模拟健康快照；不执行修复。 |

## 5. Agent 迁移计划（顺序固定）

所有迁移均遵循 `Draft → Registered → Approved → Active` 生命周期；本 Draft Artifact 只允许完成受控登记与非生产验证，**不授权 Active 或生产运行**。每次迁移必须建立独立审批、测试证据和回滚点，前一 Agent 验收完成后才可开始下一 Agent。

| 顺序 / Agent | Agent ID | 初始版本 | 权限（上限） | Capability | 输入 | 输出 | 风险 |
|---|---|---|---|---|---|---|---|
| 1. health-agent | `agt_ops_health_phase3_001` | `0.1.0` | L1；仅 Hub→Runtime；合成/脱敏健康快照只读 | Observe, Analyze, Recommend | 合成或脱敏的服务健康快照 | 健康状态、证据引用、异常与人工建议 | Low：错误状态判断；无修复权限。 |
| 2. connectivity-agent | `agt_ops_connectivity_phase3_001` | `0.1.0` | L1；仅已批准的离线连接状态样本 | Observe, Analyze, Recommend | 合成/脱敏连接状态快照 | 链路风险、覆盖范围、不确定性 | Low：误判风险；禁止探测、DNS/HTTP、远程连接及网络配置。 |
| 3. report-agent | `agt_ops_report_phase3_001` | `0.1.0` | L1；读取已批准、脱敏的 Agent 报告 | Analyze, Recommend | 已校验报告信封和测试证据 | 汇总报告、来源、新鲜度、限制 | Low：错误汇总；禁止修改源报告或触发任务。 |
| 4. data-agent | `agt_ops_data_phase3_001` | `0.1.0` | L1；仅合成/脱敏非生产数据集 | Observe, Analyze, Recommend | 批准的合成或脱敏样本 | 聚合指标、口径、置信度、限制 | Medium：数据泄露/误读；禁止原始生产数据、Core/SAP、导出和写入。 |
| 5. ceo-agent | `agt_ceo_decision_phase3_001` | `0.1.0` | L1；只读已批准报告摘要 | Analyze, Recommend | Report Center 的脱敏、可追溯报告 | CEO 决策辅助、风险、机会、待人工决策事项 | Medium：建议误用；禁止自动决策、审批、分派、通知或执行。 |

## 6. 权限控制

### 6.1 L0–L4 权限等级

| 等级 | 定义 | Phase 3 状态 |
|---|---|---|
| L0 | 无访问；仅文档与审计元数据查看。 | 可用于审计员。 |
| L1 | 受控 Observe/Analyze/Recommend；仅合成或脱敏非生产输入；无写入。 | **Phase 3 Agent 的最高允许等级。** |
| L2 | 已批准的受限只读业务数据访问。 | 禁止。 |
| L3 | 受限写入或受控业务动作。 | 禁止。 |
| L4 | 高风险、跨系统或生产执行。 | 禁止。 |

### 6.2 决策模型与禁止权限扩大

- **RBAC：** 平台管理员仅管理基础设施；Registry 管理员仅管理登记；审计员只读审计；Agent Owner 只能提交本 Agent 变更。职责必须分离。
- **ABAC：** 每个请求同时校验环境、目的、数据分类、Agent ID/版本/状态、审批有效期、风险、时间、来源和输出目的地。
- **Capability：** Runtime 只接受 Hub 签发的短时、不可转授、受众绑定、最小范围能力令牌；令牌必须绑定 Agent、版本、任务、输入 schema 和过期时间。
- **最终授权：** `RBAC ∩ ABAC ∩ Registry capability ∩ 批准范围 ∩ 当前状态`；任一项未知或拒绝即拒绝。
- 不得通过角色、属性、令牌、配置、缓存、人工口头指令或 Agent 间转发扩大任何权限。能力、数据、环境、输出目标或动作范围扩大必须作为新 Agent 版本重新注册、验证与审批。

## 7. 备份方案

所有备份必须在变更前完成、加密、访问受控、记录校验和与恢复演练结果；备份中不得包含明文密钥、令牌或真实生产数据。

| 备份对象 | 最小内容 | 时点与保留 | 恢复验证 |
|---|---|---|---|
| Registry 备份 | schema、登记记录、版本、生命周期、审批引用、策略版本、审计索引与撤销清单 | 每次 Registry 变更前后；按经批准保留策略保存 | 在隔离环境校验完整性并恢复只读副本。 |
| Agent 配置备份 | 每个 Agent manifest、能力、权限、输入输出 schema、负责人、风险和状态 | 每次版本/权限变更前后 | 校验 manifest 签名/校验和与 Registry 版本一致。 |
| Runtime 配置备份 | 镜像版本/摘要、环境模板、网络策略、身份引用、健康与紧急停止配置 | 部署前、配置变更前后 | 隔离环境启动并验证默认拒绝、健康与审计。 |
| Compose 备份 | 已批准 Compose 文件、覆盖文件、变量键名清单（不含秘密值）、部署版本与校验和 | 每次部署前后 | 以隔离变量文件执行配置解析与版本比对。 |

## 8. 回滚方案

**触发条件：** 权限校验失败、未授权访问尝试、错误激活、审计缺失、健康检查失败、报告 schema 违规、异常网络出口或任何范围违反。触发后立即停止新增任务、撤销短时令牌、将受影响 Agent 置为 `Suspended`，并保留证据。

| 恢复对象 | 回滚动作 | 完成判定 |
|---|---|---|
| Agent 版本回退 | 停止新版本任务；撤销其令牌；将 Registry 指针恢复至上一已批准版本；重新校验 manifest 与审计。 | 旧版本状态、能力和审批引用一致；新版本无法接收任务。 |
| Registry 恢复 | 冻结写入；恢复最近已验证 Registry 备份；重放经批准且有审计证据的必要变更；校验撤销清单。 | Registry 完整性通过；所有非 Active/撤销 Agent 均被拒绝。 |
| Runtime 恢复 | 停止受影响 Runtime；恢复已验证镜像和配置；重新应用默认拒绝网络与身份策略。 | 健康、令牌校验、审计和紧急停止验证均通过。 |
| 配置恢复 | 恢复已批准 Compose、Hub、Gateway、策略和 Report Center 配置快照；不得从未知工作目录复制配置。 | 配置校验和匹配；未产生新增端口、路由、权限或数据源。 |

回滚不是范围扩大或继续执行的授权。恢复后必须生成异常记录、完成根因分析，并在新的审批后才可重新尝试。

## 9. 验收标准

| 验收项 | 通过标准 | 证据 |
|---|---|---|
| Agent Hub 运行 | Hub 可用、仅经 Gateway 接收请求、默认拒绝未知请求。 | 健康响应、Gateway 日志、拒绝审计。 |
| Registry 正常 | 记录、版本、状态、审批和撤销状态可验证；未注册 Agent 被拒绝。 | 查询结果、签名/完整性校验、审计事件。 |
| Agent 注册成功 | `health-agent` 按顺序完成 Draft/Registered 验证，元数据与 schema 完整。 | Registry 记录、负责人确认、注册审计。 |
| Health Check 通过 | Hub、Registry、Runtime 与 Report Center 均健康；策略/Registry 故障 fail-closed。 | 健康检查报告与故障注入结果。 |
| Report 生成成功 | Report Center 生成含 Agent ID、版本、时间、证据、新鲜度、限制和审计引用的脱敏测试报告。 | 报告 ID、schema 验证、审计关联。 |
| 权限验证通过 | L0–L4、RBAC、ABAC、Capability 的允许与拒绝路径均测试；无 L2+、SAP/Core/生产数据或 Execute 权限。 | 授权测试矩阵、拒绝日志、配置审查。 |

任何一项失败或证据缺失，Phase 3 验收不通过，系统保持/恢复为不可执行状态。

## 10. 审批门禁

执行前必须逐项确认并在执行报告中记录：

- [ ] **Artifact Approved：** 本 Artifact 的明确版本已由授权审批人批准，Draft 状态已解除。
- [ ] **执行窗口确认：** 已确认开始/结束时间、影响范围、监控、值守、停止条件与回滚窗口。
- [ ] **负责人确认：** 变更负责人、平台负责人、Registry Owner、安全/权限责任人、验证人及回滚负责人已确认可用。

任何一项未确认，**不得执行**。审批仅授权本 Artifact 明确范围内的步骤，不授权生产数据、SAP/Core 访问或自动业务执行。

## 11. 执行报告

实际执行必须使用并完整填写：[`VAFOX_CONTROL_PLANE_PHASE3_AGENT_HUB_ACCEPTANCE_REPORT.md`](VAFOX_CONTROL_PLANE_PHASE3_AGENT_HUB_ACCEPTANCE_REPORT.md)。报告未完成、证据缺失或验收不通过时，不得将 Artifact 标记为已完成或批准上线。

## 12. 禁止事项

以下行为绝对禁止：

1. 绕过审批或在 Draft/未批准状态下执行。
2. 运行未注册、非 Active、版本不匹配、审批失效或被暂停的 Agent。
3. 绕过 Gateway、Hub、Registry、策略决策或资源侧校验。
4. 绕过 RBAC、ABAC、Capability 或借用/转授其他主体权限。
5. 接入生产数据、SAP、Core 真实数据或其访问路径。
6. 自动业务执行，或以建议、报告、重试、批处理、脚本或人工口头指令间接触发执行。
