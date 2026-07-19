# VAFOX 服务地图

本表区分“仓库定义”与“已部署”。除工作流和配置文件明确声明的内容外，运行状态、镜像标签、健康状态、扩缩容与真实主机位置均为 **TBD**。

| 服务 / 组件 | 职责 | 运行模型与接口 | 依赖 / 数据边界 |
| --- | --- | --- | --- |
| Gateway（foundation） | 外部 API 入口与上游路由 | 根 Compose 服务，宿主端口默认 8080；`GET /health`。 | 依赖 Auth、Core Data、AI、Memory；仅为 foundation 定义。 |
| Auth / Core Data / AI / Memory（foundation） | 登录、数据、AI、记忆的基础服务边界 | 根 Compose 的内部服务；`GET /health`。 | 分别依赖 PostgreSQL、Redis 或 MinIO；生产映射为 **TBD**。 |
| PostgreSQL / Redis / MinIO（foundation） | 关系数据、缓存/队列、对象存储 | 根 Compose 使用持久卷与健康检查。 | 不应推断为生产实例或公开端口。 |
| `foxbrain-web` / `foxbrain-api` / `foxbrain-worker` | 生产工作流要求的 Web、API 和 Worker 运行时 | Production Deploy 构建前三者，检查其与基础设施服务健康；内部 health/runtime 在 `127.0.0.1:8088` 被验证。 | 对应的 Compose 定义、端口和镜像来源在当前根 Compose 中未提供，均为 **TBD**。 |
| Qdrant / Nginx | 生产工作流要求的向量与反向代理组件 | 与上述生产服务同列为 required services。 | Compose 声明、持久化及端口为 **TBD**。 |
| Core read-only API | 面向应用的 SAP Mirror 只读访问边界 | systemd 服务；本地 `:8090/healthz`；Nginx 将 `core.vafox.com` 转发至该端口。 | 仅本地 SAP Mirror 凭据；只接受认证的 GET/HEAD；不使用 SAP 生产凭据。 |
| Gateway public-data proxy | 向 Gateway 提供受限公开数据 | systemd 服务；Nginx 转发到 `127.0.0.1:8091`。 | 调用 Core 的 `public:read` 接口；Core token 在服务器环境文件中。 |
| Explorer identity | Explorer 登录与购买记录匹配 | systemd 服务；Nginx 转发到 `127.0.0.1:8092`。 | 使用独立 `explorer:match` Core token；短信服务配置与状态为 **TBD**。 |
| Enterprise AI | 数字劳动力与补货分析 | 独立 AI 发布工作流；Nginx 片段代理至 `127.0.0.1:5010`。 | 从 `core.vafox.com` 读取事实；不写 SAP。 |
| SAP Mirror SQL Server | SAP 镜像存储 | 独立 Compose，容器 1433 映射到 loopback `:11433`。 | 数据同步来源、作业实际运行与数据新鲜度为 **TBD**。 |

## 已声明的服务调用

1. Gateway public-data proxy 和 Enterprise AI 分别通过 HTTPS 调用 `core.vafox.com`，并使用范围受限的服务器侧令牌。
2. Core API 是应用访问 SAP Mirror 的唯一声明路径，且为只读。
3. Huyan Nginx 示例将页面流量交给 `foxbrain-web:3000`，API 流量交给 `foxbrain-api:8000`；此为配置示例，不构成已部署证明。

## 健康检查与运行证据

- Foundation Compose 为 Auth、Core Data、AI、Memory、PostgreSQL、Redis 和 MinIO 定义健康依赖；服务通用健康端点为 `GET /health`。
- Production Deploy 在部署后等待八个 required services 健康，并验证 `127.0.0.1:8088/health/runtime`；最近一次实际执行结果为 **TBD**。
- `healthcheck.sh` 也检查同名八个服务和本地 Web/API 路径，但它与根 foundation Compose 的服务名不一致，因此应先确认目标 Compose 文件，再在生产环境运行。
