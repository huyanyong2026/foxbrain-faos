"""Minimal JWT and authorization middleware for the foundation layer."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from functools import wraps


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def issue_token(subject: str, roles: list[str], ttl_seconds: int | None = None) -> str:
    ttl = ttl_seconds or int(os.getenv("JWT_TTL_SECONDS", "3600"))
    header = _b64(b'{"alg":"HS256","typ":"JWT"}')
    payload = _b64(json.dumps({"sub": subject, "roles": roles, "iat": int(time.time()),
                               "exp": int(time.time()) + ttl}, separators=(",", ":")).encode())
    signing_input = f"{header}.{payload}".encode()
    signature = _b64(hmac.new(os.environ["JWT_SECRET"].encode(), signing_input, hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"


def verify_token(token: str) -> dict:
    try:
        header, payload, signature = token.split(".")
        expected = _b64(hmac.new(os.environ["JWT_SECRET"].encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
        claims = json.loads(_unb64(payload))
        if not hmac.compare_digest(signature, expected) or claims["exp"] < time.time():
            raise ValueError("invalid token")
        return claims
    except (ValueError, KeyError, json.JSONDecodeError) as error:
        raise PermissionError("invalid or expired bearer token") from error


def require_roles(*allowed_roles):
    """WSGI middleware/decorator enforcing a bearer token and any listed role."""
    def decorator(app):
        @wraps(app)
        def wrapped(environ, start_response):
            authorization = environ.get("HTTP_AUTHORIZATION", "")
            if not authorization.startswith("Bearer "):
                return _forbidden(start_response, "missing bearer token")
            try:
                claims = verify_token(authorization.removeprefix("Bearer "))
            except PermissionError as error:
                return _forbidden(start_response, str(error))
            if allowed_roles and not set(claims.get("roles", [])).intersection(allowed_roles):
                return _forbidden(start_response, "insufficient permissions")
            environ["vafox.claims"] = claims
            return app(environ, start_response)
        return wrapped
    return decorator


def _forbidden(start_response, message):
    body = json.dumps({"error": "unauthorized", "message": message}).encode()
    start_response("401 Unauthorized", [("Content-Type", "application/json"), ("Content-Length", str(len(body)))])
    return [body]
