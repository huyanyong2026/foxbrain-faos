# Sprint010 Decision Engine Summary

## Scope

Sprint010 adds the first evidence-based Decision Engine Foundation on top of the existing huyan.vafox.com codebase.

This is an incremental upgrade. It does not rebuild the project, does not develop ai.vafox.com, does not connect to production SAP, and does not require any external AI API.

## Added Database Tables

- `decision_insights`
- `decision_evidence`
- `decision_actions`

Each `decision_insights` record stores `metric_snapshot`, `evidence`, `suggestion`, and `action_options`. Each generated insight is blocked unless it has at least one traceable evidence item with `source_type` and `source_id`.

## Added Pages

- `/decision`
- `/decision/insights`

The page shows high-severity insights, risk summaries, evidence, suggested action options, human status update controls, Knowledge Graph context, and Memory preparation.

## Added APIs

- `GET /api/decision/insights`
- `GET /api/decision/insights/:id`
- `POST /api/decision/rebuild`
- `PATCH /api/decision/insights/:id`
- `POST /api/decision/insights/:id/status`
- `POST /api/decision/insights/:id/actions`
- `GET /api/objects/:id/decisions`

## Rule-Based Insight Generation

Initial rules use local imported data and calibrated metrics only:

- inventory cost basis missing
- metric quality warnings
- pending Object Match suggestions
- inventory product with no matched sales
- low brand gross margin
- low store gross margin
- Knowledge Graph nodes without edges

## Dashboard Integration

CEO Dashboard now includes:

- Decision Insights count
- High Severity count
- Decision Evidence count
- Top 3 decision risks
- Latest accepted decision
- Decision Engine entry

## Memory Integration

When an insight is accepted or resolved, the system prepares a draft `enterprise_memories` record with:

- what was found
- evidence summary
- human decision note
- expected impact placeholder

This preserves decision learning without auto-executing business actions.

## Knowledge Graph Integration

Every generated insight creates a `decision` node in `knowledge_graph_nodes` with source `decision_insights`.

When a related enterprise object exists, the engine creates a source-linked `DECISION_ABOUT` edge. All generated graph edges keep `source_type` and `source_id`.

## Guardrails

- `all_decision_insights_must_have_evidence`
- `rule_based_decision_engine_no_external_ai_api_no_auto_execution`
- high-risk actions remain draft or pending review
- no production SAP connection
- no unsupported AI judgement

