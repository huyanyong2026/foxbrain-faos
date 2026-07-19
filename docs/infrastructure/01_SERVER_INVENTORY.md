# VAFOX 服务器清单

**状态：基于仓库配置的清单，不是生产环境盘点。** 本仓库未提供已验证的主机名、IP、云账号、可用区、操作系统版本、规格、磁盘容量或服务器归属；这些字段均为 **TBD**。不要将域名或部署路径推断为单独服务器。

| 逻辑节点 / 职责 | 仓库证据 | 已知运行方式 | 主机、IP、区域与规格 |
| --- | --- | --- | --- |
| VAFOX 主生产运行时 | Production Deploy 工作流使用 `PRODUCTION_SSH_HOST`、`PRODUCTION_SSH_USER` 和可配置部署路径（默认 `/opt/foxbrain`）。 | Docker Compose；工作流要求 `foxbrain-web`、`foxbrain-api`、`foxbrain-worker`、PostgreSQL、Redis、MinIO、Qdrant、Nginx 均健康。 | **TBD** |
| Enterprise Data Core | Core API 发布工作流使用独立的 `CORE_SERVER_HOST` / `CORE_SERVER_USER`。 | `foxbrain-core-api.service` 在 `/opt/foxbrain-core/api` 运行只读 API。 | **TBD**（是否与主运行时共机亦为 TBD） |
| Enterprise AI | AI 发布工作流使用独立的 `AI_SERVER_HOST` / `AI_SERVER_USER`。 | 在 `/opt/ai-vafox/releases/<commit>/apps/ai` 以其 Compose 示例运行，并更新 `current-enterprise-ai` 符号链接。 | **TBD**（是否与主运行时或 Core 共机亦为 TBD） |
| Gateway 辅助服务 | Gateway 部署单元使用 `/opt/foxbrain`，但未声明宿主机。 | `firefox-gateway-data.service` 与 `firefox-explorer-identity.service` 由 systemd 管理。 | **TBD** |
| SAP Mirror 数据库 | 独立 Compose 文件声明本地回环端口 `127.0.0.1:11433`。 | SQL Server 容器 `foxbrain-sap-mirror-sql`，持久卷为 `foxbrain_sap_mirror_data`。 | **TBD** |

## 已声明的服务器侧路径与身份

| 项目 | 已知值 | 备注 |
| --- | --- | --- |
| 主运行时目录 | `/opt/foxbrain`（工作流默认值） | 可由生产 secret 覆盖。 |
| Core API 目录 / 环境文件 | `/opt/foxbrain-core/api` / `/opt/foxbrain-core/api/core-api.env` | 环境文件由服务器管理，不应提交。 |
| AI 发布根目录 / 共享环境文件 | `/opt/ai-vafox/releases` / `/opt/ai-vafox/.env` | 当前发布链接为 `/opt/ai-vafox/current-enterprise-ai`。 |
| Gateway 静态根目录 | `/var/www/firefox-gateway/current` | Nginx 示例中的建议路径；实际启用状态为 **TBD**。 |
| systemd 用户 | Core：`foxcore`；Gateway 服务：`www-data` | 账户是否已在任一服务器创建为 **TBD**。 |

## 待补充的生产盘点项

在只读访问生产环境后，记录每个逻辑节点的：云提供商/账号、主机标识和私有/公网 IP、地区与可用区、OS 与补丁级别、CPU/内存/磁盘、Docker 与 Compose 版本、挂载卷、备份位置与最后成功恢复演练。所有未从仓库或生产证据验证的信息保持 **TBD**。
