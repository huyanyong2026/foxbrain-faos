# Sprint003: Knowledge Pipeline｜企业知识流水线

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint001 VAFOX Drive, Sprint002 Object Engine

---

## 1. Sprint Goal

让 VAFOX Drive 中上传的文件，真正变成 AI 可以搜索、总结、引用和未来问答的企业知识。

Sprint003 不要求一次完成真正大模型推理，但必须建立完整的知识流水线架构：

```text
Document
↓
Extract Text
↓
Chunk
↓
Summary
↓
Tags
↓
Knowledge Records
↓
Search Index
↓
Ready for AI Q&A
```

---

## 2. Core Principle

> 文件不是终点，知识才是终点。

VAFOX Drive 负责存文件；Knowledge Pipeline 负责把文件变成企业知识资产。

---

## 3. Data Model

### 3.1 knowledge_items 表

新增：

```text
knowledge_items
```

字段建议：

```text
id
document_id
object_type
object_id
title
content
summary
tags JSON
source_type
source_path
chunk_index
confidence
status
created_at
updated_at
```

### 3.2 document_chunks 表

新增：

```text
document_chunks
```

字段建议：

```text
id
document_id
chunk_index
content
token_count
summary
embedding_status
metadata JSON
created_at
updated_at
```

如项目不支持 token 统计，可先用字符长度替代。

---

## 4. Processing Status

Documents 处理状态至少支持：

```text
pending
extracting
chunking
summarizing
indexed
failed
```

---

## 5. Text Extraction

根据文件类型实现基础文本提取：

- txt / md / csv：直接读取文本
- PDF：优先用可用库提取文本，如暂时困难可保留占位并记录 unsupported
- docx：提取正文文本
- xlsx / xls：提取 sheet 文本和表格内容
- 图片 / 视频 / 音频：先建立 OCR/ASR 占位，不要求完全实现

要求：

- 不能因某个文件提取失败导致系统崩溃
- 失败要记录 failed reason
- 原始文件必须保留

---

## 6. Chunking Rule

将 extracted_text 切分成 chunks。

建议：

- 每段 800-1200 中文字符
- 保留 chunk_index
- 保留 document_id
- 内容太短则只生成 1 个 chunk

---

## 7. Summary and Tags

先实现规则型或占位型摘要：

- summary：取前 300-500 字生成基础摘要
- tags：根据文件名、分类、对象、关键词生成

未来再接入 DeepSeek / OpenAI API。

不要在 Sprint003 强制依赖外部 API。

---

## 8. Knowledge UI

新增或升级页面：

```text
/knowledge
```

页面显示：

- 知识总数
- 已处理文件数
- 失败文件数
- 最近知识
- 可搜索知识
- 按对象筛选
- 按分类筛选

### Knowledge Detail

每条知识可以查看：

- 来源文件
- 来源对象
- chunk 内容
- 摘要
- 标签
- 创建时间

---

## 9. Drive Integration

在 Drive 文件详情页增加：

```text
知识处理结果
```

显示：

- 提取文本状态
- chunk 数量
- knowledge_items 数量
- 处理失败原因
- 重新处理按钮

---

## 10. API Requirements

新增或升级：

```text
POST /api/knowledge/process-document/:documentId
GET  /api/knowledge/items
GET  /api/knowledge/items/:id
GET  /api/knowledge/search?q=
GET  /api/documents/:id/chunks
POST /api/documents/:id/reprocess
```

遵循现有项目 API 风格，不强制路径完全一致。

---

## 11. Search Requirement

实现基础全文搜索：

- 文件名
- extracted_text
- knowledge_items.content
- tags
- object name if available

不要求向量搜索，但必须预留 embedding_status 字段。

---

## 12. QA Acceptance

Sprint003 验收标准：

- 上传 txt/md/csv/xlsx/docx 后可以生成 extracted_text 或 knowledge_items。
- 文件详情能显示处理结果。
- /knowledge 页面可访问。
- 能搜索知识内容。
- 处理失败不会影响系统稳定。
- 能手动重新处理某个文件。
- knowledge_items 和 document_chunks 数据表正常创建。
- 不破坏 Sprint001 Drive 和 Sprint002 Object Engine。
- 烟测通过。

---

## 13. Codex Implementation Instruction

Codex 必须先检查现有 Sprint001 和 Sprint002 的实现。

严禁推倒重写。

只做增量升级。

不要开发 ai.vafox.com。

不要强制接入外部 AI API。

完成后提交代码，并生成：

```text
SPRINT003_KNOWLEDGE_PIPELINE_SUMMARY.md
```

总结必须包括：

- 数据库变更
- 新增 API
- 新增 UI
- 支持的文件类型
- 当前不能处理的类型
- 测试结果
- 下一步建议
