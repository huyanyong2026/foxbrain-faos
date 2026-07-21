"""Validated, deployment-injected configuration for Phase 1B only."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingProfile:
    id: str
    provider: str
    model_id: str
    model_version: str
    dimension: int
    max_input_tokens: int
    distance: str = "Cosine"
    endpoint: str | None = None
    api_key_env: str | None = None
    timeout_seconds: float = 20.0
    max_retries: int = 2
    health_endpoint: str | None = None


@dataclass(frozen=True)
class Phase1BSettings:
    profiles: dict[str, EmbeddingProfile]
    qdrant_url: str | None
    collection_alias: str
    chunk_target_tokens: int
    chunk_overlap_tokens: int
    default_embedding_profile: str | None = None

    @classmethod
    def from_env(cls, environ=os.environ):
        raw = environ.get("EMBEDDING_PROFILE_REGISTRY", "{}")
        try:
            items = json.loads(raw)
        except json.JSONDecodeError as error:
            raise ValueError("EMBEDDING_PROFILE_REGISTRY must be valid JSON") from error
        if not isinstance(items, dict):
            raise ValueError("EMBEDDING_PROFILE_REGISTRY must be an object")
        profiles = {}
        for profile_id, value in items.items():
            if not isinstance(value, dict):
                raise ValueError("embedding profile must be an object")
            try:
                profile = EmbeddingProfile(id=profile_id, provider=value["provider"],
                    model_id=value["model_id"], model_version=value["model_version"],
                    dimension=int(value["dimension"]), max_input_tokens=int(value["max_input_tokens"]),
                    distance=value.get("distance", "Cosine"), endpoint=value.get("endpoint"),
                    api_key_env=value.get("api_key_env"), timeout_seconds=float(value.get("timeout_seconds", 20)),
                    max_retries=int(value.get("max_retries", 2)), health_endpoint=value.get("health_endpoint"))
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"invalid embedding profile: {profile_id}") from error
            if profile.provider not in {"openai-compatible", "deepseek-compatible", "hunyuan", "bge-m3", "openai", "jina"} or profile.dimension < 1 or profile.timeout_seconds <= 0 or profile.max_retries < 0:
                raise ValueError(f"invalid embedding profile: {profile_id}")
            profiles[profile_id] = profile
        target, overlap = int(environ.get("MEMORY_CHUNK_TARGET_TOKENS", "512")), int(environ.get("MEMORY_CHUNK_OVERLAP_TOKENS", "64"))
        if target < 1 or overlap < 0 or overlap >= target:
            raise ValueError("invalid chunk token limits")
        default_profile = environ.get("EMBEDDING_DEFAULT_PROFILE") or next(iter(profiles), None)
        if default_profile is not None and default_profile not in profiles:
            raise ValueError("EMBEDDING_DEFAULT_PROFILE is not configured")
        return cls(profiles, environ.get("QDRANT_URL"), environ.get("QDRANT_COLLECTION_ALIAS", "memory_chunks_v1"), target, overlap, default_profile)
