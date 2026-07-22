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
