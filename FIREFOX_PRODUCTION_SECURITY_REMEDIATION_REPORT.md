# FireFox Production Security Remediation Report

## 整改时间

2026-07-14 09:51-10:03（Asia/Shanghai）

## 整改范围

1. 移除 `huyan.vafox.com` 的旧 SAP 同步配置、服务、容器和本地副本。
2. 收紧 `ai.vafox.com` 的防火墙规则和 Docker 宿主机端口。

没有修改 SAP、Core 数据或业务数据库，没有增加 SAP 权限。

## Huyan 整改结果

- Portal 环境文件已替换为 Core-only 配置，只包含：
  - `CORE_BASE_URL`
  - `CORE_API_TOKEN`
- 运行进程中的 `SAP_*` 键数量：0。
- 运行进程中的 `FOX_SYNC_*` 键数量：0。
- 已移除旧容器：
  - `foxbrain-sap-mirror-sql`
  - `sap-sync-db`
- 已移除对应本地数据卷。
- 已移除旧同步目录、旧环境文件、旧定时服务、旧 Cron 入口和 SAP 同步部署备份。
- 已清除历史备份中的旧 SAP 直连环境文件和明文主机配置；未删除经营数据库备份。
- 已移除数据库中的 3 个旧同步连接和 5 个旧手工同步任务。
- Portal 已停止自动生成本地 SAP 测试副本和生产 SAP 占位连接，同步环境默认固定为 Core-only。
- 已关闭本地 11433、15432 监听端口。
- Portal 重启后状态：active。
- Portal 到 `core.vafox.com` 只读状态接口：HTTP 200。
- 公网首页：HTTP 200。
- 最终残留检查：旧同步连接 0、旧同步任务 0、旧 SAP 环境文件 0、包含生产 SAP 主机的文本配置 0。

安全整改记录：

`/opt/backups/security-remediation-20260714-095116`

该目录只保存脱敏操作清单，不保存旧 SAP 密钥或旧数据库副本。

## AI 整改结果

- 删除 UFW 公网放行规则：
  - `3000:3100/tcp`
  - `9443/tcp`
- 当前入站规则只保留：
  - SSH 22
  - HTTP 80
  - HTTPS 443
- 保留到 SAP 公网地址的出站拒绝规则。
- 13 个 Docker 宿主机端口全部改为 `127.0.0.1` 绑定。
- 非本机 Docker 端口映射数量：0。
- PostgreSQL、Redis、Milvus、Dify、n8n、Portainer、Sandbox、插件服务和企业微信服务均不再直接暴露公网。
- Nginx 继续通过本机端口访问所需服务。
- 所有容器无 unhealthy 状态。
- AI 健康接口：HTTP 200。
- Dify API 健康接口：HTTP 200。
- AI 到 Core 只读状态接口：HTTP 200。
- AI 容器运行时 `SAP_*` 键数量：0。

回滚备份：

`/opt/backups/security-remediation-20260714-095301`

备份目录权限为 0700，旧 Compose 副本权限为 0600。

## 公网验证

| 检查项 | 结果 |
|---|---|
| `https://huyan.vafox.com/` | 200 |
| Huyan 受保护页面 | 正常跳转登录 |
| `https://ai.vafox.com/auth/login` | 200 |
| `https://ai.vafox.com/ops-api/health` | 200 |
| `https://gateway.vafox.com/` | 200 |
| `https://gateway.vafox.com/api/core/status` | 200 |
| Core 公共接口无令牌访问 | 401，符合预期 |
| AI 3000/5001/5432/9443 公网访问 | 均不可达 |
| Huyan 11433/15432 公网访问 | 均不可达 |

## 最终状态

两项指定 P1 风险已经完成整改：

1. `huyan.vafox.com` 不再保留可运行的旧 SAP 同步配置、容器或本地副本，当前只从 Core API 读取。
2. `ai.vafox.com` 的内部容器端口已全部限制为本机访问，主机防火墙只开放必要的 22/80/443。

生产服务当前正常。
