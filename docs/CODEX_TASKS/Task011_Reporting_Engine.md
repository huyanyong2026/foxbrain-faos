# Task011 Reporting Engine

## Completed

- Added `/reports` Report Center.
- Added report, report template and report schedule models.
- Added default report templates.
- Added draft generation framework.
- Added review flow: generate, approve, reject, archive.
- Added Markdown and HTML export payloads.
- Added report schedule model for later n8n automation.
- Added JSON APIs for reports, templates and schedules.
- Updated health check with Reporting Engine status.
- Preserved existing login, SAP sync, Jarvis, Knowledge, Memory, Graph and Multi-Agent modules.

## APIs

- `GET /api/reports`
- `POST /api/reports`
- `GET /api/reports/{id}`
- `PUT /api/reports/{id}`
- `POST /api/reports/{id}/generate`
- `POST /api/reports/{id}/approve`
- `POST /api/reports/{id}/reject`
- `POST /api/reports/{id}/archive`
- `POST /api/reports/{id}/export`
- `GET /api/report-templates`
- `POST /api/report-templates`
- `GET /api/report-schedules`
- `POST /api/report-schedules`

## Safety

All reports are drafts until reviewed. The system must not invent business facts.
