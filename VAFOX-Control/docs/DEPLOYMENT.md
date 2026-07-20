# VAFOX Orchestrator V1 部署说明

## 范围与安全边界

此 Docker Compose 包仅启动本机的 `orchestrator-api`、`orchestrator-web` 和
`postgres:16-alpine`。它不包含生产连接、SAP 连接、Dify 连接、远程命令或自动部署
逻辑。PostgreSQL 的 `5432` 只在独立的 `orchestrator_default` Docker 网络中可用，
不会发布到宿主机。

已确认的运行时技术栈为 Python 3.11/FastAPI/Uvicorn API、React 19 + TypeScript +
Vite Web（由 Nginx 提供静态文件）以及 PostgreSQL 16。Compose 不会拉起、调用或配置
其他服务。

## 前置条件

- Docker Engine 及 Docker Compose v2。
- 宿主机端口 `8001` 与 `3001` 未被占用。
- 本地工作副本；不要将 `.env` 或本地密码提交到版本库。

## 启动

```bash
cd VAFOX-Control
cp .env.example .env
# 编辑 .env：设置唯一的本地 POSTGRES_PASSWORD。
docker compose up --build -d
docker compose ps
```

Compose 使用具名卷 `vafox-orchestrator-pgdata` 保存 PostgreSQL 数据；首次创建卷时，
会执行 `infra/postgres/init.sql`。初始化脚本只创建本地 registry 元数据表，且不会
配置任何外部系统。

## 验证

```bash
curl --fail http://localhost:8001/health/live
curl --fail http://localhost:8001/health/ready
curl --fail http://localhost:3001/
docker compose ps
```

预期三个服务均为 running/healthy。PostgreSQL 不映射宿主机端口；如需仅为本地诊断
访问数据库，请使用 `docker compose exec postgres psql -U vafox_orchestrator -d vafox_orchestrator`。

## 停止与清理

```bash
cd VAFOX-Control
docker compose down
# 仅在确认可以删除本地开发数据时执行：
docker compose down -v
```

`down` 会保留数据库卷；`down -v` 会移除 `vafox-orchestrator-pgdata`，下次启动将重新
执行初始化脚本。
