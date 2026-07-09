# Sprint002: Object Engine｜企业对象引擎

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint001 FoxBrain Drive Foundation

---

## 1. Sprint Goal

建立 FoxBrain 的统一企业对象引擎。

FoxBrain 不再按零散页面开发，而是把企业中的所有核心实体统一建模为 Object。门店、员工、品牌、产品、供应商、客户、合同、文件、会议、任务都应该遵循同一套对象规范。

Sprint002 完成后，huyan.vafox.com 必须具备一个可用的「对象中心」，可以创建、查看、编辑、搜索企业核心对象，并能与 Sprint001 的 Documents / Drive 文件建立关联。

---

## 2. Product Principle

> Everything is an Object.

企业中所有有长期价值的信息，都应该成为对象。

对象不是普通资料页，而是企业数字生命体。每个对象都应支持：

- 基本资料
- 文件关联
- 图片/视频关联
- 标签
- AI 摘要占位
- 时间轴占位
- 关联对象占位
- 搜索
- 状态管理

---

## 3. First Object Types

Sprint002 至少实现以下核心对象类型：

```text
store       门店
employee    员工
brand       品牌
product     产品
supplier    供应商
customer    客户
contract    合同
project     项目
meeting     会议
task        任务
```

文件 document 已在 Sprint001 完成，Sprint002 要让 documents 可以关联到这些对象。

---

## 4. Object Center UI

新增或升级页面：

```text
/object-center
/objects
```

如果现有路由不同，请按项目现有规范命名，但菜单名称必须清晰显示为：

```text
对象中心
```

### 4.1 Object Center 首页

首页展示：

- 对象类型卡片
- 每类对象数量
- 最近更新对象
- 快速新建
- 搜索框
- 与 Drive 的关联入口

建议入口：

```text
门店
员工
品牌
产品
供应商
客户
合同
项目
会议
任务
```

### 4.2 Object List

每类对象列表应显示：

- 名称
- 类型
- 状态
- 标签
- 关联文件数量
- 更新时间
- 操作：查看 / 编辑 / 归档

### 4.3 Object Detail

对象详情页应包含：

1. 基本信息
2. AI 摘要占位
3. 关联文件
4. 关联对象占位
5. 时间轴占位
6. 标签
7. 备注

---

## 5. Data Model

### 5.1 enterprise_objects 表

建议新增统一表：

```text
enterprise_objects
```

字段建议：

```text
id
object_type
name
code
description
status
tags JSON
metadata JSON
ai_summary
created_by
created_at
updated_at
archived_at
```

说明：

- object_type 用于区分 store / employee / brand 等。
- metadata 用于保存不同对象类型的差异字段。
- 先统一表，后续必要时再拆分专项表。
- 不能破坏现有数据库。

### 5.2 object_relations 表

建议新增：

```text
object_relations
```

字段建议：

```text
id
source_object_type
source_object_id
target_object_type
target_object_id
relation_type
description
confidence
created_by
created_at
```

用于未来知识图谱。

### 5.3 documents 关联对象

Sprint001 documents 已有：

```text
related_object_type
related_object_id
```

Sprint002 要让 UI 可以把文件关联到对象。

---

## 6. API Requirements

新增或升级 API：

```text
GET    /api/objects
POST   /api/objects
GET    /api/objects/:id
PATCH  /api/objects/:id
DELETE /api/objects/:id 或 PATCH archived_at
GET    /api/objects/:id/documents
POST   /api/objects/:id/documents/:documentId/link
DELETE /api/objects/:id/documents/:documentId/unlink
GET    /api/object-types
```

如果已有 API 风格不同，请遵循现有风格。

---

## 7. Default Object Templates

为不同 object_type 提供基础字段模板。

### Store 门店

metadata 建议字段：

```text
address
area
opening_date
rent
manager
phone
```

### Employee 员工

```text
role
store
join_date
phone
status
```

### Brand 品牌

```text
brand_origin
supplier
website
positioning
main_categories
```

### Product 产品

```text
brand
sku
category
season
barcode
```

### Supplier 供应商

```text
contact_person
phone
wechat
payment_terms
```

### Customer 客户

```text
phone
wechat
level
source
```

---

## 8. AI Placeholder Requirements

暂时不要求完整 AI 推理，但必须预留：

- ai_summary 字段
- generateObjectSummary(objectId) 服务函数
- suggestRelations(objectId) 服务函数占位
- object timeline 数据结构占位

---

## 9. Integration With Drive

在 Drive 文件详情页增加：

```text
关联到对象
```

允许选择：

- 对象类型
- 对象名称

关联后，对象详情页能看到该文件。

---

## 10. QA Acceptance

Sprint002 验收标准：

- 首页可以进入对象中心。
- 能创建至少 6 类对象：门店、员工、品牌、产品、供应商、客户。
- 能查看对象列表。
- 能查看对象详情。
- 能编辑对象。
- 能归档对象。
- Drive 文件能关联到对象。
- 对象详情页能看到关联文件。
- 数据库迁移兼容旧数据。
- 不破坏 Sprint001 Drive 功能。
- 基础烟测通过。

---

## 11. Codex Implementation Instruction

Codex 必须先检查当前项目结构和 Sprint001 实现。

严禁推倒重写。

只做增量升级。

不要开发 ai.vafox.com。

完成后提交代码，并生成：

```text
SPRINT002_OBJECT_ENGINE_SUMMARY.md
```

总结内容包括：

- 改动文件
- 数据库变更
- API 列表
- UI 入口
- 测试结果
- 已知限制
- 下一步建议
