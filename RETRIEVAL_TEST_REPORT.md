# Enterprise Retrieval Test Report

`PYTHONPATH=. pytest -q tests/test_retrieval.py tests/test_memory_factory_phase1b.py` verifies citation normalization, top-K forwarding, server-provided owner scope, filter wiring, embedding-unavailable mapping, and the Phase 1B-off `503` behavior. Query logs can use `query_hash`; neither query text nor document text needs to be logged.

Hybrid retrieval is intentionally a boundary only: a future ranker can combine keyword, vector, and rerank scores behind `RetrievalService` without changing the HTTP authorization contract.
