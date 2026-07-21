"""Read-only Knowledge API layered on M3 Memory Retrieval and ACL."""
from __future__ import annotations

import json
import uuid
from urllib.parse import parse_qs
from urllib.request import Request, urlopen
from wsgiref.simple_server import make_server

from packages.vafox_foundation.http import json_response, service_app
from services.memory.acl import auth_context, can_access
from services.memory.app import MemoryService

DOMAINS = frozenset({"company", "brand", "product", "sales", "store", "sop", "activity"})


class MemoryRetrievalClient:
    """Internal adapter for M3's retrieval HTTP boundary; it never accepts client ACL."""
    def __init__(self, endpoint="http://memory-api:8080", timeout_seconds=10):
        self.endpoint, self.timeout_seconds = endpoint.rstrip("/"), timeout_seconds

    def vector_search(self, query, top_k, context, tags_any=(), include_text=True, **_):
        payload = json.dumps({"query": query, "top_k": top_k, "include_text": include_text,
                              "filters": {"tags_any": list(tags_any)}}).encode()
        headers = {"Content-Type": "application/json", "X-VAFOX-Organization-ID": context.organization_id,
                   "X-VAFOX-User-ID": context.owner_id, "X-VAFOX-Department-ID": context.department_id or "",
                   "X-VAFOX-Role-Scope": ",".join(sorted(context.role_scopes))}
        request = Request(f"{self.endpoint}/api/v1/search/vector", data=payload, headers=headers, method="POST")
        with urlopen(request, timeout=self.timeout_seconds) as response:
            return json.loads(response.read() or b"{}")


def _query(environ):
    return {key: values[-1] for key, values in parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True).items()}


def _knowledge_fields(record):
    metadata = record.get("metadata") or {}
    knowledge = metadata.get("knowledge") if isinstance(metadata, dict) else {}
    return knowledge if isinstance(knowledge, dict) else {}


def create_app(memory_service=None, retrieval_service=None):
    memory = memory_service or MemoryService()
    retrieval = retrieval_service or MemoryRetrievalClient()

    def item_from_result(result, record):
        fields = _knowledge_fields(record)
        citation = dict(result.get("citation") or {})
        citation["memory_id"] = record["id"]
        return {"knowledge_id": record["id"], "domain": fields.get("domain"),
                "title": fields.get("title") or record.get("name"), "content": result.get("content", ""),
                "source": result.get("source") or record.get("source"), "citation": citation,
                "score": result.get("score"), "metadata": {key: fields.get(key) for key in ("brand", "product", "store")}}

    def search(environ, start_response, recommend=False):
        context = auth_context(environ)
        if not context: return json_response(start_response, 401, {"error": "authentication_required"}), 401
        args = _query(environ)
        query = args.get("need" if recommend else "query", "").strip()
        scenario = args.get("scenario", "").strip()
        default_limit, max_limit = (5, 20) if recommend else (10, 50)
        try: limit = int(args.get("limit", default_limit))
        except ValueError: limit = 0
        domain = args.get("domain")
        if (not query or len(query) > 4096 or not 1 <= limit <= max_limit or
                (recommend and (not scenario or len(scenario) > 200)) or (domain and domain not in DOMAINS)):
            return json_response(start_response, 400, {"error": "invalid_query"}), 400
        tags = tuple(tag.strip() for tag in args.get("tags", "").split(",") if tag.strip())
        # owner/organization/department/visibility query fields are intentionally ignored.
        try:
            response = retrieval.vector_search(query=query, top_k=limit * 3, context=context,
                                                tags_any=tags, include_text=True)
        except (RuntimeError, OSError, TimeoutError):
            return json_response(start_response, 503, {"error": "retrieval_unavailable"}), 503
        items = []
        for result in response.get("results", []):
            record = memory.get(result.get("memory_id", ""))
            if not record or record.get("status") != "active" or not can_access(context, record):
                continue
            fields = _knowledge_fields(record)
            if fields.get("domain") not in DOMAINS or (domain and fields.get("domain") != domain):
                continue
            if any(fields.get(key) != args[key] for key in ("brand", "product", "store") if args.get(key)):
                continue
            # Retrieval tag-any is only a candidate optimisation; AND semantics are enforced here.
            if any(tag not in record.get("tags", []) for tag in tags):
                continue
            items.append(item_from_result(result, record))
            if len(items) == limit: break
        payload = {"items": items, "next_cursor": None}
        if recommend:
            payload.update({"scenario": scenario, "need": query, "recommendation_score": "retrieval_score"})
        else:
            payload.update({"query_id": str(uuid.uuid4())})
        return json_response(start_response, 200, payload), 200

    def detail(environ, start_response):
        context = auth_context(environ)
        if not context: return json_response(start_response, 401, {"error": "authentication_required"}), 401
        knowledge_id = environ["PATH_INFO"].rsplit("/", 1)[-1]
        try: uuid.UUID(knowledge_id)
        except ValueError: return json_response(start_response, 400, {"error": "invalid_knowledge_id"}), 400
        record = memory.get(knowledge_id)
        if not record or record.get("status") != "active":
            return json_response(start_response, 404, {"error": "knowledge_not_found"}), 404
        if not can_access(context, record):
            return json_response(start_response, 403, {"error": "forbidden"}), 403
        fields = _knowledge_fields(record)
        if fields.get("domain") not in DOMAINS:
            return json_response(start_response, 404, {"error": "knowledge_not_found"}), 404
        resolved = memory.content(knowledge_id)
        if not resolved: return json_response(start_response, 404, {"error": "knowledge_not_found"}), 404
        _, raw = resolved
        content = raw.decode("utf-8", errors="replace")
        result = {"knowledge_id": record["id"], "domain": fields["domain"], "title": fields.get("title") or record["name"],
                  "source": record["source"], "brand": fields.get("brand"), "product": fields.get("product"),
                  "store": fields.get("store"), "tags": record.get("tags", []), "owner": record.get("owner_id"),
                  "visibility": record.get("visibility"), "created_at": record.get("created_at"),
                  "updated_at": record.get("updated_at"), "content": content,
                  "citations": [{"memory_id": record["id"], "source": record["source"]}], "metadata": fields}
        return json_response(start_response, 200, result), 200

    base = service_app("knowledge")
    def app(environ, start_response):
        path, method = environ["PATH_INFO"], environ["REQUEST_METHOD"]
        if method == "GET" and path == "/api/knowledge/search": return search(environ, start_response)[0]
        if method == "GET" and path == "/api/knowledge/recommend": return search(environ, start_response, True)[0]
        if method == "GET" and path.startswith("/api/knowledge/"): return detail(environ, start_response)[0]
        return base(environ, start_response)
    return app


def app(environ, start_response):
    """Lazy entry point; tests and compositions inject M3 dependencies explicitly."""
    return create_app()(environ, start_response)
if __name__ == "__main__":
    make_server("0.0.0.0", 8080, app).serve_forever()
