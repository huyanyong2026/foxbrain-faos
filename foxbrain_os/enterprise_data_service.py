"""Read-only Enterprise Data Core client used by application services."""

from __future__ import annotations

import json
import hashlib
import hmac
import ssl
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen


class EnterpriseDataClient:
    def __init__(self, base_url, token, expected_host="core.vafox.com", timeout=8, cache_seconds=60):
        self.base_url = str(base_url or "").rstrip("/") + "/"
        self.token = str(token or "")
        self.expected_host = expected_host
        self.timeout = int(timeout)
        self.cache_seconds = max(0, int(cache_seconds))
        self._cache = {}
        parsed = urlparse(self.base_url)
        if parsed.scheme != "https" or parsed.hostname != expected_host:
            raise ValueError("Enterprise Data Core must use https://{}".format(expected_host))

    def get(self, path, params=None):
        clean_path = str(path or "").lstrip("/")
        url = urljoin(self.base_url, clean_path)
        if params:
            url += ("&" if "?" in url else "?") + urlencode(params)
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != self.expected_host:
            raise ValueError("Enterprise Data Core request escaped the approved host")
        cached = self._cache.get(url)
        now = time.monotonic()
        if cached and now - cached[0] <= self.cache_seconds:
            return cached[1]
        headers = {"Accept": "application/json", "User-Agent": "VAFOX-Enterprise/1.0"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        request = Request(url, headers=headers, method="GET")
        try:
            with urlopen(request, timeout=self.timeout, context=ssl.create_default_context()) as response:
                result = {
                    "ok": response.status == 200,
                    "status": response.status,
                    "data": json.loads(response.read().decode("utf-8")),
                    "url": url,
                }
        except HTTPError as exc:
            result = {"ok": False, "status": exc.code, "error": "core_http_error", "data": None}
        except (URLError, TimeoutError, json.JSONDecodeError):
            result = {"ok": False, "status": 503, "error": "core_unavailable", "data": None}
        if result["ok"]:
            self._cache[url] = (now, result)
        return result

    def summary(self):
        return self.get("api/v1/business/summary")

    def data_health(self):
        return self.get("api/v1/data-health")

    def objects(self, object_type, limit=50, offset=0):
        if object_type not in {"stores", "products", "brands", "suppliers", "customers"}:
            raise ValueError("unsupported business object")
        return self.get(
            "api/v1/objects/{}".format(object_type),
            {"limit": int(limit), "offset": int(offset)},
        )

    def customer_purchases(self, customer_id, limit=200):
        customer_id = str(customer_id or "").strip()
        if not customer_id:
            raise ValueError("customer id is required")
        return self.get(
            "api/v1/objects/customers/{}/purchases".format(quote(customer_id, safe="")),
            {"limit": int(limit)},
        )

    def explorer_customer_match(self, phone, limit=500):
        digits = "".join(character for character in str(phone or "") if character.isdigit())
        if digits.startswith("86") and len(digits) == 13:
            digits = digits[2:]
        if len(digits) != 11 or not digits.startswith("1"):
            raise ValueError("valid phone is required")
        phone_hash = hmac.new(self.token.encode("utf-8"), digits.encode("utf-8"), hashlib.sha256).hexdigest()
        return self.get(
            "api/v1/explorer/customer-match",
            {"phone_hash": phone_hash, "limit": int(limit)},
        )


def build_enterprise_data_client(base_url, token, **kwargs):
    return EnterpriseDataClient(base_url, token, **kwargs)
