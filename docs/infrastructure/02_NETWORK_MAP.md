# VAFOX 网络地图

**范围：仓库中声明的监听、反向代理与服务依赖。** DNS 解析、证书实际签发情况、防火墙规则、负载均衡器、VPC/子网和跨主机路由均为 **TBD**。

```text
Internet
  │  HTTPS（实际监听与 DNS：TBD）
  ├─ gateway.vafox.com ─ Nginx ── 127.0.0.1:8091  Gateway public-data proxy
  │                              └ 127.0.0.1:8092  Explorer identity service
  ├─ core.vafox.com ─── Nginx ── 127.0.0.1:8090  Core read-only API
  ├─ ai.vafox.com ───── existing HTTPS server ── 127.0.0.1:5010 Enterprise AI
  └─ huyan.vafox.com ── Nginx ── foxbrain-web:3000 / foxbrain-api:8000

Enterprise AI ─ HTTPS + token ──> core.vafox.com (read-only)
Gateway proxy ─ HTTPS + public token ──> core.vafox.com (read-only)
SAP mirror client ─ loopback only ──> 127.0.0.1:11433 (SQL Server container)
```

## 公开与本地监听

| 接入点 | 协议 / 端口 | 上游 | 仓库声明的限制 |
| --- | --- | --- | --- |
| `gateway.vafox.com` | HTTP 80 重定向；HTTPS 443 | `127.0.0.1:8091`、`127.0.0.1:8092` | TLS 1.2/1.3；公开数据仅经 `/api/public/`；Explorer 经 `/explorer` 与 `/api/explorer/`。 |
| `core.vafox.com` | HTTP 80 重定向；HTTPS 443 | `127.0.0.1:8090` | 每 IP 10r/s，突发 30；`/healthz` 不公开；请求体上限 1k。 |
| `ai.vafox.com` | HTTPS server 内的路由片段 | `127.0.0.1:5010` | 保留既有 `/api`、`/console`、`/v1`、`/wecom`、`/n8n` 路由；完整 server block、TLS 与 443 监听为 **TBD**。 |
| `huyan.vafox.com` | HTTP 80（仓库示例） | Compose DNS：`foxbrain-web:3000`、`foxbrain-api:8000` | HTTPS 配置、容器网络定义及生产启用状态为 **TBD**。 |
| Foundation Gateway | 宿主 `${GATEWAY_PORT:-8080}` → 容器 8080 | Compose 内部服务 | 仅适用于根目录 `docker-compose.yml` 的 foundation stack。 |
| SAP Mirror | `127.0.0.1:11433` → 容器 1433 | SQL Server | 仅回环绑定；宿主/容器所在节点为 **TBD**。 |

## Compose 内部网络

根目录 foundation Compose 创建桥接网络 `vafox`。Gateway 依赖 Auth、Core Data、AI 和 Memory；这些服务再依赖 PostgreSQL、Redis 或 MinIO 的健康检查。该网络模型与生产工作流要求的 `foxbrain-*` 服务清单不同；两者的生产对应关系为 **TBD**，不得据此推断实际拓扑。

## 网络控制待核验

- 仅应公开经批准的 HTTP(S) 入口；PostgreSQL、Redis、MinIO、Qdrant 和 SAP Mirror 的实际防火墙/安全组规则为 **TBD**。
- Nginx 示例将 Core、Gateway 辅助服务和 AI 上游绑定到 loopback；应在目标服务器上以 `ss -tlnp`、`nginx -T` 和防火墙规则验证。
- Core 与 AI/Gateway 的令牌、TLS 终止位置、证书续期机制及网络分段均为 **TBD**。
