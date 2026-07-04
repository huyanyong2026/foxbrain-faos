# 24 Decision Memory / 决策记忆

## 目标

决策记忆用于记录公司重要经营选择，帮助后续 AI 和管理层理解“当时为什么这么决定”。

## 页面与 API

- `/decisions`
- `GET /api/decisions`
- `POST /api/decisions`

## 字段

- `decision_title`
- `decision_context`
- `options_considered`
- `selected_option`
- `reason`
- `risks`
- `owner`
- `decision_date`
- `related_objects`
- `follow_up_task`

## 示例场景

- 是否长期 59 折销售 Osprey
- 是否提回 Osprey 期货
- 是否扩展大店
- 是否调整 KAILAS 折扣
- 是否推进 VAFOX 自有品牌

## 与 Memory Engine 的关系

创建决策时，可以同步生成一条 `business_decision` 类型的待审核记忆。审核通过后，AI CEO 可以在日报中引用该决策作为长期上下文。

## 后续升级

- 决策详情页
- 关联任务
- 关联知识库
- 关联 Research Result
- 复盘提醒
- 决策效果追踪
