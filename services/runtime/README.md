# FoxBrain Runtime

`POST /api/runtime/wecom/query` is the read-only WeCom entry point. It resolves
the supplied FoxBrain identity scope, applies RBAC, selects the role-specific
intelligence route and returns business evidence plus an audit id. WeCom calls
this service, never Dify directly.

Routes: CEO → `huyan-ceo-intelligence`; Store Manager → `store-intelligence`;
Buyer → `procurement-intelligence`; Employee → `sales-intelligence`.

The response always contains 经营摘要, 数据依据, 风险, AI建议 and Citation. If no
verified evidence is available, it explicitly says so rather than creating facts.
All routes are read-only: SAP writes, automatic procurement, sales and payments
are not supported.

## Core Evidence Adapter

Set `CORE_DATA_URL` and the least-privileged `CORE_DATA_TOKEN` to enable the
adapter. It reads only the five `/api/v1/{domain}` endpoints and retains the
source, timestamp, version, and confidence fields in every citation. Without
both settings, the Runtime safely returns the explicit missing-evidence response.
CEO reads Sales, Inventory, and Customer; Buyer reads Product and Inventory;
Store Manager reads Store, Sales, and Customer.
