# Sprint018.5 Copilot Real Data Test Report

## Local Checks

### Syntax

```text
python -m py_compile portal_v2.py
```

Result:

```text
PASS
```

### Local Calibration Smoke Test

Validated questions:

- 今天企业有什么主要风险？
- Osprey库存怎么样？有哪些风险？
- Kailas销售和库存表现怎么样？
- 南山店经营情况怎么样？
- 火星店滑雪板库存怎么样？

Result summary:

```text
PASS: Copilot sessions created with evidence.
PASS: Evidence count returned for each question.
PASS: Unknown or unmatched entity can produce data-insufficient response.
PASS: Feedback can be stored.
PASS: Memory draft can be created as draft.
PASS: Test sessions/messages/feedback cleaned by test_run_id.
PASS: Test memory draft archived instead of remaining active.
```

Observed local smoke result:

```text
known business questions: evidence_count up to 30
unknown entity question: reliable=false
cleanup: deleted_sessions=5, deleted_messages=10, deleted_feedback=1, archived_memories=1
```

## Data Sufficiency

When entity-specific evidence is unavailable, Copilot marks the answer unreliable and lists missing evidence.

Example missing evidence:

```text
store_evidence:火星店
```

## Feedback

Validated feedback persistence for:

- missing evidence feedback

Supported feedback types:

- useful
- not_useful
- needs_review
- correction
- missing_evidence

## Memory Draft

Validated:

- memory draft creation from Copilot answer
- memory remains `draft`
- memory links back to `copilot_message`
- cleanup archives test draft

## Regression

Existing Sprint001-Sprint018 features were not removed or replaced.

## Production Real Data Validation

Production validation is recorded separately in:

```text
SPRINT018_5_PRODUCTION_DEPLOYMENT_REPORT.md
SPRINT018_5_EVIDENCE_AUDIT_REPORT.md
SPRINT018_5_TEST_DATA_CLEANUP_REPORT.md
```

