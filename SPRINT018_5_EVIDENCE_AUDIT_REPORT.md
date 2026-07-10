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

Production result:

```text
reliable=true
evidence_count=15
freshness_status=no_published_sync
```

Evidence categories observed:

- `business_health`
- `business_metrics_snapshots`
- `business_rules`
- `decision_insights`
- `knowledge_graph_nodes`
- `sync_freshness`

### Osprey库存怎么样？有哪些风险？

Expected evidence:

- Inventory Intelligence
- Brand Intelligence
- SAP inventory
- SAP sales
- Business Rules
- Decision evidence

Production result:

```text
reliable=false
missing=brand_evidence:Osprey, inventory_intelligence
evidence_count=15
freshness_status=no_published_sync
```

Audit conclusion:

```text
Production data is currently insufficient for a reliable Osprey inventory conclusion. Copilot correctly blocked a reliable conclusion.
```

### Kailas销售和库存表现怎么样？

Expected evidence:

- Brand Intelligence
- SAP sales
- SAP inventory
- Inventory Intelligence
- Data Lake metrics

Production result:

```text
reliable=false
missing=brand_evidence:Kailas, inventory_intelligence
evidence_count=15
freshness_status=no_published_sync
```

Audit conclusion:

```text
Production data is currently insufficient for a reliable Kailas sales/inventory conclusion. Copilot correctly blocked a reliable conclusion.
```

### 南山店经营情况怎么样？

Expected evidence:

- Store Intelligence
- SAP sales
- SAP inventory
- Decision Insights
- Business Health

Production result:

```text
reliable=false
missing=store_evidence:南山店, store_intelligence
evidence_count=15
freshness_status=no_published_sync
```

Audit conclusion:

```text
Production data is currently insufficient for a reliable Nanshan Store conclusion. Copilot correctly blocked a reliable conclusion.
```

### Data Insufficient Question

Expected behavior:

```text
当前数据不足，无法形成可靠结论。
```

Production result:

```text
question=火星店滑雪板库存怎么样？
reliable=false
missing=store_evidence:火星店, inventory_intelligence
```

## Audit Rule

Reliable answers require both general enterprise evidence and entity-specific evidence when the question names a brand or store.

No secrets, database credentials, or SAP connection strings are included in this report.
