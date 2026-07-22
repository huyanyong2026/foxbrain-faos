"""Sprint 1 FastAPI foundation: identity, read-only Core, and AI query flow.

The module intentionally has no SAP connector.  Production Core is populated by
the SAP mirror, while this service only exposes the four normalized resources
through GET endpoints.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="VAFOX FoxBrain Foundation", version="1.0.0-sprint1")

ROLE_PERMISSIONS = {
    "ceo": {"*"},
    "manager": {"ai.query", "core.product.read", "core.sales.read", "core.inventory.read", "core.store.read"},
    "store_manager": {"ai.query", "core.product.read", "core.sales.read", "core.inventory.read", "core.store.read"},
    "employee": {"ai.query", "core.product.read"},
    "buyer": {"ai.query", "core.product.read", "core.inventory.read"},
    "product_manager": {"ai.query", "core.product.read", "core.sales.read", "core.inventory.read"},
}
REDIRECTS = {"ceo": "https://huyan.vafox.com", "employee": "https://ai.vafox.com", "system": "https://control.vafox.com"}
SECRET = os.environ.get("FOXBRAIN_TOKEN_SECRET", "development-only-change-before-production").encode()
TOKEN_TTL = int(os.environ.get("FOXBRAIN_TOKEN_TTL_SECONDS", "28800"))


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1, max_length=512)


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    resource: Literal["product", "sales", "inventory", "store"] = "product"
    store_id: str | None = Field(default=None, max_length=80)


# Replace these seeds with an IdP-backed PostgreSQL repository in deployment.
USERS = {
    "ceo": {"password": "change-me", "id": "usr-ceo", "roles": ["ceo"], "scope": {"company": ["*"]}},
    "employee": {"password": "change-me", "id": "usr-employee", "roles": ["employee"], "scope": {"self": ["usr-employee"]}},
    "system": {"password": "change-me", "id": "svc-system", "roles": ["system"], "scope": {"company": ["*"]}},
}
AI_EMPLOYEES = {
    "ai-inventory-analyst": {"id": "ai-inventory-analyst", "name": "Inventory Analyst", "roles": ["buyer"], "data_scope": {"company": ["*"]}, "status": "active"},
}
CORE_DATA = {
    "product": [{"id": "product-001", "name": "Example Outdoor Pack", "source": "sap_mirror"}],
    "sales": [{"id": "sale-001", "store_id": "store-001", "amount": 0, "source": "sap_mirror"}],
    "inventory": [{"id": "inventory-001", "store_id": "store-001", "on_hand": 0, "source": "sap_mirror"}],
    "store": [{"id": "store-001", "name": "Example Store", "source": "sap_mirror"}],
}
AUDIT_LOG: list[dict] = []


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def audit(event: str, actor: str | None, **details: object) -> str:
    audit_id = f"audit_{secrets.token_urlsafe(12)}"
    AUDIT_LOG.append({"id": audit_id, "event": event, "actor": actor, "at": now(), "details": details})
    return audit_id


def permissions(roles: list[str]) -> set[str]:
    result: set[str] = set()
    for role in roles:
        result.update(ROLE_PERMISSIONS.get(role, set()))
    return result


def issue_token(context: dict) -> str:
    payload = {"sub": context["user_id"], "roles": context["roles"], "scope": context["data_scope"], "exp": int((datetime.now(timezone.utc) + timedelta(seconds=TOKEN_TTL)).timestamp())}
    encoded = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).rstrip(b"=")
    signature = hmac.new(SECRET, encoded, hashlib.sha256).digest()
    return f"{encoded.decode()}.{base64.urlsafe_b64encode(signature).rstrip(b'=').decode()}"


def identity_from_authorization(authorization: str | None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    try:
        encoded, supplied = authorization[7:].split(".", 1)
        expected = base64.urlsafe_b64encode(hmac.new(SECRET, encoded.encode(), hashlib.sha256).digest()).rstrip(b"=").decode()
        if not hmac.compare_digest(supplied, expected):
            raise ValueError("bad signature")
        payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
        if payload["exp"] < datetime.now(timezone.utc).timestamp():
            raise ValueError("expired")
        return {"user_id": payload["sub"], "roles": payload["roles"], "data_scope": payload["scope"], "permissions": sorted(permissions(payload["roles"]))}
    except (KeyError, ValueError, json.JSONDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from None


def require(identity: dict, permission: str) -> None:
    if "*" not in identity["permissions"] and permission not in identity["permissions"]:
        audit("permission.denied", identity["user_id"], permission=permission)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing permission: {permission}")


def acl_allows(identity: dict, resource: str, store_id: str | None = None) -> bool:
    """ACL + data-scope gate; company scope is global, store scope is explicit."""
    scope = identity["data_scope"]
    if "*" in scope.get("company", []):
        return True
    if resource == "product" and identity["user_id"] in scope.get("self", []):
        return True
    return bool(store_id and store_id in scope.get("store", []))


@app.get("/healthz")
def health() -> dict:
    return {"status": "ok", "services": ["identity", "gateway", "core", "runtime"], "sap_mode": "read_only"}


@app.post("/gateway/v1/login")
def login(request: LoginRequest) -> dict:
    user = USERS.get(request.username)
    if not user or not hmac.compare_digest(request.password, user["password"]):
        audit("login.failed", request.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    context = {"user_id": user["id"], "roles": user["roles"], "data_scope": user["scope"], "permissions": sorted(permissions(user["roles"]))}
    route_role = "system" if request.username == "system" else ("ceo" if "ceo" in user["roles"] else "employee")
    audit_id = audit("login.succeeded", user["id"], roles=user["roles"])
    return {"access_token": issue_token(context), "token_type": "bearer", "expires_in": TOKEN_TTL, "session_id": secrets.token_urlsafe(24), "user_context": context, "redirect_to": REDIRECTS[route_role], "audit_id": audit_id}


@app.get("/identity/v1/me")
def me(authorization: str | None = Header(default=None)) -> dict:
    return identity_from_authorization(authorization)


@app.get("/identity/v1/ai-employees")
def ai_employees(authorization: str | None = Header(default=None)) -> dict:
    identity = identity_from_authorization(authorization)
    if "*" not in identity["permissions"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="AI employee registry is restricted")
    return {"data": list(AI_EMPLOYEES.values())}


@app.get("/core/v1/{resource}")
def core_read(resource: Literal["product", "sales", "inventory", "store"], authorization: str | None = Header(default=None)) -> dict:
    identity = identity_from_authorization(authorization)
    require(identity, f"core.{resource}.read")
    if not all(acl_allows(identity, resource, item.get("store_id") or item.get("id")) for item in CORE_DATA[resource]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Data scope does not allow this resource")
    audit_id = audit("core.read", identity["user_id"], resource=resource, source="sap_mirror", mode="read_only")
    return {"data": CORE_DATA[resource], "source": "sap_mirror", "mode": "read_only", "audit_id": audit_id}


@app.post("/runtime/v1/query")
def ai_query(request: QueryRequest, authorization: str | None = Header(default=None)) -> dict:
    identity = identity_from_authorization(authorization)
    require(identity, "ai.query")
    required_permission = f"core.{request.resource}.read"
    require(identity, required_permission)
    if not acl_allows(identity, request.resource, request.store_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Data scope does not allow this query")
    citation = {"id": f"core:{request.resource}:sprint1", "source": "core.vafox.com", "resource": request.resource, "lineage": "SAP B1 -> Core mirror -> API -> AI Runtime", "mode": "read_only"}
    audit_id = audit("runtime.query", identity["user_id"], resource=request.resource, question=request.question, citation_id=citation["id"])
    return {"answer": f"FoxBrain received the {request.resource} query. Sprint 1 returns governed read-only Core context.", "identity_context": {"user_id": identity["user_id"], "roles": identity["roles"], "data_scope": identity["data_scope"]}, "citations": [citation], "audit_id": audit_id}


@app.get("/audit/v1/events")
def audit_events(authorization: str | None = Header(default=None)) -> dict:
    identity = identity_from_authorization(authorization)
    if "*" not in identity["permissions"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Audit access is restricted")
    return {"events": AUDIT_LOG}
