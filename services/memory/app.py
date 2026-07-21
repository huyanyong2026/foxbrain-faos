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
from .acl import auth_context, can_access


class ObjectStorage:
    """Small dependency-free S3-compatible client for the existing MinIO service."""
    def __init__(self, endpoint, access_key, secret_key, region="us-east-1"):
        if not endpoint or not access_key or not secret_key:
            raise ValueError("MinIO endpoint, access key, and secret key are required")
        self.endpoint, self.access_key, self.secret_key, self.region = endpoint.rstrip("/"), access_key, secret_key, region
    def request(self, method, bucket, key="", body=b"", content_type="application/octet-stream"):
        now = datetime.now(timezone.utc); stamp, amz_date = now.strftime("%Y%m%d"), now.strftime("%Y%m%dT%H%M%SZ")
        parsed = urlparse(self.endpoint)
        # A reverse proxy may publish MinIO below a path prefix.  SigV4 signs
        # that prefix too, otherwise MinIO returns SignatureDoesNotMatch.
        base_path = parsed.path.rstrip("/")
        target = f"{base_path}/{quote(bucket, safe='')}/{quote(key, safe='/') if key else ''}"
        host = parsed.netloc; payload_hash = hashlib.sha256(body).hexdigest()
        headers = {"host": host, "x-amz-content-sha256": payload_hash, "x-amz-date": amz_date}
        if body: headers["content-type"] = content_type
        canonical_headers = "".join(f"{key}:{value}\n" for key, value in sorted(headers.items()))
        signed_headers = ";".join(sorted(headers)); scope = f"{stamp}/{self.region}/s3/aws4_request"
        canonical = f"{method}\n{target}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        string_to_sign = f"AWS4-HMAC-SHA256\n{amz_date}\n{scope}\n{hashlib.sha256(canonical.encode()).hexdigest()}"
        def sign(key, value): return hmac.new(key, value.encode(), hashlib.sha256).digest()
        signing_key = sign(sign(sign(sign(("AWS4" + self.secret_key).encode(), stamp), self.region), "s3"), "aws4_request")
        headers["Authorization"] = f"AWS4-HMAC-SHA256 Credential={self.access_key}/{scope}, SignedHeaders={signed_headers}, Signature={hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()}"
        request = Request(f"{parsed.scheme}://{parsed.netloc}{target}", data=body if method in {"PUT", "POST"} else None, method=method, headers=headers)
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
    def create(self, name, content, content_type, source, acl, metadata, tags=()):
        memory_id = str(uuid.uuid4()); storage_path = f"memory/{memory_id}/{name}"
        self._ensure_bucket(); self.storage.put_object(self.bucket, storage_path, content, content_type)
        try:
            with self._connection() as connection, connection.cursor() as cursor:
                cursor.execute("INSERT INTO memory_items (id,name,type,size,source,owner,organization_id,department_id,owner_id,role_scope,visibility,metadata,storage_path) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s)", (memory_id, name, content_type, len(content), source, acl.owner_id, acl.organization_id, acl.department_id, acl.owner_id, acl.upload_role_scope, acl.upload_visibility, json.dumps(metadata), storage_path))
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
            cursor.execute("SELECT id,name,type,size,source,owner,organization_id,department_id,owner_id,role_scope,visibility,metadata,storage_path,status,created_at,updated_at FROM memory_items WHERE id=%s", (memory_id,)); row = cursor.fetchone()
            tags = self._tags(cursor, memory_id) if row else []
        if not row or row[8] == "deleted": return None
        keys = ("id", "name", "type", "size", "source", "owner", "organization_id", "department_id", "owner_id", "role_scope", "visibility", "metadata", "storage_path", "status", "created_at", "updated_at")
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
            cursor.execute(f"SELECT id,name,type,size,source,owner,organization_id,department_id,owner_id,role_scope,visibility,metadata,storage_path,status,created_at,updated_at FROM memory_items WHERE {clause} ORDER BY created_at DESC LIMIT 100", params); rows = cursor.fetchall()
            tags_by_item = {str(row[0]): self._tags(cursor, row[0]) for row in rows}
        keys = ("id", "name", "type", "size", "source", "owner", "organization_id", "department_id", "owner_id", "role_scope", "visibility", "metadata", "storage_path", "status", "created_at", "updated_at")
        results = [{key: value.isoformat() if isinstance(value, datetime) else str(value) if isinstance(value, uuid.UUID) else value for key, value in zip(keys, row)} for row in rows]
        for result in results: result["tags"] = tags_by_item[result["id"]]
        return results
    def iter_active(self, batch_size=200):
        """Yield all active memories for offline reindexing; never exposes deleted data."""
        offset = 0
        while True:
            with self._connection() as connection, connection.cursor() as cursor:
                cursor.execute("SELECT id FROM memory_items WHERE status='active' ORDER BY id LIMIT %s OFFSET %s", (batch_size, offset))
                identifiers = [str(row[0]) for row in cursor.fetchall()]
            if not identifiers: return
            for memory_id in identifiers:
                item = self.get(memory_id)
                if item: yield item
            offset += len(identifiers)

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
            metadata_text = fields.get("metadata").get_payload(decode=True).decode("utf-8") if fields.get("metadata") else "{}"
            tags_text = fields.get("tags").get_payload(decode=True).decode("utf-8") if fields.get("tags") else "[]"
        elif content_type.startswith("application/json"):
            try: payload = json.loads(_body(environ) or b"{}")
            except json.JSONDecodeError: return json_response(start_response, 400, {"error": "invalid_json"}), 400
            raw = str(payload.get("content", "")).encode("utf-8")
            name, media_type = payload.get("name"), payload.get("type", "text/plain")
            source, metadata_text = payload.get("source"), json.dumps(payload.get("metadata", {}))
            tags_text = json.dumps(payload.get("tags", []))
        else:
            return json_response(start_response, 415, {"error": "unsupported_media_type"}), 415
        context = auth_context(environ)
        if not context:
            return json_response(start_response, 401, {"error": "authentication_required"}), 401
        if not name or not source:
            return json_response(start_response, 400, {"error": "name_source_required"}), 400
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
        return json_response(start_response, 201, service.create(name, raw, media_type, source, context, metadata, tags)), 201
    return handler


def create_app(memory_service: MemoryService | None = None, retrieval_service=None, qdrant_client=None, index_jobs=None, dify_adapter=None):
    service = memory_service or MemoryService()
    class UnavailableRetrieval:
        def vector_search(self, **kwargs): raise RuntimeError("phase1b_not_configured")
        def related(self, **kwargs): raise RuntimeError("phase1b_not_configured")
    retrieval = retrieval_service or UnavailableRetrieval()
    # The Qdrant client is also injected.  Consequently this API never discovers
    # or connects to an environment's Qdrant instance during Phase 1A startup.
    qdrant = qdrant_client
    jobs = index_jobs
    adapter = dify_adapter
    # Phase 1B is deliberately opt-in through dependency injection.  This keeps
    # Phase 1A startup and its production topology untouched.
    def require_context(environ, start_response):
        context = auth_context(environ)
        if not context:
            json_response(start_response, 401, {"error": "authentication_required"})
        return context
    def vector_search(environ, start_response):
        try: payload = json.loads(_body(environ) or b"{}")
        except json.JSONDecodeError: return json_response(start_response, 400, {"error": "invalid_json"}), 400
        query, top_k, filters = payload.get("query"), payload.get("top_k", 10), payload.get("filters", {})
        if not isinstance(query, str) or not query.strip() or len(query) > 4096 or not isinstance(top_k, int) or not 1 <= top_k <= 50 or not isinstance(filters, dict):
            return json_response(start_response, 400, {"error": "invalid_vector_search_request"}), 400
        context = auth_context(environ)
        if not context: return json_response(start_response, 401, {"error": "authentication_required"}), 401
        # Owner and ACL fields in client filters are intentionally ignored.  The
        # gateway-derived AuthContext is the only authority for Qdrant scope.
        try:
            result = retrieval.vector_search(query=query, top_k=top_k, context=context,
                tags_any=tuple(filters.get("tags", filters.get("tags_any", ()))), source=filters.get("source"), created_at_gte=filters.get("created_after", filters.get("created_at_gte")), created_at_lte=filters.get("created_before"), exclude_memory_id=filters.get("exclude_memory_id"), memory_id=filters.get("memory_id"),
                include_text=bool(payload.get("include_text", False)), embedding_profile=payload.get("embedding_profile"))
        except ValueError as error:
            return json_response(start_response, 400, {"error": str(error)}), 400
        except RuntimeError as error:
            return json_response(start_response, 503, {"error": str(error)}), 503
        return json_response(start_response, 200, result), 200
    def require_item_owner(memory_id, environ):
        record = service.get(memory_id)
        if not record: return None, (404, {"error": "memory_not_found"})
        context = auth_context(environ)
        if not context: return None, (401, {"error": "authentication_required"})
        if not can_access(context, record): return None, (403, {"error": "forbidden"})
        return record, None
    def reindex(environ, start_response):
        if jobs is None: return json_response(start_response, 503, {"error": "phase1b_not_configured"}), 503
        memory_id = environ["PATH_INFO"].split("/")[4]; record, failure = require_item_owner(memory_id, environ)
        if failure: return json_response(start_response, *failure), failure[0]
        try: payload = json.loads(_body(environ) or b"{}")
        except json.JSONDecodeError: return json_response(start_response, 400, {"error": "invalid_json"}), 400
        profile, chunk_profile = payload.get("embedding_profile", "default"), payload.get("chunk_profile", "recursive-whitespace-v1")
        if not isinstance(profile, str) or not isinstance(chunk_profile, str) or not isinstance(payload.get("force", False), bool):
            return json_response(start_response, 400, {"error": "invalid_reindex_request"}), 400
        job, created = jobs.create(memory_id, record["owner_id"], profile, chunk_profile, record["updated_at"], payload.get("force", False))
        return json_response(start_response, 202, {"job_id": job.id, "status": job.status, "created": created}), 202
    def job_status(environ, start_response):
        if jobs is None: return json_response(start_response, 503, {"error": "phase1b_not_configured"}), 503
        job = jobs.get(environ["PATH_INFO"].rsplit("/", 1)[-1])
        if not job: return json_response(start_response, 404, {"error": "not_found"}), 404
        record, failure = require_item_owner(job.memory_id, environ)
        if failure: return json_response(start_response, *failure), failure[0]
        return json_response(start_response, 200, job.__dict__), 200
    def dify_retrieve(environ, start_response):
        if adapter is None: return json_response(start_response, 503, {"error": "phase1b_not_configured"}), 503
        try: payload = json.loads(_body(environ) or b"{}")
        except json.JSONDecodeError: return json_response(start_response, 400, {"error": "invalid_json"}), 400
        query, top_k, filters = payload.get("query"), payload.get("top_k", 5), payload.get("filters", {})
        if not isinstance(query, str) or not query.strip() or not isinstance(top_k, int) or not 1 <= top_k <= 50 or not isinstance(filters, dict):
            return json_response(start_response, 400, {"error": "invalid_retrieve_request"}), 400
        try: return json_response(start_response, 200, adapter.retrieve(environ.get("HTTP_AUTHORIZATION", "").removeprefix("Bearer "), query, top_k, filters)), 200
        except PermissionError: return json_response(start_response, 401, {"error": "invalid_service_credential"}), 401
        except RuntimeError as error: return json_response(start_response, 503, {"error": str(error)}), 503
    def related(environ, start_response):
        memory_id = environ["PATH_INFO"].split("/")[4]
        from urllib.parse import parse_qs
        args = parse_qs(environ.get("QUERY_STRING", "")); top_k = int(args.get("top_k", ["5"])[0]) if args.get("top_k", ["5"])[0].isdigit() else 0
        context = auth_context(environ)
        if not context: return json_response(start_response, 401, {"error": "authentication_required"}), 401
        if not 1 <= top_k <= 20: return json_response(start_response, 400, {"error": "invalid_top_k"}), 400
        record, failure = require_item_owner(memory_id, environ)
        if failure: return json_response(start_response, *failure), failure[0]
        try: result = retrieval.related(memory_id=memory_id, top_k=top_k, context=context, embedding_profile=args.get("embedding_profile", [None])[0])
        except KeyError: return json_response(start_response, 404, {"error": "not_found"}), 404
        except PermissionError: return json_response(start_response, 403, {"error": "forbidden"}), 403
        except RuntimeError as error: return json_response(start_response, 503, {"error": str(error)}), 503
        return json_response(start_response, 200, result), 200
    def item(environ, start_response):
        memory_id = environ["PATH_INFO"].rsplit("/", 1)[-1]
        if environ["REQUEST_METHOD"] == "GET":
            result, failure = require_item_owner(memory_id, environ)
            if failure: return json_response(start_response, *failure), failure[0]
            return json_response(start_response, 200, result), 200
        _, failure = require_item_owner(memory_id, environ)
        if failure: return json_response(start_response, *failure), failure[0]
        if not service.delete(memory_id):
            return json_response(start_response, 404, {"error": "not_found"}), 404
        start_response("204 No Content", [("Content-Length", "0")])
        return [b""], 204
    def search(environ, start_response):
        from urllib.parse import parse_qs
        query = parse_qs(environ.get("QUERY_STRING", "")).get("q", [""])[0]
        context = auth_context(environ)
        if not context: return json_response(start_response, 401, {"error": "authentication_required"}), 401
        owner = None
        tag = parse_qs(environ.get("QUERY_STRING", "")).get("tag", [None])[0]
        if not query: return json_response(start_response, 400, {"error": "query_required"}), 400
        return json_response(start_response, 200, {"items": [item for item in service.search(query, owner, tag) if can_access(context, item)]}), 200
    def vector_health(environ, start_response):
        if qdrant is None:
            return json_response(start_response, 503, {"status": "unavailable", "error": "phase1b_not_configured"}), 503
        try:
            return json_response(start_response, 200, qdrant.health()), 200
        except Exception:
            return json_response(start_response, 503, {"status": "unavailable", "error": "qdrant_unavailable"}), 503
    def collections(environ, start_response):
        if qdrant is None:
            return json_response(start_response, 503, {"error": "phase1b_not_configured"}), 503
        try:
            return json_response(start_response, 200, {"collections": qdrant.collections(), "alias": qdrant.collection_alias}), 200
        except Exception:
            return json_response(start_response, 503, {"error": "qdrant_unavailable"}), 503
    def collections_init(environ, start_response):
        if qdrant is None:
            return json_response(start_response, 503, {"error": "phase1b_not_configured"}), 503
        try:
            payload = json.loads(_body(environ) or b"{}")
            dimension = payload["dimension"]
            collection = payload.get("collection")
            distance = payload.get("distance", "Cosine")
            if not isinstance(dimension, int) or isinstance(dimension, bool) or not isinstance(collection, (str, type(None))) or not isinstance(distance, str):
                raise ValueError
        except (json.JSONDecodeError, KeyError, ValueError):
            return json_response(start_response, 400, {"error": "invalid_collection_init_request"}), 400
        try:
            return json_response(start_response, 201, qdrant.initialize(dimension, collection, distance)), 201
        except ValueError as error:
            return json_response(start_response, 400, {"error": str(error)}), 400
        except Exception:
            return json_response(start_response, 503, {"error": "qdrant_unavailable"}), 503
    routes = {("POST", "/api/v1/memory/receive"): _receive(service), ("GET", "/api/v1/memory/search"): search}
    base = service_app("memory", routes)
    def content(environ, start_response):
        memory_id = environ["PATH_INFO"].rsplit("/", 2)[-2]
        _, failure = require_item_owner(memory_id, environ)
        if failure: return json_response(start_response, *failure), failure[0]
        result = service.content(memory_id)
        if not result:
            return json_response(start_response, 404, {"error": "not_found"}), 404
        record, raw = result
        start_response("200 OK", [("Content-Type", record["type"]), ("Content-Length", str(len(raw))), ("Content-Disposition", f'attachment; filename="{record["name"]}"')])
        return [raw], 200
    def app(environ, start_response):
        path, method = environ["PATH_INFO"], environ["REQUEST_METHOD"]
        if path == "/health/vector" and method == "GET":
            return vector_health(environ, start_response)[0]
        if path == "/collections" and method == "GET":
            return collections(environ, start_response)[0]
        if path == "/collections/init" and method == "POST":
            return collections_init(environ, start_response)[0]
        if path == "/api/v1/search/vector" and method == "POST":
            return vector_search(environ, start_response)[0]
        if path.startswith("/api/v1/memory/") and path.endswith("/reindex") and method == "POST":
            return reindex(environ, start_response)[0]
        if path.startswith("/api/v1/index-jobs/") and method == "GET":
            return job_status(environ, start_response)[0]
        if path == "/api/v1/adapters/dify/retrieve" and method == "POST":
            return dify_retrieve(environ, start_response)[0]
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
