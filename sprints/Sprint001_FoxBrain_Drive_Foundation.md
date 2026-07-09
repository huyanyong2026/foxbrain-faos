# Sprint001: FoxBrain Drive Foundation

Status: Implemented locally
Target: huyan.vafox.com
Priority: P0

## Goal

Build FoxBrain Drive as the first usable enterprise knowledge entry.

The CEO should be able to upload documents, Excel files, images, videos and SAP exports. The system should store them safely, show them in a clear file center, and prepare them for AI processing.

## Product Requirements Implemented

- FoxBrain Drive entry at `/drive`
- Upload button and upload form
- File center list
- Categories
- File type filter
- Search box
- Processing status
- Recent files
- Processing queue
- Metadata stored in `documents`
- API layer for upload, list, detail, update, archive and reprocess

## Supported File Types

- PDF
- Word: doc, docx
- Excel: xls, xlsx, csv
- PowerPoint: ppt, pptx
- Images: jpg, jpeg, png, webp
- Videos: mp4, mov
- Audio: mp3, wav, m4a
- Text: txt, md
- Archive: zip

## Default Categories

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

## APIs

- `POST /api/drive/upload`
- `GET /api/drive/files`
- `GET /api/drive/files/:id`
- `GET /api/drive/files/:id/download`
- `DELETE /api/drive/files/:id`
- `PATCH /api/drive/files/:id`
- `POST /api/drive/files/:id/reprocess`
- `GET /api/drive/categories`

## Rollback

The sprint is additive. Rollback by reverting the Sprint001 commit. Existing upload and knowledge pages are not removed.
