# Sprint018.5 Test Data Cleanup Report

## Cleanup Design

Sprint018.5 adds selective test cleanup for Copilot validation data.

Endpoint:

```text
POST /api/copilot/test-cleanup
```

Required field:

```text
test_run_id
```

Safety condition:

```text
test_run_id must start with SPRINT0185_TEST
```

## Cleanup Scope

For matching test runs only:

- delete matching `copilot_sessions`
- delete matching `copilot_messages`
- delete matching `copilot_feedback`
- archive matching Copilot-created `enterprise_memories`
- remove matching memory relations
- remove matching test timeline events

## Protected Data

The cleanup does not touch:

- real Copilot sessions without matching `test_run_id`
- real Copilot messages without matching `test_run_id`
- real enterprise memories unrelated to test Copilot messages
- business rules
- decision insights
- SAP imported data
- Data Lake records

## Local Cleanup Test

Observed local result:

```text
deleted_sessions=5
deleted_messages=10
deleted_feedback=1
archived_memories=1
```

Result:

```text
PASS
```

## Production Cleanup Test

Test run:

```text
SPRINT0185_TEST_PROD_20260711
```

Production cleanup result:

```text
deleted_sessions=5
deleted_messages=10
deleted_feedback=2
archived_memories=1
```

Result:

```text
PASS
```

Safety confirmation:

```text
Only records matching test_run_id were cleaned.
Real sessions and real enterprise memories were not selected by this cleanup.
```
