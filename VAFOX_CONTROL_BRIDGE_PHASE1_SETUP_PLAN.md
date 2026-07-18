# VAFOX Control Bridge Phase 1 Setup Plan

## 0. 目标与范围

### 0.1 Phase 1 总目标

VAFOX Control Bridge 第一阶段的目标是建立一条安全、可审计、低风险的控制链基础，使 Codex Cloud 能够围绕用户明确授权的运维需求生成方案、产出可审查 Artifact，并通过用户电脑上的 `VAFOX-Control` 工作区与 Huyan Control Plane 形成受控衔接。

当前目标只覆盖方案设计、目录规划、流程定义、安全边界和验收标准，不执行任何服务器操作。

### 0.2 当前架构

```text
Codex Cloud
      |
      |
用户电脑 VAFOX-Control
      |
      |
Huyan Robot Gateway / Control Plane
      |
---------------------
|                   |
AI                  Core

ai.vafox.com        core.vafox.com
```

### 0.3 服务器信息

| 角色 | IP | 域名 | Phase 1 处理方式 |
| --- | --- | --- | --- |
| Huyan | `140.143.207.194` | `huyan.vafox.com` | 仅规划 Control Plane 目录与流程，不登录、不修改 |
| AI | `1.13.254.217` | `ai.vafox.com` | 仅纳入健康检查规划，不登录、不修改 |
| Core | `139.199.174.36` | `core.vafox.com` | 仅纳入健康检查规划，不登录、不修改 |

### 0.4 明确不做事项

Phase 1 不进行任何服务器端操作，包括但不限于：

- 不 SSH 登录 Huyan、AI、Core 服务器。
- 不创建、修改或删除服务器目录。
- 不安装软件包。
- 不修改生产配置。
- 不重启服务。
- 不执行部署、升级、切换 release 或数据删除操作。

---

## 一、用户电脑 VAFOX-Control 初始化

### 1.1 本地工作区目录

在用户电脑上规划以下目录结构：

```text
VAFOX-Control/
├── plans/
├── artifacts/
├── approvals/
├── scripts/
├── reports/
└── backups/
```

### 1.2 目录职责

| 目录 | 职责 | 内容示例 | 权限建议 |
| --- | --- | --- | --- |
| `plans/` | 存放 Codex Cloud 生成的实施计划、任务拆解、变更方案和回滚方案。 | `VAFOX_CONTROL_BRIDGE_PHASE1_SETUP_PLAN.md`、`DAILY_HEALTH_CHECK_PLAN.md` | 普通可读写；纳入版本管理或定期备份 |
| `artifacts/` | 存放经方案生成后的执行产物，但 Phase 1 默认只生成、不执行。 | Ansible playbook 草案、shell 脚本草案、配置模板、检查清单 | 可读写；执行前必须审批 |
| `approvals/` | 存放用户审批记录、授权单、执行窗口确认和风险接受记录。 | `APPROVAL_2026-07-18_DAILY_HEALTH_CHECK.md` | 建议只追加，不覆盖历史 |
| `scripts/` | 存放本地辅助脚本，用于整理 Artifact、校验报告格式、归档文件等。 | `validate_report.sh`、`package_artifacts.sh` | 默认不可自动执行生产操作 |
| `reports/` | 存放从 Huyan Control Plane 或人工检查流程回收的报告。 | `VAFOX_DAILY_HEALTH_REPORT.md`、周报、异常报告 | 可读写；按日期归档 |
| `backups/` | 存放本地计划、Artifact、审批和报告的备份副本。 | `2026-07-18-control-bridge-phase1.tar.gz` | 建议加密或限制本机账户访问 |

### 1.3 本地初始化原则

- 所有计划先落在 `plans/`，不直接转化为服务器操作。
- 所有可执行 Artifact 先落在 `artifacts/`，必须经过人工审查。
- 所有授权必须落在 `approvals/`，且记录授权人、授权时间、授权范围和过期时间。
- 所有执行结果必须回收到 `reports/`，并与对应审批记录建立引用关系。
- 所有关键文件定期复制到 `backups/`，避免计划、审批和报告丢失。

---

## 二、Codex Cloud 工作流程

### 2.1 总体流程

```text
需求输入
  ↓
方案生成
  ↓
Artifact 生成
  ↓
用户审批
  ↓
执行授权
  ↓
报告回收
```

### 2.2 需求输入

用户在 Codex Cloud 中输入运维需求，例如：

- “生成每日健康报告方案”。
- “检查 Huyan、AI、Core 三台服务器的关键服务状态”。
- “规划 Huyan Robot Gateway 的目录结构”。

需求输入阶段必须明确：

- 目标服务器范围。
- 允许检查的项目。
- 明确禁止的操作。
- 是否只生成方案，还是允许生成待审批 Artifact。
- 是否需要报告模板。

### 2.3 方案生成

Codex Cloud 根据需求生成 Markdown 方案，默认写入本地 `VAFOX-Control/plans/`。

方案必须包含：

- 目标和范围。
- 涉及服务器和域名。
- 风险等级。
- 操作边界。
- 审批条件。
- 回滚或停止条件。
- 报告格式。

### 2.4 Artifact 生成

在用户确认方案方向后，Codex Cloud 可以生成 Artifact 草案，默认写入 `VAFOX-Control/artifacts/`。

Artifact 类型包括：

- 健康检查脚本草案。
- Ansible playbook 草案。
- 报告模板。
- 检查项清单。
- 本地归档脚本。

Phase 1 中 Artifact 的默认状态是“待审查”，不得默认执行。

### 2.5 用户审批

用户审批记录写入 `VAFOX-Control/approvals/`。

审批记录至少包含：

- 审批编号。
- 审批人。
- 审批时间。
- 对应计划文件。
- 对应 Artifact 文件列表。
- 允许执行的主机范围。
- 允许执行的命令范围。
- 有效时间窗口。
- 明确禁止事项。

### 2.6 执行授权

执行授权必须满足以下条件：

1. 有已归档的计划文件。
2. 有已归档的 Artifact 文件。
3. 有审批记录。
4. 授权范围明确到主机、任务、时间窗口和命令类别。
5. 任务属于 Phase 1 允许范围，例如只读健康检查。

如果任一条件不满足，执行应被拒绝或暂停。

### 2.7 报告回收

执行完成后，报告必须回收到 `VAFOX-Control/reports/`。

报告内容至少包含：

- 执行时间。
- 执行来源。
- 目标主机。
- 检查项结果。
- 异常摘要。
- 风险建议。
- 对应审批编号。
- 对应 Artifact 版本。

---

## 三、Huyan Control Plane 准备

### 3.1 服务器端规划目录

在 Huyan 服务器上规划以下目录结构：

```text
/opt/vafox-control/
├── ansible/
├── runner/
├── agent/
├── artifacts/
├── reports/
├── backups/
└── logs/
```

注意：Phase 1 只规划该目录结构，不执行服务器创建目录操作。

### 3.2 目录职责

| 目录 | 职责 | 内容示例 | Phase 1 状态 |
| --- | --- | --- | --- |
| `/opt/vafox-control/ansible/` | 存放未来面向 Huyan、AI、Core 的 Ansible inventory、playbook 和 role。 | `inventory.ini`、`health_check.yml` | 仅规划 |
| `/opt/vafox-control/runner/` | 存放受控任务执行器，用于读取授权、执行只读任务并生成报告。 | `run_health_check.sh`、任务调度入口 | 仅规划 |
| `/opt/vafox-control/agent/` | 存放未来 Huyan Robot Gateway agent 组件。 | agent 配置、心跳组件 | 仅规划 |
| `/opt/vafox-control/artifacts/` | 存放从用户电脑同步到 Huyan 的已审批 Artifact。 | 已审批脚本、playbook、模板 | 仅规划 |
| `/opt/vafox-control/reports/` | 存放服务器端生成的报告，等待回收到用户电脑。 | `VAFOX_DAILY_HEALTH_REPORT.md` | 仅规划 |
| `/opt/vafox-control/backups/` | 存放 Control Plane 自身配置、脚本和报告备份。 | 按日期归档包 | 仅规划 |
| `/opt/vafox-control/logs/` | 存放 runner、agent、同步任务和审计日志。 | `runner.log`、`audit.log` | 仅规划 |

### 3.3 Huyan Control Plane 设计原则

- Huyan 是控制入口，不在 Phase 1 中承担自动部署职责。
- Huyan 对 AI 和 Core 的检查应优先采用只读方式。
- Huyan 不保存长期高权限凭据，凭据使用必须可轮换、可审计、可撤销。
- 所有任务执行必须产生日志。
- 所有任务执行必须关联审批编号。
- 所有报告必须可回收到用户电脑。

---

## 四、第一阶段安全原则

### 4.1 禁止事项

Phase 1 明确禁止以下自动化行为：

- 禁止自动修改生产配置。
- 禁止自动升级系统、依赖、服务或应用。
- 禁止自动切换 release。
- 禁止自动删除数据、日志、备份、数据库记录或用户文件。
- 禁止自动重启生产服务。
- 禁止自动执行数据库写操作。
- 禁止自动变更防火墙、安全组、DNS、证书或负载均衡配置。

### 4.2 默认只读原则

第一阶段默认只允许只读检查，例如：

- 读取系统基本信息。
- 查看服务状态。
- 查看磁盘、内存、CPU 使用情况。
- 查看端口监听状态。
- 查看最近错误日志摘要。
- 检查 HTTP/HTTPS 健康端点。

### 4.3 人工审批原则

任何从“生成 Artifact”进入“执行 Artifact”的动作，都必须经过人工审批。

审批必须明确：

- 允许执行什么。
- 在哪里执行。
- 什么时候执行。
- 哪些命令禁止执行。
- 出现异常时如何停止。

### 4.4 审计原则

每次执行必须留下审计信息：

- 任务 ID。
- 审批 ID。
- Artifact 版本或哈希。
- 执行人或执行来源。
- 目标主机。
- 开始时间和结束时间。
- 执行结果。
- 报告文件路径。

---

## 五、第一批自动化任务规划

### 5.1 优先任务：每日健康报告

第一批自动化任务优先规划“每日健康报告”，用于低风险地建立 Control Bridge 的报告链路。

目标报告文件：

```text
VAFOX_DAILY_HEALTH_REPORT.md
```

### 5.2 检查范围

每日健康报告覆盖以下对象：

| 对象 | IP | 域名 | 检查目标 |
| --- | --- | --- | --- |
| Huyan | `140.143.207.194` | `huyan.vafox.com` | Control Plane 基础状态、磁盘、CPU、内存、关键进程、日志摘要 |
| AI | `1.13.254.217` | `ai.vafox.com` | 域名连通性、HTTP/HTTPS 响应、服务可用性摘要 |
| Core | `139.199.174.36` | `core.vafox.com` | 域名连通性、HTTP/HTTPS 响应、服务可用性摘要 |

### 5.3 建议检查项

#### Huyan

- 主机名和系统时间。
- CPU 使用率。
- 内存使用率。
- 磁盘使用率。
- 关键端口监听状态。
- Control Plane 目录存在性。
- Runner 或 Agent 进程状态。
- 最近错误日志摘要。

#### AI

- DNS 解析 `ai.vafox.com` 是否指向预期 IP。
- HTTP/HTTPS 可访问性。
- 健康端点响应状态，如果未来暴露 `/health` 或类似端点。
- TLS 证书有效期。
- 基础延迟。

#### Core

- DNS 解析 `core.vafox.com` 是否指向预期 IP。
- HTTP/HTTPS 可访问性。
- 健康端点响应状态，如果未来暴露 `/health` 或类似端点。
- TLS 证书有效期。
- 基础延迟。

### 5.4 报告模板

`VAFOX_DAILY_HEALTH_REPORT.md` 建议包含：

```markdown
# VAFOX Daily Health Report

## 1. Metadata

- Report Date:
- Generated By:
- Approval ID:
- Artifact Version:
- Scope:

## 2. Overall Status

- Huyan:
- AI:
- Core:
- Overall Risk Level:

## 3. Huyan Checks

| Check | Status | Detail |
| --- | --- | --- |
| System Time |  |  |
| CPU |  |  |
| Memory |  |  |
| Disk |  |  |
| Ports |  |  |
| Logs |  |  |

## 4. AI Checks

| Check | Status | Detail |
| --- | --- | --- |
| DNS |  |  |
| HTTP/HTTPS |  |  |
| Health Endpoint |  |  |
| TLS |  |  |
| Latency |  |  |

## 5. Core Checks

| Check | Status | Detail |
| --- | --- | --- |
| DNS |  |  |
| HTTP/HTTPS |  |  |
| Health Endpoint |  |  |
| TLS |  |  |
| Latency |  |  |

## 6. Findings

- Critical:
- Warning:
- Info:

## 7. Recommended Actions

- Immediate:
- Later:
- No Action Needed:

## 8. Audit Trail

- Task ID:
- Started At:
- Finished At:
- Runner:
- Source Artifact:
```

### 5.5 每日健康报告执行策略

Phase 1 推荐先采用以下策略：

1. Codex Cloud 生成健康检查方案和报告模板。
2. 用户审查方案。
3. 用户批准只读健康检查 Artifact。
4. Artifact 被放入本地 `VAFOX-Control/artifacts/`。
5. 在授权窗口内由用户手动触发或由未来 Huyan runner 执行。
6. 报告生成后回收到 `VAFOX-Control/reports/`。
7. 用户审查报告并决定是否进入下一阶段。

---

## 六、后续阶段

### Phase 2：Huyan Robot Gateway 建立

目标：在 Huyan 上建立受控 Robot Gateway，使其能够接收已审批任务、执行只读检查、生成报告并回传结果。

重点能力：

- Gateway 基础目录和配置。
- 审批文件校验。
- Artifact 签名或哈希校验。
- 任务执行日志。
- 报告回传机制。

### Phase 3：AI/Core 接入

目标：将 AI 和 Core 纳入 Huyan Control Plane 的受控检查范围。

重点能力：

- AI/Core 只读健康检查。
- 基础服务状态检查。
- HTTP/HTTPS 可用性监控。
- 异常报告聚合。

### Phase 4：自动备份

目标：在审批和安全边界下建立自动备份能力。

重点能力：

- 备份计划。
- 备份对象清单。
- 备份存储位置。
- 备份完整性校验。
- 恢复演练方案。

### Phase 5：自动部署

目标：在备份、审批、回滚和审计机制成熟后，引入自动部署能力。

重点能力：

- 构建 Artifact 管理。
- 灰度发布流程。
- 健康检查门禁。
- 自动回滚预案。
- 发布审计日志。

### Phase 6：自动升级

目标：在自动部署稳定后，引入系统、依赖和服务的受控升级能力。

重点能力：

- 升级前检查。
- 升级窗口审批。
- 兼容性验证。
- 分批升级。
- 升级后健康检查。
- 回滚或降级方案。

---

## 七、验收标准

### 7.1 Phase 1 验收条件

当以下条件全部满足时，可认为 VAFOX Control Bridge Phase 1 建成：

1. 用户电脑 `VAFOX-Control/` 工作区目录规划完成，并明确每个目录职责。
2. Codex Cloud 到用户电脑的“需求输入 → 方案生成 → Artifact 生成 → 用户审批 → 执行授权 → 报告回收”流程被文档化。
3. Huyan Control Plane 的 `/opt/vafox-control/` 目录规划完成，并明确每个目录职责。
4. 第一阶段安全原则明确，并形成禁止事项清单。
5. 每日健康报告任务完成方案设计，明确检查对象、检查项和报告模板。
6. `VAFOX_DAILY_HEALTH_REPORT.md` 的报告结构已定义。
7. 已明确 Phase 2 至 Phase 6 的后续演进路径。
8. 所有计划均保持“只设计方案，不执行服务器操作”的边界。

### 7.2 Control Bridge 基础建成标准

当以下能力具备时，可认为 Control Bridge 的基础控制链已经建成：

- Codex Cloud 能稳定生成结构化计划和待审批 Artifact。
- 用户电脑 `VAFOX-Control` 能保存计划、Artifact、审批、报告和备份。
- Huyan Control Plane 有清晰的目录、执行器、Agent、报告和日志规划。
- 所有执行动作都必须先有审批记录。
- 所有执行结果都能生成报告并回收到用户电脑。
- 所有任务都有审计链路，可追踪到需求、计划、Artifact、审批、执行和报告。
- 系统默认只读、默认不自动修改生产、默认不自动升级、默认不自动切换 release、默认不自动删除数据。

### 7.3 进入 Phase 2 的前置条件

进入 Phase 2 前，应完成以下准备：

- Phase 1 计划通过用户审查。
- 每日健康报告模板通过用户审查。
- Artifact 审批格式通过用户审查。
- 用户确认 Huyan Robot Gateway 的最小权限模型。
- 用户确认 Phase 2 仍不包含自动部署、自动升级和自动删除数据。

---

## 8. Phase 1 结论

VAFOX Control Bridge Phase 1 的核心不是执行自动化，而是建立可控边界：

- 先有方案。
- 再有 Artifact。
- 再有审批。
- 再有授权。
- 最后才有执行和报告。

在该阶段完成前，任何自动化都不应越过只读健康检查和人工审批边界。
