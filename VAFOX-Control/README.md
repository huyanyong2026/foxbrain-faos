# VAFOX Control Plane V1

`VAFOX-Control/` 是 `control.vafox.com` 的第一版**架构与代码框架**。它提供控制平面元数据的统一边界，不包含生产连接、远程命令执行或部署执行器。

## 硬性边界

- **不接入 SAP**：没有 SAP 客户端、凭据或数据模型。
- **不接入 Dify 生产**：没有 Dify URL、token 或生产适配器。
- **不修改服务器**：Server Registry 只保存声明式元数据；不会 SSH、探测或配置任何主机。
- **不连接生产**：Deployment Registry 只接受 `local`、`development`、`staging`；生产环境输入会被 API 验证拒绝。

## Monorepo 目录

```text
VAFOX-Control/
├── apps/
│   ├── api/                 # Python FastAPI Control API
│   └── web/                 # React + Vite 控制台框架
├── packages/contracts/      # 未来前后端共享契约的保留位置
├── infra/postgres/          # PostgreSQL 规范迁移（不自动执行）
├── docs/                    # API 与架构说明
├── tests/                   # API 边界测试
└── pyproject.toml           # Python workspace 和测试配置
```

## Registry 架构

| Registry | 主数据 | V1 职责 | 明确不做 |
| --- | --- | --- | --- |
| Server Registry | 名称、环境、区域、受控 endpoint、标签、状态 | 服务宿主的可发现性元数据 | SSH、服务器扫描、修改服务器 |
| Service Registry | `server_id`、版本、endpoint、能力、状态 | 已注册服务的目录 | 调用 SAP 或 Dify |
| Health Check | 资源类型、资源 ID、状态、延迟、详情、时间 | 接收受控健康上报并维护当前状态 | 主动探测生产依赖 |
| Deployment Registry | `service_id`、版本、artifact digest、环境、变更单、状态 | 保存非生产发布意图与审计关联 | 构建、发布、流量切换或生产部署 |

`servers → services → deployments` 是外键关系。`health_checks` 为 Server/Service 的历史附表，当前状态冗余在两张 registry 表中，便于控制台读取。完整 DDL 见 [`infra/postgres/001-control-plane.sql`](infra/postgres/001-control-plane.sql)。V1 运行时刻意采用内存 repository；尚未配置数据库连接。

## Control API

接口、请求约束和安全边界见 [`docs/API.md`](docs/API.md)。API 统一使用 `/api/v1` 前缀；本地运行时还公开 `/health/live` 与 `/health/ready`。FastAPI 会生成 `/api/v1/openapi.json`。

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

## 后续接入原则

持久化适配器、认证授权、审计追加日志与 Agent 上报签名必须经过单独的设计审查后才可接入。未来任何生产部署能力必须在独立审批工作流、最小权限服务身份、不可变制品以及经批准的变更单下实现；不得由当前 V1 scaffold 直接扩展为生产执行器。
