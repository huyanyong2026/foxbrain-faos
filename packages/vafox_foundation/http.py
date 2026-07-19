"""Dependency-free HTTP primitives shared by VAFOX foundation services."""
from __future__ import annotations

import json
import logging
import os
import time
import uuid
from http import HTTPStatus
from typing import Callable
from wsgiref.util import setup_testing_defaults

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(), format="%(message)s")
LOGGER = logging.getLogger("vafox")


def json_response(start_response, status: int, payload: dict):
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    start_response(f"{status} {HTTPStatus(status).phrase}", [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
        ("X-Content-Type-Options", "nosniff"),
    ])
    return [body]


def service_app(service_name: str, routes: dict[str, Callable] | None = None):
    routes = routes or {}
    def app(environ, start_response):
        setup_testing_defaults(environ)
        request_id = environ.get("HTTP_X_REQUEST_ID") or str(uuid.uuid4())
        path, method = environ["PATH_INFO"], environ["REQUEST_METHOD"]
        started = time.monotonic()
        try:
            service_paths = {service_name, service_name.replace("-data", "")}
            if method == "GET" and path in {"/health", "/healthz", "/api/v1/health", *(f"/api/v1/{name}/health" for name in service_paths)}:
                response = json_response(start_response, 200, {"status": "ok", "service": service_name})
                status = 200
            elif (handler := routes.get((method, path))):
                response, status = handler(environ, start_response)
            else:
                response = json_response(start_response, 404, {"error": "not_found", "request_id": request_id})
                status = 404
        except Exception:  # Do not leak internal details through the foundation boundary.
            LOGGER.exception(json.dumps({"event": "request_failed", "service": service_name, "request_id": request_id}))
            response = json_response(start_response, 500, {"error": "internal_error", "request_id": request_id})
            status = 500
        LOGGER.info(json.dumps({"event": "request", "service": service_name, "method": method,
                               "path": path, "status": status, "request_id": request_id,
                               "duration_ms": round((time.monotonic() - started) * 1000, 2)}))
        return response
    return app
