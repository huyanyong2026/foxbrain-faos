# Sprint004 Global Search + Enterprise Timeline Summary

## Scope
- Implemented Sprint004 on the existing huyan.vafox.com portal codebase.
- Kept Sprint001 Drive, Sprint002 Object Engine, and Sprint003 Knowledge Pipeline intact.
- This sprint does not build ai.vafox.com.
- This sprint does not require any external AI API.

## Modified Files
- `portal_v2.py`
- `tests/v6_smoke_check.py`
- `SPRINT004_GLOBAL_SEARCH_TIMELINE_SUMMARY.md`

## Database Changes
- Upgraded `timeline_events` with compatibility columns:
  - `entity_type`
  - `entity_id`
  - `event_type`
  - `description`
  - `source_type`
  - `source_id`
  - `metadata`
  - `occurred_at`
- Added timeline indexes:
  - `idx_timeline_entity`
  - `idx_timeline_source`
  - `idx_timeline_event_type`

## New / Upgraded Pages
- `/search`
  - Searches Drive files, enterprise objects, knowledge items, and document chunks.
  - Supports result filters for type, category, object type, status, and date range.
- Object detail page
  - Added Enterprise Timeline panel.
  - Allows manual timeline notes.
  - Shows automatic events for object updates, document links, and knowledge creation.

## API Interfaces
- `GET /api/search?q=`
- `GET /api/search/suggestions?q=`
- `GET /api/timeline?entity_type=&entity_id=`
- `POST /api/timeline`
- `GET /api/objects/:id/timeline`

## Search Result Types
- `file`
- `object`
- `knowledge`
- `chunk`

## Timeline Event Types
- `object_created`
- `object_updated`
- `document_linked`
- `knowledge_created`
- `manual_note`
- Existing `system_event` compatibility remains available through the timeline table.

## Compatibility Notes
- Existing `timeline_events` fields are preserved.
- New timeline fields are added through `ensure_column`, so existing databases can upgrade in place.
- No forced external AI API dependency was added.
- Existing Drive, Object Engine, and Knowledge Pipeline workflows remain available.

## Test Results
- Passed:
  - `python -m py_compile portal_v2.py tests/v6_smoke_check.py`
  - `tests/v6_smoke_check.py` smoke runner: 112 tests, 0 failures.

## Sprint005 Recommendation
- Add Relationship Explorer and saved search views:
  - Saved search presets for CEO, store manager, purchasing, and knowledge roles.
  - Timeline filters by event type and source.
  - Cross-object relationship timeline views.
  - Exportable audit trail for selected entities.
