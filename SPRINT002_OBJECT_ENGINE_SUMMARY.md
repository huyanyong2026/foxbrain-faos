# Sprint002 Object Engine Summary

## Scope

Sprint002 adds the FoxBrain Object Engine on top of the existing huyan.vafox.com portal without rebuilding the project or changing the ai.vafox.com boundary.

## Changed Files

- `portal_v2.py`
- `tests/v6_smoke_check.py`
- `SPRINT002_OBJECT_ENGINE_SUMMARY.md`

## Database Changes

Added compatible tables:

- `enterprise_objects`
  - `id`, `object_type`, `name`, `code`, `description`, `status`, `tags`, `metadata`, `ai_summary`, `created_by`, `created_at`, `updated_at`, `archived_at`
- `object_relations`
  - `id`, `source_object_type`, `source_object_id`, `target_object_type`, `target_object_id`, `relation_type`, `description`, `confidence`, `created_by`, `created_at`

Existing Sprint001 `documents.related_object_type` and `documents.related_object_id` are reused for Drive-to-object links.

## API List

- `GET /api/object-types`
- `GET /api/objects`
- `POST /api/objects`
- `GET /api/objects/:id`
- `PATCH /api/objects/:id`
- `DELETE /api/objects/:id`
- `GET /api/objects/:id/documents`
- `POST /api/objects/:id/documents/:documentId/link`
- `DELETE /api/objects/:id/documents/:documentId/unlink`

Compatibility endpoint retained:

- `GET /api/object-engine`

## UI Entrances

- `/object-center`
- `/objects`
- `/drive` now includes object linking controls.

Object Center supports:

- object type cards
- object counts
- recent updates
- search and type filtering
- quick create
- list/detail/edit/archive
- linked Drive files
- AI summary placeholder
- relation suggestions placeholder
- timeline placeholder

## Object Types

Implemented the required first object types:

- `store`
- `employee`
- `brand`
- `product`
- `supplier`
- `customer`
- `contract`
- `project`
- `meeting`
- `task`

## Test Results

Passed on local branch `sprint002-object-engine`:

- Python compile check: `portal_v2.py` and `tests/v6_smoke_check.py`
- Smoke checks: `tests/v6_smoke_check.py`, 106 tests, 0 failures

## Known Limitations

- AI summary generation is currently a placeholder through `generateObjectSummary(objectId)`.
- Relation discovery is currently a placeholder through `suggestRelations(objectId)`.
- Object timeline is a placeholder structure and will later absorb Drive, workflow, task, approval and SAP events.
- Drive file detail is API-first; the current Drive list now provides a practical object-linking control.

## Next Step

Sprint003 should connect Object Engine with Knowledge Pipeline so documents can become structured enterprise knowledge objects and later feed graph relationships.
