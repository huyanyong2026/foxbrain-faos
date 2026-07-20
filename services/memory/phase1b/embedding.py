"""Provider-neutral embedding contract and HTTP adapters."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol
from urllib.request import Request, urlopen

from .config import EmbeddingProfile


@dataclass(frozen=True)
class EmbeddingCapabilities:
    model_id: str
    model_version: str
    dimension: int
    max_input_tokens: int
    distance: str = "Cosine"


@dataclass(frozen=True)
class EmbedInput:
    id: str
    text: str


@dataclass(frozen=True)
class EmbedRequest:
    model_ref: str
    inputs: tuple[EmbedInput, ...]
    input_type: str
    idempotency_key: str


@dataclass(frozen=True)
class EmbedResponse:
    model_id: str
    model_version: str
    dimension: int
    vectors: dict[str, list[float]]
    failures: dict[str, str]


class EmbeddingProvider(Protocol):
    def capabilities(self) -> EmbeddingCapabilities: ...
    def embed(self, request: EmbedRequest) -> EmbedResponse: ...


class HttpEmbeddingProvider:
    """Base adapter; credentials are supplied by the deployment, never payloads."""
    def __init__(self, profile: EmbeddingProfile, endpoint: str, api_key: str | None = None):
        self.profile, self.endpoint, self.api_key = profile, endpoint, api_key
    def capabilities(self):
        return EmbeddingCapabilities(self.profile.model_id, self.profile.model_version, self.profile.dimension, self.profile.max_input_tokens, self.profile.distance)
    def _post(self, payload):
        headers = {"Content-Type": "application/json"}
        if self.api_key: headers["Authorization"] = f"Bearer {self.api_key}"
        request = Request(self.endpoint, data=json.dumps(payload).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=20) as response: return json.loads(response.read())


class BgeM3Provider(HttpEmbeddingProvider):
    def embed(self, request):
        data = self._post({"model": self.profile.model_id, "input": [item.text for item in request.inputs]})
        return _response(self.profile, request, data.get("data", data.get("embeddings", [])))


class OpenAIEmbeddingProvider(HttpEmbeddingProvider):
    def embed(self, request):
        data = self._post({"model": self.profile.model_id, "input": [item.text for item in request.inputs], "encoding_format": "float"})
        return _response(self.profile, request, data.get("data", []))


class JinaEmbeddingProvider(HttpEmbeddingProvider):
    def embed(self, request):
        data = self._post({"model": self.profile.model_id, "input": [item.text for item in request.inputs], "task": "retrieval.query" if request.input_type == "query" else "retrieval.passage"})
        return _response(self.profile, request, data.get("data", []))


def _response(profile, request, rows):
    vectors, failures = {}, {}
    for index, item in enumerate(request.inputs):
        row = rows[index] if index < len(rows) else None
        vector = row.get("embedding") if isinstance(row, dict) else row
        if not isinstance(vector, list) or len(vector) != profile.dimension: failures[item.id] = "invalid_vector_dimension"
        else: vectors[item.id] = vector
    return EmbedResponse(profile.model_id, profile.model_version, profile.dimension, vectors, failures)


def provider_for(profile, endpoint, api_key=None):
    return {"bge-m3": BgeM3Provider, "openai": OpenAIEmbeddingProvider, "jina": JinaEmbeddingProvider}[profile.provider](profile, endpoint, api_key)
