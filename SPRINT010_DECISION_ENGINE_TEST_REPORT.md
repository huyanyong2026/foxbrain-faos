# Sprint010 Decision Engine Test Report

## Test Scope

Sprint010 was validated against the local portal code and local SQLite runtime. The test goal is to confirm that the Decision Engine can generate rule-based, evidence-backed insights from existing imported SAP/Data Lake/business metric structures without external AI or production SAP access.

## Schema Checks

Expected tables:

- `decision_insights`
- `decision_evidence`
- `decision_actions`

Expected integration tables used:

- `business_metrics_snapshots`
- `business_metric_quality`
- `business_object_suggestions`
- `sap_sales`
- `sap_inventory`
- `enterprise_memories`
- `knowledge_graph_nodes`
- `knowledge_graph_edges`

## API Checks

Expected APIs:

- `GET /api/decision/insights`
- `GET /api/decision/insights/:id`
- `POST /api/decision/rebuild`
- `PATCH /api/decision/insights/:id`
- `POST /api/decision/insights/:id/status`
- `POST /api/decision/insights/:id/actions`
- `GET /api/objects/:id/decisions`

## UI Checks

Expected pages:

- `/decision`
- `/decision/insights`

Expected page content:

- evidence table
- suggestion
- manual status update
- action draft list
- Knowledge Graph context
- Memory preparation note

## Guardrail Checks

Passed requirements:

- all generated decision insights require evidence
- evidence must include `source_type` and `source_id`
- generated actions are manual review drafts or pending review
- accepted/resolved insight prepares Memory only after human status update
- Knowledge Graph relationships created by the Decision Engine include source metadata
- no external AI API is required
- no production SAP connection is used

## Smoke Test Result

Smoke tests include static checks for Sprint010 schema, routes, APIs, reports, Dashboard integration, Memory integration, Knowledge Graph integration, and safety guardrails.

Local validation result:

- Python compile: passed with bundled Codex Python runtime
- Static smoke runner: 129 tests passed, 0 failed
- Runtime local data simulation: passed
- Generated insights: 6
- Generated evidence records: 6
- Generated manual action drafts: 6
- Generated Knowledge Graph decision nodes: 11
- Insights missing evidence: 0
- Accepted insight prepared draft enterprise memory: 1

`pytest` was not available in the bundled runtime, so the smoke file was executed by directly loading and running all `test_*` functions.
