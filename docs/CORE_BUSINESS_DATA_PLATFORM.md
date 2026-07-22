# VAFOX Business Data Core

`core.vafox.com` is the read-only enterprise data core. Its only source is the
SAP mirror; it must never connect to SAP production for writes, alter inventory
or orders, or trigger automated procurement.

```
SAP B1 -> SAP Mirror (read only) -> Core Data Services -> AI Runtime -> Business Brain
```

## Domain APIs

All endpoints return the same evidence envelope: `data`, `source`, `timestamp`,
`version`, `confidence`, and `mode: read_only`.

| API | Domain fields | Required scopes |
| --- | --- | --- |
| `GET /api/v1/products` | `product_id`, `sku`, `brand`, `category`, `cost`, `price`, `status`, `lifecycle` | `product:read` or `enterprise:read` |
| `GET /api/v1/sales` | `order_id`, `store`, `sku`, `quantity`, `amount`, `margin`, `date` | `sales:read`, `store:read`, or `enterprise:read` |
| `GET /api/v1/inventory` | `sku`, `store_id`, `quantity`, `age`, `turnover`, `risk` | `inventory:read` or `enterprise:read` |
| `GET /api/v1/customers` | `customer_id`, `member_level`, `purchase_history`, `equipment_profile`, `activity_interest` | `customer:assigned`, `customers:read`, or `enterprise:read` |
| `GET /api/v1/stores` | `store_id`, `name`, `region`, `sales`, `target` | `store:read` or `enterprise:read` |

The token policy applies RBAC before a reader is called. A `store_manager` is
further restricted to assigned `store_ids` for store and sales domain data.

Sales facts are read from the synchronized `sap_sales_orders` and
`sap_sales_order_lines` projection in SAP Mirror, not from SAP B1 directly.

## Runtime evidence adapter

`CoreEvidenceAdapter` maps CEO questions to Sales, Inventory, and Customer;
Buyer questions to Product and Inventory; and Store questions to Store, Sales,
and Customer. It discards unavailable, malformed, or empty domain responses.
Consequently the runtime explicitly reports missing evidence rather than
creating an operating fact. Each returned citation retains source, timestamp,
version, and confidence.
