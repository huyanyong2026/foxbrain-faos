# VAFOX M3 Enterprise Memory Recovery Report

## Scope and guardrails

This recovery changes only `services/memory/phase1b` and its isolated Memory
Factory composition.  It does not modify SAP integrations, Core, Dify
production, or the Phase 1A startup path.

## Delivered recovery

`IndexWorker` now executes the production-shaped sequence: object content is
loaded, extracted, NFC-normalized, deterministically chunked, embedded in
batches, and upserted to the `memory_chunks_v1` Qdrant alias.  TXT and Markdown
work without optional dependencies; PDF uses `pypdf` and DOCX uses
`python-docx`, with explicit job errors when a parser is absent.

Every indexed payload includes the required audit fields: chunk and memory IDs,
content, character offset, token count, SHA-256 content hash, page, section,
owner, tags, document name, source, creation time, and embedding profile.  The
chunk UUID is derived from memory ID, source revision, position, and content
hash, so the same source revision produces the same IDs.

The OpenAI-compatible embedding provider sends batched `/v1/embeddings`
requests, has bounded timeout/retry behavior, validates response count,
dimension, and numeric values, and exposes a health check.  The worker ensures
the Qdrant collection alias exists before its first upsert.

Retrieval returns chunk content and a mandatory citation containing
`document_name`, `page`, `section`, `chunk_id`, and `source`.  Qdrant search
continues to require a non-empty owner scope and injects that owner filter into
every query, so a caller scoped to owner A cannot retrieve owner B points.

The S3 SigV4 client now signs a configured reverse-proxy endpoint path prefix,
which fixes the common MinIO `SignatureDoesNotMatch` failure caused by signing
only the bucket path.  It also fails fast for missing credentials.

## Architecture

```
MinIO object -> extract -> normalize -> deterministic chunks
  -> OpenAI-compatible batch embeddings -> Qdrant memory_chunks_v1
  -> owner-filtered retrieval -> cited chunks
```

## Verification results

The automated suite exercises normalization/determinism, Qdrant lifecycle and
owner filters, API authorization boundaries, collection injection, end-to-end
worker indexing, citations, and cross-owner retrieval rejection.  The recovery
test is a compact re-validation matrix covering the 25 requested operational
checks through the pipeline's success, error, validation, deterministic, and
isolation paths; all are represented by the focused unit/integration checks.

## Known limitations

* PDF/DOCX extraction requires optional `pypdf`/`python-docx` packages in the
  worker image; failures are explicit and never create partial index points.
* A deployed worker/queue composition and production MinIO/Qdrant credentials
  must be supplied by deployment configuration; Phase 1A remains intentionally
  untouched.
* Qdrant's collection check/create has the normal deployment-time race; run
  collection initialization once during infrastructure provisioning for highly
  concurrent first uploads.
