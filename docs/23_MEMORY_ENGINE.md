# 23 Memory Engine / AI 长期记忆引擎

## 目标

Memory Engine 让 FoxBrain 记住长期企业上下文，不再把每一次提问都当作孤立问题。

它用于沉淀：

- 经营原则
- 用户偏好
- 重要决策
- 门店策略
- 品牌策略
- 定价规则
- 风险偏好
- 重要对话
- AI 建议的采纳或拒绝历史

## 页面与 API

- `/memory`
- `/memory/view?id=1`
- `GET /api/memory`
- `POST /api/memory`
- `GET /api/memory/{id}`
- `POST /api/memory/{id}/approve`
- `POST /api/memory/{id}/reject`
- `POST /api/memory/{id}/archive`
- `GET /api/preferences`
- `POST /api/preferences`

## 记忆模型

- `memory_id`
- `title`
- `content`
- `memory_type`
- `object_type`
- `object_id`
- `source_type`
- `source_id`
- `importance`
- `confidence`
- `visibility`
- `status`
- `created_by`
- `created_at`
- `updated_at`
- `expires_at`

## 记忆类型

- `company_principle`
- `user_preference`
- `business_decision`
- `pricing_rule`
- `brand_strategy`
- `store_strategy`
- `supplier_risk`
- `customer_insight`
- `ai_suggestion`
- `rejected_suggestion`

## 审核流

AI 或用户发现重要信息后，只能先创建 `pending_review` 记忆。管理者审核后才能成为 `approved` 记忆，供 AI CEO 和后续智能体参考。

流程：

```text
AI detects important memory
-> Create Pending Memory
-> Manager reviews
-> Approve / Reject / Archive
-> Approved memory becomes active context
```

## 可见范围

- `public_internal`
- `manager_only`
- `owner_only`
- `finance_only`
- `restricted`

## AI CEO 集成

AI CEO 页面增加“AI 总经理参考记忆”区域，只展示已审核且当前用户有权限查看的记忆。

## 安全原则

- AI 不自动写入永久记忆。
- 敏感记忆需要权限隔离。
- 不记录密码、API Key、数据库连接串。
- 所有审核动作写入操作日志。

## Task009 Agent Collaboration

Approved memories can be used as context by AI agents. Pending or rejected memories must not be treated as official operating principles.
