# Enterprise Data Core Read-Only API

This service is the only application-facing path to the SAP mirror.

- It loads credentials for the local `SAP_MIRROR` database only.
- It never loads or receives SAP production credentials.
- Only authenticated `GET` and `HEAD` requests are accepted.
- Raw SQL is not exposed. Table access is controlled by an allowlist.
- `gateway.vafox.com` receives only `public:read`; enterprise facts stay private.

Secrets belong in `/opt/foxbrain-core/api/core-api.env` on the server and must
never be committed.
