"""VAFOX Memory Factory V1: receive, object storage, metadata, and text index APIs."""
from __future__ import annotations

import hashlib
import hmac
import io
import json
import os
import uuid
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
from typing import Any
from wsgiref.simple_server import make_server


from packages.vafox_foundation.http import json_response, service_app


class ObjectStorage:
    """Small dependency-free S3-compatible client for the existing MinIO service."""
    def __init__(self, endpoint, access_key, secret_key, region="us-east-1"):
        self.endpoint, self.access_key, self.secret_key, self.region = endpoint.rstrip("/"), access_key, secret_key, region
    def request(self, method, bucket, key="", body=b"", content_type="application/octet-stream"):
        now = datetime.now(timezone.utc); stamp, amz_date = now.strftime("%Y%m%d"), now.strftime("%Y%m%dT%H%M%SZ")
        target = f"/{quote(bucket, safe='')}/{quote(key, safe='/') if key else ''}"
        parsed = urlparse(self.endpoint); host = parsed.netloc; payload_hash = hashlib.sha256(body).hexdigest()
        headers = {"host": host, "x-amz-content-sha256": payload_hash, "x-amz-date": amz_date}
        if body: headers["content-type"] = content_type
        canonical_headers = "".join(f"{key}:{value}\n" for key, value in sorted(headers.items()))
        signed_headers = ";".join(sorted(headers)); scope = f"{stamp}/{self.region}/s3/aws4_request"
        canonical = f"{method}\n{target}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        string_to_sign = f"AWS4-HMAC-SHA256\n{amz_date}\n{scope}\n{hashlib.sha256(canonical.encode()).hexdigest()}"
        def sign(key, value): return hmac.new(key, value.encode(), hashlib.sha256).digest()
        signing_key = sign(sign(sign(sign(("AWS4" + self.secret_key).encode(), stamp), self.region), "s3"), "aws4_request")
        headers["Authorization"] = f"AWS4-HMAC-SHA256 Credential={self.access_key}/{scope}, SignedHeaders={signed_headers}, Signature={hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()}"
        request = Request(self.endpoint + target, data=body if method in {"PUT", "POST"} else None, method=method, headers=headers)
        try:
            return urlopen(request, timeout=float(os.getenv("STORAGE_TIMEOUT_SECONDS", "10")))
        except HTTPError as error:
            if error.code == 404: return None
            raise
    def ensure_bucket(self, bucket):
        if self.request("HEAD", bucket) is None: self.request("PUT", bucket)
    def put_object(self, bucket, key, body, content_type): self.request("PUT", bucket, key, body, content_type)
    def get_object(self, bucket, key):
        response = self.request("GET", bucket, key)
        return response.read() if response else None
    def delete_object(self, bucket, key): self.request("DELETE", bucket, key)


class MemoryService:
    def __init__(self):
        self.database_url = os.environ["DATABASE_URL"]
        self.bucket = os.getenv("MINIO_BUCKET", "vafox-memory")
        self.storage = ObjectStorage(os.environ["MINIO_ENDPOINT"], os.environ["MINIO_ROOT_USER"], os.environ["MINIO_ROOT_PASSWORD"], os.getenv("MINIO_REGION", "us-east-1"))
    def _connection(self):
        import psycopg2
        return psycopg2.connect(self.database_url)
    def _ensure_bucket(self): self.storage.ensure_bucket(self.bucket)
    def create(self, name, content, content_type, source, owner, metadata, tags=()):
        memory_id = str(uuid.uuid4()); storage_path = f"memory/{memory_id}/{name}"
        self._ensure_bucket(); self.storage.put_object(self.bucket, storage_path, content, content_type)
        try:
            with self._connection() as connection, connection.cursor() as cursor:
                cursor.execute("INSERT INTO memory_items (id,name,type,size,source,owner,metadata,storage_path) VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s)", (memory_id, name, content_type, len(content), source, owner, json.dumps(metadata), storage_path))
                cursor.execute("INSERT INTO storage_objects (id,memory_id,storage_path,bucket,size) VALUES (%s,%s,%s,%s,%s)", (str(uuid.uuid4()), memory_id, storage_path, self.bucket, len(content)))
                cursor.executemany("INSERT INTO memory_tags (memory_id,tag) VALUES (%s,%s)", [(memory_id, tag) for tag in tags])
        except Exception:
            self.storage.delete_object(self.bucket, storage_path); raise
        return {"memory_id": memory_id, "storage_path": storage_path}
    def _tags(self, cursor, memory_id):
        cursor.execute("SELECT tag FROM memory_tags WHERE memory_id=%s ORDER BY tag", (memory_id,))
        return [row[0] for row in cursor.fetchall()]
    def get(self, memory_id):
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT id,name,type,size,source,owner,metadata,storage_path,status,created_at,updated_at FROM memory_items WHERE id=%s", (memory_id,)); row = cursor.fetchone()
            tags = self._tags(cursor, memory_id) if row else []
        if not row or row[8] == "deleted": return None
        keys = ("id", "name", "type", "size", "source", "owner", "metadata", "storage_path", "status", "created_at", "updated_at")
        result = {key: value.isoformat() if isinstance(value, datetime) else str(value) if isinstance(value, uuid.UUID) else value for key, value in zip(keys, row)}
        result["tags"] = tags
        return result
    def content(self, memory_id):
        item = self.get(memory_id)
        if not item: return None
        raw = self.storage.get_object(self.bucket, item["storage_path"])
        return (item, raw) if raw is not None else None
    def delete(self, memory_id):
        item = self.get(memory_id)
        if not item: return False
        self.storage.delete_object(self.bucket, item["storage_path"])
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute("UPDATE memory_items SET status='deleted',updated_at=now() WHERE id=%s", (memory_id,)); cursor.execute("UPDATE storage_objects SET deleted_at=now() WHERE memory_id=%s", (memory_id,))
        return True
    def search(self, query, owner=None, tag=None):
        clause = "status='active' AND (name ILIKE %s OR metadata::text ILIKE %s)"; params = [f"%{query}%", f"%{query}%"]
        if owner: clause += " AND owner=%s"; params.append(owner)
        if tag: clause += " AND EXISTS (SELECT 1 FROM memory_tags WHERE memory_tags.memory_id=memory_items.id AND tag=%s)"; params.append(tag)
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(f"SELECT id,name,type,size,source,owner,metadata,storage_path,status,created_at,updated_at FROM memory_items WHERE {clause} ORDER BY created_at DESC LIMIT 100", params); rows = cursor.fetchall()
            tags_by_item = {str(row[0]): self._tags(cursor, row[0]) for row in rows}
        keys = ("id", "name", "type", "size", "source", "owner", "metadata", "storage_path", "status", "created_at", "updated_at")
        results = [{key: value.isoformat() if isinstance(value, datetime) else str(value) if isinstance(value, uuid.UUID) else value for key, value in zip(keys, row)} for row in rows]
        for result in results: result["tags"] = tags_by_item[result["id"]]
        return results

def _body(environ):
    return environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0))


def _receive(service: MemoryService):
    def handler(environ, start_response):
        content_type = environ.get("CONTENT_TYPE", "")
        if content_type.startswith("multipart/form-data"):
            from email.parser import BytesParser
            raw_request = _body(environ)
            message = BytesParser().parsebytes(f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + raw_request)
            fields = {}
            for part in message.walk():
                if part.is_multipart(): continue
                field_name = part.get_param("name", header="content-disposition")
                if field_name: fields[field_name] = part
            upload = fields.get("file")
            if upload is None or not upload.get_filename():
                return json_response(start_response, 400, {"error": "file_required"}), 400
            raw, name = upload.get_payload(decode=True) or b"", upload.get_filename()
            media_type = upload.get_content_type() or "application/octet-stream"
            source = fields.get("source").get_payload(decode=True).decode("utf-8").strip() if fields.get("source") else None
            owner = fields.get("owner").get_payload(decode=True).decode("utf-8").strip() if fields.get("owner") else None
            metadata_text = fields.get("metadata").get_payload(decode=True).decode("utf-8") if fields.get("metadata") else "{}"
            tags_text = fields.get("tags").get_payload(decode=True).decode("utf-8") if fields.get("tags") else "[]"
        elif content_type.startswith("application/json"):
            try: payload = json.loads(_body(environ) or b"{}")
            except json.JSONDecodeError: return json_response(start_response, 400, {"error": "invalid_json"}), 400
            raw = str(payload.get("content", "")).encode("utf-8")
            name, media_type = payload.get("name"), payload.get("type", "text/plain")
            source, owner, metadata_text = payload.get("source"), payload.get("owner"), json.dumps(payload.get("metadata", {}))
            tags_text = json.dumps(payload.get("tags", []))
        else:
            return json_response(start_response, 415, {"error": "unsupported_media_type"}), 415
        if not name or not source or not owner:
            return json_response(start_response, 400, {"error": "name_source_owner_required"}), 400
        if any(character in name for character in ("/", "\\", "\r", "\n")):
            return json_response(start_response, 400, {"error": "invalid_file_name"}), 400
        try:
            metadata = json.loads(metadata_text)
            if not isinstance(metadata, dict): raise ValueError()
        except (TypeError, ValueError, json.JSONDecodeError):
            return json_response(start_response, 400, {"error": "metadata_must_be_object"}), 400
        try:
            tags = json.loads(tags_text)
            if not isinstance(tags, list) or any(not isinstance(tag, str) or not tag.strip() for tag in tags): raise ValueError()
            tags = sorted(set(tag.strip() for tag in tags))
        except (TypeError, ValueError, json.JSONDecodeError):
            return json_response(start_response, 400, {"error": "tags_must_be_string_array"}), 400
        return json_response(start_response, 201, service.create(name, raw, media_type, source, owner, metadata, tags)), 201
    return handler


def create_app(memory_service: MemoryService | None = None, retrieval_service=None):
    service = memory_service or MemoryService()
    class UnavailableRetrieval:
        def vector_search(self, **kwargs): raise RuntimeError("phase1b_not_configured")
        def related(self, **kwargs): raise RuntimeError("phase1b_not_configured")
    retrieval = retrieval_service or UnavailableRetrieval()
    # Phase 1B is deliberately opt-in through dependency injection.  This keeps
    # Phase 1A startup and its production topology untouched.
    def authorized_owners(environ):
        # Authentication middleware supplies this trusted, comma-separated claim.
        # A client body field is never used to expand the authorization boundary.
        return tuple(owner.strip() for owner in environ.get("HTTP_X_VAFOX_AUTHORIZED_OWNERS", "").split(",") if owner.strip())
    def vector_search(environ, start_response):
        try: payload = json.loads(_body(environ) or b"{}")
        except json.JSONDecodeError: return json_response(start_response, 400, {"error": "invalid_json"}), 400
        query, top_k, filters = payload.get("query"), payload.get("top_k", 10), payload.get("filters", {})
        if not isinstance(query, str) or not query.strip() or len(query) > 4096 or not isinstance(top_k, int) or not 1 <= top_k <= 50 or not isinstance(filters, dict):
            return json_response(start_response, 400, {"error": "invalid_vector_search_request"}), 400
        owners = authorized_owners(environ)
        requested = filters.get("owners")
        if not owners: return json_response(start_response, 401, {"error": "authentication_required"}), 401
        if requested is not None and (not isinstance(requested, list) or not set(requested).issubset(owners)):
            return json_response(start_response, 403, {"error": "owner_not_authorized"}), 403
        try:
            result = retrieval.vector_search(query=query, top_k=top_k, owners=tuple(requested) if requested is not None else owners,
                tags_any=tuple(filters.get("tags_any", ())), source=filters.get("source"), created_at_gte=filters.get("created_at_gte"),
                include_text=bool(payload.get("include_text", False)), embedding_profile=payload.get("embedding_profile"))
        except RuntimeError as error:
            return json_response(start_response, 503, {"error": str(error)}), 503
        return json_response(start_response, 200, result), 200
    def related(environ, start_response):
        memory_id = environ["PATH_INFO"].split("/")[4]
        from urllib.parse import parse_qs
        args = parse_qs(environ.get("QUERY_STRING", "")); top_k = int(args.get("top_k", ["5"])[0]) if args.get("top_k", ["5"])[0].isdigit() else 0
        owners = authorized_owners(environ)
        if not owners: return json_response(start_response, 401, {"error": "authentication_required"}), 401
        if not 1 <= top_k <= 20: return json_response(start_response, 400, {"error": "invalid_top_k"}), 400
        try: result = retrieval.related(memory_id=memory_id, top_k=top_k, owners=owners, embedding_profile=args.get("embedding_profile", [None])[0])
        except KeyError: return json_response(start_response, 404, {"error": "not_found"}), 404
        except PermissionError: return json_response(start_response, 403, {"error": "forbidden"}), 403
        except RuntimeError as error: return json_response(start_response, 503, {"error": str(error)}), 503
        return json_response(start_response, 200, result), 200
    def item(environ, start_response):
        memory_id = environ["PATH_INFO"].rsplit("/", 1)[-1]
        if environ["REQUEST_METHOD"] == "GET":
            result = service.get(memory_id)
            if not result:
                return json_response(start_response, 404, {"error": "not_found"}), 404
            return json_response(start_response, 200, result), 200
        if not service.delete(memory_id):
            return json_response(start_response, 404, {"error": "not_found"}), 404
        start_response("204 No Content", [("Content-Length", "0")])
        return [b""], 204
    def search(environ, start_response):
        from urllib.parse import parse_qs
        query = parse_qs(environ.get("QUERY_STRING", "")).get("q", [""])[0]
        owner = parse_qs(environ.get("QUERY_STRING", "")).get("owner", [None])[0]
        tag = parse_qs(environ.get("QUERY_STRING", "")).get("tag", [None])[0]
        if not query: return json_response(start_response, 400, {"error": "query_required"}), 400
        return json_response(start_response, 200, {"items": service.search(query, owner, tag)}), 200
    routes = {("POST", "/api/v1/memory/receive"): _receive(service), ("GET", "/api/v1/memory/search"): search}
    base = service_app("memory", routes)
    def content(environ, start_response):
        memory_id = environ["PATH_INFO"].rsplit("/", 2)[-2]
        result = service.content(memory_id)
        if not result:
            return json_response(start_response, 404, {"error": "not_found"}), 404
        record, raw = result
        start_response("200 OK", [("Content-Type", record["type"]), ("Content-Length", str(len(raw))), ("Content-Disposition", f'attachment; filename="{record["name"]}"')])
        return [raw], 200
    def app(environ, start_response):
        path, method = environ["PATH_INFO"], environ["REQUEST_METHOD"]
        if path == "/api/v1/search/vector" and method == "POST":
            return vector_search(environ, start_response)[0]
        if path.startswith("/api/v1/memory/") and path.endswith("/related") and method == "GET":
            return related(environ, start_response)[0]
        if path.startswith("/api/v1/memory/items/") and path.endswith("/content") and method == "GET":
            return content(environ, start_response)[0]
        if path.startswith("/api/v1/memory/items/") and method in {"GET", "DELETE"}:
            return item(environ, start_response)[0]
        return base(environ, start_response)
    return app


app = create_app()
if __name__ == "__main__":
    make_server("0.0.0.0", 8080, app).serve_forever()
