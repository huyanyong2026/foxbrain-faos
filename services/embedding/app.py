"""HTTP boundary for the versioned semantic_v2 embedding provider."""
from __future__ import annotations

import json
import os
import time
from wsgiref.simple_server import make_server

from packages.vafox_foundation.http import json_response, service_app
from services.memory.phase1b.config import EmbeddingProfile
from services.memory.phase1b.embedding import EmbeddingError, provider_for


def _body(environ):
    return environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0))


def provider_from_env(environ=os.environ):
    """Create the M4 provider without changing M3's profile registry."""
    profile = EmbeddingProfile(
        "semantic_v2", environ.get("SEMANTIC_V2_PROVIDER", "bge-m3"),
        environ.get("SEMANTIC_V2_MODEL", "semantic_v2"),
        environ.get("SEMANTIC_V2_VERSION", "v2"), int(environ.get("SEMANTIC_V2_DIMENSION", "1024")),
        int(environ.get("SEMANTIC_V2_MAX_INPUT_TOKENS", "8192")),
        endpoint=environ.get("SEMANTIC_V2_ENDPOINT"), timeout_seconds=float(environ.get("SEMANTIC_V2_TIMEOUT_SECONDS", "20")),
        max_retries=int(environ.get("SEMANTIC_V2_MAX_RETRIES", "2")), health_endpoint=environ.get("SEMANTIC_V2_HEALTH_ENDPOINT"),
    )
    if not profile.endpoint:
        raise ValueError("SEMANTIC_V2_ENDPOINT is required")
    return provider_for(profile, profile.endpoint, environ.get("SEMANTIC_V2_API_KEY"),
                        timeout_seconds=profile.timeout_seconds, max_retries=profile.max_retries,
                        health_endpoint=profile.health_endpoint)


def create_app(embedding_provider=None):
    provider = embedding_provider or provider_from_env()
    capabilities = provider.capabilities()

    def embed(environ, start_response, batch=False):
        try:
            payload = json.loads(_body(environ) or b"{}")
        except json.JSONDecodeError:
            return json_response(start_response, 400, {"error": "invalid_json"}), 400
        texts = payload.get("texts") if batch else [payload.get("text")]
        max_batch = int(os.getenv("SEMANTIC_V2_MAX_BATCH", "128"))
        if (not isinstance(texts, list) or not texts or len(texts) > max_batch or
                any(not isinstance(text, str) or not text.strip() for text in texts)):
            return json_response(start_response, 400, {"error": "invalid_embedding_input"}), 400
        started = time.monotonic()
        try:
            vectors = provider.embed_batch(texts)
        except (EmbeddingError, TimeoutError, OSError):
            return json_response(start_response, 503, {"error": "embedding_unavailable"}), 503
        result = {"dimension": capabilities.dimension, "model": capabilities.model_id,
                  "version": capabilities.model_version, "latency_ms": round((time.monotonic() - started) * 1000, 2)}
        if batch: result["vectors"] = vectors
        else: result["vector"] = vectors[0]
        return json_response(start_response, 200, result), 200

    def health(environ, start_response):
        result = provider.health_check()
        status = 200 if result.get("status") == "ok" else 503
        result.update({"model": capabilities.model_id, "version": capabilities.model_version, "dimension": capabilities.dimension})
        return json_response(start_response, status, result), status

    base = service_app("embedding", {("POST", "/embed"): lambda e, s: embed(e, s),
                                     ("POST", "/embed_batch"): lambda e, s: embed(e, s, True)})
    def app(environ, start_response):
        if environ["REQUEST_METHOD"] == "GET" and environ["PATH_INFO"] == "/health":
            return health(environ, start_response)[0]
        return base(environ, start_response)
    return app


def app(environ, start_response):
    """Create the configured provider at service request time after environment loading."""
    return create_app()(environ, start_response)
if __name__ == "__main__":
    make_server("0.0.0.0", 8080, app).serve_forever()
