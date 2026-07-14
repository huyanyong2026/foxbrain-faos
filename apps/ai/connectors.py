"""Read-only connectors for FoxBrain enterprise context sources."""

from __future__ import annotations

import json
import ssl
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


_CONNECTOR_CACHE = {}


class ReadOnlyJSONConnector:
    def __init__(self, base_url, expected_host, token="", timeout=8, cache_seconds=60):
        self.base_url = str(base_url or "").rstrip("/") + "/"
        self.expected_host = expected_host
        self.token = token
        self.timeout = int(timeout)
        self.cache_seconds = max(0, int(cache_seconds))
        self._cache = {}
        parsed = urlparse(self.base_url)
        if parsed.scheme != "https" or parsed.hostname != expected_host:
            raise ValueError("连接地址必须使用 https://{}".format(expected_host))

    def get_json(self, path):
        clean_path = str(path or "").lstrip("/")
        url = urljoin(self.base_url, clean_path)
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != self.expected_host:
            raise ValueError("连接请求超出允许的企业域名")
        cached = self._cache.get(url)
        now = time.monotonic()
        if cached and now - cached[0] <= self.cache_seconds:
            return cached[1]
        headers = {"Accept": "application/json", "User-Agent": "FoxBrain-AI/1.0"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        request = Request(url, headers=headers, method="GET")
        try:
            with urlopen(request, timeout=self.timeout, context=ssl.create_default_context()) as response:
                result = {"ok": True, "status": response.status, "data": json.loads(response.read().decode("utf-8"))}
                self._cache[url] = (now, result)
                return result
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            return {"ok": False, "error": str(exc), "data": None}

    def business_objects(self, object_type, limit=50, offset=0):
        if object_type not in {"stores", "products", "brands", "suppliers", "customers"}:
            raise ValueError("unsupported business object")
        return self.get_json(
            "api/v1/objects/{}?limit={}&offset={}".format(object_type, int(limit), int(offset))
        )

    def data_health(self):
        return self.get_json("api/v1/data-health")


def data_core_connector(base_url, token=""):
    key = ("core", str(base_url), str(token))
    if key not in _CONNECTOR_CACHE:
        _CONNECTOR_CACHE[key] = ReadOnlyJSONConnector(base_url, "core.vafox.com", token)
    return _CONNECTOR_CACHE[key]


def ceo_brain_connector(base_url, token=""):
    return ReadOnlyJSONConnector(base_url, "huyan.vafox.com", token)


def living_enterprise_connector(base_url, token=""):
    return ReadOnlyJSONConnector(base_url, "huyan.vafox.com", token)
