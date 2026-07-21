"""Trusted enterprise-memory authorization context and ACL predicates."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthContext:
    organization_id: str
    department_id: str | None
    owner_id: str
    role_scopes: frozenset[str]

    @property
    def is_admin(self) -> bool:
        return "admin" in self.role_scopes

    @property
    def upload_visibility(self) -> str:
        """Visibility is derived solely from trusted identity claims."""
        if self.is_admin or "organization" in self.role_scopes:
            return "organization"
        if self.department_id and "department" in self.role_scopes:
            return "department"
        return "private"

    @property
    def upload_role_scope(self) -> str:
        return "admin" if self.is_admin else self.upload_visibility


def auth_context(environ) -> AuthContext | None:
    """Build context from gateway-injected headers, never request payload fields."""
    organization_id = environ.get("HTTP_X_VAFOX_ORGANIZATION_ID", "").strip()
    owner_id = environ.get("HTTP_X_VAFOX_USER_ID", "").strip()
    department_id = environ.get("HTTP_X_VAFOX_DEPARTMENT_ID", "").strip() or None
    scopes = frozenset(scope.strip() for scope in environ.get("HTTP_X_VAFOX_ROLE_SCOPE", "").split(",") if scope.strip())
    return AuthContext(organization_id, department_id, owner_id, scopes) if organization_id and owner_id else None


def can_access(context: AuthContext, record: dict) -> bool:
    if context.organization_id != record.get("organization_id"):
        return False
    if context.is_admin or context.owner_id == record.get("owner_id"):
        return True
    visibility = record.get("visibility")
    return visibility == "organization" or (visibility == "department" and context.department_id == record.get("department_id"))
