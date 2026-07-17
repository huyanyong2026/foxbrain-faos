# VAFOX Gateway API Design

Version: Genesis-Construction-003-1

## Runtime

### GET `/health/runtime`

Returns Gateway runtime health metadata.

## Identity

### POST `/identity/login`

Request:

```json
{
  "credential_type": "mobile_phone",
  "credential_value": "+8613800000000",
  "role_hint": "employee"
}
```

Response:

```json
{
  "vid": "VID-VAFOX-...",
  "session_token": "...",
  "roles": ["employee"],
  "route": "https://ai.vafox.com",
  "manual_system_selection": false
}
```

### GET `/identity/me`

Requires bearer session token. Returns VID and active roles.

### GET `/identity/context`

Requires bearer session token. Returns VID, roles, relationships, growth stage, permissions, mission context, and resolved route.

### GET `/identity/roles`

Requires bearer session token. Returns roles and permissions.

## Routing

### GET `/routing/resolve`

Requires bearer session token. Returns automatic route and confirms manual system selection is disabled.

## Security Notes

Tokens are signed, short-lived, and validated server-side. Public API responses must not include SAP records, private business data, secrets, or internal configuration.
