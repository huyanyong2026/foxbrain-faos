# Sprint019.2 AI Connected Enterprise Drive Summary

## Scope

Sprint019.2 upgrades the existing VAFOX Drive upload center into an AI connected enterprise drive on the current `huyan.vafox.com` portal. This is an incremental upgrade only. It does not add SAP write access, does not modify production SAP, and does not develop `ai.vafox.com`.

## Pre-upgrade inventory

- Existing runtime: single Python portal service, `firefox-portal.service`.
- Existing production directory: `/opt/firefox-portal`.
- Existing upload roots: `/opt/firefox-portal/uploads`, including `drive`, `stores`, `products`, `employees`, and `knowledge`.
- Existing production uploaded files: 14 files found in upload inventory before deployment.
- Existing Drive foundations: `documents`, `document_chunks`, `knowledge_items`, file upload, basic AI extraction, summary, and Knowledge Pipeline.

## Architecture

The upgraded Drive now uses:

- `documents` as the canonical file record.
- `drive_folders` for folder hierarchy.
- `drive_file_versions` for immutable version history.
- `drive_file_processing_jobs`, `drive_file_extractions`, `drive_file_chunks`, and `drive_file_ai_summaries` for AI processing state and evidence.
- `drive_file_object_links` and `drive_file_link_suggestions` for business object linking.
- `drive_file_permissions` and `drive_visibility` for permission foundation.
- `drive_file_events` and `drive_trash_records` for audit and soft delete.

## Main routes

- `/drive`
- `/drive/recent`
- `/drive/starred`
- `/drive/shared`
- `/drive/trash`
- `/drive/search`
- `/drive/folders/{id}`
- `/drive/files/{id}`

## APIs

- `GET /api/drive/files`
- `GET /api/drive/files/{id}`
- `GET /api/drive/files/{id}/download`
- `GET /api/drive/categories`
- `POST /api/drive/upload`
- `POST /api/drive/folders`
- `POST /api/drive/files/{id}/rename`
- `POST /api/drive/files/{id}/move`
- `POST /api/drive/files/{id}/star`
- `POST /api/drive/files/{id}/unstar`
- `POST /api/drive/files/{id}/delete`
- `POST /api/drive/files/{id}/restore`
- `POST /api/drive/files/{id}/reprocess`

## Supported previews

- Image preview: jpg, jpeg, png, gif, webp.
- PDF preview: browser iframe.
- Text preview: txt, md, csv, tsv, json, log.
- Office files: original saved, download and AI summary available; full online rendering remains a known future integration.

## Safety

- Original files are not deleted.
- New uploads use UUID storage names and do not silently overwrite.
- Content hash is saved for duplicate detection.
- Duplicate files are accepted but return a duplicate warning and keep both records.
- Soft delete moves files to Drive trash and records audit data.
- Existing files are migrated by metadata only; physical files remain in place.

