# Sprint005: CEO Dashboard｜老板驾驶舱重构

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint001 Drive, Sprint002 Object Engine, Sprint003 Knowledge Pipeline, Sprint004 Search + Timeline

---

## 1. Sprint Goal

将 huyan.vafox.com 首页从“入口集合”升级为真正的 CEO Brain Dashboard。

目标：老板每天打开首页，30 秒内知道：

- 最近新增了什么资料
- 哪些文件正在处理
- 企业对象数量与变化
- 最近知识更新
- 最近时间轴事件
- 今日重点入口
- 可以直接搜索整个企业

首页不是复杂报表，而是老板每天的企业第二大脑入口。

---

## 2. Core Principle

> CEO Dashboard should help the CEO think, not overwhelm the CEO with charts.

不要堆满图表。

首页应当清晰、安静、聚焦，体现 VAFOX Enterprise Brain 的定位。

---

## 3. Dashboard Layout

建议首页结构：

```text
VAFOX Enterprise Brain
早上好，呼总。

[全局搜索框：搜索门店、品牌、产品、合同、文件、知识……]

今日摘要
- 新上传文件
- 已处理知识
- 待处理文件
- 新增对象
- 最新时间轴事件

核心入口
- VAFOX Drive
- 对象中心
- 知识中心
- 全局搜索
- 企业时间轴
- AI问企业（占位）

最近动态
- 最近文件
- 最近对象
- 最近知识
- 最近时间轴

系统状态
- Drive 正常
- Object Engine 正常
- Knowledge Pipeline 正常
- Search 正常
- Timeline 正常
```

---

## 4. Dashboard Data API

新增或升级：

```text
GET /api/dashboard/ceo
```

返回建议：

```json
{
  "summary": {
    "documents_total": 0,
    "documents_pending": 0,
    "documents_processed": 0,
    "objects_total": 0,
    "knowledge_items_total": 0,
    "timeline_events_total": 0
  },
  "recent_documents": [],
  "recent_objects": [],
  "recent_knowledge": [],
  "recent_timeline": [],
  "system_status": []
}
```

---

## 5. UI Requirements

### 5.1 Top Section

显示：

```text
VAFOX Enterprise Brain
企业第二大脑
```

并提供全局搜索框。

### 5.2 CEO Summary Cards

卡片建议：

- 文件总数
- 待处理文件
- 企业对象
- 知识条目
- 时间轴事件

### 5.3 Core Entry Cards

入口必须包含：

- VAFOX Drive -> /drive
- 对象中心 -> /object-center or /objects
- 知识中心 -> /knowledge
- 全局搜索 -> /search
- 企业时间轴 -> /timeline or object timeline entry
- AI问企业 -> placeholder, future Sprint

### 5.4 Recent Activity

显示最近：

- 上传文件
- 创建对象
- 生成知识
- 时间轴事件

---

## 6. System Status

首页显示基础模块状态：

```text
Drive Engine
Object Engine
Knowledge Engine
Search Engine
Timeline Engine
```

状态可先基于数据库/API是否可查询实现，不要求复杂健康检查。

---

## 7. Keep Existing Entry Usability

如果首页已有十大入口，不要粗暴删除。

可以重构为“核心入口 + 更多入口”。

必须保证现有已上线入口仍可访问。

---

## 8. QA Acceptance

Sprint005 验收标准：

- 首页显示 VAFOX Enterprise Brain 定位。
- 首页有全局搜索框。
- 首页展示 Drive / Object / Knowledge / Search / Timeline 核心入口。
- 首页展示文件、对象、知识、时间轴摘要数据。
- 首页展示最近文件、最近对象、最近知识、最近时间轴。
- /api/dashboard/ceo 可用。
- 不破坏 Sprint001-004 功能。
- 烟测通过。

---

## 9. Codex Implementation Instruction

Codex 必须从 main 拉取最新代码。

严禁推倒重写。

只做增量升级。

不要开发 ai.vafox.com。

不要强制接入外部 AI API。

完成后提交代码并生成：

```text
SPRINT005_CEO_DASHBOARD_SUMMARY.md
```

总结必须包括：

- 首页改动
- Dashboard API
- 数据来源
- UI入口
- 测试结果
- 已知限制
- 下一步建议
