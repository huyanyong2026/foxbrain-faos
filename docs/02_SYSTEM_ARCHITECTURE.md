# 02 System Architecture / 系统架构

当前实现采用渐进升级，不推倒重做。

## 当前核心文件

- `portal_v2.py`：门户、登录、权限、首页、档案、知识、文档、AI 查询。
- `sync_sap_b1.py`：SAP B1 同步脚本。
- `wiki_ai_plan_content.json`：Wiki 初始化内容。
- `.env.example`：环境变量模板。

## 当前数据层

- SQLite：门户账号、档案、知识条目、文件记录、日志、时间轴、关联关系。
- PostgreSQL：SAP B1 同步快照。
- JSON summary：门户读取经营摘要。

## 目标结构

- `backend/`：后端服务。
- `frontend/`：前端应用。
- `ai/`：智能体、提示词、模型适配。
- `knowledge/`：知识库解析、分类、向量化。
- `sap/`：SAP B1 同步和分析。
- `workflow/`：审批和任务流。
- `deployment/`：部署脚本。
- `docs/`：产品和工程文档。

