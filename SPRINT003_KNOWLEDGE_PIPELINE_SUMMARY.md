# Sprint003 Knowledge Pipeline Summary

## Scope

Sprint003 upgrades the existing huyan.vafox.com codebase incrementally. It keeps Sprint001 Drive and Sprint002 Object Engine available, does not build ai.vafox.com, and does not require any external AI API.

## Database Changes

Compatible schema updates:

- Added `document_chunks`
  - `id`, `document_id`, `chunk_index`, `content`, `token_count`, `summary`, `embedding_status`, `metadata`, `created_at`, `updated_at`
- Extended `knowledge_items`
  - `document_id`, `content`, `source_path`, `chunk_index`, `confidence`
- Extended `documents`
  - `processing_error`

Existing tables remain in use:

- `documents`
- `knowledge_items`
- `knowledge_chunks`
- `enterprise_objects`

## New API

- `POST /api/knowledge/process-document/:documentId`
- `GET /api/knowledge/items`
- `GET /api/knowledge/items/:id`
- `GET /api/knowledge/search?q=`
- `GET /api/documents/:id/chunks`
- `POST /api/documents/:id/reprocess`

Existing Drive reprocess is also connected to the same pipeline:

- `POST /api/drive/files/:id/reprocess`

## New UI

- `/knowledge` is upgraded into the Knowledge Pipeline page.
- `/knowledge/view?id=` shows knowledge details, summaries, source context and chunks.
- `/drive` continues to work and uploaded files now run through the Knowledge Pipeline.
- `/api/drive/files/:id` returns `knowledge_processing` metrics.

## Processing Flow

Implemented local, rule-based processing:

```text
Document
-> Extract Text
-> Chunk
-> Summary
-> Tags
-> Knowledge Records
-> Search Index
-> Ready for AI Q&A
```

## Supported File Types

Text extraction supports:

- `txt`
- `md`
- `csv`
- `json`
- `docx`
- `xlsx`
- `xls`
- `pdf` when the local PDF library is available

## Current Unsupported or Placeholder Types

The system records a failed processing reason instead of crashing:

- images: OCR placeholder
- video/audio: ASR placeholder
- unsupported PDFs when no local extraction library is available
- legacy Office formats when no local parser is available

## Test Results

Passed on local branch `sprint003-knowledge-pipeline`:

- Python compile check: `portal_v2.py` and `tests/v6_smoke_check.py`
- Smoke checks: `tests/v6_smoke_check.py`, 109 tests, 0 failures

## Next Step

Sprint004 should connect the Knowledge Pipeline output with Object Engine relationships and a lightweight citation layer for AI Q&A.
