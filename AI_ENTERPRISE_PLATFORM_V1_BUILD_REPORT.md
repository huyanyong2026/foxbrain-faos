# FoxBrain Enterprise AI Platform V1 建设报告

## 建设结果

在现有 `ai.vafox.com` 登录服务、Dify、n8n 和企业微信桥接基础上，完成独立业务应用第一版。没有推倒现有基础设施，也没有占用 Dify 的 `/api` 路由。

## 六个模块

1. AI工作台：带企业对象和 evidence 提问，AI未返回时明确等待，结果默认待人工确认。
2. Agent中心：经营、库存、品牌、内容、企业资料五类 Agent，明确只读权限和审批边界。
3. 企业微信连接：保留现有回调桥接，消息只能形成知识或任务草稿。
4. 知识中心：知识草稿必须有来源、对象关联和依据，未经确认不进入正式知识。
5. 任务中心：AI任务默认待审批，负责人批准后才进入执行。
6. AI反馈学习：采纳、拒绝、修改和效果反馈先形成学习候选，再次人工复核。

## 企业连接

- `core.vafox.com`：HTTPS、域名锁定、只读 GET。
- `huyan.vafox.com`：读取 CEO Brain 状态；批准后的决策交换接口预留，默认不自动发送。
- Living Enterprise：通过 CEO Brain 的只读对象接口获取上下文。
- 企业微信：沿用独立回调桥接，不在业务页面展示密钥。

## 数据库变化

新增：`ai_agents`、`enterprise_connections`、`ai_agent_runs`、`ai_knowledge_items`、`ai_tasks`、`ai_feedback`、`ai_evidence_links`、`wecom_connections`。

全部使用幂等建表，不修改现有 `auth_users` 数据。

## 安全边界

- 不连接或修改 SAP，不增加 SAP 写权限。
- Data Core 和 Living Enterprise 只读。
- 所有外部连接必须 HTTPS 且锁定企业域名。
- 所有 AI 结果和任务必须有 evidence。
- AI结果、任务、学习反馈均要求人工确认。
- CSRF、登录、角色权限和安全响应头已加入。
- 服务器密钥仅通过环境变量配置，不进入 GitHub。

## 部署状态

当前为代码与配置模板阶段，尚未替换生产 `vafox-auth`。生产部署必须先备份 `/opt/ai-vafox`、PostgreSQL 数据和 Nginx 配置，再进行候选容器验证。

## 测试结果

- Python 编译检查：通过。
- AI平台专项测试与既有系统联合回归：65 项全部通过。
- 隔离 Docker 构建：通过。
- 临时 PostgreSQL 建表：8/8 张表。
- Agent 初始化：5/5 个。
- 健康接口：200，明确 `sap_write=false`。
- CEO Brain 拉取接口：无服务令牌 403，有服务令牌 200。
- 登录页与静态资源：200。
- 六个业务页面未登录访问：全部正确跳转登录。
- 测试容器、网络、文件和候选镜像：全部清理。
- 生产 `vafox-auth`、Dify、n8n、企业微信服务：测试期间持续运行，未切换流量。
