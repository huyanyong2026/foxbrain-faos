# Sprint006 Memory Engine Summary

## Scope
- Implemented Sprint006 on the existing huyan.vafox.com portal codebase.
- Kept Sprint001 Drive, Sprint002 Object Engine, Sprint003 Knowledge Pipeline, Sprint004 Global Search + Timeline, and Sprint005 CEO Dashboard available.
- This sprint does not build ai.vafox.com.
- This sprint does not require any external AI API.

## New Tables
- `enterprise_memories`
  - Stores decision, meeting, risk, strategy, operation, purchase, pricing, store, brand, and supplier memories.
  - Captures `reason`, `decision`, `impact`, `risk_level`, status, tags, related object, related document, related knowledge, and related timeline references.
- `memory_relations`
  - Stores future-ready memory relationship links for objects, documents, knowledge, and other targets.

## New / Upgraded UI
- `/memory`
- `/memories`
- The page now shows:
  - New memory form
  - Memory type filter
  - Risk level filter
  - Tag filter
  - Search box
  - Recent memories
  - Decision memories
  - Risk memories
  - Memory detail and edit form

## New API
- `GET /api/memories`
- `POST /api/memories`
- `GET /api/memories/:id`
- `PATCH /api/memories/:id`
- `DELETE /api/memories/:id`
- `GET /api/memory-types`
- `GET /api/objects/:id/memories`

## Dashboard Integration
Dashboard integration is included.
- CEO Dashboard now includes:
  - `enterprise_memories_total`
  - `high_risk_memories_total`
  - `recent_memories`
  - Core entry: 企业记忆 -> `/memory`

## Search Integration
Search integration is included.
- Global Search now includes result type `memory`.
- Search covers:
  - title
  - summary
  - content
  - reason
  - decision
  - tags

## Timeline Integration
Timeline integration is included.
- Creating a memory linked to an object writes `memory_created`.
- Updating a memory linked to an object writes `memory_updated`.
- Timeline source type is `enterprise_memory`.

## Test Results
- Passed:
  - `python -m py_compile portal_v2.py tests/v6_smoke_check.py`
  - `tests/v6_smoke_check.py` smoke runner: 117 tests, 0 failures.

## Known Limitations
- Knowledge relationship fields are stored and exposed, but deep bidirectional knowledge graph traversal is left for a later sprint.
- Memory quality review workflow is basic status tracking for now.
- Memory search is SQL text search and does not require an external vector or AI API.

## Sprint007 Recommendation
- Add Memory Review and Evidence Pack:
  - Review queue for high-risk memories.
  - Evidence packet view combining documents, knowledge, timeline, and related objects.
  - Memory confidence and source completeness scoring.
  - CEO Daily Brief can cite enterprise memories as reasons behind recommendations.
