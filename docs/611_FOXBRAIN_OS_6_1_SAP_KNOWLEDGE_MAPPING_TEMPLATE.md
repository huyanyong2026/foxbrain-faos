# FoxBrain OS 6.1 SAP Knowledge Mapping Template

This template defines how SAP or synced business tables are transformed into knowledge objects.

| Mapping | Source | Key | Entity | Knowledge Category | Notes |
| --- | --- | --- | --- | --- | --- |
| `sap-map-brand` | `sap_items` / local `brands` | `brand` / `brand_code` | `brand` | 品牌知识 | Brand sales, margin, inventory and cooperation notes. |
| `sap-map-product` | `sap_items` / local `products` | `item_code` / `product_code` | `product` | 商品知识 | Product profile, SKU, pricing, season, sales and inventory context. |
| `sap-map-store` | `sap_store_sales_summary` / local `stores` | `whs_code` / `store_code` | `store` | 门店知识 | Store or warehouse performance and risk context. |
| `sap-map-customer` | `sap_customers` / local `customers` | `card_code` / `customer_code` | `customer` | 客户知识 | Customer profile and membership context. |
| `sap-map-supplier` | `sap_suppliers` / local `suppliers` | `card_code` / `supplier_code` | `supplier` | 供应商知识 | Supplier profile, contact and payment terms. |

## Generation Rules

- Use existing synced data first.
- Do not invent missing SAP fields.
- Generated knowledge defaults to `manager_only`.
- Every generated item must have `source_type = sap_knowledge`.
- Every generated item must have a source snapshot.
- Every generated item must be chunked for AI query.

## Acceptance Checklist

- SAP knowledge page opens.
- API returns mappings, snapshots and generation status.
- Manual generation creates or updates knowledge records.
- Querying Jarvis or AI Query can cite generated knowledge.
- No SAP writeback is performed.

