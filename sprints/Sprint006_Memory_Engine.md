# Sprint006: Memory Engine｜企业记忆引擎

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint001 Drive, Sprint002 Object Engine, Sprint003 Knowledge Pipeline, Sprint004 Search + Timeline, Sprint005 CEO Dashboard

---

## 1. Sprint Goal

建立 VAFOX 的企业记忆引擎，让系统不仅能保存文件、对象、知识和时间轴，还能记录“为什么做出某个决定”。

Memory Engine 的目标不是普通备忘录，而是沉淀企业经营过程中的原因、背景、判断、风险和结果。

完成 Sprint006 后，CEO 可以新增一条企业记忆，例如：

> 2026年决定谨慎处理 Osprey 期货，原因是库存压力、香港价格、返点变化、代理风险。

这条记忆可以关联：

- 对象：品牌、供应商、门店、员工、项目
- 文件：合同、会议纪要、Excel、图片
- 知识：knowledge_items
- 时间轴：timeline_events

---

## 2. Core Principle

> Data tells what happened. Memory explains why it happened.

数据告诉企业发生了什么。

记忆解释企业为什么这样做。

---

## 3. Memory Types

至少支持以下记忆类型：

```text
decision        决策记忆
meeting         会议记忆
risk            风险记忆
strategy        战略记忆
operation       运营记忆
purchase        采购记忆
pricing         价格记忆
store           门店记忆
brand           品牌记忆
supplier        供应商记忆
```

---

## 4. Data Model

### 4.1 enterprise_memories 表

新增：

```text
enterprise_memories
```

字段建议：

```text
id
title
memory_type
summary
content
reason
decision
impact
risk_level
status
tags JSON
related_object_type
related_object_id
related_document_id
related_knowledge_id
related_timeline_event_id
created_by
occurred_at
created_at
updated_at
archived_at
```

说明：

- reason 用于记录为什么。
- decision 用于记录最终决定。
- impact 用于记录后续影响，可先为空。
- risk_level 支持 low / medium / high / critical。
- status 支持 draft / active / reviewed / archived。

### 4.2 memory_relations 表

可选但建议新增：

```text
memory_relations
```

字段：

```text
id
memory_id
target_type
target_id
relation_type
description
created_at
```

用于未来知识图谱。

---

## 5. UI Requirements

新增页面：

```text
/memory
/memories
```

页面名称：

```text
企业记忆
```

### 5.1 Memory Home

显示：

- 新建记忆按钮
- 记忆类型筛选
- 风险等级筛选
- 标签筛选
- 搜索框
- 最近记忆
- 决策记忆
- 风险记忆

### 5.2 Memory Create/Edit

表单字段：

- 标题
- 类型
- 摘要
- 内容
- 原因
- 决策
- 影响
- 风险等级
- 状态
- 标签
- 关联对象
- 关联文件
- 关联知识
- 发生时间

### 5.3 Memory Detail

详情页显示：

- 标题
- 类型
- 摘要
- 原因
- 决策
- 影响
- 风险等级
- 关联对象
- 关联文件
- 关联知识
- 相关时间轴
- 创建时间

---

## 6. API Requirements

新增或升级：

```text
GET    /api/memories
POST   /api/memories
GET    /api/memories/:id
PATCH  /api/memories/:id
DELETE /api/memories/:id 或归档
GET    /api/memory-types
GET    /api/objects/:id/memories
```

搜索应支持：

- title
- summary
- content
- reason
- decision
- tags

---

## 7. Timeline Integration

创建或更新记忆时，自动写入 timeline_events：

```text
memory_created
memory_updated
```

如果记忆关联对象，则写入该对象时间轴。

例如：

- KAILAS 品牌对象下出现“新增决策记忆”。
- 南山店对象下出现“新增运营记忆”。

---

## 8. Dashboard Integration

CEO Dashboard 中新增：

- 企业记忆总数
- 最近记忆
- 高风险记忆数量

核心入口加入：

```text
企业记忆 -> /memory
```

---

## 9. Search Integration

Global Search 必须搜索企业记忆：

- memory title
- summary
- content
- reason
- decision
- tags

搜索结果类型新增：

```text
memory
```

---

## 10. QA Acceptance

Sprint006 验收标准：

- /memory 页面可访问。
- 可以新建企业记忆。
- 可以编辑企业记忆。
- 可以查看企业记忆详情。
- 可以按类型和风险筛选。
- 可以关联对象。
- 可以关联文件或知识（若实现成本高，可先做对象和文件关联，知识关联保留字段）。
- 创建记忆后，对象时间轴出现 memory_created 事件。
- Dashboard 显示记忆摘要。
- Global Search 可以搜到记忆。
- 不破坏 Sprint001-005 功能。
- 烟测通过。

---

## 11. Codex Implementation Instruction

Codex 必须从 main 拉取最新代码。

严禁推倒重写。

只做增量升级。

不要开发 ai.vafox.com。

不要强制接入外部 AI API。

完成后提交代码并生成：

```text
SPRINT006_MEMORY_ENGINE_SUMMARY.md
```

总结必须包括：

- 新增数据表
- 新增 API
- 新增 UI
- Dashboard 集成
- Search 集成
- Timeline 集成
- 测试结果
- 已知限制
- 下一步建议
