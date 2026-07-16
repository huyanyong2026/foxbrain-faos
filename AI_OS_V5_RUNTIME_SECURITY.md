# AI OS V5 Runtime Security

Runtime APIs expose only operational metadata needed for deployment verification.

Allowed: version, status, build time, commit, environment, timestamp, and capability flags.

Forbidden: business data, customer data, financial data, SAP table rows, credentials, tokens, and internal network details.

RBAC and audit logging remain enforced for internal verification pages. Existing business logic and SAP read-only controls are unchanged.
