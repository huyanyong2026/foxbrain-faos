# VAFOX SAP Mirror

This stack hosts the read-only VAFOX mirror of the SAP B1 company database.

Security boundaries:

- SAP production is accessed with a dedicated login limited to `SELECT` and `VIEW DEFINITION`.
- No software is installed on the SAP production server.
- Secrets live only in `/opt/foxbrain-sap-mirror/mirror.env` on the production host.
- VAFOX applications read the mirror and never write SAP production data.
- AI output, calculations and decisions stay in VAFOX databases, not in the mirror.
- Initial BACPAC import and later refreshes require reconciliation before publication.

The mirror is bound to `127.0.0.1:11433`; it is not exposed to the public network.
