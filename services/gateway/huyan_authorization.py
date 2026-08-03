"""Huyan-specific translation from portal identity claims to Business API claims."""

HUYAN_PORTAL = "huyan.vafox.com"
HUYAN_CEO_ROLE = "VAFOX_CEO"
ALL_DATA = "ALL_DATA"


def business_authorization(claims: dict, path: str) -> tuple[list[str], str]:
    """Map the trusted Huyan CEO identity only for the aligned V1.4 APIs."""
    raw_roles = claims.get("role_scopes", claims.get("roles", claims.get("role", [])))
    if isinstance(raw_roles, str):
        raw_roles = [raw_roles]
    roles = [str(role) for role in raw_roles] if isinstance(raw_roles, list) else []
    data_scope = str(claims.get("data_scope", ""))
    aligned_paths = {
        "/api/business/sales-analysis",
        "/api/business/member-analysis",
        "/api/business/customer-analysis",
        "/api/business/product-analysis",
        "/api/business/inventory-analysis",
        "/api/business/customer-intelligence",
    }
    if (path in aligned_paths and claims.get("portal") == HUYAN_PORTAL
            and HUYAN_CEO_ROLE in roles and data_scope == ALL_DATA):
        roles = [*roles, "ceo"]
    return roles, data_scope
