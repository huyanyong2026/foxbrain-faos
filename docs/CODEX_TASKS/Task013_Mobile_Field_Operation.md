# Task013 Mobile Field Operation Engine

## Completed

- Added `/mobile` Mobile Operation Center.
- Added `/mobile/tasks` mobile task view.
- Added `/mobile/review` manager review center.
- Added `field_submissions` model.
- Added photo upload flow using mobile file inputs.
- Added store note, product photo, customer feedback, inventory issue, competitor observation and knowledge feed submission types.
- Added mobile task completion with result note and photos.
- Added submission review actions.
- Added convert-to-task flow.
- Added convert-to-knowledge flow.
- Added Enterprise WeChat placeholder status API.
- Updated health check.
- Updated docs and README.

## APIs

- `GET /api/mobile`
- `GET /api/mobile/tasks`
- `POST /api/mobile/submissions`
- `GET /api/mobile/submissions`
- `GET /api/mobile/submissions/{id}`
- `PUT /api/mobile/submissions/{id}`
- `POST /api/mobile/submissions/{id}/approve`
- `POST /api/mobile/submissions/{id}/reject`
- `POST /api/mobile/submissions/{id}/convert-to-task`
- `POST /api/mobile/submissions/{id}/convert-to-knowledge`
- `GET /api/mobile/notifications`
- `GET /api/wecom/status`

## Safety

Enterprise WeChat is placeholder only. No external send happens without secure credentials and approval.
