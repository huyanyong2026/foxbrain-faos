# VAFOX 部署规则

## 1. 证据优先与变更边界

1. 本目录只记录仓库证据；服务器、网络、凭据和运行状态未知时必须标记 **TBD**，不得以域名、路径或示例配置推断事实。
2. 生产秘密只保存在服务器管理的环境文件或 GitHub Secrets；不得提交 `.env`、令牌、密码、私钥、真实业务数据或 SAP 生产凭据。
3. Core API 仅使用本地 SAP Mirror 凭据，保持 GET/HEAD 只读边界；Gateway 只使用 `public:read`，Explorer 使用独立 `explorer:match` 范围。
4. 数据库、缓存、对象/向量存储及 SAP Mirror 不得直接暴露公网；任何例外须在变更前补充已验证的网络与审批记录（目前为 **TBD**）。

## 2. 发布流程

### 主生产运行时

`main` 推送或手动触发 `Production Deploy`。流程应：验证提交和工作流脚本、执行两组 pytest、生成并校验 `deployment.json`、以临时 `.env.example` 运行 `docker compose config`，然后使用受保护的生产 SSH 配置部署。

服务器端规则：

1. 先确认部署目录已有服务器管理的 `.env`，并执行生产环境校验；缺少该文件即失败。
2. 记录前一提交；部署失败时以工作流 trap checkout 前一提交并执行 `docker compose up -d --build --remove-orphans` 回滚。
3. 使用指定提交重置工作树，生成部署元数据，验证 Compose，构建 `foxbrain-web`、`foxbrain-api`、`foxbrain-worker`，再启动服务。
4. 等待 required services 健康，验证本地 runtime 元数据；仅在通过后清理回滚脚本。

实际 SSH 目标、部署目录覆盖值、服务 Compose 来源及已执行的发布记录均为 **TBD**。

### Core 与 AI 独立发布

- `deploy-ai-replenishment.yml` 先测试 AI/Core，再先发布 Core API，最后发布 AI。Core 发布会备份 API 文件和环境文件、重启 systemd，并在本地 `:8090/healthz` 失败时恢复。
- AI 发布会写入以提交命名的 release 目录，构建/启动其 Compose，验证 `127.0.0.1:5010/ops-api/health`，之后才更新 `current-enterprise-ai` 符号链接。
- Nginx 路由变更前必须备份现有配置、评审 location 优先级并运行 `nginx -t`；AI 路由不得覆盖既有 `/api`、`/console`、`/v1`、`/wecom`、`/n8n`。

## 3. 发布前后检查

| 阶段 | 最低要求 | 证据 / 状态 |
| --- | --- | --- |
| 发布前 | 工作树干净；测试通过；生成的 metadata 提交匹配；Compose 配置可解析。 | CI 设计已声明；最近结果 **TBD**。 |
| 变更前 | 备份应用、环境、Nginx 配置及数据恢复点；确认回滚提交。 | 生产备份与恢复演练证据 **TBD**。 |
| 发布后 | required services 健康；runtime metadata 与期望提交/版本匹配；检查公共入口和 Core/AI 本地 health。 | 最近生产验证 **TBD**。 |
| 失败 | 停止推进，执行对应工作流的回滚路径，保留日志和版本证据。 | 回滚演练结果 **TBD**。 |

## 4. 运维规则

- 先用生产环境实际采用的 Compose 文件核对服务名，再运行 `healthcheck.sh`；该脚本要求 `foxbrain-*` 服务，而根 foundation Compose 使用另一组服务名。
- 升级前进行备份；禁止在备份完成前删除 `/opt/foxbrain`、`/opt/firefox-portal`、`/opt/firefox-sap-sync`、`/etc/nginx` 或 `/etc/letsencrypt`。
- 将所有生产验证输出、实际主机盘点、端口/防火墙审计、证书状态和恢复演练结果回填到受控运维记录；本仓库当前未包含这些实时证据，状态为 **TBD**。
