# Sprint018.5 Evidence Audit Report

## Evidence Categories

Enterprise Copilot can now cite:

- `sync_freshness`
- `business_metrics_snapshots`
- `data_lake_sources`
- `business_health`
- `inventory_intelligence`
- `brand_intelligence`
- `store_intelligence`
- `sap_inventory`
- `sap_sales`
- `enterprise_objects`
- `knowledge_graph_nodes`
- `business_rules`
- `decision_insights`
- `daily_intelligence_reports`
- `daily_intelligence_items`
- `enterprise_memories`
- global search result categories

## Calibration Questions

### 今天企业有什么主要风险？

Expected evidence:

- Daily Intelligence
- Business Health
- Decision Insights
- Business Rules
- Sync freshness

### Osprey库存怎么样？有哪些风险？

Expected evidence:

- Inventory Intelligence
- Brand Intelligence
- SAP inventory
- SAP sales
- Business Rules
- Decision evidence

### Kailas销售和库存表现怎么样？

Expected evidence:

- Brand Intelligence
- SAP sales
- SAP inventory
- Inventory Intelligence
- Data Lake metrics

### 南山店经营情况怎么样？

Expected evidence:

- Store Intelligence
- SAP sales
- SAP inventory
- Decision Insights
- Business Health

### Data Insufficient Question

Expected behavior:

```text
当前数据不足，无法形成可靠结论。
```

## Audit Rule

Reliable answers require both general enterprise evidence and entity-specific evidence when the question names a brand or store.

No secrets, database credentials, or SAP connection strings are included in this report.

