# Sprint004: Global Search + Enterprise Timeline｜全局搜索与企业时间轴

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint001 Drive, Sprint002 Object Engine, Sprint003 Knowledge Pipeline

---

## 1. Sprint Goal

让 VAFOX 从“能存文件、能建对象、能生成知识”升级为“能统一搜索企业全部信息，并为每个对象形成时间轴”。

Sprint004 完成后，CEO 可以在一个搜索框中搜索：

- 文件
- 企业对象
- 知识条目
- 文档切片
- 标签
- 分类
- AI 摘要

同时，每个对象详情页应出现初版 Enterprise Timeline，用于记录该对象相关文件、知识、创建、更新和关联事件。

---

## 2. Core Principle

> VAFOX 不是文件柜，而是企业记忆系统。

全局搜索解决“找得到”。

时间轴解决“记得住”。

---

## 3. Global Search Requirements

### 3.1 Search Entry

新增或升级全局搜索入口：

```text
/search
```

并在首页、Drive、Object Center、Knowledge 页面提供明显搜索入口。

搜索框占位建议：

```text
搜索门店、品牌、产品、合同、文件、知识……
```

### 3.2 Search Scope

必须至少搜索：

```text
documents.filename
documents.original_filename
documents.category
documents.tags
documents.ai_summary
documents.extracted_text
enterprise_objects.name
enterprise_objects.description
enterprise_objects.tags
enterprise_objects.ai_summary
enterprise_objects.metadata
knowledge_items.title
knowledge_items.content
knowledge_items.summary
knowledge_items.tags
document_chunks.content
```

### 3.3 Search Result Types

搜索结果必须区分类型：

```text
file
object
knowledge
chunk
```

每条结果显示：

- 类型图标
- 标题
- 摘要/命中内容
- 来源
- 关联对象
- 更新时间
- 点击进入详情

### 3.4 Filters

提供基础筛选：

- 类型：文件 / 对象 / 知识 / 文档片段
- 分类
- 对象类型
- 处理状态
- 时间范围

不要求复杂高级搜索，但架构要可扩展。

---

## 4. Search API

新增或升级：

```text
GET /api/search?q=
GET /api/search/suggestions?q=
```

返回结构建议：

```json
{
  "query": "KAILAS",
  "total": 12,
  "results": [
    {
      "type": "object",
      "id": "...",
      "title": "KAILAS",
      "snippet": "品牌对象...",
      "url": "/objects/...",
      "score": 0.9,
      "updated_at": "..."
    }
  ]
}
```

---

## 5. Enterprise Timeline Requirements

### 5.1 timeline_events 表

新增统一时间轴表：

```text
timeline_events
```

字段建议：

```text
id
entity_type
entity_id
event_type
title
description
source_type
source_id
metadata JSON
created_by
occurred_at
created_at
```

说明：

- entity_type/entity_id 表示时间轴属于哪个对象。
- source_type/source_id 表示事件来源，例如 document、knowledge_item、system、manual。
- occurred_at 表示事件真实发生时间。

### 5.2 Event Types

至少支持：

```text
object_created
object_updated
document_linked
knowledge_created
manual_note
system_event
```

### 5.3 Auto Events

自动生成以下事件：

- 新建对象 → object_created
- 编辑对象 → object_updated
- 文件关联对象 → document_linked
- 文档生成 knowledge_items → knowledge_created

### 5.4 Object Detail Timeline

在对象详情页增加：

```text
企业时间轴
```

显示：

- 时间
- 事件类型
- 标题
- 描述
- 来源链接

---

## 6. Timeline API

新增或升级：

```text
GET  /api/timeline?entity_type=&entity_id=
POST /api/timeline
GET  /api/objects/:id/timeline
```

允许手动添加一条时间轴备注：

```text
manual_note
```

---

## 7. UI Requirements

### 7.1 Search Page

页面结构：

```text
Global Search
[ 搜索框 ]
[类型筛选] [分类筛选] [时间范围]

Results
- Object result
- File result
- Knowledge result
- Chunk result
```

### 7.2 Timeline Panel

对象详情页中增加 Timeline Panel。

如果没有事件，显示：

```text
暂无时间轴事件。随着文件、知识和经营记录增加，这里会自动形成企业记忆。
```

---

## 8. QA Acceptance

Sprint004 验收标准：

- /search 页面可访问。
- 可以搜索到 documents。
- 可以搜索到 enterprise_objects。
- 可以搜索到 knowledge_items。
- 可以搜索到 document_chunks。
- 搜索结果可点击进入对应详情。
- 对象详情页出现时间轴面板。
- 新建对象会生成时间轴事件。
- 文件关联对象会生成时间轴事件。
- 文档处理生成知识后可生成知识事件或在对象关联时出现。
- 不破坏 Sprint001、Sprint002、Sprint003 功能。
- 烟测通过。

---

## 9. Codex Implementation Instruction

Codex 必须先从 main 拉取最新代码。

严禁推倒重写。

只做增量升级。

不要开发 ai.vafox.com。

不要强制接入外部 AI API。

完成后提交代码，并生成：

```text
SPRINT004_GLOBAL_SEARCH_TIMELINE_SUMMARY.md
```

总结必须包括：

- 新增数据表
- 新增 API
- 新增 UI
- 搜索范围
- 自动时间轴事件
- 测试结果
- 已知限制
- 下一步建议
