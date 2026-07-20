# Embedding Provider Test Report

## Scope

Sprint A delivers a provider-neutral embedding integration. The default transport is
the OpenAI-compatible `POST /v1/embeddings` format; the endpoint and model are
deployment configuration, not vendor-specific code.

## Configuration

Set `EMBEDDING_PROFILE_REGISTRY` to a JSON object. Each profile requires `provider`,
`model_id`, `model_version`, `dimension`, and `max_input_tokens`. Use
`provider: "openai-compatible"` for the default transport, and configure `endpoint`,
optional `api_key_env`, `timeout_seconds`, `max_retries`, and `health_endpoint`.
Set `EMBEDDING_DEFAULT_PROFILE` to select the initial provider. `EMBEDDING_ENDPOINT`
and `EMBEDDING_API_KEY` are fallback values for deployments that share an endpoint/key.

## Acceptance Results

| Criterion | Result | Evidence |
| --- | --- | --- |
| Single text | Pass | `test_single_and_batch_embedding_use_openai_compatible_request` |
| Batch text | Pass | `test_single_and_batch_embedding_use_openai_compatible_request` |
| Timeout and retry | Pass | `test_timeout_is_retried_then_reported` |
| Configuration/provider switch | Pass | `test_settings_select_default_provider_and_build_router`, `test_router_switches_provider_and_reports_health` |
| Unit tests | Pass | `pytest -q tests/test_embedding_provider.py tests/test_memory_factory_phase1b.py` |

## Operational Notes

`health_check()` calls the configured health URL and returns a structured `ok` or
`unhealthy` result. Runtime switching is explicit through
`EmbeddingProviderRouter.switch(profile_id)` and rejects unconfigured profiles.
