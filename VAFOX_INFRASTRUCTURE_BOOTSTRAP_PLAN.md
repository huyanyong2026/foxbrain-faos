# VAFOX 三服务器基础设施接管方案

> 目标：建立未来自动化升级基础，停止继续以单点修脚本方式维护生产环境。
>
> 原则：先审计、再标准化、再自动化；所有接管动作必须可追踪、可回滚、可审计。

## 0. 服务器清单

| 服务器 | 公网 IP | 默认用户 | 建议角色 | 接管优先级 |
| --- | --- | --- | --- | --- |
| Huyan | `140.143.207.194` | `ubuntu` | 前端、网关、Nginx 入口、轻量业务服务 | P0 |
| AI | `1.13.254.217` | `ubuntu` | AI 服务、模型编排、Release 构建与灰度验证 | P0 |
| Core | `139.199.174.36` | `root` | 核心数据、数据库、共享存储、备份源 | P0 |

## 1. 三服务器架构

### 1.1 目标架构

```text
Users / Operators
        |
        v
+----------------------------+
| Huyan                      |
| - Public Nginx gateway     |
| - TLS termination          |
| - Web / API reverse proxy  |
| - Static assets            |
+-------------+--------------+
              |
              | Internal/API traffic over SSH tunnel/VPC/private ACL where available
              v
+----------------------------+           +----------------------------+
| AI                         |<--------->| Core                       |
| - AI runtime services      |           | - Database / data services |
| - Release candidate test   |           | - Canonical business data  |
| - Batch inference jobs     |           | - Backup source            |
+----------------------------+           +----------------------------+
```

### 1.2 接管阶段

1. **只读审计阶段**：运行本仓库提供的 `server_audit_*.sh`，收集系统、Docker、Nginx、磁盘、网络、定时任务与备份线索。
2. **基线冻结阶段**：记录当前服务端口、镜像版本、Nginx 配置、数据目录、部署脚本、定时任务与证书路径。
3. **标准化阶段**：统一 Docker Compose 目录、Nginx 配置目录、日志目录、备份目录与发布目录。
4. **自动化阶段**：引入 GitHub Actions 自动部署、AI Release 流程、Core 数据同步、自动备份与自动回滚。

## 2. SSH 接入方式

### 2.1 推荐 SSH 配置

在运维终端或 CI/CD Runner 中维护以下 `~/.ssh/config` 条目：

```sshconfig
Host vafox-huyan
  HostName 140.143.207.194
  User ubuntu
  IdentityFile ~/.ssh/vafox_deploy_key
  IdentitiesOnly yes
  ServerAliveInterval 30
  ServerAliveCountMax 3

Host vafox-ai
  HostName 1.13.254.217
  User ubuntu
  IdentityFile ~/.ssh/vafox_deploy_key
  IdentitiesOnly yes
  ServerAliveInterval 30
  ServerAliveCountMax 3

Host vafox-core
  HostName 139.199.174.36
  User root
  IdentityFile ~/.ssh/vafox_deploy_key
  IdentitiesOnly yes
  ServerAliveInterval 30
  ServerAliveCountMax 3
```

### 2.2 密钥与权限

- 使用专用部署密钥，不复用个人 SSH 密钥。
- GitHub Actions 使用 `SSH_PRIVATE_KEY` Secret 注入部署密钥。
- 首次接管前记录 `authorized_keys` 指纹，不直接覆盖原文件。
- 后续建议逐步创建统一的 `deploy` 用户，并通过 `sudoers.d` 精确授权部署命令。

### 2.3 SSH 验证命令

```bash
ssh vafox-huyan 'hostname && whoami && date -Is'
ssh vafox-ai 'hostname && whoami && date -Is'
ssh vafox-core 'hostname && whoami && date -Is'
```

## 3. Docker 统一管理

### 3.1 目录规范

建议在每台服务器统一使用：

```text
/opt/vafox/
  apps/
    <service-name>/
      docker-compose.yml
      .env
      releases/
      shared/
  logs/
  backups/
  scripts/
```

### 3.2 Compose 管理原则

- 每个服务必须具备明确的 `image` 或 `build` 来源。
- 每个服务必须具备 `restart` 策略和 `healthcheck`。
- 生产环境变量统一放在服务器本地 `.env`，不提交明文密钥到 Git。
- 镜像使用不可变标签，例如 Git SHA：`ghcr.io/org/service:<git_sha>`。
- 所有容器日志必须可通过 `docker compose logs` 查询。

### 3.3 接管检查项

- `docker ps --format ...`：确认运行容器。
- `docker images`：确认镜像来源和历史标签。
- `docker network ls`：确认跨服务网络。
- `docker volume ls`：确认持久化数据。
- `docker compose config`：确认 Compose 配置可解析。

## 4. Nginx 统一管理

### 4.1 配置规范

建议统一使用：

```text
/etc/nginx/
  nginx.conf
  sites-available/
    vafox-<service>.conf
  sites-enabled/
    vafox-<service>.conf -> ../sites-available/vafox-<service>.conf
```

### 4.2 网关原则

- Huyan 作为公网入口优先承接 TLS、静态资源与反向代理。
- AI 与 Core 默认不直接暴露公网服务，除非审计确认已有公网依赖。
- 每个站点配置必须包含访问日志和错误日志路径。
- 修改 Nginx 前必须执行 `nginx -t`。
- 自动部署仅在配置测试通过后执行 reload。

### 4.3 接管检查项

- `nginx -T`：导出有效配置用于审计。
- `systemctl is-active nginx`：确认服务状态。
- `ss -lntp`：确认监听端口。
- `certbot certificates` 或证书目录检查：确认 TLS 证书来源与有效期。

## 5. GitHub Actions 自动部署

### 5.1 部署目标

- `main` 分支合并后自动构建镜像。
- 镜像推送到 GHCR 或现有镜像仓库。
- 通过 SSH 登录目标服务器，拉取新镜像，执行健康检查。
- 健康检查失败时自动回滚到上一版本。

### 5.2 推荐 Secrets

| Secret | 用途 |
| --- | --- |
| `SSH_PRIVATE_KEY` | 服务器部署密钥 |
| `HUYAN_HOST` | `140.143.207.194` |
| `HUYAN_USER` | `ubuntu` |
| `AI_HOST` | `1.13.254.217` |
| `AI_USER` | `ubuntu` |
| `CORE_HOST` | `139.199.174.36` |
| `CORE_USER` | `root` |
| `REGISTRY_TOKEN` | 镜像仓库 Token |
| `ENV_*` | 环境变量或密钥引用 |

### 5.3 工作流步骤

1. Checkout 代码。
2. 运行测试、Lint、构建。
3. 构建 Docker 镜像并以 Git SHA 打 tag。
4. 推送镜像。
5. SSH 到目标服务器。
6. 写入 release manifest。
7. `docker compose pull && docker compose up -d`。
8. 执行服务健康检查。
9. 失败时使用 manifest 回滚上一镜像标签。

## 6. AI Release 流程

### 6.1 Release 分层

| 阶段 | 说明 | 是否影响生产 |
| --- | --- | --- |
| Candidate | 在 AI 服务器构建候选版本并运行离线检查 | 否 |
| Shadow | 读取生产样本或脱敏数据执行影子验证 | 否 |
| Canary | 小流量或内部用户验证 | 是，低风险 |
| Stable | 全量发布 | 是 |

### 6.2 AI Release 准入条件

- 模型、Prompt、Agent 配置均有版本号。
- Release 包含变更摘要、风险点、回滚方式。
- 核心指标通过阈值检查：错误率、响应时间、成本、业务准确率。
- 与 Core 数据交互必须只读验证后再开放写路径。

### 6.3 Release 产物

```text
release_manifest.json
ai_model_version.txt
prompt_version.txt
agent_config_version.txt
rollback_manifest.json
healthcheck_report.md
```

## 7. Core 数据同步

### 7.1 原则

- Core 是核心数据可信源。
- 同步流程必须区分只读同步、增量同步、双向同步。
- 默认禁止无审计的双向同步。
- 所有同步任务必须记录开始时间、结束时间、源、目标、数据量、校验结果。

### 7.2 建议方案

- 文件同步：`rsync --dry-run` 审计后再启用正式同步。
- 数据库同步：优先使用只读账号、逻辑备份、增量 binlog 或数据库原生复制机制。
- 对 AI 训练、分析、报表任务优先使用 Core 的只读副本或脱敏快照。

### 7.3 校验指标

- 表数量、行数量、校验和。
- 文件数量、总大小、mtime 范围。
- 同步失败告警。
- 最近一次成功同步时间。

## 8. 自动备份

### 8.1 备份范围

- Core：数据库、业务上传文件、核心配置、密钥指纹、定时任务清单。
- AI：模型配置、Prompt、Release manifest、服务配置。
- Huyan：Nginx 配置、TLS 证书元数据、前端构建产物、网关配置。

### 8.2 备份策略

| 类型 | 频率 | 保留周期 | 存储位置 |
| --- | --- | --- | --- |
| 快照备份 | 每日 | 7-14 天 | 本机 + 异地 |
| 逻辑备份 | 每日 | 30 天 | Core + 对象存储 |
| Release 备份 | 每次发布 | 90 天 | `/opt/vafox/backups/releases` |
| 配置备份 | 每次变更 | 180 天 | Git 私有仓库或加密对象存储 |

### 8.3 备份检查

- 每次备份生成 manifest。
- 每周至少一次恢复演练。
- 备份必须加密、压缩并校验 checksum。
- 备份告警必须进入人工可见渠道。

## 9. 自动回滚

### 9.1 回滚触发条件

- 健康检查失败。
- 容器无法启动或重复重启。
- 关键接口 5xx 超阈值。
- AI Release 指标低于准入阈值。
- 数据同步校验失败。

### 9.2 回滚策略

1. 读取当前 `release_manifest.json`。
2. 找到上一稳定版本镜像 tag、Compose 文件与环境变量版本。
3. 执行 `docker compose pull` 与 `docker compose up -d`。
4. 运行健康检查。
5. 写入 `rollback_report.md`。
6. 通知负责人。

### 9.3 回滚注意事项

- 数据库 Schema 变更必须支持向后兼容或具备独立数据回滚方案。
- AI Prompt/Agent 配置必须可按版本回退。
- Nginx 配置修改必须保留上一份已通过 `nginx -t` 的配置。
- 回滚脚本不得删除生产数据。

## 10. 只读审计执行报告模板

> 以下模板用于三台服务器执行 `server_audit_*.sh` 后统一填报。

````markdown
# VAFOX 服务器只读审计执行报告

## 基本信息

- 服务器：Huyan / AI / Core
- IP：
- 执行用户：
- 执行时间：
- 审计脚本：
- 脚本 Git Commit：

## 执行命令

```bash
bash server_audit_<server>.sh
```

## 只读约束确认

- [ ] 未修改系统配置
- [ ] 未删除文件
- [ ] 未重启服务
- [ ] 未修改数据库
- [ ] 未执行写入型部署命令

## 审计摘要

| 项目 | 结果 | 风险等级 | 备注 |
| --- | --- | --- | --- |
| 系统版本 |  |  |  |
| SSH 接入 |  |  |  |
| Docker |  |  |  |
| Nginx |  |  |  |
| 端口监听 |  |  |  |
| 定时任务 |  |  |  |
| 磁盘容量 |  |  |  |
| 备份线索 |  |  |  |
| 数据目录 |  |  |  |

## 发现的问题

1.
2.
3.

## 建议动作

1.
2.
3.

## 附件

- 审计输出文件：
- 截图或日志摘要：
````

## 11. 下一步落地顺序

1. 在三台服务器分别执行只读审计脚本。
2. 汇总执行报告并确认当前生产拓扑。
3. 建立 `/opt/vafox` 标准目录和 release manifest 规范。
4. 将 Docker Compose 与 Nginx 配置纳入版本化管理。
5. 接入 GitHub Actions 部署到非核心服务。
6. 建立 AI Release 候选验证流程。
7. 建立 Core 只读数据同步与备份校验。
8. 最后启用自动回滚和告警。
