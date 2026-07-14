# Task003: Knowledge Engine and AI Query Foundation

## Status

Completed as a foundation upgrade.

## Scope

Task003 upgrades VAFOX from basic file storage to an AI-ready enterprise knowledge system.

## Delivered

- Knowledge Item model expanded with source, object relation, summary, keywords, status, visibility, and embedding fields.
- Document-to-Knowledge pipeline added to upload flow.
- Chunk model added for future vector search and citation answers.
- Summary, keyword, auto tag, manual tag, and embedding status placeholders added.
- AI Query Center V1 added with safe answer structure.
- Citation-ready response model prepared.
- Knowledge relation fields prepared for archive objects.
- Knowledge dashboard added with metrics, search, source grouping, and empty states.
- Knowledge search added for title, content, summary, keywords, tags, and source type.
- Knowledge JSON APIs added.
- Permissions added for knowledge visibility.
- Existing login, role system, archive engine, SAP sync, and dashboard preserved.

## API Endpoints

- `GET /api/knowledge`
- `POST /api/knowledge`
- `GET /api/knowledge/{id}`
- `GET /api/knowledge/search`
- `POST /api/knowledge/from-document`
- `GET /api/knowledge/chunks`
- `POST /api/knowledge/query`
- `GET /api/knowledge/query-history`

## AI Safety

Current AI Query V1 does not invent business conclusions. It searches internal knowledge, returns citation-ready sources, and clearly states limitations until model, vector database, Dify, and SAP reasoning are connected.

## Next Tasks

Task004 should add real document parsing/OCR and file detail pages.

Task005 should connect Dify/n8n knowledge workflows and scheduled SAP knowledge snapshots.
