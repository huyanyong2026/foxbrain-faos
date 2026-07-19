# VAFOX Control Plane Phase 2 基础环境建设执行 Artifact

> **状态：Draft（草案）— 未审批不得执行。**
>
> 本 Artifact 仅定义 `control.vafox.com` Phase 2 基础环境的受控变更范围、门禁、证据、验证和回滚要求。它**不构成执行授权**，不自动执行服务器操作，不发起 SSH 连接，亦不修改腾讯云、Huyan、AI、Core 或任何生产系统。

## 一、Artifact Metadata

| 字段 | 内容 |
| --- | --- |
| Artifact ID | `VAFOX-CONTROL-PLANE-P2-FOUNDATION-001` |
| 标题 | VAFOX Control Plane Phase 2 基础环境建设执行 Artifact |
| 版本 | `v1.0.0-draft` |
| 创建时间 | `2026-07-19 UTC` |
| 生成工具 | Codex（文档生成；未连接目标环境） |
| 目标服务器 | `control.vafox.com`（公网：`114.132.55.178`；内网：`172.16.16.6`） |
| 前置状态 | Phase 1 Security Hardening 已完成；执行时仍须逐项复核。 |
| 风险等级 | **High**：涉及容器运行时、服务配置、持久化目录及控制面基础服务。 |
| 审批状态 | **Draft — 未审批，不得执行。** |
| 执行窗口 | `{{APPROVED_CHANGE_WINDOW_UTC}}` |
| 回滚位置 | `{{APPROVED_OFF_HOST_BACKUP_URI}}`；主机短期暂存：`/opt/vafox-control/backups/`。 |
| 关联计划 | `VAFOX_CONTROL_PLANE_PHASE2_FOUNDATION_PLAN.md` |
| 执行报告 | `VAFOX_CONTROL_PLANE_PHASE2_FOUNDATION_REPORT.md` |

### 1.1 变更范围与不变边界

**计划纳入范围：** Docker Engine、Docker Compose v2、固定版本和镜像来源治理、`/opt/vafox-control/` 标准目录、隔离网络、最小权限服务运行基线，以及 Registry、Hub、Approval、Report、Dashboard Backend 的服务准备。

**明确不在本 Artifact 的执行范围：** 腾讯云实例/安全组/DNS 修改；对 Huyan、AI、Core 的连接或配置修改；生产数据迁移；自动化发布；业务功能上线；未批准端口开放；任何 Secret 明文处理。

### 1.2 角色与停止条件

| 角色 | 必须在审批前明确 | 职责 |
| --- | --- | --- |
| 系统负责人 | `{{SYSTEM_OWNER}}` | 确认资产、业务影响、窗口和验收。 |
| 安全审批人 | `{{SECURITY_APPROVER}}` | 审核镜像、权限、网络、Secret 与风险接受。 |
| 执行负责人 | `{{EXECUTION_OWNER}}` | 仅在批准窗口按已批准清单执行并记录证据。 |
| 回滚负责人 | `{{ROLLBACK_OWNER}}` | 确认离机备份、恢复路径与回滚验证。 |
| 独立复核人 | `{{REVIEWER}}` | 复核关键门禁、验证结果和最终报告。 |

出现以下任一情况必须立即停止，不得进入下一步：审批缺失或过期；目标身份不一致；Phase 1 控制失效；备份不可读；镜像来源、digest 或扫描结论不一致；出现未批准网络暴露/特权权限；健康、日志、审计或恢复验证失败。

## 二、执行前检查

> **放行条件：** 下表全部为“通过”，有可追溯证据和有效审批后，才可在批准窗口开始人工受控执行。所有时间记录 UTC；报告仅引用脱敏证据，不记录凭据、私钥、Token 或密码。

| ID | 检查项 | 通过标准 | 结果 | 证据/记录引用 | 确认人/时间（UTC） |
| --- | --- | --- | --- | --- | --- |
| PRE-01 | Artifact 与审批 | Artifact ID、版本、范围、风险、窗口和回滚计划与批准变更单一致。 | `{{RESULT}}` | `{{CHANGE_REFERENCE}}` | `{{OWNER_UTC}}` |
| PRE-02 | 服务器身份确认 | 独立核对 FQDN、公网 IP `114.132.55.178`、内网 IP `172.16.16.6`、资产编号和 SSH 主机指纹；不以单一来源确认。 | `{{RESULT}}` | `{{ASSET_REFERENCE}}` | `{{OWNER_UTC}}` |
| PRE-03 | Phase 1 安全状态 | SSH Key only、root 远程禁止、密码登录禁止、UFW active、Fail2Ban active 均已验证且无未批准例外。 | `{{RESULT}}` | `{{SECURITY_EVIDENCE}}` | `{{OWNER_UTC}}` |
| PRE-04 | 磁盘空间 | 容量、inode、日志与 Docker 数据目录均满足批准阈值；为备份、回滚和日志保留足够余量。 | `{{RESULT}}` | `{{CAPACITY_EVIDENCE}}` | `{{OWNER_UTC}}` |
| PRE-05 | 网络状态 | DNS/时间同步、批准的入出站路径、UFW 规则与监听端口基线已复核；无新增公网暴露需求。 | `{{RESULT}}` | `{{NETWORK_EVIDENCE}}` | `{{OWNER_UTC}}` |
| PRE-06 | SSH 状态 | 已保留受控可用管理会话，并确认独立验证会话和带外恢复路径；不得断开唯一会话。 | `{{RESULT}}` | `{{SSH_RECOVERY_REFERENCE}}` | `{{OWNER_UTC}}` |
| PRE-07 | 备份状态 | 配置、Artifact、拟部署服务配置及当前运行状态备份已加密、校验、离机存放并完成读取验证。 | `{{RESULT}}` | `{{BACKUP_MANIFEST}}` | `{{OWNER_UTC}}` |
| PRE-08 | 发布输入 | Docker/Compose 固定版本、镜像 digest、SBOM（如适用）、漏洞/许可证审查、配置提交和 Secret 引用均获批准。 | `{{RESULT}}` | `{{RELEASE_MANIFEST}}` | `{{OWNER_UTC}}` |

## 三、Docker 基础环境

### 3.1 设计与执行控制

| 控制域 | 必须满足的设计/验证要求 |
| --- | --- |
| Docker Engine 安装 | 仅安装批准的受支持稳定版本；记录发行来源、包版本、校验依据、安装时间与变更单。不得使用未审查脚本或无版本约束安装。 |
| Docker Compose 安装 | 使用批准的 Docker Compose v2 插件并固定版本；Compose 定义按服务纳入版本控制和评审。 |
| 版本固定 | Engine、Compose、镜像名称与不可变 digest 必须进入 release manifest；禁止 `latest`、浮动 tag 或未记录的升级。 |
| 镜像来源管理 | 仅允许批准的官方来源、内部仓库或经审查镜像；拉取前确认来源、所有权、许可证、SBOM（如有）和漏洞扫描结论。 |
| 镜像校验 | 部署前复核 digest/签名策略（如适用）与清单一致；镜像扫描高风险问题须已修复、明确豁免或阻止上线。 |
| 容器最小权限 | 默认非 root；移除不必要 capability；可行时只读根文件系统；仅挂载必需目录；设置资源限制、健康检查、重启策略和日志轮转。禁止 `privileged`、Docker socket、host network、任意宿主机目录挂载，除非另有专项书面批准。 |
| 网络隔离 | 每服务域独立内部网络；仅批准入口可暴露；数据库、内部 API、管理端点不对公网开放；网络策略按最小连通性验证。 |

### 3.2 Docker 执行记录

| 项目 | 批准版本/digest | 实际结果 | 验证证据 | 执行人/UTC |
| --- | --- | --- | --- | --- |
| Docker Engine | `{{APPROVED_ENGINE_VERSION}}` | `{{RESULT}}` | `{{EVIDENCE}}` | `{{OWNER_UTC}}` |
| Docker Compose v2 | `{{APPROVED_COMPOSE_VERSION}}` | `{{RESULT}}` | `{{EVIDENCE}}` | `{{OWNER_UTC}}` |
| Docker daemon 基线 | `{{APPROVED_DAEMON_CONFIG_REF}}` | `{{RESULT}}` | `{{EVIDENCE}}` | `{{OWNER_UTC}}` |
| 网络隔离基线 | `{{APPROVED_NETWORK_POLICY_REF}}` | `{{RESULT}}` | `{{EVIDENCE}}` | `{{OWNER_UTC}}` |

## 四、目录初始化

### 4.1 规划目录

```text
/opt/vafox-control/
├── agents/       # Agent 工作区、受控定义和运行时数据
├── registry/     # Agent Registry 持久化数据
├── approvals/    # 审批记录、策略和不可变归档
├── reports/      # 健康、执行和审计报告
├── artifacts/    # 经批准的交付物、校验清单和证据
├── logs/         # Docker、Agent、执行及审计日志
├── backups/      # 加密备份暂存、清单和恢复演练记录
└── config/       # 非密钥配置、Compose 定义、模板和版本清单
```

### 4.2 初始化门禁

- 仅指定部署服务账号与对应服务组可写入必要目录；应用不以 `root` 日常运行。
- 服务之间不得共享可写工作目录；权限、属主、ACL（如使用）和挂载清单必须记录在报告。
- `config/` 只能保存非敏感配置、模板与 Secret 引用；不得保存明文 Secret。
- `backups/` 不是唯一备份位置；其内容须加密、校验并复制至批准的独立目标。
- 创建目录前后记录目录清单和权限摘要；不得覆盖、移动或删除非本范围内容。

| 目录 | 预期用途 | 服务写入主体 | 初始化结果/证据 |
| --- | --- | --- | --- |
| `agents/` | Agent 运行数据 | `{{APPROVED_SERVICE_IDENTITY}}` | `{{RESULT_EVIDENCE}}` |
| `registry/` | Registry 数据 | `{{APPROVED_SERVICE_IDENTITY}}` | `{{RESULT_EVIDENCE}}` |
| `approvals/` | 审批数据与归档 | `{{APPROVED_SERVICE_IDENTITY}}` | `{{RESULT_EVIDENCE}}` |
| `reports/` | 报告产物 | `{{APPROVED_SERVICE_IDENTITY}}` | `{{RESULT_EVIDENCE}}` |
| `artifacts/` | 版本化交付物 | `{{APPROVED_SERVICE_IDENTITY}}` | `{{RESULT_EVIDENCE}}` |
| `logs/` | 结构化日志 | `{{APPROVED_SERVICE_IDENTITY}}` | `{{RESULT_EVIDENCE}}` |
| `backups/` | 加密暂存和清单 | `{{APPROVED_BACKUP_IDENTITY}}` | `{{RESULT_EVIDENCE}}` |
| `config/` | 非密钥配置 | `{{APPROVED_DEPLOY_IDENTITY}}` | `{{RESULT_EVIDENCE}}` |

## 五、基础服务准备

> 本阶段准备服务边界、受控配置、网络、服务身份和健康检查；**不自动启用生产控制动作，不连接或修改 Huyan、AI、Core。**

| 服务 | 准备内容 | 最小安全边界 | 完成门禁 |
| --- | --- | --- | --- |
| Agent Registry | 身份、能力、版本、状态和注册记录的数据/接口准备。 | 仅认证内部访问；数据落于 `registry/`；变更可审计。 | 健康检查、备份、网络隔离和审计通过。 |
| Agent Hub | Agent 发现、路由、调度入口和受控通信准备。 | 仅选择已登记 Agent；无直接生产写权限；请求追踪与限流。 | 不存在绕过 Registry/Approval 的路径。 |
| Approval Center | 高风险动作、发布、权限与例外审批状态准备。 | 默认拒绝；审批绑定主体、动作、目标、时限；记录不可静默篡改。 | 身份、角色、时间戳、理由和审计验证通过。 |
| Report Center | 运行、执行、风险、审计报告汇集准备。 | 来源身份和完整性校验；敏感字段脱敏；输出在 `reports/`。 | 生成、查询、访问控制和留存策略通过。 |
| Dashboard Backend | 聚合状态和受权查询接口准备。 | 只读优先；仅经内部服务 API；不直接暴露数据库。 | 鉴权、速率限制、查询审计和健康检查通过。 |

服务启用顺序：**Registry → Hub → Approval Center → Report Center → Dashboard Backend**。任一前置服务的健康、身份、网络或审计不通过，后续服务不得启用。

## 六、配置管理

1. **环境变量：** 使用版本化 `.env.example` 或等效模板，只定义名称、格式、非敏感默认策略、必填条件和所属服务；实际环境文件不得提交 Git、进入镜像层、普通日志或报告。
2. **Secret 占位：** 本 Artifact 仅允许 `{{SECRET_REFERENCE}}`、`{{SECRET_VERSION}}` 等受控引用。数据库凭据、令牌、证书私钥和恢复密钥必须在批准的 Secret 管理系统或等效加密存储中管理，并采用按服务、按环境独立的最小访问权限。
3. **配置版本管理：** Compose、策略、模板和非敏感配置纳入 Git；生产部署必须关联批准提交、release 标签、镜像 digest、迁移版本（如适用）和变更单。配置变更须评审、可追溯、可恢复。
4. **启动前校验：** 必填变量、格式、允许值、Secret 引用可用性和依赖连通性必须验证；失败时安全停止，不得使用隐式默认值或降级安全控制。

## 七、日志审计

| 日志类别 | 最低覆盖范围 | 控制要求 |
| --- | --- | --- |
| Docker 日志 | daemon、容器 stdout/stderr、生命周期、健康状态、镜像/版本。 | 结构化 UTC 时间、服务名与关联 ID；轮转、容量阈值和告警。 |
| Agent 日志 | 注册、调用、状态变化、错误、策略决策。 | 记录 Agent ID、请求 ID、服务身份、结果和错误码；脱敏。 |
| 执行日志 | 工作流、部署、任务、恢复和人工变更。 | 记录审批引用、目标、输入摘要、开始/结束时间和结果。 |
| 审计日志 | 登录、授权、审批、配置变更、Secret 访问和管理操作。 | 记录主体、动作、对象、来源、时间、结果和理由；访问控制与完整性保护。 |

- 日志按服务分区落于 `logs/` 或批准的集中式日志目标；不得记录密码、Token、私钥或完整敏感载荷。
- 审计日志的读取、导出、删除和保留策略变更本身也必须审计；定期检查认证失败、权限提升、审批绕过、镜像漂移和备份失败。

## 八、备份方案

| 备份对象 | 内容 | 最低要求 | 状态/证据 |
| --- | --- | --- | --- |
| 配置备份 | Compose、非敏感配置、策略、模板、版本清单。 | 每次批准变更前后生成版本化快照；Git 历史与离机副本可用。 | `{{RESULT_EVIDENCE}}` |
| Artifact 备份 | Artifact、报告附件、校验和、审批/证据引用。 | 加密存储、完整性校验、独立目标留存、保留策略可追溯。 | `{{RESULT_EVIDENCE}}` |
| 服务配置备份 | daemon/Compose 服务配置、网络策略、目录权限、服务版本与运行状态摘要。 | 部署前创建，离机保存，完成读取/恢复演练；不含明文 Secret。 | `{{RESULT_EVIDENCE}}` |

所有备份须记录创建时间、创建人、来源版本、文件清单、SHA-256、加密状态、保留期限、离机 URI 和读取验证结果。仅有本机副本、无法读取、无校验和或无恢复责任人的备份均视为不通过。

## 九、部署验证

| 验证域 | 通过标准 | 结果 | 证据/复核人 |
| --- | --- | --- | --- |
| Docker 状态 | Engine/Compose 版本符合批准清单；容器版本、健康检查、资源限制、重启策略和隔离网络符合设计。 | `{{RESULT}}` | `{{EVIDENCE_REVIEWER}}` |
| 目录状态 | 根目录及八个子目录完整；权限最小化；持久化映射正确；无 Secret 或范围外数据。 | `{{RESULT}}` | `{{EVIDENCE_REVIEWER}}` |
| 服务状态 | 五项服务按依赖顺序运行；健康检查通过；最小授权链路有效；不存在绕过身份/审批的调用路径。 | `{{RESULT}}` | `{{EVIDENCE_REVIEWER}}` |
| 日志状态 | Docker、Agent、执行、审计日志可写、可检索、脱敏、关联、轮转；告警路径已验证。 | `{{RESULT}}` | `{{EVIDENCE_REVIEWER}}` |
| 备份状态 | 三类备份已加密、校验、离机留存；抽样恢复或读取验证成功。 | `{{RESULT}}` | `{{EVIDENCE_REVIEWER}}` |
| 安全状态 | Phase 1 控制仍有效；无特权容器、未批准端口、明文 Secret、共享密钥或未审查镜像。 | `{{RESULT}}` | `{{EVIDENCE_REVIEWER}}` |

## 十、回滚方案

> 回滚触发后，先停止扩大影响并保留必要诊断证据；仅由批准的回滚负责人使用已验证备份和上一稳定 release 操作。不得以开放 SSH、禁用 UFW/审计、使用浮动镜像或复制明文 Secret 作为恢复捷径。

| 回滚域 | 回滚方法 | 回滚后最低验证 |
| --- | --- | --- |
| Docker 回退 | 隔离异常版本，使用上一稳定 release 的批准 Compose 定义、固定镜像 digest 与版本清单重建服务。 | 容器健康、资源限制、网络策略、依赖和日志均通过。 |
| 配置恢复 | 从部署前批准的非敏感配置快照恢复；通过 Secret 管理系统恢复对应 Secret **引用/版本**，不在配置库写入明文。 | 配置版本、引用解析、启动校验和审计记录正确。 |
| 目录恢复 | 依据部署前目录/权限清单恢复目录结构、属主、最小权限和受控持久化数据；仅恢复本 Artifact 范围。 | 八个目录完整、权限正确、无越权写入或数据泄漏。 |
| 服务恢复 | 按 Registry → Approval Center → Hub → Report Center → Dashboard Backend 的依赖顺序恢复数据和服务。 | 最小授权闭环、健康检查、审计、备份和安全基线通过。 |

回滚完成后，必须更新本 Artifact 的执行报告，记录触发时间、原因、影响、恢复来源/版本、实际步骤、验证结果、遗留风险和后续审批结论。

## 十一、执行报告模板

执行结束后必须填写并归档 `VAFOX_CONTROL_PLANE_PHASE2_FOUNDATION_REPORT.md`。未生成完整报告，不得宣告本阶段执行完成或验收通过。报告模板包含：

- 执行时间；
- 执行人；
- Artifact 版本；
- 安装内容；
- 验证结果；
- 异常；
- 回滚情况。

## 十二、禁止事项

以下事项为绝对禁止项；发现后必须停止、记录异常并通知审批人和回滚负责人：

1. **禁止绕过审批：** 未批准、窗口外、审批过期、范围不一致或门禁失败时不得执行或继续。
2. **禁止明文密码：** 不得在代码、Git、Compose、环境文件、镜像、日志、报告、聊天或工单中保存、展示或传输密码及其他 Secret。
3. **禁止共享密钥：** 不得在人员、服务、环境、节点或自动化任务间复用 SSH 私钥、Token、数据库凭据或服务身份密钥。
4. **禁止直接生产修改：** 不得跳过版本化、评审、备份、验证、变更记录与批准流程直接修改生产服务、配置、数据或网络。
5. **禁止未记录执行：** 每一步实际操作、版本、时间、证据、结果、异常和回滚必须记录在执行报告；口头确认或聊天记录不能替代报告。
6. **禁止越界操作：** 不得自动执行服务器操作、发起 SSH、修改腾讯云、修改 Huyan、AI、Core，或开放未批准的端口与接口。

## 十三、审批与签署

| 角色 | 姓名/标识 | 确认内容 | 时间（UTC） | 审批/记录引用 |
| --- | --- | --- | --- |
| 系统负责人 | `{{SYSTEM_OWNER}}` | 目标、范围、窗口、影响和验收标准已确认。 | `{{UTC}}` | `{{REFERENCE}}` |
| 安全审批人 | `{{SECURITY_APPROVER}}` | 镜像、权限、网络、Secret、备份和风险控制已批准。 | `{{UTC}}` | `{{REFERENCE}}` |
| 执行负责人 | `{{EXECUTION_OWNER}}` | 已理解门禁、停止条件、验证和报告义务。 | `{{UTC}}` | `{{REFERENCE}}` |
| 回滚负责人 | `{{ROLLBACK_OWNER}}` | 离机备份、恢复位置、恢复责任与演练证据已确认。 | `{{UTC}}` | `{{REFERENCE}}` |
| 独立复核人 | `{{REVIEWER}}` | 已复核所有执行前门禁与最终验收证据。 | `{{UTC}}` | `{{REFERENCE}}` |

**执行授权声明：** 在上述签署、变更单和执行窗口均有效前，本 Artifact 始终为 Draft，不得用于执行任何环境操作。
