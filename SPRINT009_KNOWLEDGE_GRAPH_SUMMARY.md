# Sprint009 Knowledge Graph Summary

## Scope

Sprint009 builds the first usable Business Knowledge Graph foundation for VAFOX Enterprise OS.

It is an incremental upgrade:

- No architecture rewrite.
- No ai.vafox.com work.
- No production SAP connection.
- Sprint001-008.5 features remain available.
- All graph relationships require traceable sources.

## Engine

VAFOX Enterprise OS module:

- Knowledge Graph

Connected upstream modules:

- Enterprise Drive
- Enterprise Data Lake
- Object Engine
- Knowledge Engine
- Memory Engine
- Dashboard Engine

## Database Changes

Existing graph tables are preserved and extended.

Extended `knowledge_graph_nodes`:

- `object_id`
- `name`
- `metadata`
- `source_type`
- `source_id`

Extended `knowledge_graph_edges`:

- `source_node_id`
- `target_node_id`
- `relation_type`
- `confidence`
- `source_type`
- `source_id`
- `metadata`

Compatibility is preserved for existing columns:

- `node_id`
- `entity_id`
- `label`
- `properties_json`
- `source_json`
- `edge_id`
- `from_node_id`
- `to_node_id`
- `edge_type`
- `evidence_json`

## Graph Generation

New builder:

- `build_business_knowledge_graph`

Generation sources:

- `enterprise_objects`
- `object_relations`
- `sap_sales`
- `sap_inventory`
- `documents`
- `knowledge_items`
- `enterprise_memories`
- `decision_memories`

Supported relationship examples:

- Brand `HAS_PRODUCT` Product
- Store `SELLS` Product
- Employee `SELLS` Product
- Store `STOCKS` Product
- Document `DESCRIBES` Object
- Knowledge `DESCRIBES` Object
- Memory `RELATES` Object

All graph relationships require traceable sources through:

- `source_type`
- `source_id`
- `evidence_json`

No unsupported relationship is generated.

## UI Changes

New page:

- `/knowledge-graph`

Features:

- Search graph nodes.
- View relationship list.
- View enterprise understanding indicators.
- Trigger graph build.
- Open node context JSON.

Updated object detail page:

- Shows Knowledge Graph relationships for the current object.
- Links to `/knowledge-graph`.

## API Changes

New and updated APIs:

- `GET /api/graph/summary`
- `GET /api/graph/nodes`
- `GET /api/graph/edges`
- `GET /api/graph/node/:id`
- `GET /api/graph/relations/:id`
- `GET /api/graph/context/:id`
- `GET /api/graph/search?q=`
- `POST /api/graph/build`

Context API returns:

- object/node information
- relationships
- neighbor nodes
- related knowledge
- related memory
- metrics

## Dashboard Changes

CEO Dashboard now includes Enterprise Understanding indicators:

- Graph nodes
- Graph relationships
- Connected brands
- Connected products

The homepage remains concise. Detailed graph content is behind `/knowledge-graph`.

## Search Changes

Global Search now includes:

- `knowledge_graph`
- `knowledge_graph_edge`

This allows graph context discovery from the existing search entry.

## Safety

No production SAP connection was made. Sprint009 only reads existing local tables and uploaded/imported SAP data already in VAFOX.

