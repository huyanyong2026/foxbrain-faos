# VAFOX Control Bridge Architecture

## 0. 总览

本文设计 `VAFOX Control Bridge` 架构，用于在不让 Codex Cloud 直接访问生产服务器的前提下，通过用户电脑审批与 Huyan Robot Gateway 执行，实现对 AI、Core 等受控节点的安全自动化管理。

```text
Codex Cloud
      |
      | 方案 / Artifact / 报告请求
      v
用户电脑 VAFOX Control Bridge
      |
      | 审批后同步 / 人工确认 / 安全转发
      v
Huyan Robot Gateway / Control Plane
      |
      | Ansible / Runner / Agent
      v
-------------------------
|                       |
AI                      Core
1.13.254.217            139.199.174.36
ai.vafox.com            core.vafox.com
```

## 1. 当前服务器清单

| 角色 | 公网 IP | 域名 | 登录用户 | 定位 |
| --- | --- | --- | --- | --- |
| Huyan | `140.143.207.194` | `huyan.vafox.com` | `ubuntu` | VAFOX Robot Gateway / Control Plane |
| AI | `1.13.254.217` | `ai.vafox.com` | `ubuntu` | AI 受控节点 |
| Core | `139.199.174.36` | `core.vafox.com` | `root` | Core 受控节点 |

## 2. 设计原则

1. **Codex Cloud 不直接访问生产服务器**：Codex Cloud 只负责生成规划、脚本、配置、Runbook、审计说明和报告模板，不持有生产服务器 SSH Key，不发起到生产服务器的网络连接。
2. **用户电脑作为安全中转和审批节点**：用户电脑保存待执行 Artifact，进行人工审阅、签名、审批和同步，是所有自动化动作进入生产环境前的控制点。
3. **Huyan 作为 VAFOX Robot Gateway / Control Plane**：Huyan 负责接收已审批 Artifact，执行 Ansible Playbook、Runner 作业、Agent 调度、备份和报告归档。
4. **AI 和 Core 作为受控节点**：AI 与 Core 不主动接受 Codex Cloud 指令，只接受 Huyan Control Plane 的受控操作。
5. **最小权限与可审计**：每次变更都应有计划、Artifact、审批记录、执行日志、回滚方案和最终报告。

## 3. 用户电脑目录结构

建议在用户电脑创建固定工作目录：

```text
VAFOX-Control/
├── plans/
│   ├── draft/
│   ├── approved/
│   └── archived/
├── artifacts/
│   ├── incoming/
│   ├── reviewed/
│   ├── approved/
│   └── rejected/
├── scripts/
│   ├── sync-to-huyan/
│   ├── validate/
│   └── local-tools/
├── reports/
│   ├── execution/
│   ├── inspection/
│   ├── backup/
│   └── incidents/
├── approvals/
│   ├── pending/
│   ├── signed/
│   └── revoked/
├── inventory/
│   ├── production.yml
│   └── staging.yml
├── keys/
│   ├── README.md
│   └── encrypted/
└── logs/
    ├── sync.log
    └── audit.log
```

### 3.1 目录职责

| 目录 | 职责 |
| --- | --- |
| `plans/` | 保存 Codex Cloud 生成的规划文档、执行步骤、风险分析和回滚方案。 |
| `artifacts/` | 保存脚本、Playbook、配置文件、服务模板、检查清单等可执行交付物。 |
| `scripts/` | 保存本地校验、同步、打包、签名、审批辅助脚本。 |
| `reports/` | 保存 Huyan 返回的执行报告、巡检报告、备份报告和事故报告。 |
| `approvals/` | 保存人工审批记录、签名文件、审批元数据和撤销记录。 |
| `inventory/` | 保存本地可读的环境清单，用于审阅，不直接替代 Huyan 端生产 Inventory。 |
| `keys/` | 只保存加密后的密钥材料或密钥说明，不保存明文生产私钥。 |
| `logs/` | 保存本地同步、审批、校验和操作日志。 |

## 4. Codex Cloud 工作流程

Codex Cloud 的工作边界是“生成与解释”，不是“直连与执行”。推荐流程如下：

```text
用户提出目标
  ↓
Codex Cloud 生成方案
  ↓
Codex Cloud 生成 Artifact
  ↓
同步到用户电脑 VAFOX-Control/artifacts/incoming
  ↓
用户电脑本地校验
  ↓
用户人工审批
  ↓
审批后同步到 Huyan
  ↓
Huyan 执行
  ↓
Huyan 返回报告到用户电脑
```

### 4.1 生成方案

Codex Cloud 根据用户目标输出以下内容：

- 背景与目标说明。
- 影响范围：Huyan、AI、Core 或未来节点。
- 前置条件。
- 变更步骤。
- 风险点。
- 验证方法。
- 回滚方案。
- 预计执行时间。
- 需要用户确认的问题。

### 4.2 生成 Artifact

Artifact 可以包括：

- Ansible Playbook。
- Shell 脚本。
- systemd service 文件。
- Nginx / Docker / Compose / Kubernetes 配置。
- 数据库迁移脚本。
- 巡检脚本。
- 备份脚本。
- 回滚脚本。
- 报告模板。

所有 Artifact 必须满足：

1. 默认 dry-run 或 check mode 优先。
2. 包含幂等设计。
3. 包含失败退出码。
4. 包含日志输出。
5. 包含回滚路径。
6. 不包含明文密码、Token 或生产私钥。

### 4.3 同步到电脑

同步方式可以是：

- 用户手动下载。
- Git 分支 / Pull Request。
- 加密压缩包。
- 本地 CLI 拉取任务包。

进入用户电脑后，Artifact 默认放入：

```text
VAFOX-Control/artifacts/incoming/<task-id>/
```

### 4.4 等待审批

用户电脑执行本地校验：

- 文件完整性校验。
- 危险命令扫描。
- 目标主机确认。
- SSH 用户确认。
- 变更窗口确认。
- 回滚脚本确认。

审批通过后，将审批文件写入：

```text
VAFOX-Control/approvals/signed/<task-id>.approval.yml
```

未审批的 Artifact 不允许同步到 Huyan 执行目录。

## 5. Huyan Control Plane 设计

Huyan 是 VAFOX Robot Gateway / Control Plane，建议根目录为：

```text
/opt/vafox-control/
├── ansible/
│   ├── inventories/
│   ├── playbooks/
│   ├── roles/
│   └── group_vars/
├── runner/
│   ├── jobs/
│   ├── queue/
│   ├── running/
│   ├── completed/
│   └── failed/
├── agent/
│   ├── bin/
│   ├── config/
│   ├── state/
│   └── hooks/
├── backup/
│   ├── configs/
│   ├── manifests/
│   ├── snapshots/
│   └── restore-tests/
├── reports/
│   ├── execution/
│   ├── inspection/
│   ├── backup/
│   └── rollback/
├── approvals/
│   ├── received/
│   └── verified/
├── artifacts/
│   ├── received/
│   ├── staged/
│   └── archived/
├── logs/
│   ├── runner.log
│   ├── ansible.log
│   └── audit.log
└── tmp/
```

### 5.1 Ansible

Ansible 负责对 AI 和 Core 执行标准化任务：

- 主机巡检。
- 包升级。
- 配置发布。
- 服务部署。
- 服务重启。
- 健康检查。
- 回滚恢复。

建议 Inventory 模型：

```yaml
all:
  children:
    ai:
      hosts:
        ai.vafox.com:
          ansible_host: 1.13.254.217
          ansible_user: ubuntu
    core:
      hosts:
        core.vafox.com:
          ansible_host: 139.199.174.36
          ansible_user: vafox-exec
```

> Core 当前登录用户为 `root`，但目标设计应迁移到 `vafox-exec` 受限执行账号，避免长期使用 root 直连执行自动化任务。

### 5.2 Runner

Runner 负责任务生命周期：

1. 接收已审批 Artifact。
2. 校验审批签名和任务元数据。
3. 创建任务目录。
4. 执行 dry-run。
5. 等待二次确认或策略自动放行。
6. 执行正式任务。
7. 收集日志和结果。
8. 生成报告。
9. 将报告同步回用户电脑。

任务状态：

```text
received -> validated -> staged -> dry-run -> approved-run -> running -> completed
                                                    └──────────────> failed
                                                    └──────────────> rolled-back
```

### 5.3 Agent

Agent 是 Huyan 本地守护组件，可通过 systemd 运行，负责：

- 监听 `/opt/vafox-control/runner/queue`。
- 验证任务文件和审批文件。
- 调用 Ansible Runner 或受控 Shell Runner。
- 统一写入审计日志。
- 控制并发和锁。
- 处理超时与失败回滚。

### 5.4 Backup

Backup 模块负责：

- 备份 Huyan 自身配置。
- 备份 AI / Core 关键配置。
- 记录备份 Manifest。
- 定期执行恢复演练。
- 保存备份校验和。

建议备份分层：

- L1：配置备份，频率高，体积小。
- L2：应用数据备份，按服务窗口执行。
- L3：系统级快照，由云厂商或专用备份服务器执行。

### 5.5 Reports

Reports 模块生成统一格式报告：

- `task-id`。
- 执行人 / 审批人。
- 目标节点。
- 执行时间。
- 变更摘要。
- 命令摘要。
- 成功 / 失败状态。
- 关键日志摘要。
- 验证结果。
- 回滚状态。
- 后续建议。

## 6. 服务器连接模型

### 6.1 连接方向

```text
用户电脑  -> Huyan
Huyan     -> AI
Huyan     -> Core
AI        -X-> Codex Cloud
Core      -X-> Codex Cloud
Codex     -X-> Huyan / AI / Core
```

`-X->` 表示禁止直接连接或不纳入自动化访问路径。

### 6.2 Huyan 到 AI

- 源：`huyan.vafox.com` / `140.143.207.194`。
- 目标：`ai.vafox.com` / `1.13.254.217`。
- 推荐用户：`vafox-exec`，过渡期可使用 `ubuntu`。
- 协议：SSH over Tailscale / WireGuard 优先，公网 SSH 作为受控备用。
- 权限：sudo 白名单限制在必要命令集合。

### 6.3 Huyan 到 Core

- 源：`huyan.vafox.com` / `140.143.207.194`。
- 目标：`core.vafox.com` / `139.199.174.36`。
- 当前用户：`root`。
- 目标用户：`vafox-exec`。
- 协议：SSH over Tailscale / WireGuard 优先。
- 权限：禁止默认 root 自动化；将 root 用于初始化、紧急恢复和 break-glass 场景。

## 7. 安全设计

### 7.1 SSH Key

- Codex Cloud 不保存生产 SSH Key。
- 用户电脑保存本地加密密钥或使用硬件密钥。
- Huyan 保存只用于访问 AI / Core 的受限部署密钥。
- 每个方向使用独立 Key：
  - 用户电脑 -> Huyan。
  - Huyan -> AI。
  - Huyan -> Core。
- SSH Key 必须设置 passphrase 或由系统 Keychain / Secret Manager 托管。
- 定期轮换 Key，并将轮换记录写入审计日志。

### 7.2 Tailscale / WireGuard

推荐建立私有管理网络：

```text
用户电脑 <-> Huyan <-> AI
                 └-> Core
```

策略：

- SSH 管理端口优先只监听内网地址。
- 公网 SSH 使用防火墙白名单限制来源 IP。
- Tailscale ACL / WireGuard peer 配置限制节点间访问范围。
- 控制面流量与业务流量分离。

### 7.3 权限隔离

- 用户电脑负责审批，不直接批量操作 AI / Core。
- Huyan 负责执行，不负责生成未经审批的变更。
- AI / Core 只接受 Huyan 的自动化操作。
- 生产 Secret 不进入 Codex Cloud。
- Artifact 进入 Huyan 前必须有审批记录。

### 7.4 `vafox-exec` 账号

在 Huyan、AI、Core 上统一规划 `vafox-exec` 自动化账号：

- 禁止密码登录。
- 只允许 SSH Key 登录。
- 使用 sudoers 白名单授权。
- 禁止交互式高危命令，除非处于 break-glass 流程。
- 配置命令日志和 TTY 审计。
- 对不同节点使用不同授权范围。

### 7.5 审批与防误操作

审批文件建议包含：

```yaml
task_id: VAFOX-YYYYMMDD-001
requested_by: user
approved_by: user
approved_at: "2026-07-18T00:00:00Z"
targets:
  - ai.vafox.com
  - core.vafox.com
artifact_sha256: "..."
plan_sha256: "..."
dry_run_required: true
rollback_required: true
production_window: "manual-confirmed"
```

Runner 必须拒绝以下任务：

- 无审批文件。
- 审批文件与 Artifact 哈希不匹配。
- 目标节点不在 Inventory 白名单。
- 无回滚方案的高风险变更。
- 包含明文 Secret 的任务包。

## 8. 自动化流程

### 8.1 巡检

目标：周期性检查 Huyan、AI、Core 状态。

内容：

- CPU、内存、磁盘、网络。
- systemd 服务状态。
- Docker / 容器状态。
- 证书有效期。
- 安全更新状态。
- 登录失败记录。
- 关键业务端口。

输出：

```text
/opt/vafox-control/reports/inspection/<date>-inspection.md
VAFOX-Control/reports/inspection/<date>-inspection.md
```

### 8.2 备份

目标：在部署和升级前确保可恢复。

流程：

1. 生成备份计划。
2. 用户审批备份范围。
3. Huyan 执行配置和数据备份。
4. 生成 Manifest 和校验和。
5. 执行抽样恢复测试。
6. 返回备份报告。

### 8.3 部署

目标：以可审计、可回滚方式发布服务或配置。

流程：

1. Codex Cloud 生成部署计划和 Artifact。
2. 用户电脑审阅并批准。
3. Huyan 执行 dry-run。
4. 用户确认正式执行。
5. Huyan 部署到 AI / Core。
6. 执行健康检查。
7. 返回部署报告。

### 8.4 升级

目标：升级系统包、运行时、应用版本或模型服务。

流程：

1. 读取当前版本。
2. 生成升级矩阵。
3. 确认兼容性和停机窗口。
4. 备份。
5. 分节点升级。
6. 分阶段验证。
7. 保留旧版本回滚路径。

### 8.5 回滚

目标：当部署或升级失败时快速恢复。

流程：

1. Runner 检测失败或用户触发回滚。
2. 锁定当前任务，停止继续扩散。
3. 调用对应回滚 Artifact。
4. 恢复配置、服务、数据或版本。
5. 执行健康检查。
6. 生成回滚报告。

## 9. 未来扩展

### 9.1 新增 GPU 服务器

用途：模型训练、推理、批处理任务。

接入方式：

- 加入 Huyan Inventory 的 `gpu` group。
- 使用 `vafox-exec` 账号。
- 纳入巡检、GPU 指标、驱动版本、CUDA 版本检查。
- 增加模型服务部署和驱动升级 Runbook。

### 9.2 新增 BI 服务器

用途：报表、数据分析、内部看板。

接入方式：

- 加入 Huyan Inventory 的 `bi` group。
- 单独定义数据访问权限。
- 加强数据库凭证隔离。
- 增加报表服务备份和权限审计。

### 9.3 新增备份服务器

用途：集中保存配置备份、数据备份和离线归档。

接入方式：

- 加入 Huyan Inventory 的 `backup` group。
- Huyan 将备份 Manifest 同步到备份服务器。
- 启用不可变备份或版本化存储。
- 定期执行恢复演练。

### 9.4 多环境扩展

未来可增加：

- `dev` 开发环境。
- `staging` 预发布环境。
- `production` 生产环境。
- 多区域容灾节点。
- 多审批人策略。
- ChatOps 通知与审批。

## 10. 最终目标流程

最终实现闭环：

```text
用户提出目标

↓

ChatGPT / Codex 规划

↓

用户电脑审批

↓

Huyan 机器人执行

↓

AI / Core 自动运行

↓

返回报告
```

## 11. 建议落地阶段

### 阶段一：手工审批 + 手工同步

- 建立 `VAFOX-Control/` 本地目录。
- 建立 `/opt/vafox-control/` Huyan 目录。
- 手工复制 Artifact。
- 手工运行 Ansible Playbook。
- 手工归档报告。

### 阶段二：审批文件 + Runner 队列

- 引入标准审批 YAML。
- 引入 Artifact 哈希校验。
- 引入 Runner queue。
- 引入统一报告模板。

### 阶段三：Agent 守护进程

- Huyan 上运行 `vafox-control-agent`。
- 自动消费已审批任务。
- 自动执行 dry-run、正式执行、回滚和报告上传。

### 阶段四：完整控制面

- 私有网络固定化。
- 多服务器 Inventory。
- 多审批策略。
- 自动巡检、备份、部署、升级、回滚。
- 报告与审计可视化。

## 12. 非目标

本方案不包含以下动作：

- 不直接登录 Huyan、AI 或 Core。
- 不执行任何服务器命令。
- 不修改任何生产服务器配置。
- 不分发 SSH Key。
- 不触发部署、备份、升级或回滚。
