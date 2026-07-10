# Sprint019.2: AI Connected Enterprise Drive｜企业AI网盘

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint019 / Sprint019.1

---

## 1. Sprint Goal

Upgrade FoxBrain Drive from a basic upload area into a business-grade enterprise file system that feels as easy to use as a mainstream cloud drive, while ensuring every file can be understood, indexed, linked, searched, cited, and used by FoxBrain AI.

Target experience:

```text
上传 / 拖拽 / 新建文件夹
↓
像网盘一样浏览、预览、搜索、移动、重命名、下载
↓
AI自动识别内容、摘要、分类、提取对象和时间
↓
关联门店 / 品牌 / 产品 / 员工 / 顾客 / 供应商 / 项目
↓
进入 Knowledge / Memory / Graph / Copilot
↓
任何 AI 回答都可回到原始文件和具体页码/段落
```

The user must feel that this is first a reliable enterprise drive, and second an AI-connected knowledge system.

---

## 2. Product Principles

1. Easy like a consumer cloud drive.
2. Traceable like an enterprise archive.
3. Connected like a knowledge graph.
4. Searchable by both filename and meaning.
5. AI must cite original files; no unsupported claims.
6. Original files must never be silently overwritten or deleted.
7. File storage, metadata, AI extraction, and knowledge objects must remain separable.
8. Large-file processing must be asynchronous and visible.
9. Permissions must be respected by AI retrieval.
10. Mobile upload and preview must work for common file types.

---

## 3. Drive UX Requirements

### 3.1 Main Page

Route:

```text
/drive
```

Must provide:

- Left folder tree.
- Main file list area.
- Breadcrumb navigation.
- Grid and list view.
- Sort by name, upload time, modified time, size, type, AI status.
- Search box.
- Filter by file type, owner, business object, AI processing status, date.
- Upload button.
- New folder button.
- Multi-select.
- Batch move, download, archive, tag, and delete-to-trash.
- Recent files.
- Starred files.
- Shared / team files foundation.
- Trash.

Do not show technical database language on the normal user interface.

### 3.2 File Operations

Support:

- Upload one or multiple files.
- Drag and drop.
- Folder upload when supported.
- Create folder.
- Rename.
- Move.
- Copy.
- Download.
- Star / unstar.
- Archive.
- Soft delete to trash.
- Restore from trash.
- Permanent delete only with explicit second confirmation and authorization.
- Duplicate detection by hash.
- Version upload instead of silent overwrite.

### 3.3 Upload Experience

Upload panel must show:

- Filename.
- File size.
- Upload progress.
- Upload result.
- Duplicate warning.
- AI indexing state.
- Retry button.
- Cancel button where possible.

Upload must not freeze the page.

### 3.4 Preview

Clicking a file must open a file detail / preview page or drawer.

Supported preview priority:

1. PDF
2. Images
3. TXT / Markdown
4. Word documents
5. Excel / CSV
6. PowerPoint
7. Audio metadata and transcript when available
8. Video metadata, poster, and transcript when available
9. Unsupported file type: show metadata and download option

Preview must never require the user to download first when the format can be safely rendered.

### 3.5 File Detail

Route example:

```text
/drive/files/{id}
```

Show:

- Original filename.
- Current filename.
- Folder path.
- File type.
- Size.
- Hash.
- Upload time.
- Modified time.
- Uploader.
- Version history.
- AI processing status.
- AI summary.
- Extracted keywords.
- Extracted dates.
- Related objects.
- Related knowledge.
- Related memories.
- Related decisions.
- Related conversations.
- Source / lineage.
- Open, download, move, rename, add tag, archive actions.

---

## 4. AI Connection Requirements

Every eligible file should pass through an asynchronous AI connection pipeline:

```text
Original File
↓
Metadata Extraction
↓
Text / Table / Media Extraction
↓
Chunking
↓
Classification
↓
Entity Detection
↓
Business Object Suggestions
↓
Knowledge Drafts
↓
Graph Relationship Suggestions
↓
Search Index
↓
Copilot Retrieval
```

### 4.1 AI Processing States

Use user-friendly statuses:

- Waiting
- Reading
- Understanding
- Ready for AI
- Needs confirmation
- Failed
- Unsupported

Technical error detail belongs in system management, not the main user view.

### 4.2 AI Summary

For supported files generate:

- One-sentence summary.
- Short executive summary.
- Key facts.
- Important dates.
- Important amounts.
- Named business entities.
- Risks / obligations when relevant.
- Suggested business-object links.

Do not publish uncertain extraction as confirmed fact.

### 4.3 Business Object Linking

Files can be linked to one or many:

- Store
- Brand
- Product
- Supplier
- Employee
- Customer
- Project
- Contract
- Decision
- Meeting
- Other enterprise object

Automatic detection should create suggestions, not silently create business objects.

### 4.4 Ask This File

File detail page must include:

```text
Ask this file
```

Questions must use only the current file plus explicitly permitted linked context.

Answers must include evidence such as:

- page number
- sheet name
- row range
- paragraph / chunk reference
- timestamp for audio / video transcript

If the file does not contain the answer, respond clearly that the file does not provide enough evidence.

### 4.5 Ask This Folder

Folder page should support:

```text
Ask this folder
```

The answer must cite specific files and locations.

### 4.6 Copilot Integration

Enterprise Copilot must be able to retrieve Drive content while respecting:

- user permissions
- folder permissions
- archive / trash state
- AI-ready status
- source freshness
- object links

Copilot evidence cards must open the source file directly at the relevant page / sheet / chunk when possible.

---

## 5. Data Model

Add or extend tables similar to:

```text
drive_folders
drive_files
drive_file_versions
drive_file_tags
drive_file_tag_links
drive_file_permissions
drive_file_processing_jobs
drive_file_extractions
drive_file_chunks
drive_file_object_links
drive_file_link_suggestions
drive_file_ai_summaries
drive_file_events
drive_file_shares
drive_trash_records
```

Important fields for `drive_files`:

```text
id
folder_id
original_name
current_name
storage_key
mime_type
extension
size_bytes
content_hash
status
ai_status
owner_id
uploaded_by
created_at
updated_at
archived_at
deleted_at
current_version_id
```

Important fields for versions:

```text
id
file_id
version_number
storage_key
content_hash
size_bytes
uploaded_by
created_at
change_note
```

Original versions must be preserved according to retention rules.

---

## 6. Search Requirements

Global Drive search must support:

### Exact Search

- filename
- folder name
- tag
- uploader
- object name
- date
- file type

### Semantic Search

Examples:

- 南山店租赁合同
- Osprey返点文件
- 2025年品牌合作政策
- 员工提成方案
- Kailas销售分析

Search results must show why the file matched:

- filename match
- tag match
- object relation
- content excerpt
- semantic similarity

Search must not expose files the user lacks permission to access.

---

## 7. File-Type Intelligence

### PDF / Word

- extract headings and paragraphs
- preserve page references when available
- detect contracts, reports, policies, manuals

### Excel / CSV

- show sheet list
- preview table
- detect headers
- preserve sheet and row lineage
- allow "Ask this sheet"
- large spreadsheets use sampling and structured import rather than loading everything into browser

### Images

- preview
- metadata
- AI caption
- business-object suggestion
- optional text extraction

### Audio / Video

- preserve original file
- store duration and metadata
- asynchronous transcript when configured
- transcript timestamps
- AI summary and key topics

Do not block normal file use while AI processing is incomplete.

---

## 8. Knowledge, Memory, Graph Integration

Files should not automatically become approved knowledge or memory.

Correct flow:

```text
File
↓
AI extraction
↓
Knowledge draft / Memory draft / Object link suggestion
↓
Human review where required
↓
Approved asset
```

Knowledge Graph links must retain source file and extraction evidence.

Examples:

```text
合同文件 → relates_to → 南山店
品牌政策 → governs → Osprey
会议纪要 → supports → Decision
员工培训文档 → applies_to → Employee Role
```

---

## 9. Permissions and Security

Implement permission foundation:

- Owner
- Administrator
- Department / group
- Specific user
- Read
- Upload
- Edit metadata
- Move
- Download
- Share
- Delete
- AI access

AI retrieval permission must never exceed file access permission.

Security requirements:

- Never store secrets in GitHub.
- Validate file type and size.
- Sanitize filenames.
- Prevent path traversal.
- Use content hash.
- Virus / malware scan integration point.
- Signed or protected download URLs when architecture supports it.
- Audit file actions.
- Soft delete by default.
- Backup before production migration.

---

## 10. Performance Requirements

- Paginated file list.
- Lazy folder tree.
- Thumbnail generation asynchronously.
- Chunked or resumable upload foundation for large files.
- Background AI processing queue.
- Avoid synchronous full-document AI processing in web request.
- Cache safe previews and summaries.
- Show progress rather than a frozen page.

Initial practical acceptance:

- 1,000+ files remain usable.
- Common folder navigation feels immediate.
- Upload progress is visible.
- Preview does not block the whole app.
- AI processing can retry independently.

---

## 11. UI Routes

Required:

```text
/drive
/drive/recent
/drive/starred
/drive/shared
/drive/trash
/drive/folders/{id}
/drive/files/{id}
/drive/search
/drive/processing
```

System management routes may include:

```text
/system/drive/storage
/system/drive/processing
/system/drive/security
/system/drive/audit
```

---

## 12. API Requirements

At minimum:

```text
GET    /api/drive/folders
POST   /api/drive/folders
PATCH  /api/drive/folders/{id}
POST   /api/drive/folders/{id}/move

GET    /api/drive/files
POST   /api/drive/files/upload
GET    /api/drive/files/{id}
PATCH  /api/drive/files/{id}
POST   /api/drive/files/{id}/move
POST   /api/drive/files/{id}/copy
POST   /api/drive/files/{id}/star
POST   /api/drive/files/{id}/archive
DELETE /api/drive/files/{id}
POST   /api/drive/files/{id}/restore
GET    /api/drive/files/{id}/download
GET    /api/drive/files/{id}/preview
GET    /api/drive/files/{id}/versions
POST   /api/drive/files/{id}/versions

GET    /api/drive/search
GET    /api/drive/processing
POST   /api/drive/files/{id}/reprocess
GET    /api/drive/files/{id}/ai-summary
POST   /api/drive/files/{id}/ask
POST   /api/drive/folders/{id}/ask
GET    /api/drive/files/{id}/links
POST   /api/drive/files/{id}/links
```

Use existing project conventions where reasonable.

---

## 13. Migration Requirements

Existing uploaded documents must not be lost.

Migration must:

1. Inventory existing files.
2. Map existing document records into Drive records.
3. Preserve original storage paths.
4. Compute hashes where safe.
5. Keep old URLs compatible or redirect.
6. Mark AI status correctly.
7. Avoid duplicate records.
8. Generate a migration report.
9. Support rollback.

---

## 14. Mobile UX

Mobile must support:

- photo upload
- document upload
- recent files
- folder navigation
- preview
- ask this file
- star
- download
- share foundation

Avoid desktop-only multi-column layouts that become unusable on phone.

---

## 15. Acceptance Tests

Must validate:

- Create nested folders.
- Upload PDF, image, Word, Excel, CSV, and unsupported sample.
- Multi-file upload.
- Duplicate upload warning.
- Rename and move.
- Version upload.
- Preview supported files.
- Download original.
- Soft delete and restore.
- AI status progression.
- AI summary generation.
- Ask this file with evidence.
- Ask this folder with evidence.
- Link file to brand / store / product.
- Copilot retrieves permitted file evidence.
- Copilot cannot retrieve unauthorized file.
- Search by filename and meaning.
- Existing documents remain available after migration.
- Mobile upload and preview.
- No production SAP write access.
- No ai.vafox.com development.

---

## 16. Production Rollout

Before deployment:

- backup production code
- backup database
- backup / inventory existing uploaded files
- verify storage capacity
- verify upload size limits
- verify reverse proxy limits
- verify permissions
- run migration dry-run

Deploy incrementally.

Do not permanently delete any original uploaded file during migration.

---

## 17. Deliverables

Generate:

```text
SPRINT019_2_AI_CONNECTED_ENTERPRISE_DRIVE_SUMMARY.md
SPRINT019_2_AI_CONNECTED_ENTERPRISE_DRIVE_TEST_REPORT.md
SPRINT019_2_DRIVE_MIGRATION_REPORT.md
SPRINT019_2_AI_EVIDENCE_AUDIT_REPORT.md
SPRINT019_2_DRIVE_SECURITY_REPORT.md
SPRINT019_2_MOBILE_UX_TEST_REPORT.md
SPRINT019_2_PRODUCTION_DEPLOYMENT_REPORT.md
```

Summary must include:

- architecture
- tables
- storage model
- routes and APIs
- supported previews
- AI pipeline
- object linking
- knowledge / memory / graph integration
- permissions
- migration result
- performance result
- known limitations

---

## 18. Safety Boundary

- Do not connect SAP write permissions.
- Do not modify production SAP.
- Do not develop ai.vafox.com.
- Do not delete original enterprise files.
- Do not auto-approve uncertain AI knowledge.
- Do not expose unauthorized files to Copilot.
- Do not place secrets in repository.
- Do not replace the existing system with an unrelated rewrite.

---

## 19. Codex Execution Instruction

Implement this Sprint from latest main on branch:

```text
sprint019-2-ai-connected-enterprise-drive
```

First inspect current document / upload implementation and produce a short pre-upgrade inventory in the summary.

Use incremental migration. Keep existing file access working.

Prioritize in this order:

1. Reliable folder and file operations.
2. Preview and open experience.
3. Migration of existing files.
4. AI processing status and summary.
5. Ask this file / folder with evidence.
6. Object links and Copilot retrieval.
7. Permissions foundation.
8. Mobile and performance polish.
9. Production deployment with backup and rollback.
