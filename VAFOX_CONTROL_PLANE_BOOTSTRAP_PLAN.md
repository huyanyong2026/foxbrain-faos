# VAFOX Control Plane Bootstrap Plan

## 0. 目标与边界

本计划用于将 `ai.vafox.com`（`1.13.254.217`，以下简称 **AI 节点**）逐步建设为 **VAFOX Automation Control Plane**，最终形成：

```text
Codex → VAFOX Control Plane → Huyan / AI / Core 自动化管理
```

当前纳管节点：

| 节点 | IP | 角色定位 |
| --- | --- | --- |
| Huyan | `140.143.207.194` | 业务 / 运行节点 |
| AI | `1.13.254.217` | Control Plane / 自动化中枢 |
| Core | `139.199.174.36` | 核心服务 / 基础能力节点 |

### 明确边界

- **只设计，不执行**：本文档不包含任何立即执行的变更动作。
- 所有命令均为未来实施阶段的参考命令，执行前必须经过变更审批、窗口确认与备份确认。
- Bootstrap 阶段以“最小权限、可回滚、可审计”为核心原则。

## 1. Bootstrap 阶段划分

### Phase 0：现状确认与冻结窗口

目标：在不修改服务器状态的前提下确认基础信息。

设计事项：

1. 确认三台服务器的公网 IP、系统版本、SSH 端口、防火墙策略、云厂商安全组。
2. 确认 `ai.vafox.com` DNS A 记录指向 `1.13.254.217`。
3. 建立变更窗口、回滚负责人、紧急联系人。
4. 冻结自动化接入前的基线状态，包括：
   - `/etc/passwd`、`/etc/group`、`/etc/sudoers`、`/etc/ssh/sshd_config`。
   - 防火墙规则与云安全组规则。
   - 当前运行服务清单。

交付物：

- 节点清单与访问矩阵。
- 变更窗口记录。
- 初始基线快照清单。

### Phase 1：AI 节点 Control Plane 基础目录与账号

目标：在 AI 节点建立自动化控制平面的文件系统与专用执行身份。

设计事项：

1. 初始化 `/opt/vafox-control` 目录结构。
2. 建立 `vafox-exec` 专用账号。
3. 配置最小 sudo 权限。
4. 准备 SSH key 管理目录。
5. 建立审计日志目录与权限边界。

交付物：

- `/opt/vafox-control` 目录设计。
- `vafox-exec` 用户权限模型。
- sudoers 白名单草案。

### Phase 2：SSH Key 接入与节点信任链

目标：建立 AI 节点到 Huyan、AI、Core 的受控 SSH 自动化通道。

设计事项：

1. 生成或导入 Control Plane 专用 SSH key。
2. 将公钥接入三台服务器的目标执行账号。
3. 禁止使用个人 SSH key 作为自动化 key。
4. 配置 `known_hosts` 固定主机指纹，避免首次连接交互与中间人风险。
5. 按节点、环境、用途区分 key 的命名与生命周期。

交付物：

- SSH key 命名规范。
- 主机指纹登记表。
- 节点接入状态矩阵。

### Phase 3：Tailscale / WireGuard 私有网络接入

目标：将自动化管理流量逐步迁移到私有网络，减少公网 SSH 暴露。

设计事项：

1. 优先评估 Tailscale，备选 WireGuard。
2. 为 Control Plane 与三台服务器建立私网地址。
3. 通过 ACL 限制仅 AI 节点可管理 Huyan / AI / Core 的指定端口。
4. 逐步将 Ansible inventory 从公网 IP 切换到私网 IP。
5. 公网 SSH 保留为应急通道，但限制来源 IP 与登录账号。

交付物：

- 私网拓扑图。
- Tailscale ACL 或 WireGuard peer 配置草案。
- 公网到私网切换计划。

### Phase 4：Ansible 初始化

目标：在 AI 节点建立标准化、可审计、可重复执行的自动化基础。

设计事项：

1. 在 `/opt/vafox-control/ansible` 初始化 inventory、playbooks、roles、group_vars。
2. 按节点角色分组：`control_plane`、`huyan`、`core`、`all_managed`。
3. 所有 playbook 默认支持 `--check` dry-run。
4. 使用 Ansible Vault 或外部 secret manager 管理敏感信息。
5. 将首次任务限制在只读审计与健康检查。

交付物：

- Ansible 目录结构。
- Inventory 设计。
- 首批只读 playbook 清单。

### Phase 5：GitHub Actions Runner 接入

目标：允许 GitHub Actions 触发受控自动化，但不直接暴露 root 权限。

设计事项：

1. Runner 部署在 AI 节点，并以非 root 用户运行。
2. Runner 不直接持有高权限 secret，只能调用受控脚本或 Ansible playbook。
3. GitHub Environments 设置人工审批门禁。
4. 区分只读 workflow、变更 workflow、紧急回滚 workflow。
5. 通过 branch protection 和 required reviewers 限制自动化入口。

交付物：

- Runner 权限模型。
- Workflow 触发策略。
- GitHub Environments 审批矩阵。

### Phase 6：第一批自动化任务上线

目标：以低风险、可观测任务验证 Control Plane 链路。

设计事项：

1. 优先上线只读任务。
2. 其次上线无状态或低风险修复任务。
3. 所有任务必须具备日志、dry-run、超时、失败告警。
4. 变更类任务必须具备回滚 playbook 或手动回滚步骤。

交付物：

- 第一批自动化任务列表。
- 任务风险等级。
- 验收报告模板。

## 2. `/opt/vafox-control` 目录初始化

建议目录结构：

```text
/opt/vafox-control/
├── README.md
├── bin/
│   ├── vafox-run
│   └── vafox-audit
├── ansible/
│   ├── ansible.cfg
│   ├── inventories/
│   │   ├── production.ini
│   │   └── production.private.ini
│   ├── playbooks/
│   │   ├── audit.yml
│   │   ├── healthcheck.yml
│   │   └── bootstrap-verify.yml
│   ├── roles/
│   ├── group_vars/
│   └── host_vars/
├── runners/
│   └── github-actions/
├── ssh/
│   ├── keys/
│   ├── known_hosts
│   └── config
├── secrets/
│   └── README.md
├── logs/
│   ├── ansible/
│   ├── runner/
│   └── audit/
├── backups/
│   ├── pre-bootstrap/
│   └── rollback/
└── docs/
    ├── access-matrix.md
    ├── rollback.md
    └── runbooks.md
```

权限设计：

| 路径 | Owner | Mode | 说明 |
| --- | --- | --- | --- |
| `/opt/vafox-control` | `root:vafox-control` | `0750` | Control Plane 根目录 |
| `/opt/vafox-control/bin` | `root:vafox-control` | `0750` | 受控入口脚本 |
| `/opt/vafox-control/ansible` | `vafox-exec:vafox-control` | `0750` | Ansible 工作区 |
| `/opt/vafox-control/ssh/keys` | `vafox-exec:vafox-control` | `0700` | 私钥目录 |
| `/opt/vafox-control/secrets` | `root:vafox-control` | `0750` | Secret 元数据，不存明文 |
| `/opt/vafox-control/logs` | `vafox-exec:vafox-control` | `0750` | 执行日志 |
| `/opt/vafox-control/backups` | `root:vafox-control` | `0750` | 备份与回滚材料 |

未来参考命令（设计，不执行）：

```bash
sudo groupadd --system vafox-control
sudo mkdir -p /opt/vafox-control/{bin,ansible,runners/github-actions,ssh/keys,secrets,logs/{ansible,runner,audit},backups/{pre-bootstrap,rollback},docs}
sudo chown -R root:vafox-control /opt/vafox-control
sudo chmod 0750 /opt/vafox-control
```

## 3. `vafox-exec` 账号建立

账号定位：

- `vafox-exec` 是自动化执行账号，不是个人登录账号。
- 不允许使用 root 作为默认自动化入口。
- 不允许共享个人账号执行自动化。

建议设计：

| 项 | 设计 |
| --- | --- |
| 用户名 | `vafox-exec` |
| 主组 | `vafox-control` |
| Shell | `/bin/bash` 或受限 shell，按任务成熟度决定 |
| Home | `/home/vafox-exec` |
| 密码登录 | 禁用 |
| SSH 登录 | 仅 key 登录 |
| sudo | 最小命令白名单 |

未来参考命令（设计，不执行）：

```bash
sudo useradd --system --create-home --home-dir /home/vafox-exec --shell /bin/bash --gid vafox-control vafox-exec
sudo passwd -l vafox-exec
sudo install -d -m 0700 -o vafox-exec -g vafox-control /home/vafox-exec/.ssh
```

sudoers 草案：

```text
# /etc/sudoers.d/vafox-exec
Defaults:vafox-exec !requiretty
Defaults:vafox-exec secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

vafox-exec ALL=(root) NOPASSWD: /usr/bin/systemctl status *, /usr/bin/journalctl *, /usr/bin/apt-get update, /usr/bin/yum check-update
```

原则：

1. 初期仅开放只读或低风险命令。
2. 每新增一个 sudo 权限，必须对应一个自动化任务与回滚方案。
3. 禁止配置 `vafox-exec ALL=(ALL) NOPASSWD:ALL`。

## 4. SSH Key 接入

### Key 类型与命名

建议使用 Ed25519：

```text
/opt/vafox-control/ssh/keys/vafox-control-prod-ed25519
/opt/vafox-control/ssh/keys/vafox-control-prod-ed25519.pub
```

命名规则：

```text
vafox-control-<environment>-<algorithm>
```

### SSH config 草案

```text
Host huyan-prod
  HostName 140.143.207.194
  User vafox-exec
  IdentityFile /opt/vafox-control/ssh/keys/vafox-control-prod-ed25519
  UserKnownHostsFile /opt/vafox-control/ssh/known_hosts
  IdentitiesOnly yes
  PasswordAuthentication no

Host ai-prod
  HostName 1.13.254.217
  User vafox-exec
  IdentityFile /opt/vafox-control/ssh/keys/vafox-control-prod-ed25519
  UserKnownHostsFile /opt/vafox-control/ssh/known_hosts
  IdentitiesOnly yes
  PasswordAuthentication no

Host core-prod
  HostName 139.199.174.36
  User vafox-exec
  IdentityFile /opt/vafox-control/ssh/keys/vafox-control-prod-ed25519
  UserKnownHostsFile /opt/vafox-control/ssh/known_hosts
  IdentitiesOnly yes
  PasswordAuthentication no
```

### 接入流程设计

1. 在 AI 节点生成或导入 Control Plane 专用 key。
2. 离线登记 public key 指纹。
3. 将 public key 加入三台服务器 `vafox-exec` 的 `authorized_keys`。
4. 记录每台服务器的 host key 指纹。
5. 进行只读 SSH 连通性验证。
6. 将公网 HostName 逐步替换为 Tailscale / WireGuard 私网地址。

## 5. Tailscale / WireGuard 接入

### 推荐路线

优先采用 Tailscale，原因：

- ACL 管理更直观。
- 节点加入与退网简单。
- 易于审计设备与 key。
- 适合小规模多节点自动化控制平面。

WireGuard 作为备选方案，适用于希望完全自管控制面与密钥分发的场景。

### Tailscale 设计

| 节点 | Tailnet 名称建议 | 角色 |
| --- | --- | --- |
| AI | `ai-control-plane` | 自动化控制入口 |
| Huyan | `huyan-prod` | 被管理节点 |
| Core | `core-prod` | 被管理节点 |

ACL 草案：

```json
{
  "ACLs": [
    {
      "Action": "accept",
      "Users": ["group:vafox-automation"],
      "Ports": ["huyan-prod:22", "core-prod:22", "ai-control-plane:22"]
    }
  ]
}
```

### WireGuard 设计

如采用 WireGuard：

- AI 节点作为 hub。
- Huyan 与 Core 作为 peer。
- 仅允许 VPN 网段访问 SSH 管理端口。
- peer key 轮换纳入季度安全流程。

## 6. Ansible 初始化

### 目录与配置

`/opt/vafox-control/ansible/ansible.cfg` 草案：

```ini
[defaults]
inventory = inventories/production.ini
remote_user = vafox-exec
private_key_file = /opt/vafox-control/ssh/keys/vafox-control-prod-ed25519
host_key_checking = True
retry_files_enabled = False
stdout_callback = yaml
log_path = /opt/vafox-control/logs/ansible/ansible.log

[ssh_connection]
ssh_args = -F /opt/vafox-control/ssh/config
pipelining = True
```

### Inventory 草案

```ini
[control_plane]
ai-prod ansible_host=1.13.254.217

[huyan]
huyan-prod ansible_host=140.143.207.194

[core]
core-prod ansible_host=139.199.174.36

[all_managed:children]
control_plane
huyan
core
```

### 首批 Playbook

| Playbook | 类型 | 目的 | 风险 |
| --- | --- | --- | --- |
| `audit.yml` | 只读 | 收集系统版本、用户、端口、服务 | 低 |
| `healthcheck.yml` | 只读 | 检查磁盘、内存、CPU、网络 | 低 |
| `bootstrap-verify.yml` | 只读 | 验证账号、sudo、SSH、目录权限 | 低 |
| `package-cache-check.yml` | 低变更 | 检查包索引，不升级 | 中低 |

执行原则：

```bash
ansible-playbook playbooks/audit.yml --check --diff
ansible-playbook playbooks/healthcheck.yml --check
```

## 7. GitHub Actions Runner

### Runner 部署原则

1. Runner 运行在 AI 节点。
2. Runner 用户与 `vafox-exec` 分离，建议为 `github-runner`。
3. Runner 只能通过受控 wrapper 调用 Ansible，不直接写入系统关键路径。
4. Runner 只接受受保护分支或手动审批环境触发。
5. Runner 日志写入 `/opt/vafox-control/logs/runner`。

### 推荐权限链路

```text
GitHub Workflow
  → github-runner 用户
  → /opt/vafox-control/bin/vafox-run
  → vafox-exec
  → Ansible playbook
  → Managed Nodes
```

### Workflow 分类

| Workflow | 触发方式 | 权限 | 审批 |
| --- | --- | --- | --- |
| `audit.yml` | 手动 / 定时 | 只读 | 不需要或轻审批 |
| `healthcheck.yml` | 手动 / 定时 | 只读 | 不需要或轻审批 |
| `maintenance.yml` | 手动 | 变更 | 需要审批 |
| `rollback.yml` | 手动 | 回滚 | 需要审批 + 双人确认 |

## 8. 第一批自动化任务

建议第一批任务按低风险优先排序：

| 优先级 | 任务 | 节点 | 类型 | 验收方式 |
| --- | --- | --- | --- | --- |
| P0 | SSH 连通性检查 | Huyan / AI / Core | 只读 | 三台节点均可连通 |
| P0 | 系统健康检查 | Huyan / AI / Core | 只读 | 输出 CPU、内存、磁盘、负载 |
| P0 | 服务清单采集 | Huyan / AI / Core | 只读 | 生成 systemd 服务清单 |
| P0 | 端口监听采集 | Huyan / AI / Core | 只读 | 生成监听端口报告 |
| P1 | 安全基线审计 | Huyan / AI / Core | 只读 | 检查 root 登录、密码登录、sudoers |
| P1 | 日志采集 | Huyan / AI / Core | 只读 | 收集最近错误日志摘要 |
| P1 | 包更新检查 | Huyan / AI / Core | 低变更 | 仅检查，不升级 |
| P2 | 指定服务重启 | 指定节点 | 变更 | 需审批与回滚 |
| P2 | 配置文件分发 | 指定节点 | 变更 | 需 diff、备份、回滚 |

## 9. 权限安全

### 核心原则

1. **最小权限**：每个账号、key、workflow 仅拥有完成任务所需权限。
2. **职责分离**：个人登录、Runner、自动化执行账号分离。
3. **默认只读**：Bootstrap 初期默认只读，变更类任务后置。
4. **强审计**：所有自动化执行必须记录调用人、commit、workflow run、playbook、目标节点、结果。
5. **可回滚**：每项变更必须有回滚路径。

### 安全控制项

| 控制项 | 设计 |
| --- | --- |
| SSH | 禁止密码登录，固定 host key，限制来源 |
| sudo | 白名单，不允许全量 NOPASSWD |
| Secret | 不提交 Git，不写明文日志 |
| Runner | 非 root，受保护分支，Environment 审批 |
| Ansible | Vault 管理敏感变量，默认 check mode |
| 网络 | 优先私网管理，公网仅应急 |
| 日志 | 本地保留 + 可选远程归档 |
| Key 轮换 | 建议季度轮换，离职或泄露立即轮换 |

### 禁止项

- 禁止将 root 私钥放入 GitHub Secrets。
- 禁止在 Git 仓库提交私钥、token、服务器密码。
- 禁止自动化账号拥有无限制 root 权限。
- 禁止跳过 host key checking。
- 禁止在未验证备份的情况下执行破坏性变更。

## 10. 回滚方案

### 回滚分层

| 层级 | 回滚对象 | 回滚方式 |
| --- | --- | --- |
| L1 | SSH key | 从 `authorized_keys` 移除新 key，恢复旧 key |
| L2 | 用户账号 | 锁定或删除 `vafox-exec`，恢复 sudoers |
| L3 | sudoers | 删除 `/etc/sudoers.d/vafox-exec`，执行语法校验 |
| L4 | Ansible | 回退 Git commit 或禁用 playbook |
| L5 | Runner | 停止 runner service，移除 GitHub runner registration |
| L6 | 私网 | 禁用 Tailscale / WireGuard peer，恢复公网应急通道 |
| L7 | 配置变更 | 使用 `/opt/vafox-control/backups/rollback` 中的备份恢复 |

### 回滚触发条件

任一条件满足即进入回滚评估：

1. 自动化导致任一节点 SSH 不可达。
2. 自动化导致关键服务不可用。
3. sudoers 语法错误或权限扩大超出审批范围。
4. Runner 被异常调用或疑似 secret 泄露。
5. Tailscale / WireGuard 接入导致网络路径异常。

### 回滚演练要求

- Bootstrap 完成前至少演练一次 SSH key 回滚。
- GitHub Actions Runner 上线前至少演练一次禁用 runner。
- 首个变更类 playbook 上线前必须完成备份恢复演练。

## 11. 验收标准

### 阶段验收

| 阶段 | 验收标准 |
| --- | --- |
| Phase 0 | 三台节点信息、访问矩阵、基线快照清单完成 |
| Phase 1 | `/opt/vafox-control` 目录、`vafox-exec` 账号、sudoers 草案通过评审 |
| Phase 2 | AI 节点可通过专用 key 访问 Huyan / AI / Core，host key 固定 |
| Phase 3 | 私网管理通道可用，公网 SSH 收敛为应急路径 |
| Phase 4 | Ansible inventory 可 ping 三台节点，只读 playbook 可执行 |
| Phase 5 | GitHub Actions Runner 可触发只读任务，变更任务受审批保护 |
| Phase 6 | 第一批 P0 / P1 自动化任务稳定运行并产生日志 |

### 最终验收

最终实现以下链路：

```text
Codex
  → GitHub Pull Request / Workflow Dispatch
  → GitHub Actions Runner on AI Node
  → /opt/vafox-control/bin/vafox-run
  → Ansible Control Plane
  → Huyan / AI / Core
```

最终验收清单：

- [ ] `ai.vafox.com` 稳定作为 VAFOX Automation Control Plane。
- [ ] `/opt/vafox-control` 目录结构与权限符合设计。
- [ ] `vafox-exec` 自动化账号完成接入，且不具备无限制 root 权限。
- [ ] SSH key、known_hosts、节点 inventory 完成登记。
- [ ] Tailscale 或 WireGuard 私网管理路径可用。
- [ ] Ansible 可对三台服务器执行只读审计与健康检查。
- [ ] GitHub Actions Runner 可触发受控自动化任务。
- [ ] 第一批 P0 / P1 自动化任务通过验收。
- [ ] 所有变更类任务具备审批、日志、dry-run、回滚方案。
- [ ] 能够从 Codex 驱动 PR / Workflow，最终由 VAFOX Control Plane 管理三台服务器。
