"""Small, dependency-free Qdrant client for the isolated Phase 1B index.

The adapter only talks to the URL explicitly injected by a test or deployment.
It is never constructed by the Phase 1A application path.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Callable
from urllib.request import Request, urlopen


PAYLOAD_FIELDS = frozenset({
    "memory_id", "chunk_id", "owner", "tags", "source", "created_at",
    "content_hash", "embedding_profile",
})
PAYLOAD_INDEX_FIELDS = ("memory_id", "chunk_id", "owner", "tags", "source", "created_at", "content_hash", "embedding_profile")


class QdrantAdapter:
    """Qdrant REST client with collection, alias, point, and health operations."""

    def __init__(self, url: str, collection_alias: str = "memory_chunks_v1", api_key: str | None = None,
                 request: Callable[[str, str, dict[str, Any] | None], Any] | None = None):
        if not url:
            raise ValueError("Qdrant URL is required")
        self.url = url.rstrip("/")
        self.collection_alias = collection_alias
        self.api_key = api_key
        self._transport = request

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None):
        if self._transport:
            return self._transport(method, path, payload)
        headers = {"Accept": "application/json"}
        body = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode("utf-8")
        if self.api_key:
            headers["api-key"] = self.api_key
        request = Request(self.url + path, data=body, headers=headers, method=method)
        with urlopen(request, timeout=10) as response:
            raw = response.read()
        return json.loads(raw) if raw else {"result": True}

    @staticmethod
    def point_id(chunk_id: str, embedding_profile: str) -> str:
        """Create a deterministic Qdrant point id without retaining any text."""
        import uuid
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{chunk_id}:{embedding_profile}"))

    @staticmethod
    def validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
        if set(payload) != PAYLOAD_FIELDS:
            raise ValueError("payload must contain exactly the Phase 1B payload fields")
        if not all(isinstance(payload[key], str) and payload[key] for key in PAYLOAD_FIELDS - {"tags"}):
            raise ValueError("payload string fields must be non-empty strings")
        if not isinstance(payload["tags"], list) or any(not isinstance(tag, str) or not tag for tag in payload["tags"]):
            raise ValueError("tags must be an array of non-empty strings")
        try:
            datetime.fromisoformat(payload["created_at"].replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("created_at must be RFC 3339") from error
        return {key: payload[key] for key in sorted(PAYLOAD_FIELDS)}

    def health(self) -> dict[str, Any]:
        response = self._request("GET", "/healthz")
        return {"status": "ok", "qdrant": response.get("result", response)}

    def collections(self) -> list[dict[str, Any]]:
        return self._request("GET", "/collections").get("result", {}).get("collections", [])

    def create_collection(self, collection: str, dimension: int, distance: str = "Cosine"):
        if not collection or dimension < 1 or distance not in {"Cosine", "Dot", "Euclid", "Manhattan"}:
            raise ValueError("invalid collection configuration")
        response = self._request("PUT", f"/collections/{collection}", {
            "vectors": {"content": {"size": dimension, "distance": distance}},
        })
        for field in PAYLOAD_INDEX_FIELDS:
            schema = "datetime" if field == "created_at" else "keyword"
            self._request("PUT", f"/collections/{collection}/index", {"field_name": field, "field_schema": schema})
        return response.get("result", response)

    def set_alias(self, collection: str, alias: str | None = None):
        alias = alias or self.collection_alias
        response = self._request("POST", "/aliases", {"actions": [{"create_alias": {"collection_name": collection, "alias_name": alias}}]})
        return response.get("result", response)

    def switch_alias(self, collection: str, alias: str | None = None):
        """Atomically repoint an existing alias after the new collection is accepted."""
        alias = alias or self.collection_alias
        response = self._request("POST", "/aliases", {"actions": [
            {"delete_alias": {"alias_name": alias}},
            {"create_alias": {"collection_name": collection, "alias_name": alias}},
        ]})
        return response.get("result", response)

    def initialize(self, dimension: int, collection: str | None = None, distance: str = "Cosine"):
        """Create an immutable physical collection and point the stable alias at it."""
        collection = collection or f"{self.collection_alias}__default"
        self.create_collection(collection, dimension, distance)
        self.set_alias(collection)
        return {"collection": collection, "alias": self.collection_alias, "dimension": dimension, "distance": distance}

    def upsert(self, points: list[dict[str, Any]], wait: bool = True):
        normalized = []
        for point in points:
            vector, payload = point.get("vector"), point.get("payload")
            if not isinstance(point.get("id"), str) or not isinstance(vector, list) or not vector:
                raise ValueError("point id and vector are required")
            normalized.append({"id": point["id"], "vector": {"content": vector}, "payload": self.validate_payload(payload)})
        response = self._request("PUT", f"/collections/{self.collection_alias}/points?wait={'true' if wait else 'false'}", {"points": normalized})
        return response.get("result", response)

    def delete(self, point_ids: list[str] | None = None, memory_id: str | None = None, wait: bool = True):
        if bool(point_ids) == bool(memory_id):
            raise ValueError("provide exactly one of point_ids or memory_id")
        selector = {"points": point_ids} if point_ids else {"filter": {"must": [{"key": "memory_id", "match": {"value": memory_id}}]}}
        response = self._request("POST", f"/collections/{self.collection_alias}/points/delete?wait={'true' if wait else 'false'}", selector)
        return response.get("result", response)

    @staticmethod
    def filter_for(owners, tags_any=(), source=None, created_at_gte=None, exclude_memory_id=None):
        if not owners:
            raise PermissionError("authorized owners required")
        must = [{"key": "owner", "match": {"any": sorted(set(owners))}}]
        if tags_any:
            must.append({"key": "tags", "match": {"any": sorted(set(tags_any))}})
        if source:
            must.append({"key": "source", "match": {"value": source}})
        if created_at_gte:
            must.append({"key": "created_at", "range": {"gte": created_at_gte}})
        result = {"must": must}
        if exclude_memory_id:
            result["must_not"] = [{"key": "memory_id", "match": {"value": exclude_memory_id}}]
        return result

    def search(self, vector, owners, limit, **filters):
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        payload = {"vector": {"name": "content", "vector": vector}, "limit": limit, "with_payload": True,
                   "filter": self.filter_for(owners, **filters)}
        return self._request("POST", f"/collections/{self.collection_alias}/points/search", payload).get("result", [])
