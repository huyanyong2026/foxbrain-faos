# VAFOX OS v2.0 Alpha — M3 Enterprise Memory Delivery

| Sprint | Commit | PR title | Status |
| --- | --- | --- | --- |
| B — Index Pipeline | `d2c6f7c` | Sprint B: add asynchronous Memory Factory index pipeline | complete |
| C — Enterprise Retrieval | `2734e8b` | Sprint C: add owner-scoped enterprise retrieval | complete |
| D — Dify Read-only Adapter | `18d9d32` | Sprint D: add read-only Dify adapter | complete |

## Test results

The focused alpha suite passes: index-job/idempotency/chunking/upsert, owner-scoped retrieval/citations/failure handling, and Dify credential/citation conversion. See the three sprint test reports.

## Unresolved items

PDF/DOCX extraction is intentionally behind a hardened parser integration. Production queue persistence, reconciliation scheduling, a source-chunk resolver for related content, and hybrid rank/rerank are extension points, not production claims.

## Pre-deployment checklist

- Inject versioned embedding profiles, provider credentials, and timeouts as secrets.
- Keep Qdrant on loopback/private networking; permit Dify only to the adapter/retrieval API.
- Map each Dify credential to a fixed organization scope and exercise rotation.
- Apply the index-job migration, provision the worker queue, and test delete/reconciliation operations in staging.
- Verify audit logs contain hashes/metadata only, never query text, document content, or credentials.

## M3 demonstration readiness

Ready for a desensitized staging demonstration of upload/reindex job creation, asynchronous indexing, owner-scoped search, citations, and a Dify Workflow HTTP Request call. No production deployment is included.
