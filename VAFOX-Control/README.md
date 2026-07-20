# VAFOX Control Plane V1

`VAFOX-Control/` 是 `control.vafox.com` 的第一版**架构与代码框架**。它提供控制平面元数据的统一边界，不包含生产连接、远程命令执行或部署执行器。

## 硬性边界

- **不接入 SAP**：没有 SAP 客户端、凭据或数据模型。
- **不接入 Dify 生产**：没有 Dify URL、token 或生产适配器。
- **不修改服务器**：Server Registry 只保存声明式元数据；不会 SSH、探测或配置任何主机。
- **不连接生产**：所有 Registry 都是本地内存元数据；没有生产 endpoint、数据库连接或部署执行逻辑。

## 技术栈确认

| 组件 | 已确认技术栈 | Docker 运行形态 |
| --- | --- | --- |
| `orchestrator-api` | Python 3.11、FastAPI、Uvicorn | `python:3.11-slim`，监听 `8001` |
| `orchestrator-web` | React 19、TypeScript、Vite | Node 22 构建，Nginx 监听 `3001` |
| `postgres` | PostgreSQL 16 | `postgres:16-alpine`，仅 Docker 网络内 `5432` |

## Monorepo 目录

```text
VAFOX-Control/
├── apps/
│   ├── api/                 # Python FastAPI Control API
│   └── web/                 # React + Vite 控制台框架
├── packages/contracts/      # 未来前后端共享契约的保留位置
├── infra/postgres/          # PostgreSQL 初始化脚本与规范迁移
├── docs/                    # API 与架构说明
├── tests/                   # API 边界测试
└── pyproject.toml           # Python workspace 和测试配置
```

## Registry 架构

| Registry | 主数据 | V1 职责 | 明确不做 |
| --- | --- | --- | --- |
| Server Registry | `hostname`、`ip`、`provider`、`role`、`status` | 服务宿主的声明式目录 | SSH、服务器扫描、修改服务器 |
| Service Registry | `service_name`、`server_id`、`version`、`health_status` | 已注册服务的目录 | 调用 SAP 或 Dify |
| Health Check | 状态、延迟、详情、时间 | 接收本地健康上报并维护 Service 当前状态 | 主动探测生产依赖 |
| Deployment Registry | `version`、`deploy_time`、`operator`、`rollback_version` | 保存发布记录元数据 | 构建、发布、流量切换或生产部署 |

`services.server_id` 关联 Server Registry。`health_checks` 为 Server/Service 的历史附表，Service 的当前健康状态保留在 registry 行中，便于控制台读取。Compose 首次创建本地 PostgreSQL 卷时会执行 [`infra/postgres/init.sql`](infra/postgres/init.sql)；V1 运行时仍刻意采用内存 repository，尚未配置数据库连接。

## Control API

接口、请求约束和安全边界见 [`docs/API.md`](docs/API.md)。Registry 查询接口为 `GET /api/servers`、`GET /api/services`、`GET /api/deployments`；本地运行时还公开 `GET /health/live` 与 `GET /health/ready`。FastAPI 会生成 `/api/v1/openapi.json`。

### 本地运行（不连接任何生产系统）

```bash
cd VAFOX-Control
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --app-dir apps/api --reload
```

另开终端运行前端：

```bash
cd VAFOX-Control/apps/web
npm install
npm run dev
```

### 测试

```bash
cd VAFOX-Control
pytest
```

## Docker Compose 部署包

部署包在 `VAFOX-Control/` 内，启动 `orchestrator-api`（宿主机 `8001`）、
`orchestrator-web`（宿主机 `3001`）和仅内部可达的 `postgres:16-alpine`（`5432`）。
它使用独立 Docker 网络 `orchestrator_default` 与持久卷
`vafox-orchestrator-pgdata`；三个服务都配置了健康检查。

```bash
cd VAFOX-Control
cp .env.example .env
# 在 .env 中设置仅供本地使用的 POSTGRES_PASSWORD。
docker compose up --build -d
docker compose ps
curl --fail http://localhost:8001/health/ready
curl --fail http://localhost:3001/
```

详细启动、验证、停止和数据清理步骤见 [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)。该包
不连接生产、SAP 或 Dify，也不执行自动部署。

## 后续接入原则

持久化适配器、认证授权、审计追加日志与 Agent 上报签名必须经过单独的设计审查后才可接入。未来任何生产部署能力必须在独立审批工作流、最小权限服务身份、不可变制品以及经批准的变更单下实现；不得由当前 V1 scaffold 直接扩展为生产执行器。
