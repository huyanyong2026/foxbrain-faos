import io
import json
import os
from wsgiref.util import setup_testing_defaults

os.environ.setdefault("DATABASE_URL", "postgresql://unused")
os.environ.setdefault("MINIO_ENDPOINT", "http://minio:9000")
os.environ.setdefault("MINIO_ROOT_USER", "test")
os.environ.setdefault("MINIO_ROOT_PASSWORD", "test")

from services.memory.app import create_app


class FakeMemoryService:
    def __init__(self): self.items = {}; self.deleted = []
    def create(self, name, content, content_type, source, owner, metadata, tags=()):
        memory_id = "memory-1"; self.items[memory_id] = {"id": memory_id, "name": name, "type": content_type, "size": len(content), "source": source, "owner": owner, "metadata": metadata, "tags": list(tags), "storage_path": "memory/memory-1/" + name, "status": "active", "content": content}; return {"memory_id": memory_id, "storage_path": self.items[memory_id]["storage_path"]}
    def get(self, memory_id):
        item = self.items.get(memory_id)
        return {key: value for key, value in item.items() if key != "content"} if item and item["status"] == "active" else None
    def search(self, query, owner=None, tag=None):
        return [self.get(key) for key, item in self.items.items() if self.get(key) and query.lower() in (item["name"] + json.dumps(item["metadata"])).lower() and (not owner or item["owner"] == owner) and (not tag or tag in item["tags"])]
    def delete(self, memory_id):
        if not self.get(memory_id): return False
        self.items[memory_id]["status"] = "deleted"; self.deleted.append(memory_id); return True
    def content(self, memory_id):
        return (self.get(memory_id), self.items[memory_id]["content"]) if self.get(memory_id) else None


def request(app, method, path, payload=b"", content_type="application/json"):
    environ = {}; setup_testing_defaults(environ); environ.update({"REQUEST_METHOD": method, "PATH_INFO": path.split("?", 1)[0], "QUERY_STRING": path.partition("?")[2], "CONTENT_TYPE": content_type, "CONTENT_LENGTH": str(len(payload)), "wsgi.input": io.BytesIO(payload)})
    captured = {}; body = b"".join(app(environ, lambda status, headers: captured.update(status=status, headers=headers)))
    return int(captured["status"][:3]), body


def test_receive_search_read_delete_and_health():
    service = FakeMemoryService(); app = create_app(service)
    status, body = request(app, "GET", "/health")
    assert status == 200 and json.loads(body)["service"] == "memory"
    boundary = "MemoryFactoryBoundary"
    payload = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"source\"\r\n\r\ntest\r\n"
               f"--{boundary}\r\nContent-Disposition: form-data; name=\"owner\"\r\n\r\nalice\r\n"
               f"--{boundary}\r\nContent-Disposition: form-data; name=\"metadata\"\r\n\r\n{{\"department\":\"R&D\"}}\r\n"
               f"--{boundary}\r\nContent-Disposition: form-data; name=\"tags\"\r\n\r\n[\"quarterly\", \"finance\"]\r\n"
               f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"brief.txt\"\r\nContent-Type: text/plain\r\n\r\nhello\r\n--{boundary}--\r\n").encode()
    status, body = request(app, "POST", "/api/v1/memory/receive", payload, f"multipart/form-data; boundary={boundary}")
    assert status == 201 and json.loads(body)["memory_id"] == "memory-1"
    status, body = request(app, "GET", "/api/v1/memory/search?q=R%26D")
    assert status == 200 and json.loads(body)["items"][0]["name"] == "brief.txt"
    status, body = request(app, "GET", "/api/v1/memory/items/memory-1")
    assert status == 200 and json.loads(body)["owner"] == "alice" and json.loads(body)["tags"] == ["finance", "quarterly"]
    status, _ = request(app, "DELETE", "/api/v1/memory/items/memory-1")
    assert status == 204 and service.deleted == ["memory-1"]


def test_receive_json_input_and_tag_filtering():
    service = FakeMemoryService(); app = create_app(service)
    payload = json.dumps({"name": "plan.json", "content": "important", "type": "application/json", "source": "api", "owner": "bob", "metadata": {"period": "2026-Q3"}, "tags": ["planning"]}).encode()
    status, body = request(app, "POST", "/api/v1/memory/receive", payload)
    assert status == 201 and json.loads(body)["memory_id"] == "memory-1"
    status, body = request(app, "GET", "/api/v1/memory/search?q=2026&owner=bob&tag=planning")
    assert status == 200 and json.loads(body)["items"][0]["name"] == "plan.json"
