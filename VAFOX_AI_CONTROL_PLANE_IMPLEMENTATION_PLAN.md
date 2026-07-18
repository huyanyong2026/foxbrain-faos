# VAFOX AI Control Plane Implementation Plan

> 本文仅为架构与实施路线图，不包含任何服务器操作命令，也不要求立即登录或修改 Huyan、AI、Core 任一服务器。

## 0. 背景、目标与边界

### 0.1 服务器角色

| 服务器 | 公网 IP | 当前/目标定位 |
| --- | --- | --- |
| Huyan | `140.143.207.194` | 业务入口、对外访问、边缘接入节点 |
| AI | `1.13.254.217` | AI 业务服务器；未来 VAFOX Automation Control Plane 候选主控节点 |
| Core | `139.199.174.36` | 核心业务、数据、内部服务节点 |

### 0.2 总体目标

将 AI 服务器设计为未来 VAFOX Automation Control Plane 候选节点，在不影响现有 AI 业务稳定性的前提下，逐步承载以下能力：

1. 自动化编排：以 Ansible Controller 为基础，统一管理 Huyan、Core 以及未来新增服务器。
2. 自动发布：以 GitHub Actions Runner 或受控 Webhook/Job Worker 为入口，触发标准化发布流程。
3. 自动回滚：每次发布具备可追溯版本、可回滚包、可回滚 Playbook。
4. 自动备份：面向配置、数据、制品与运行状态建立分层备份。
5. 安全执行：通过 VAFOX Agent 与 `vafox-exec` 权限模型，限制自动化系统的执行边界。
6. 安全网络：通过 Tailscale/WireGuard 建立控制面私有网络，减少公网 SSH 暴露。

### 0.3 设计边界

- 本文只输出架构方案、目录设计、权限模型、流程路线图与验收标准。
- 本文不执行任何服务器命令，不变更 SSH、网络、防火墙、服务进程或 GitHub 配置。
- AI 服务器在成为控制平面之前，必须完成业务隔离、权限隔离、密钥隔离、网络隔离与审计隔离。

## 1. 总体架构

```text
                         GitHub Repository
                                |
                                | GitHub Actions / Webhook
                                v
+---------------------------------------------------------------+
| AI Server: 1.13.254.217                                        |
|                                                               |
|  /opt/ai-vafox                 /opt/vafox-control              |
|  - AI App Runtime              - Ansible Controller            |
|  - AI Models/Jobs              - GitHub Actions Runner         |
|  - AI Logs                     - VAFOX Agent                   |
|  - AI Data Cache               - Release/Backup/Rollback Jobs  |
|                                - vafox-exec Policy Layer       |
+------------------------------+--------------------------------+
                               |
                               | Tailscale/WireGuard Control Network
                               |
              +----------------+----------------+
              |                                 |
              v                                 v
+----------------------------+     +----------------------------+
| Huyan: 140.143.207.194     |     | Core: 139.199.174.36       |
| - Edge / Gateway           |     | - Core Services / Data      |
| - VAFOX Agent              |     | - VAFOX Agent               |
| - Limited vafox-exec       |     | - Limited vafox-exec        |
+----------------------------+     +----------------------------+
```

### 1.1 架构原则

1. **业务与控制分离**：AI 业务运行在 `/opt/ai-vafox`，控制平面运行在 `/opt/vafox-control`，两者使用不同系统用户、不同环境变量、不同日志路径与不同权限边界。
2. **最小权限**：控制平面默认无 root 常驻权限，所有高危动作通过 `vafox-exec` 白名单策略执行。
3. **可审计**：所有自动化动作必须产生操作人、触发源、目标主机、Git SHA、任务 ID、开始/结束时间、结果与日志索引。
4. **可回滚**：发布前创建快照或备份点，发布产物不可变，回滚流程必须在发布设计时同步定义。
5. **私网优先**：控制流量优先走 Tailscale/WireGuard 网络，公网 SSH 仅作为紧急 break-glass 通道。
6. **渐进接入**：先只读盘点，再低风险维护任务，最后才开放发布、回滚、修复等写操作。

## 2. AI 业务与控制平面隔离

### 2.1 用户隔离

建议定义三类系统身份：

| 用户/身份 | 作用 | 权限边界 |
| --- | --- | --- |
| `ai-vafox` | 运行现有 AI 业务 | 仅拥有 `/opt/ai-vafox` 与必要运行目录权限 |
| `vafox-control` | 运行 Ansible、Runner、调度器、控制 API | 拥有 `/opt/vafox-control`，不能直接修改 AI 业务目录 |
| `vafox-exec` | 受控执行高权限动作的最小代理身份 | 只能执行白名单脚本或 sudoers 白名单命令 |

### 2.2 进程隔离

- AI 业务进程不得与控制平面进程共用 Supervisor/Systemd unit。
- 控制平面组件独立启停：Ansible Controller、GitHub Actions Runner、VAFOX Agent、任务调度器、审计服务分别独立管理。
- 控制平面故障不得导致 AI 推理、AI API、AI Dashboard 或 AI Worker 停止。

### 2.3 配置隔离

- AI 业务配置：`/opt/ai-vafox/config`。
- 控制平面配置：`/opt/vafox-control/config`。
- 敏感配置统一进入独立 secrets 目录或外部 secrets manager，不允许混放到业务仓库。
- `.env` 文件分区管理：AI 业务 `.env` 不暴露给 Runner；Runner secrets 不暴露给 AI 应用。

### 2.4 网络隔离

- AI 业务端口只开放给业务访问方。
- 控制平面端口只允许 Tailscale/WireGuard 私网访问。
- Ansible SSH、Agent RPC、Runner webhook/control API 不应直接暴露公网。

### 2.5 日志隔离

- AI 业务日志：`/var/log/ai-vafox` 或 `/opt/ai-vafox/logs`。
- 控制平面日志：`/var/log/vafox-control` 或 `/opt/vafox-control/logs`。
- 审计日志必须追加写、定期归档、不可由普通发布流程覆盖。

## 3. 目录设计

### 3.1 `/opt/ai-vafox`

```text
/opt/ai-vafox
├── app/                    # AI 业务应用代码或运行包
├── config/                 # AI 业务配置，不包含控制平面密钥
├── data/                   # AI 业务数据、缓存、索引
├── models/                 # 模型权重或模型挂载点
├── logs/                   # AI 业务日志
├── releases/               # AI 业务不可变发布版本
├── current -> releases/... # 当前运行版本软链接
├── shared/                 # 跨版本共享资源
└── tmp/                    # 临时文件
```

设计要求：

- `ai-vafox` 用户拥有写权限。
- `vafox-control` 默认只有只读盘点权限，发布任务只能通过 `vafox-exec` 执行特定发布脚本。
- `releases/` 采用时间戳或 Git SHA 命名，支持快速切换 `current` 软链接回滚。

### 3.2 `/opt/vafox-control`

```text
/opt/vafox-control
├── ansible/
│   ├── inventories/
│   │   ├── production.yml
│   │   └── staging.yml
│   ├── playbooks/
│   │   ├── site.yml
│   │   ├── deploy-ai.yml
│   │   ├── deploy-huyan.yml
│   │   ├── deploy-core.yml
│   │   ├── backup.yml
│   │   └── rollback.yml
│   ├── roles/
│   ├── group_vars/
│   └── host_vars/
├── agent/
│   ├── bin/
│   ├── config/
│   └── state/
├── runner/
│   ├── work/
│   ├── hooks/
│   └── cache/
├── exec/
│   ├── policies/
│   ├── scripts/
│   └── approvals/
├── backups/
│   ├── manifests/
│   ├── snapshots/
│   └── restore-tests/
├── releases/
│   ├── artifacts/
│   ├── manifests/
│   └── rollback-points/
├── audit/
│   ├── events/
│   ├── logs/
│   └── reports/
├── secrets/
│   ├── ansible-vault/
│   └── runtime/
├── docs/
└── tmp/
```

设计要求：

- `vafox-control` 用户拥有主要写权限。
- `secrets/` 权限最小化，并尽量迁移到专用 secrets manager 或 Ansible Vault。
- `exec/scripts/` 中脚本必须版本化、代码评审、幂等化，并由 `exec/policies/` 显式授权。
- `audit/` 与 `backups/manifests/` 不允许被普通发布任务删除。

## 4. Ansible Controller

### 4.1 定位

Ansible Controller 是 VAFOX 控制平面的第一阶段核心，用于完成：

- 服务器资产盘点。
- 基线配置校验。
- 备份任务编排。
- 标准化发布与回滚。
- VAFOX Agent 安装、升级与健康检查。

### 4.2 Inventory 设计

```yaml
all:
  children:
    vafox:
      children:
        huyan:
          hosts:
            huyan-prod:
              ansible_host: 140.143.207.194
              vafox_role: edge
        ai:
          hosts:
            ai-prod:
              ansible_host: 1.13.254.217
              vafox_role: control_candidate
        core:
          hosts:
            core-prod:
              ansible_host: 139.199.174.36
              vafox_role: core
```

### 4.3 Playbook 分层

| Playbook | 作用 | 风险等级 |
| --- | --- | --- |
| `site.yml` | 全局基线检查与状态汇总 | 低 |
| `backup.yml` | 自动备份与备份校验 | 中 |
| `deploy-ai.yml` | AI 业务发布 | 高 |
| `deploy-huyan.yml` | Huyan 边缘服务发布 | 高 |
| `deploy-core.yml` | Core 核心服务发布 | 高 |
| `rollback.yml` | 按发布 manifest 回滚 | 高 |
| `agent-health.yml` | Agent 心跳与版本检查 | 低 |

### 4.4 执行策略

- 默认使用 `--check` 或 dry-run 模式验证变更影响。
- 高风险 Playbook 必须绑定 Git SHA、release manifest、backup manifest。
- 生产环境写操作必须有审批记录，可用 GitHub Environment Approval 或控制平面审批文件承载。
- Ansible 不直接使用 root SSH 登录，需通过普通用户与 `vafox-exec` 受控升级权限。

## 5. GitHub Actions Runner

### 5.1 定位

GitHub Actions Runner 是 CI/CD 入口，不是无限制运维入口。它只负责拉取可信仓库任务、构建产物、触发控制平面任务和上传审计结果。

### 5.2 Runner 类型

建议采用 self-hosted runner，但必须满足：

- 单独运行在 `vafox-control` 用户下。
- 使用独立工作目录 `/opt/vafox-control/runner/work`。
- 禁止 Runner 直接持有生产 root 私钥。
- Runner 仅能调用受控入口，例如 VAFOX Agent API、Ansible wrapper、`vafox-exec` 白名单任务。
- 对外部 Pull Request 任务默认不允许运行在生产 Runner 上。

### 5.3 Workflow 分层

| Workflow | 作用 | 可触发环境 |
| --- | --- | --- |
| `ci.yml` | 单元测试、静态检查、构建验证 | GitHub hosted 或隔离 runner |
| `package.yml` | 生成不可变发布包 | 隔离 runner |
| `deploy-staging.yml` | 部署预发布环境 | self-hosted staging runner |
| `deploy-production.yml` | 部署生产 | AI 控制平面 runner + 审批 |
| `rollback-production.yml` | 生产回滚 | AI 控制平面 runner + 双确认 |

### 5.4 安全控制

- 使用 GitHub Environments 区分 staging/production。
- production secrets 只注入 production workflow。
- Runner Token 定期轮换。
- Runner 工作目录每次任务后清理敏感文件。
- Workflow 必须记录 Git SHA、artifact digest、部署目标和审批人。

## 6. VAFOX Agent

### 6.1 定位

VAFOX Agent 是每台服务器上的轻量代理，负责本机状态上报、任务接收、受控执行、日志收集与健康检查。AI 服务器可运行控制平面 Agent 与本机业务 Agent；Huyan/Core 运行边缘 Agent。

### 6.2 Agent 能力

1. 心跳：上报主机名、角色、Agent 版本、系统负载、磁盘空间、关键服务状态。
2. 任务执行：仅执行控制平面签名且在本机策略允许范围内的任务。
3. 日志回传：将任务日志、发布日志、回滚日志写入控制平面审计目录。
4. 健康探测：对服务端口、HTTP health endpoint、进程状态、磁盘容量进行检查。
5. 版本自检：Agent 启动时校验自身 digest 与配置版本。

### 6.3 Agent 部署拓扑

| 节点 | Agent 角色 | 主要职责 |
| --- | --- | --- |
| AI | control-agent + local-agent | 控制任务编排、本机 AI 业务部署、审计汇总 |
| Huyan | edge-agent | 边缘服务状态、网关发布、日志回传 |
| Core | core-agent | 核心服务状态、数据备份、核心发布与回滚 |

### 6.4 Agent 通信

- 控制面通道优先使用 Tailscale/WireGuard 私网地址。
- Agent 与 Controller 之间使用 mTLS 或基于短期 token 的签名请求。
- 所有任务携带任务 ID、过期时间、目标主机、允许命令、参数摘要与签名。
- Agent 拒绝未签名、过期、越权或参数不匹配的任务。

## 7. `vafox-exec` 权限模型

### 7.1 目标

`vafox-exec` 是控制平面执行高权限动作的安全边界。它不是通用 shell，不允许任意命令拼接，不提供交互式 root 终端。

### 7.2 权限模型

```text
GitHub Actions / Ansible / VAFOX Agent
        |
        v
vafox-exec request
        |
        v
Policy Check: actor + host + action + args + environment + approval
        |
        +---- deny -> audit deny event
        |
        v
Execute approved script with constrained sudo rule
        |
        v
Write audit log + return result
```

### 7.3 Policy 维度

| 维度 | 示例 |
| --- | --- |
| actor | `github-actions:deploy-production`, `ansible:backup`, `agent:core-prod` |
| host | `ai-prod`, `huyan-prod`, `core-prod` |
| action | `deploy_service`, `restart_service`, `backup_data`, `rollback_release` |
| args | release id、service name、backup id |
| environment | staging、production |
| approval | none、single approval、dual approval |
| time window | 可选维护窗口 |

### 7.4 sudoers 原则

- `vafox-exec` 只能 sudo 执行固定路径脚本。
- 固定脚本不得允许任意 shell eval。
- 参数必须白名单校验。
- 所有脚本执行前后写审计日志。
- 高风险动作必须要求审批文件或 GitHub Environment Approval 记录。

### 7.5 动作分级

| 等级 | 动作 | 审批要求 |
| --- | --- | --- |
| L1 | status、health、inventory | 无审批 |
| L2 | backup、log collect、config diff | 自动审批或单审批 |
| L3 | deploy、restart non-critical service | 单审批 |
| L4 | rollback、restart core service、schema migration | 双确认 |
| L5 | firewall、ssh policy、root key rotation | break-glass 流程，不走普通自动化 |

## 8. SSH Key 安全体系

### 8.1 Key 分类

| Key 类型 | 用途 | 保存位置 | 轮换策略 |
| --- | --- | --- | --- |
| Operator Key | 人工紧急登录 | 人员本地安全设备 | 人员变更立即轮换 |
| Ansible Deploy Key | Controller 到节点执行自动化 | AI 控制平面 secrets | 30-90 天轮换 |
| GitHub Deploy Key | 拉取私有仓库或制品 | GitHub Secrets/Deploy Keys | 90 天轮换 |
| Agent mTLS Key | Agent 与 Controller 通信 | 各节点 Agent secrets | 90 天轮换或自动证书 |
| Break-glass Key | 灾难恢复 | 离线保管 | 使用后立即轮换 |

### 8.2 SSH 原则

- 禁止控制平面使用个人私钥执行自动化。
- 禁止 root 密钥常驻 Runner 工作目录。
- AI 到 Huyan/Core 的自动化登录使用专用低权限用户。
- 节点 `authorized_keys` 应区分人类登录 key 与自动化 key，并通过 forced command 或 source address 限制自动化 key。
- SSH key 指纹、创建时间、用途、负责人、过期时间必须登记在控制平面资产清单中。

### 8.3 密钥存储

- 短期：Ansible Vault + 文件权限隔离。
- 中期：接入专用 secrets manager。
- 长期：结合硬件密钥、短期证书或 SSH CA。

### 8.4 密钥轮换流程

1. 创建新 key 或证书。
2. 灰度加入目标节点授权列表。
3. 控制平面验证新 key 可用。
4. 切换自动化任务使用新 key。
5. 移除旧 key。
6. 生成轮换审计报告。

## 9. Tailscale/WireGuard 网络

### 9.1 目标

建立 VAFOX 私有控制网络，让 AI 控制平面通过内网地址管理 Huyan 与 Core，降低公网 SSH 和管理端口暴露面。

### 9.2 网络设计

| 节点 | 网络角色 | 访问策略 |
| --- | --- | --- |
| AI | Control Plane Node | 可访问 Huyan/Core 的控制端口 |
| Huyan | Managed Node / Edge | 只接受 AI 控制平面访问管理端口 |
| Core | Managed Node / Core | 只接受 AI 控制平面访问管理端口 |

### 9.3 Tailscale 方案

- 使用 ACL 限制只有 AI 控制平面身份可访问 Huyan/Core 的 SSH、Agent、metrics 端口。
- 使用 device posture 或 tags 区分 `tag:control-plane`、`tag:edge`、`tag:core`。
- 使用 MagicDNS 或固定私网地址简化 Ansible inventory。

### 9.4 WireGuard 方案

- AI 作为 hub，Huyan/Core 作为 peer。
- 每台服务器独立私钥，peer 配置最小 AllowedIPs。
- 防火墙只允许 WireGuard 接口访问管理端口。

### 9.5 选型建议

- 第一阶段优先 Tailscale：上线快、ACL 简单、审计友好。
- 对合规、完全自管或网络策略更严格时，再演进到原生 WireGuard 或 Headscale。

## 10. Huyan 接入

### 10.1 接入定位

Huyan 是业务入口与边缘节点，接入控制平面时必须优先保护外部访问稳定性。

### 10.2 接入阶段

1. **只读盘点**：采集系统版本、磁盘、端口、服务状态、证书有效期。
2. **健康检查**：建立 HTTP/TCP health check 与日志拉取能力。
3. **备份接入**：备份网关配置、证书配置、反向代理配置、部署 manifest。
4. **发布接入**：通过 `deploy-huyan.yml` 发布静态资源、网关配置或边缘服务。
5. **回滚接入**：支持按 release manifest 回滚网关配置和服务版本。

### 10.3 Huyan 权限边界

- 默认不允许控制平面修改系统级网络策略。
- Nginx/Caddy/应用网关重载属于 L3 动作，需要审批。
- 防火墙、SSH 配置、证书私钥替换属于 L5 动作，必须走 break-glass。

## 11. Core 接入

### 11.1 接入定位

Core 是核心服务与数据节点，接入控制平面时必须优先保证数据一致性和可恢复性。

### 11.2 接入阶段

1. **只读盘点**：采集服务清单、数据目录、数据库版本、备份状态。
2. **备份优先**：在任何发布能力之前先完成备份与恢复演练。
3. **健康检查**：建立核心服务、数据库、队列、磁盘水位监控。
4. **发布接入**：仅允许有前置备份和可回滚 manifest 的发布。
5. **回滚接入**：区分应用回滚、配置回滚、数据回滚；数据回滚必须人工确认。

### 11.3 Core 权限边界

- 数据库 schema migration 属于 L4，需要双确认与备份点。
- 数据删除、数据库恢复、主从切换属于 L5 或特殊流程。
- 控制平面不得默认拥有直接读取全部业务数据的权限，只应管理备份任务与健康状态。

## 12. 自动备份

### 12.1 备份对象

| 类型 | AI | Huyan | Core |
| --- | --- | --- | --- |
| 应用配置 | 是 | 是 | 是 |
| 发布包/manifest | 是 | 是 | 是 |
| 日志 | 关键日志 | 访问/错误日志 | 关键业务日志 |
| 数据 | 模型缓存/索引 | 网关配置 | 数据库/对象数据 |
| 密钥 | 只备份加密密文或元数据 | 只备份加密密文或元数据 | 只备份加密密文或元数据 |

### 12.2 备份策略

- RPO：核心配置 ≤ 24 小时；核心数据按业务重要性定义更短窗口。
- RTO：普通服务 ≤ 1 小时；核心服务需单独定义。
- 备份分为本地快照、异地备份、离线导出三层。
- 每次生产发布前自动创建发布前备份点。
- 每周至少执行一次恢复演练或校验抽样。

### 12.3 备份 Manifest

每次备份生成 manifest：

```yaml
backup_id: 2026-07-18T000000Z-core-prod-predeploy
host: core-prod
scope:
  - config
  - database
  - release_manifest
git_sha: example-sha
created_by: vafox-control
checksum: sha256:...
retention: 30d
restore_playbook: rollback.yml
```

## 13. 自动发布

### 13.1 发布流程

```text
Code Merge
  -> CI Test
  -> Build Artifact
  -> Generate Release Manifest
  -> Approval for Production
  -> Pre-deploy Backup
  -> Deploy to Target
  -> Health Check
  -> Smoke Test
  -> Mark Release Active
  -> Audit Report
```

### 13.2 Release Manifest

每个发布必须生成 manifest：

```yaml
release_id: 2026-07-18T000000Z-ai-prod-example
service: ai-vafox
host_group: ai
artifact_digest: sha256:...
git_sha: example-sha
previous_release: 2026-07-17T000000Z-ai-prod-example
backup_id: 2026-07-18T000000Z-ai-prod-predeploy
deploy_playbook: deploy-ai.yml
rollback_playbook: rollback.yml
health_checks:
  - http://127.0.0.1:8080/health
  - systemd:ai-vafox
```

### 13.3 发布策略

- AI：优先采用蓝绿或 `current` 软链接切换。
- Huyan：优先配置校验后 reload，避免直接 restart。
- Core：先备份、再部署，涉及数据结构变更时必须分离 migration 与应用发布。

## 14. 自动回滚

### 14.1 回滚触发条件

- 发布后 health check 失败。
- Smoke test 失败。
- 关键错误率超过阈值。
- 人工触发回滚。
- 控制平面检测到发布后核心依赖不可用。

### 14.2 回滚流程

```text
Rollback Request
  -> Validate Release Manifest
  -> Validate Backup Manifest
  -> Approval Check
  -> Stop or Drain Current Service
  -> Restore Previous Release/Config
  -> Restart or Reload Service
  -> Health Check
  -> Audit Report
```

### 14.3 回滚分级

| 类型 | 说明 | 审批 |
| --- | --- | --- |
| 应用回滚 | 切回上一版本代码/镜像/软链接 | 单审批或自动触发 |
| 配置回滚 | 恢复上一个配置快照 | 单审批 |
| 数据回滚 | 恢复数据库或对象数据 | 双确认 |
| 网络回滚 | 防火墙、路由、SSH 策略恢复 | break-glass |

## 15. 未来新增服务器扩展方式

### 15.1 标准接入流程

1. 在资产登记表中创建服务器记录：hostname、IP、角色、负责人、环境、数据等级。
2. 加入 Tailscale/WireGuard 控制网络。
3. 创建自动化低权限用户与专用 key。
4. 将主机加入 Ansible inventory。
5. 执行只读基线检查。
6. 安装 VAFOX Agent。
7. 配置主机级 `vafox-exec` policy。
8. 接入备份策略。
9. 接入健康检查与审计日志。
10. 按角色接入发布与回滚 Playbook。

### 15.2 角色模板

| 角色 | 模板 |
| --- | --- |
| edge | 网关、证书、边缘缓存、静态资源发布 |
| app | 应用运行、服务发布、日志采集 |
| worker | 队列消费、任务调度、批处理发布 |
| data | 数据库、备份、恢复演练、容量监控 |
| ai | 模型、推理服务、向量索引、GPU/CPU 资源监控 |
| control | Controller、Runner、Agent、审计与密钥管理 |

### 15.3 Inventory 扩展示例

```yaml
new-app-prod:
  ansible_host: 10.0.0.10
  vafox_role: app
  vafox_environment: production
  vafox_agent_enabled: true
  vafox_backup_policy: standard
  vafox_deploy_policy: app-blue-green
```

## 16. 完整实施路线图

### Phase 0：设计确认与资产盘点

目标：确认 AI 作为控制平面候选的可行性。

交付物：

- 三台服务器资产清单。
- 服务清单、端口清单、数据目录清单。
- 密钥清单与访问路径清单。
- 控制平面风险评估。

验收标准：

- 已明确 AI 业务与控制平面边界。
- 已明确哪些动作可以自动化，哪些必须 break-glass。
- 已确认不会因控制平面上线影响 AI 业务。

### Phase 1：目录、用户与权限基线设计

目标：建立 `/opt/ai-vafox` 与 `/opt/vafox-control` 的逻辑边界。

交付物：

- 目录规范。
- 用户/组权限矩阵。
- 日志路径规范。
- secrets 存储规范。

验收标准：

- AI 业务用户与控制平面用户分离。
- 控制平面不能直接覆盖 AI 业务运行目录。
- 所有敏感文件有明确属主、权限和轮换责任人。

### Phase 2：控制网络设计

目标：建立私有控制通道方案。

交付物：

- Tailscale ACL 或 WireGuard peer 设计。
- 管理端口访问矩阵。
- 公网暴露面收敛计划。

验收标准：

- AI 可通过私网身份访问 Huyan/Core 管理端口。
- Huyan/Core 不向公网开放不必要管理入口。
- 控制网络具备设备身份与访问审计。

### Phase 3：Ansible Controller MVP

目标：实现只读自动化与备份编排。

交付物：

- `production.yml` inventory。
- `site.yml` 只读检查。
- `backup.yml` 初版。
- Ansible Vault/secrets 方案。

验收标准：

- 可生成三台服务器状态报告。
- 可执行非破坏性健康检查。
- 可生成备份 manifest。

### Phase 4：VAFOX Agent MVP

目标：建立节点侧统一状态与任务执行接口。

交付物：

- Agent 心跳协议。
- Agent 任务签名规范。
- Agent 日志回传规范。
- Huyan/Core/AI 三类 Agent role 定义。

验收标准：

- 每台服务器可上报健康状态。
- Agent 拒绝未签名和越权任务。
- Agent 任务日志进入控制平面审计目录。

### Phase 5：`vafox-exec` 安全执行层

目标：替代任意 shell 执行，建立白名单任务模型。

交付物：

- Policy schema。
- sudoers 白名单原则。
- L1-L5 动作分级。
- 审批记录格式。

验收标准：

- 低风险任务可自动执行。
- 高风险任务必须审批。
- 任意命令拼接和交互式 root shell 被禁止。

### Phase 6：GitHub Actions Runner 接入

目标：建立标准 CI/CD 入口。

交付物：

- Runner 隔离目录规范。
- GitHub Environment 审批策略。
- workflow 分层设计。
- Runner secrets 与生产 secrets 隔离策略。

验收标准：

- CI 与生产部署分离。
- 生产部署必须带 Git SHA、artifact digest、审批记录。
- Runner 不能直接持有 root 权限。

### Phase 7：自动备份正式化

目标：使发布前备份与周期性备份成为强制前置条件。

交付物：

- 备份策略矩阵。
- 备份 manifest。
- 恢复演练 runbook。
- 备份保留与清理策略。

验收标准：

- Core 发布前必须存在有效备份点。
- 每个备份都可校验 checksum。
- 至少一个恢复演练通过。

### Phase 8：自动发布 MVP

目标：先低风险服务，再逐步覆盖 AI、Huyan、Core。

交付物：

- release manifest。
- AI 发布 Playbook。
- Huyan 发布 Playbook。
- Core 发布 Playbook。
- Smoke test 定义。

验收标准：

- 每次发布可追溯到 Git SHA 和 artifact digest。
- 发布失败会自动停止流程并生成审计报告。
- Huyan/Core 发布具备前置检查。

### Phase 9：自动回滚 MVP

目标：建立可验证回滚路径。

交付物：

- rollback manifest。
- 上一版本定位规则。
- 配置恢复流程。
- 数据恢复审批流程。

验收标准：

- AI 应用可快速切回上一版本。
- Huyan 网关配置可恢复到上一有效配置。
- Core 数据相关回滚必须经过双确认。

### Phase 10：新增服务器标准化扩展

目标：让 VAFOX 控制平面可以持续扩容。

交付物：

- 新服务器 onboarding checklist。
- 角色模板。
- inventory 变更规范。
- Agent 注册与退役流程。

验收标准：

- 新增服务器无需临时设计即可接入。
- 新节点默认只读接入，逐步提升权限。
- 退役节点会撤销 key、Agent token、网络访问与 inventory 记录。

## 17. 风险与缓解

| 风险 | 影响 | 缓解 |
| --- | --- | --- |
| AI 业务与控制平面资源竞争 | AI 服务性能下降 | 进程、用户、目录、资源限制隔离 |
| Runner 被滥用 | 生产权限泄露 | 不直接持有 root key，使用审批与 `vafox-exec` |
| SSH key 泄露 | 节点被控制 | 专用 key、定期轮换、forced command、私网限制 |
| 自动发布失败 | 服务不可用 | 预检查、备份、health check、自动回滚 |
| 数据回滚误操作 | 数据丢失 | 双确认、恢复演练、不可变备份 |
| 控制网络配置错误 | 节点不可管理 | 保留 break-glass 通道与变更回滚策略 |

## 18. 最小可行落地顺序

推荐按以下顺序推进：

1. 完成资产盘点与边界确认。
2. 在 AI 上逻辑划分 `/opt/ai-vafox` 与 `/opt/vafox-control`。
3. 建立控制网络方案，但先不收敛公网入口。
4. 建立 Ansible 只读 inventory 与健康检查。
5. 建立备份 manifest 与恢复演练。
6. 建立 VAFOX Agent 心跳与审计。
7. 建立 `vafox-exec` 白名单执行。
8. 接入 GitHub Actions Runner。
9. 先发布 AI 非核心服务，再接入 Huyan，最后接入 Core。
10. 完成回滚演练后，再扩大自动化权限范围。

## 19. 最终目标状态

AI 服务器作为 VAFOX Automation Control Plane 候选节点时，应达到以下状态：

- `/opt/ai-vafox` 与 `/opt/vafox-control` 完全隔离。
- Ansible Controller 可以统一编排 AI、Huyan、Core。
- GitHub Actions Runner 可以触发受控发布和回滚，但不直接持有 root 权限。
- VAFOX Agent 在三台服务器上提供健康、审计和受控执行能力。
- `vafox-exec` 成为所有高权限自动化动作的唯一入口。
- SSH key、Agent token、Runner token 均有登记、轮换和吊销流程。
- 控制流量优先通过 Tailscale/WireGuard 私网。
- Huyan 与 Core 以最小权限、分阶段方式接入。
- 自动备份、自动发布、自动回滚都有 manifest、审批、审计和演练记录。
- 新服务器可通过标准 onboarding 流程加入 VAFOX 自动化体系。
