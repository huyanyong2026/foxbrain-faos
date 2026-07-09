# Sprint001: FoxBrain Drive Foundation

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0

---

## 1. Goal

Build FoxBrain Drive as the first usable enterprise knowledge entry.

The CEO should be able to upload documents, Excel files, images, videos and SAP exports. The system should store them safely, show them in a clear file center, and prepare them for AI processing.

## 2. Product Requirements

### 2.1 Drive Home

Create a main entry called **FoxBrain Drive**.

It should show:

- upload button
- drag-and-drop upload area
- recent files
- folders / categories
- file type filter
- search box
- processing status

### 2.2 Supported File Types

Support at minimum:

- PDF
- Word: doc, docx
- Excel: xls, xlsx, csv
- PowerPoint: ppt, pptx
- Images: jpg, jpeg, png, webp
- Videos: mp4, mov
- Audio: mp3, wav, m4a
- Text: txt, md
- Archive: zip

### 2.3 File Metadata

For every uploaded file, store:

- id
- original filename
- storage path
- mime type
- file size
- extension
- upload time
- uploader
- category
- tags
- processing status
- related object type
- related object id
- AI summary
- extracted text path or field
- version number

### 2.4 Default Categories

Create default categories:

- 门店库
- 员工库
- 品牌库
- 产品库
- 供应商库
- 客户库
- 合同库
- 财务库
- 销售库
- 库存库
- 采购库
- 培训资料库
- 内容素材库
- 会议纪要库
- SAP数据
- 未分类文件库

### 2.5 Upload Flow

After upload:

```text
File uploaded
↓
Save file
↓
Create document record
↓
Detect file type
↓
Assign default category
↓
Set processing_status = pending
↓
Show in Drive
```

### 2.6 AI Processing Placeholder

If AI processing is not fully ready, create the pipeline interface now:

- pending
- processing
- completed
- failed

Create placeholder service functions:

- extractText(file)
- generateSummary(text)
- generateTags(text)
- classifyFile(metadata, text)
- linkToObject(metadata, text)

These can be simple placeholders first, but the architecture must be ready.

## 3. UI Requirements

### 3.1 CEO Friendly

The interface must be simple. Do not make it look like a complex admin backend.

Suggested layout:

```text
FoxBrain Drive
企业所有资料的入口

[Upload Files] [Upload Folder] [Import SAP Export]

Search...

Categories
Recent Files
Processing Queue
```

### 3.2 File Card

Each file card or row should show:

- file icon
- filename
- category
- upload time
- size
- processing status
- AI summary status
- related object if available

## 4. Backend Requirements

Create or update APIs:

- POST /api/drive/upload
- GET /api/drive/files
- GET /api/drive/files/:id
- DELETE /api/drive/files/:id
- PATCH /api/drive/files/:id
- POST /api/drive/files/:id/reprocess

## 5. Database Requirements

Create table or model: `documents`.

Suggested fields:

```text
id
filename
original_filename
file_path
mime_type
extension
size_bytes
category
tags JSON
processing_status
ai_summary
extracted_text
related_object_type
related_object_id
version
created_by
created_at
updated_at
```

If the project already has a database schema, adapt to existing style and do not break existing data.

## 6. QA Acceptance

Sprint001 is accepted when:

- CEO can open FoxBrain Drive from homepage.
- User can upload at least PDF, Excel, image and Word files.
- Uploaded files appear in list.
- File metadata is stored.
- Files have categories.
- Processing status is visible.
- File can be opened or downloaded.
- File can be deleted or archived.
- API errors are handled.
- No existing pages are broken.

## 7. Codex Instruction

Codex must inspect the existing codebase first.

Do not rewrite the whole project.

Upgrade in-place.

Keep huyan.vafox.com focused on CEO Brain.

Do not implement ai.vafox.com.

## 8. Deliverables

- working Drive page
- upload API
- document database model
- file list UI
- file metadata management
- processing status architecture
- updated README or implementation notes
