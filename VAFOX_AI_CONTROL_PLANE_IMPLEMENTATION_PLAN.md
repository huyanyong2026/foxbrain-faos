# VAFOX AI Control Plane 实施方案

## 0. 目标与边界

### 0.1 目标

将 `ai.vafox.com`（`1.13.254.217`，下称 **AI 节点**）评估并规划为未来 **VAFOX 自动化控制中心 / Control Plane**，用于统一承载自动化编排、配置发布、部署流水线、备份调度、回滚编排与运维审计能力。

### 0.2 当前节点

| 节点 | 公网 IP | 角色定位 |
| --- | --- | --- |
| Huyan | `140.143.207.194` | 业务节点 / 被控节点 |
| AI | `1.13.254.217` | AI 业务节点；拟承载 Control Plane |
| Core | `139.199.174.36` | 核心业务节点 / 被控节点 |

### 0.3 实施边界

本方案仅输出设计与实施规划，不执行任何服务器操作，不修改远端服务器配置，不创建账号，不安装软件，不启动部署任务。

---

## 1. AI 业务与 Control Plane 隔离方案

AI 节点同时承担现有 AI 业务与未来自动化控制中心能力时，必须采用“同机逻辑隔离、权限隔离、网络隔离、数据隔离、发布隔离”的设计，避免 Control Plane 故障、权限扩大或自动化误操作影响 AI 线上业务。

### 1.1 隔离原则

1. **业务优先**：AI 业务是对外服务，Control Plane 是内部运维能力；任何资源冲突时优先保障 AI 业务。
2. **最小权限**：Control Plane 仅获得执行自动化所需的最小系统权限、SSH 权限、仓库权限与 Secret 权限。
3. **单向控制**：Control Plane 可以通过受控通道访问 Huyan、AI、Core；被控节点不得反向访问 Control Plane 的敏感目录、密钥与 Runner 工作区。
4. **密钥分域**：AI 业务密钥、Ansible 密钥、GitHub Actions 密钥、备份密钥分开存放、分开授权、分开轮换。
5. **可审计**：所有自动化入口必须有日志、提交记录、工作流记录、Ansible 执行记录与主机侧 sudo 审计记录。

### 1.2 隔离层次

| 隔离层 | AI 业务 | Control Plane | 规划说明 |
| --- | --- | --- | --- |
| 目录 | `/opt/ai-vafox` | `/opt/vafox-control` | 目录、权限、日志、备份策略分离 |
| 账号 | `ai-vafox` 或现有业务账号 | `vafox-exec` | 禁止共用业务运行账号 |
| Systemd | `ai-vafox-*` | `vafox-control-*` | 服务命名空间分离 |
| 网络 | 对公网开放业务入口 | 仅 VPN / 内网 / GitHub 出站 | Control Plane 不直接暴露公网管理入口 |
| Secret | AI 应用 `.env` / Secret Store | Ansible Vault / GitHub Secrets | 不跨域读取 |
| 日志 | `/var/log/ai-vafox` | `/var/log/vafox-control` | 分开采集与保留 |
| 资源 | CPU / Memory 业务保障 | 限额运行 | 通过 systemd slice / cgroup 限制自动化任务 |

### 1.3 推荐部署形态

AI 节点上建议采用以下部署形态：

```text
AI Node: ai.vafox.com / 1.13.254.217

/opt/ai-vafox
  └── 对外 AI 业务运行域

/opt/vafox-control
  └── VAFOX Control Plane 运行域
      ├── ansible controller
      ├── github actions runner
      ├── backup orchestrator
      ├── deploy orchestrator
      └── rollback orchestrator
```

Control Plane 服务建议默认只监听 `127.0.0.1`、Tailscale/WireGuard 私网地址或 Unix Socket；如必须提供 Web 控制台，应仅通过 VPN 访问，并追加 SSO、MFA、IP allowlist 与审计日志。

---

## 2. `/opt/ai-vafox` 与 `/opt/vafox-control` 目录规划

### 2.1 `/opt/ai-vafox`：AI 业务目录

`/opt/ai-vafox` 仅用于 AI 业务应用、模型服务、业务配置与业务日志，不存放 Control Plane 密钥或自动化工作区。

```text
/opt/ai-vafox/
├── app/                         # AI 业务应用代码或发布产物
├── releases/                    # AI 业务历史发布版本
│   ├── 20260718-001/
│   └── 20260718-002/
├── current -> releases/<version> # 当前线上版本软链
├── shared/                      # 跨版本共享资源
│   ├── config/                  # AI 业务配置；不包含控制面密钥
│   ├── data/                    # 业务运行数据
│   ├── models/                  # 模型文件或模型挂载点
│   └── uploads/                 # 用户上传或业务附件
├── logs/                        # AI 业务日志，可软链到 /var/log/ai-vafox
├── scripts/                     # 业务级脚本，仅限 AI 业务使用
└── README.md                    # 本目录用途说明
```

权限建议：

| 路径 | Owner | Group | Mode | 说明 |
| --- | --- | --- | --- | --- |
| `/opt/ai-vafox` | `ai-vafox` | `ai-vafox` | `0750` | AI 业务根目录 |
| `/opt/ai-vafox/shared/config` | `ai-vafox` | `ai-vafox` | `0750` | 业务配置 |
| `/opt/ai-vafox/shared/data` | `ai-vafox` | `ai-vafox` | `0750` | 业务数据 |
| `/opt/ai-vafox/logs` | `ai-vafox` | `adm` | `0750` | 业务日志 |

### 2.2 `/opt/vafox-control`：Control Plane 目录

`/opt/vafox-control` 用于自动化控制中心，所有内容应由 `vafox-exec` 管理，避免 root 长期持有工作目录。

```text
/opt/vafox-control/
├── ansible/
│   ├── inventories/
│   │   ├── production/
│   │   │   ├── hosts.yml
│   │   │   └── group_vars/
│   │   └── staging/
│   ├── playbooks/
│   │   ├── deploy.yml
│   │   ├── rollback.yml
│   │   ├── backup.yml
│   │   └── healthcheck.yml
│   ├── roles/
│   ├── collections/
│   ├── vault/
│   │   ├── production.vault.yml
│   │   └── staging.vault.yml
│   └── ansible.cfg
├── runner/
│   ├── actions-runner/          # GitHub Actions self-hosted runner 程序
│   ├── work/                    # Runner 工作目录
│   └── hooks/                   # pre/post job 清理与审计钩子
├── repos/
│   ├── infra/                   # IaC / Ansible 仓库只读或受控检出
│   └── app/                     # 应用仓库发布用检出目录
├── backups/
│   ├── manifests/               # 备份清单与校验和
│   ├── staging/                 # 本地临时备份缓存
│   └── restore-tests/           # 恢复演练结果
├── deploy/
│   ├── artifacts/               # 构建产物缓存
│   ├── release-manifests/       # 发布记录
│   └── locks/                   # 部署互斥锁
├── rollback/
│   ├── plans/                   # 回滚计划模板
│   └── records/                 # 回滚执行记录
├── secrets/
│   ├── README.md                # Secret 使用规范；不提交真实密钥
│   └── vault-password-file      # 如必须落盘，需 0600 并限制 owner
├── logs/
│   ├── ansible/
│   ├── runner/
│   ├── backup/
│   ├── deploy/
│   └── rollback/
└── README.md
```

权限建议：

| 路径 | Owner | Group | Mode | 说明 |
| --- | --- | --- | --- | --- |
| `/opt/vafox-control` | `vafox-exec` | `vafox-exec` | `0750` | 控制面根目录 |
| `/opt/vafox-control/secrets` | `vafox-exec` | `vafox-exec` | `0700` | Secret 存储区 |
| `/opt/vafox-control/ansible/vault` | `vafox-exec` | `vafox-exec` | `0700` | Ansible Vault 文件 |
| `/opt/vafox-control/runner/work` | `vafox-exec` | `vafox-exec` | `0750` | Runner 工作区 |
| `/opt/vafox-control/logs` | `vafox-exec` | `adm` | `0750` | 控制面日志 |

---

## 3. Ansible Controller 设计

### 3.1 定位

AI 节点作为 Ansible Controller，不在 Huyan/Core 上安装中心化 agent。Huyan、AI、Core 均作为 Ansible managed nodes，通过 SSH 受控执行任务。

### 3.2 Inventory 设计

建议按环境、角色与节点分组：

```yaml
all:
  children:
    vafox_production:
      children:
        huyan:
          hosts:
            huyan-01:
              ansible_host: 140.143.207.194
              vafox_role: huyan
        ai:
          hosts:
            ai-01:
              ansible_host: 1.13.254.217
              vafox_role: ai_control_plane
              ansible_connection: local
        core:
          hosts:
            core-01:
              ansible_host: 139.199.174.36
              vafox_role: core
```

AI 节点本机任务建议优先使用 `ansible_connection: local`，减少本机 SSH 依赖；对 Huyan/Core 使用 SSH 私网地址优先、公网地址兜底。

### 3.3 Playbook 分类

| Playbook | 用途 | 执行策略 |
| --- | --- | --- |
| `healthcheck.yml` | 发布前后健康检查 | 所有部署与回滚必跑 |
| `backup.yml` | 应用、配置、数据库备份 | 部署前自动触发 |
| `deploy.yml` | 自动部署 | 分批、带锁、可中断 |
| `rollback.yml` | 自动回滚 | 只允许回滚到已验证版本 |
| `rotate-secrets.yml` | Secret 轮换 | 手动审批触发 |
| `bootstrap-managed-node.yml` | 节点接入初始化 | 仅一次性受控执行 |

### 3.4 执行约束

1. 启用 `--check` 与 `--diff` 作为预检阶段。
2. 生产部署使用 `serial: 1` 或按业务拓扑分批。
3. 所有危险任务必须有 tag，例如 `dangerous`, `restart`, `migration`，默认不执行危险 tag。
4. 使用 `become: true` 时必须限定命令白名单，不允许无限制 root shell。
5. 输出执行记录到 `/opt/vafox-control/logs/ansible/`，并将关键摘要写入 GitHub Actions job summary。

---

## 4. GitHub Actions Runner 设计

### 4.1 Runner 定位

AI 节点部署 self-hosted GitHub Actions Runner，用于从 GitHub 接收自动化任务，再调用本地 Ansible Controller 执行部署、备份、回滚与巡检。

### 4.2 Runner 类型

推荐使用：

- **Repository-scoped runner**：优先用于单一 VAFOX 基础设施仓库，权限边界清晰。
- **Runner group**：如使用 GitHub Organization，可创建 `vafox-production-control` runner group，仅允许指定仓库调用。
- **Ephemeral runner 优先**：条件允许时使用一次性 runner，降低工作区残留与凭据泄露风险。

### 4.3 Label 规划

```text
self-hosted
linux
x64
vafox-control
production
ai-node
```

工作流必须显式指定 label，避免其他仓库或非生产任务误用生产 Runner：

```yaml
runs-on: [self-hosted, linux, x64, vafox-control, production]
```

### 4.4 Workflow 分类

| Workflow | 触发方式 | 说明 |
| --- | --- | --- |
| `healthcheck.yml` | `workflow_dispatch`, `schedule` | 巡检 Huyan/AI/Core |
| `backup.yml` | `schedule`, `workflow_dispatch` | 自动备份与备份校验 |
| `deploy.yml` | tag / release / manual approval | 自动部署 |
| `rollback.yml` | `workflow_dispatch` + approval | 指定版本回滚 |
| `drift-detect.yml` | `schedule` | 配置漂移检测 |

### 4.5 Runner 安全策略

1. Runner 进程以 `vafox-exec` 运行，不以 root 运行。
2. Runner 工作区每个 job 后清理：源码、临时文件、token、构建产物缓存。
3. 限制可使用生产 Runner 的仓库与分支。
4. 生产部署需 GitHub Environment protection rules：审批人、分支规则、等待时间。
5. GitHub Secrets 最小化；长期密钥优先放入 Ansible Vault 或云 Secret Manager。
6. 禁止在 PR from fork 上使用生产 self-hosted runner。

---

## 5. `vafox-exec` 账号权限

### 5.1 账号定位

`vafox-exec` 是 Control Plane 专用执行账号，负责运行 GitHub Actions Runner、Ansible Controller、本地备份编排、部署编排与回滚编排。

### 5.2 基础权限

| 权限项 | 建议 |
| --- | --- |
| 登录方式 | 仅 SSH key；禁止密码登录 |
| Shell | `/bin/bash` 或受限 shell；禁止共享 root shell |
| Home | `/home/vafox-exec` |
| 主目录权限 | `0700` |
| SSH key | 每个来源独立 key；定期轮换 |
| sudo | 命令白名单；禁止 `NOPASSWD: ALL` |

### 5.3 sudo 白名单设计

`vafox-exec` 不应拥有完整 root 权限。建议仅允许以下类别命令：

| 类别 | 示例能力 | 说明 |
| --- | --- | --- |
| 服务控制 | restart/status 指定 `ai-vafox-*`, `vafox-*` 服务 | 不允许任意 systemd unit |
| 发布切换 | 更新指定目录软链 | 限定 `/opt/ai-vafox/current` 等路径 |
| 配置校验 | nginx/systemd/app config test | 仅校验命令 |
| 日志读取 | journalctl 指定 unit | 只读 |
| 备份执行 | 指定备份脚本 | 脚本路径固定、owner root、不可被 `vafox-exec` 修改 |

禁止项：

- 禁止 `sudo su`、`sudo bash`、`sudo sh`。
- 禁止 `sudo vim`、`sudo less` 等可逃逸交互命令。
- 禁止通配符过宽的 `systemctl *`。
- 禁止 `NOPASSWD: ALL`。
- 禁止 `vafox-exec` 修改自己可 sudo 执行的 root 脚本。

### 5.4 SSH 访问模型

- AI Controller 持有到 Huyan/Core 的 deploy key。
- Huyan/Core 的 `authorized_keys` 对 `vafox-exec` key 加限制：来源地址、command wrapper、no-agent-forwarding、no-X11-forwarding、no-port-forwarding。
- 如采用 Tailscale/WireGuard，优先限制 SSH 只接受 VPN 网段访问。

---

## 6. Tailscale / WireGuard 网络

### 6.1 网络目标

将 Huyan、AI、Core 放入私有运维网络，减少公网 SSH 暴露面，使 Control Plane 通过稳定私网地址管理节点。

### 6.2 Tailscale 方案

Tailscale 适合快速接入、多节点 ACL 管理与低运维成本场景。

建议规划：

| 节点 | Tailscale 名称 | 角色 |
| --- | --- | --- |
| Huyan | `huyan-01` | managed node |
| AI | `ai-control-01` | controller + managed node |
| Core | `core-01` | managed node |

ACL 规划：

1. `ai-control-01` 可访问 `huyan-01:22`、`core-01:22` 与自身管理端口。
2. Huyan/Core 不允许访问 AI Control Plane 的 Runner 工作区、Ansible API 或控制端口。
3. 管理员仅可从受信设备访问 AI Control Plane 管理端口。
4. 所有节点开启 MagicDNS，inventory 优先使用 `huyan-01`, `ai-control-01`, `core-01` 私网名称。

### 6.3 WireGuard 方案

WireGuard 适合希望完全自管、配置简单稳定、无第三方控制面的场景。

建议规划：

```text
VAFOX Ops VPN: 10.88.0.0/24

AI Control: 10.88.0.1
Huyan:      10.88.0.11
Core:       10.88.0.21
Admin:      10.88.0.100-10.88.0.199
```

访问规则：

- AI Control `10.88.0.1` -> Huyan/Core `22/tcp`：允许。
- Admin 网段 -> AI Control 管理端口：允许。
- Huyan/Core -> AI Control 管理端口：默认拒绝。
- 公网 SSH：保留应急入口但限制 IP、密钥与告警；成熟后可关闭或迁移到堡垒入口。

### 6.4 推荐选择

首期建议使用 **Tailscale** 快速建立私网控制通道；当安全与合规要求提高后，可评估迁移或并行建设 **自管 WireGuard**。无论采用哪种方案，Ansible inventory 都应抽象主机名，避免 playbook 直接绑定公网 IP。

---

## 7. Huyan / AI / Core 接入方式

### 7.1 接入分层

| 层级 | Huyan | AI | Core |
| --- | --- | --- | --- |
| 网络层 | Tailscale/WireGuard 私网 SSH | 本机 local + 私网 SSH 兜底 | Tailscale/WireGuard 私网 SSH |
| 账号层 | `vafox-exec` | `vafox-exec` | `vafox-exec` |
| 权限层 | sudo 白名单 | sudo 白名单 + 本机控制面目录权限 | sudo 白名单 |
| 配置层 | Ansible inventory 管理 | inventory 中标记 controller | Ansible inventory 管理 |
| 审计层 | auth.log / sudo log / Ansible log | runner log / ansible log / sudo log | auth.log / sudo log / Ansible log |

### 7.2 Huyan 接入

- 节点标识：`huyan-01`。
- 公网 IP：`140.143.207.194`。
- 私网优先：`huyan-01` Tailscale MagicDNS 或 `10.88.0.11` WireGuard IP。
- 管理方式：AI Controller 通过 Ansible SSH 执行 healthcheck、backup、deploy、rollback。
- 权限范围：仅允许操作 Huyan 相关服务、目录与日志。

### 7.3 AI 接入

- 节点标识：`ai-control-01`。
- 公网 IP：`1.13.254.217`。
- 角色：AI 业务节点 + Control Plane。
- 管理方式：本机任务优先使用 Ansible local connection；需要模拟远端路径时可通过私网 SSH 连接自身。
- 特别要求：AI 业务与 Control Plane 的账号、目录、日志、Secret、systemd unit 必须分离。

### 7.4 Core 接入

- 节点标识：`core-01`。
- 公网 IP：`139.199.174.36`。
- 私网优先：`core-01` Tailscale MagicDNS 或 `10.88.0.21` WireGuard IP。
- 管理方式：AI Controller 通过 Ansible SSH 执行核心服务部署、配置校验、备份与回滚。
- 权限范围：Core 权限应比 AI Control 更保守，仅开放部署与运维必需能力。

---

## 8. 自动备份

### 8.1 备份目标

自动备份应覆盖配置、数据、数据库、部署产物清单、Ansible inventory、Vault 加密文件与 Control Plane 执行记录，确保任一节点故障后可以恢复服务与自动化能力。

### 8.2 备份分类

| 类型 | 内容 | 频率 | 保留策略 |
| --- | --- | --- | --- |
| 配置备份 | `/etc` 中白名单配置、应用 config | 每日 + 部署前 | 30 天 |
| 应用数据 | `/opt/ai-vafox/shared/data` 等 | 每日 / 按业务 RPO | 7 日 + 4 周 + 6 月 |
| 数据库 | dump / snapshot | 每日 + 部署前 | 7 日 + 4 周 + 6 月 |
| 发布清单 | release manifest、版本、commit SHA | 每次部署 | 长期保留 |
| Control Plane | inventory、playbook、runner 配置、日志摘要 | 每日 | 90 天 |
| Secret | Ansible Vault 加密文件 | 每次变更 | 长期保留；不得明文备份 |

### 8.3 备份流程

```text
GitHub Actions schedule/manual
  -> backup workflow
  -> Ansible backup.yml
  -> 节点本地生成备份包
  -> 计算 sha256 checksum
  -> 上传远端对象存储或异地备份节点
  -> 写入 backup manifest
  -> 执行抽样 restore 校验
  -> 输出备份报告
```

### 8.4 备份安全

1. 备份包传输与存储必须加密。
2. Secret 只备份加密形态，不产生明文 Secret 包。
3. 备份仓库或对象存储启用版本控制、生命周期策略与删除保护。
4. 至少每月进行一次恢复演练，记录恢复耗时、缺失项与修复项。
5. 部署前备份必须与部署 release manifest 关联，作为回滚依据。

---

## 9. 自动部署

### 9.1 部署目标

自动部署应实现从 GitHub release/tag/manual dispatch 到 Huyan/AI/Core 的可审计、可暂停、可验证、可回滚发布链路。

### 9.2 部署流程

```text
开发合并到 main
  -> CI 构建与测试
  -> 生成 release artifact
  -> 创建 tag/release
  -> GitHub Environment 审批
  -> self-hosted runner 接收任务
  -> Ansible deploy precheck
  -> 自动备份
  -> 分节点部署
  -> 健康检查
  -> 流量/服务切换
  -> 写入 release manifest
  -> 发送部署报告
```

### 9.3 发布目录模型

被控节点建议使用不可变 release 目录 + `current` 软链切换：

```text
/opt/<service>/
├── releases/
│   ├── 20260718-001-<git_sha>/
│   └── 20260718-002-<git_sha>/
├── current -> releases/20260718-002-<git_sha>
└── shared/
    ├── config/
    ├── data/
    └── logs/
```

### 9.4 部署策略

| 场景 | 策略 |
| --- | --- |
| 单实例服务 | 先备份，再停机窗口内原子软链切换 |
| 多实例服务 | rolling deploy，`serial: 1`，逐个健康检查 |
| 数据库迁移 | expand/contract 模式，先兼容迁移，后清理 |
| Nginx 配置 | `nginx -t` 通过后 reload，不直接 restart |
| systemd 服务 | 先 `daemon-reload`，再 restart 指定白名单 unit |

### 9.5 部署门禁

1. CI 测试必须通过。
2. release artifact 必须带 checksum。
3. 生产 Environment 必须人工审批。
4. precheck 必须通过：磁盘、内存、端口、依赖、备份可用性。
5. 部署期间加锁，避免并发部署。
6. 部署后 healthcheck 必须通过，否则自动进入回滚判断。

---

## 10. 自动回滚

### 10.1 回滚目标

当部署失败、健康检查失败、核心指标异常或人工触发紧急恢复时，Control Plane 能够将目标节点恢复到最近一个已验证版本，并保留完整回滚记录。

### 10.2 回滚触发

| 触发方式 | 场景 |
| --- | --- |
| 自动触发 | 部署后 healthcheck 失败 |
| 人工触发 | GitHub `workflow_dispatch` 指定版本 |
| 告警触发 | 未来可由监控系统调用受控 webhook |
| 演练触发 | 定期灾备演练 |

### 10.3 回滚流程

```text
检测失败或人工触发
  -> 获取当前 release manifest
  -> 选择上一稳定版本
  -> 校验目标版本存在与 checksum
  -> 如需要，恢复配置或数据快照
  -> 切换 current 软链
  -> restart/reload 指定服务
  -> 执行 healthcheck
  -> 写入 rollback record
  -> 发送回滚报告
```

### 10.4 回滚边界

1. 代码回滚优先通过 release 软链切换完成。
2. 配置回滚必须使用部署前配置备份。
3. 数据库回滚必须谨慎：优先采用向前修复；只有在明确数据兼容性与 RPO 可接受时恢复快照。
4. 不允许回滚到未通过健康检查或 checksum 不匹配的版本。
5. 回滚也必须加锁，避免与部署任务并发。

### 10.5 回滚记录

每次回滚记录至少包含：

- 回滚时间。
- 触发人或触发系统。
- 目标节点。
- 原版本与目标版本。
- 原因。
- 执行 playbook run id。
- 健康检查结果。
- 是否涉及数据恢复。
- 后续修复事项。

---

## 11. 建议实施阶段

### Phase 0：评估与设计确认

- 确认 AI 节点资源是否足以承载 Runner、Ansible、备份临时缓存与现有 AI 业务。
- 确认 GitHub 仓库、Environment、Secrets、审批人模型。
- 确认 Tailscale 或 WireGuard 技术选型。
- 确认 `vafox-exec` sudo 白名单范围。

### Phase 1：控制面基础能力

- 建立 `/opt/vafox-control` 目录结构。
- 准备 Ansible inventory、ansible.cfg、基础 healthcheck playbook。
- 建立 GitHub Actions Runner 规划与 label。
- 接入 Huyan/AI/Core 的只读巡检能力。

### Phase 2：备份与审计

- 实施自动备份 playbook。
- 增加 backup manifest、checksum、备份报告。
- 增加日志归档与恢复演练流程。

### Phase 3：自动部署

- 建立 release artifact 与 release manifest 标准。
- 实施部署锁、precheck、部署前备份、部署后 healthcheck。
- 对低风险服务先行试点。

### Phase 4：自动回滚

- 实施 rollback playbook。
- 建立人工触发与自动触发策略。
- 完成回滚演练与记录模板。

### Phase 5：安全加固

- 收敛公网 SSH。
- 强化 VPN ACL。
- 定期轮换 SSH key、Ansible Vault 密钥、GitHub token。
- 引入配置漂移检测与基线审计。

---

## 12. 风险与控制措施

| 风险 | 影响 | 控制措施 |
| --- | --- | --- |
| AI 业务与控制面同机资源竞争 | AI 服务性能下降 | systemd/cgroup 限额、错峰任务、资源监控 |
| Runner 被滥用 | 生产权限泄露 | runner group、label、Environment 审批、禁用 fork PR |
| Ansible 误操作 | 多节点故障 | check/diff、serial、tag、limit、审批、部署锁 |
| Secret 泄露 | 全局控制权风险 | Vault、最小权限、定期轮换、日志脱敏 |
| 备份不可恢复 | 灾难恢复失败 | checksum、restore test、异地备份、恢复演练 |
| 数据库回滚破坏数据 | 数据丢失 | expand/contract、向前修复优先、RPO/RTO 审批 |
| 公网 SSH 暴露 | 入侵风险 | VPN 优先、IP allowlist、fail2ban、MFA/堡垒机 |

---

## 13. 最终推荐架构

```text
                  GitHub
        Actions / Release / Approval
                    |
                    v
        ai.vafox.com / 1.13.254.217
        AI Node + VAFOX Control Plane
        ├── /opt/ai-vafox
        │   └── AI business runtime
        └── /opt/vafox-control
            ├── GitHub Actions Runner
            ├── Ansible Controller
            ├── Backup Orchestrator
            ├── Deploy Orchestrator
            └── Rollback Orchestrator
                    |
                    | Tailscale / WireGuard private SSH
                    v
      +-------------+--------------+
      |                            |
 Huyan / 140.143.207.194     Core / 139.199.174.36
 managed node                managed node
```

最终建议：AI 节点可以作为 VAFOX 未来自动化控制中心，但必须坚持 Control Plane 与 AI 业务的强逻辑隔离；首期以 Ansible Controller + GitHub Actions self-hosted Runner + Tailscale 私网为最小可行控制面，先实现只读巡检与自动备份，再逐步开放自动部署和自动回滚能力。
