"""Resilient, provider-neutral embeddings using the OpenAI-compatible wire format."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from threading import RLock
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import EmbeddingProfile


class EmbeddingError(RuntimeError):
    """An embedding request could not be completed."""


class EmbeddingTimeoutError(EmbeddingError):
    """The configured request deadline was exceeded."""


@dataclass(frozen=True)
class EmbeddingCapabilities:
    model_id: str
    model_version: str
    dimension: int
    max_input_tokens: int
    distance: str = "Cosine"


class EmbeddingProvider(Protocol):
    """The application-facing provider contract."""
    def embed(self, text: str) -> list[float]: ...
    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...
    def health_check(self) -> dict[str, object]: ...


class OpenAICompatibleEmbeddingProvider:
    """Adapter for any service exposing ``POST /v1/embeddings`` semantics.

    No vendor SDK is required: changing endpoint, key, or model changes vendors.
    Retries only cover transient transport errors and HTTP 429/5xx responses.
    """
    def __init__(self, profile: EmbeddingProfile, endpoint: str, api_key: str | None = None,
                 timeout_seconds: float = 20, max_retries: int = 2,
                 health_endpoint: str | None = None, opener=urlopen, sleeper=time.sleep):
        if not endpoint.startswith(("http://", "https://")):
            raise ValueError("embedding endpoint must be an HTTP(S) URL")
        if timeout_seconds <= 0 or max_retries < 0:
            raise ValueError("invalid embedding retry configuration")
        self.profile, self.endpoint, self.api_key = profile, endpoint.rstrip("/"), api_key
        self.timeout_seconds, self.max_retries = timeout_seconds, max_retries
        self.health_endpoint = health_endpoint or self.endpoint.rsplit("/", 2)[0] + "/health"
        self._opener, self._sleeper = opener, sleeper

    def capabilities(self) -> EmbeddingCapabilities:
        return EmbeddingCapabilities(self.profile.model_id, self.profile.model_version,
                                     self.profile.dimension, self.profile.max_input_tokens,
                                     self.profile.distance)

    def embed(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not isinstance(texts, list) or not texts or any(not isinstance(text, str) or not text for text in texts):
            raise ValueError("texts must be a non-empty list of non-empty strings")
        payload = {"model": self.profile.model_id, "input": texts, "encoding_format": "float"}
        data = self._request(self.endpoint, "POST", payload)
        rows = data.get("data") if isinstance(data, dict) else None
        if not isinstance(rows, list) or len(rows) != len(texts):
            raise EmbeddingError("invalid embedding response count")
        vectors = []
        for row in rows:
            vector = row.get("embedding") if isinstance(row, dict) else None
            if not isinstance(vector, list) or len(vector) != self.profile.dimension:
                raise EmbeddingError("invalid_vector_dimension")
            if any(not isinstance(value, (int, float)) for value in vector):
                raise EmbeddingError("invalid_vector_value")
            vectors.append([float(value) for value in vector])
        return vectors

    def health_check(self) -> dict[str, object]:
        try:
            self._request(self.health_endpoint, "GET")
        except EmbeddingError as error:
            return {"status": "unhealthy", "provider": self.profile.id, "error": str(error)}
        return {"status": "ok", "provider": self.profile.id, "model": self.profile.model_id}

    def _request(self, url: str, method: str, payload: dict | None = None) -> dict:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = Request(url, data=body, headers=headers, method=method)
        for attempt in range(self.max_retries + 1):
            try:
                with self._opener(request, timeout=self.timeout_seconds) as response:
                    raw = response.read()
                    return json.loads(raw or b"{}")
            except TimeoutError as error:
                failure: EmbeddingError = EmbeddingTimeoutError("embedding request timed out")
            except HTTPError as error:
                failure = EmbeddingError(f"embedding HTTP {error.code}")
                if error.code not in {429, 500, 502, 503, 504}:
                    raise failure from error
            except URLError as error:
                failure = EmbeddingTimeoutError("embedding request timed out") if isinstance(error.reason, TimeoutError) else EmbeddingError("embedding network error")
            except (json.JSONDecodeError, OSError) as error:
                failure = EmbeddingError("invalid embedding response") if isinstance(error, json.JSONDecodeError) else EmbeddingError("embedding network error")
            if attempt == self.max_retries:
                raise failure
            self._sleeper(0.1 * (2 ** attempt))
        raise AssertionError("unreachable")


class EmbeddingProviderRouter:
    """Thread-safe active-provider selector for explicit runtime switching."""
    def __init__(self, providers: dict[str, EmbeddingProvider], active_provider: str):
        if not providers or active_provider not in providers:
            raise ValueError("active embedding provider is not configured")
        self._providers, self._active, self._lock = dict(providers), active_provider, RLock()

    @property
    def active_provider(self) -> str:
        with self._lock:
            return self._active

    def switch(self, provider_id: str) -> None:
        with self._lock:
            if provider_id not in self._providers:
                raise ValueError("embedding provider is not configured")
            self._active = provider_id

    def embed(self, text: str) -> list[float]:
        with self._lock:
            provider = self._providers[self._active]
        return provider.embed(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        with self._lock:
            provider = self._providers[self._active]
        return provider.embed_batch(texts)

    def health_check(self) -> dict[str, object]:
        with self._lock:
            provider_id, provider = self._active, self._providers[self._active]
        return {"active_provider": provider_id, **provider.health_check()}


# Backward-compatible factory name.  All supported legacy labels use OpenAI wire format.
def provider_for(profile: EmbeddingProfile, endpoint: str, api_key: str | None = None, **kwargs) -> OpenAICompatibleEmbeddingProvider:
    return OpenAICompatibleEmbeddingProvider(profile, endpoint, api_key, **kwargs)


def router_from_settings(settings, environ=None) -> EmbeddingProviderRouter:
    """Build the configured router without coupling it to a particular vendor."""
    import os
    environment = os.environ if environ is None else environ
    providers = {}
    for profile_id, profile in settings.profiles.items():
        endpoint = profile.endpoint or environment.get("EMBEDDING_ENDPOINT")
        if not endpoint:
            raise ValueError(f"embedding endpoint is required for profile: {profile_id}")
        api_key = environment.get(profile.api_key_env) if profile.api_key_env else environment.get("EMBEDDING_API_KEY")
        providers[profile_id] = provider_for(profile, endpoint, api_key, timeout_seconds=profile.timeout_seconds,
                                             max_retries=profile.max_retries, health_endpoint=profile.health_endpoint)
    return EmbeddingProviderRouter(providers, settings.default_embedding_profile)
