"""Small Qdrant REST adapter with mandatory server-side payload filters."""
from __future__ import annotations
import json
from urllib.request import Request, urlopen

class QdrantAdapter:
    def __init__(self, url, collection_alias="memory_chunks_v1", api_key=None): self.url, self.collection_alias, self.api_key = url.rstrip("/"), collection_alias, api_key
    def _request(self, path, payload):
        headers = {"Content-Type": "application/json"}
        if self.api_key: headers["api-key"] = self.api_key
        request = Request(self.url + path, data=json.dumps(payload).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=10) as response: return json.loads(response.read())
    @staticmethod
    def filter_for(owners, tags_any=(), source=None, created_at_gte=None, exclude_memory_id=None):
        if not owners: raise PermissionError("authorized owners required")
        must = [{"key": "owner", "match": {"any": sorted(set(owners))}}]
        if tags_any: must.append({"key": "tags", "match": {"any": sorted(set(tags_any))}})
        if source: must.append({"key": "source", "match": {"value": source}})
        if created_at_gte: must.append({"key": "created_at", "range": {"gte": created_at_gte}})
        payload = {"must": must}
        if exclude_memory_id: payload["must_not"] = [{"key": "memory_id", "match": {"value": exclude_memory_id}}]
        return payload
    def search(self, vector, owners, limit, **filters):
        payload = {"vector": {"name": "content", "vector": vector}, "limit": limit, "with_payload": True, "filter": self.filter_for(owners, **filters)}
        return self._request(f"/collections/{self.collection_alias}/points/search", payload).get("result", [])
