"""Acceptance coverage for the Sprint A embedding provider."""
import json
from urllib.error import HTTPError

import pytest

from services.memory.phase1b.config import EmbeddingProfile, Phase1BSettings
from services.memory.phase1b.embedding import (EmbeddingError, EmbeddingProviderRouter,
    EmbeddingTimeoutError, OpenAICompatibleEmbeddingProvider, router_from_settings)


class Response:
    def __init__(self, body=b"{}"):
        self.body = body
    def read(self): return self.body
    def __enter__(self): return self
    def __exit__(self, *_): return False


def profile(name="primary"):
    return EmbeddingProfile(name, "openai-compatible", "text-embedding-test", "2026-07", 3, 8192)


def test_single_and_batch_embedding_use_openai_compatible_request():
    requests = []
    def opener(request, timeout):
        requests.append((request, timeout))
        values = json.loads(request.data)["input"]
        return Response(json.dumps({"data": [{"embedding": [float(i), 2, 3]} for i, _ in enumerate(values)]}).encode())
    provider = OpenAICompatibleEmbeddingProvider(profile(), "https://embedding.example/v1/embeddings", "secret", opener=opener)
    assert provider.embed("one") == [0.0, 2.0, 3.0]
    assert provider.embed_batch(["one", "two"]) == [[0.0, 2.0, 3.0], [1.0, 2.0, 3.0]]
    assert requests[0][0].get_header("Authorization") == "Bearer secret"
    assert json.loads(requests[1][0].data)["encoding_format"] == "float"


def test_timeout_is_retried_then_reported():
    calls = []
    def opener(*_, **__):
        calls.append(True)
        raise TimeoutError()
    provider = OpenAICompatibleEmbeddingProvider(profile(), "https://embedding.example/v1/embeddings", max_retries=1, opener=opener, sleeper=lambda _: None)
    with pytest.raises(EmbeddingTimeoutError): provider.embed("one")
    assert len(calls) == 2


def test_router_switches_provider_and_reports_health():
    class Provider:
        def __init__(self, value): self.value = value
        def embed(self, _): return [self.value]
        def embed_batch(self, texts): return [[self.value] for _ in texts]
        def health_check(self): return {"status": "ok"}
    router = EmbeddingProviderRouter({"a": Provider(1), "b": Provider(2)}, "a")
    assert router.embed("x") == [1]
    router.switch("b")
    assert router.embed_batch(["x", "y"]) == [[2], [2]]
    assert router.health_check() == {"active_provider": "b", "status": "ok"}
    with pytest.raises(ValueError): router.switch("missing")


def test_settings_select_default_provider_and_build_router():
    raw = {"first": {"provider": "openai-compatible", "model_id": "m", "model_version": "1", "dimension": 3, "max_input_tokens": 8, "endpoint": "https://one/v1/embeddings"}, "second": {"provider": "openai-compatible", "model_id": "m", "model_version": "1", "dimension": 3, "max_input_tokens": 8, "endpoint": "https://two/v1/embeddings"}}
    settings = Phase1BSettings.from_env({"EMBEDDING_PROFILE_REGISTRY": json.dumps(raw), "EMBEDDING_DEFAULT_PROFILE": "second"})
    router = router_from_settings(settings, {})
    assert router.active_provider == "second"
