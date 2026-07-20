# Dify Adapter Test Report

`PYTHONPATH=. pytest -q tests/test_dify_adapter.py` verifies service-credential scope enforcement and citation conversion. The adapter only calls retrieval and contains no Qdrant client or write methods.
