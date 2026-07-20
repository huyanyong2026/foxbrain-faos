# Index Pipeline Test Report

`pytest -q tests/test_index_pipeline.py tests/test_memory_factory_phase1b.py` validates job-key idempotency, queue creation, deterministic chunking, batch embedding, Qdrant upsert payloads, unsupported extraction errors, owner checks, and the inactive-by-default Phase 1B behavior. The worker is separately composed; reindex requests return immediately and never embed synchronously.

PDF and DOCX parser packages are intentionally not bundled in this dependency-free alpha; they return `extract_failed` until a hardened extractor is deployed.
