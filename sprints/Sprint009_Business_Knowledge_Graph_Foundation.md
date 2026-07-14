# Sprint009: Business Knowledge Graph Foundation

Status: Ready for Codex
Target: huyan.vafox.com
Priority: P0
Depends on: Sprint008.5 Business Calibration

---

# 1. Sprint Goal

Build the first version of VAFOX Business Knowledge Graph.

Goal:

Transform isolated business data into connected enterprise understanding.

```text
Data
↓
Objects
↓
Relationships
↓
Knowledge Graph
↓
AI Understanding
```

---

# 2. Core Principle

> A company is not a collection of tables. A company is a network of relationships.

VAFOX must understand:

- Which products belong to which brands.
- Which products sell in which stores.
- Which employees contribute to sales.
- Which suppliers support which brands.
- Which decisions affected which business objects.

---

# 3. Graph Model

Create graph foundation:

## Nodes

```text
Store
Brand
Product
SKU
Employee
Customer
Supplier
Contract
Project
Document
Knowledge
Memory
Decision
```

## Relations

```text
Brand HAS Product
Product HAS SKU
Store SELLS Product
Employee SELLS Product
Supplier PROVIDES Brand
Document DESCRIBES Object
Memory RELATES Object
Decision AFFECTS Object
```

---

# 4. Data Model

Create:

## knowledge_graph_nodes

Fields:

```text
id
node_type
object_id
name
metadata JSON
created_at
updated_at
```

## knowledge_graph_edges

Fields:

```text
id
source_node_id
target_node_id
relation_type
confidence
source_type
source_id
created_at
```

Important:

Every edge must keep source information.

No unsupported relationship should be generated.

---

# 5. Graph Generation

Initial generation sources:

- enterprise_objects
- object_relations
- business calibration results
- sap_sales
- sap_inventory
- enterprise_memories
- documents

Examples:

Sales row:

```text
Product → Store
Product → Employee
Product → Brand
```

Inventory row:

```text
Product → Store
Product → Inventory
```

---

# 6. Graph Explorer UI

Add:

```text
/knowledge-graph
```

Features:

- Search object
- View relationships
- View related knowledge
- View related memory
- View related sales/inventory summary

Initial version does not require complex visual graph rendering.

A relationship list view is acceptable.

---

# 7. AI Preparation

Prepare APIs for future AI reasoning:

```text
GET /api/graph/node/:id
GET /api/graph/relations/:id
GET /api/graph/context/:id
```

Context API should return:

- object information
- relationships
- related knowledge
- related memory
- metrics

---

# 8. CEO Dashboard Integration

Add:

Enterprise Understanding indicators:

- Graph nodes
- Graph relationships
- Connected brands
- Connected products

Do not overload homepage.

---

# 9. QA Acceptance

Sprint009 passes when:

- Graph nodes can be created from existing objects.
- Relationships can be created with source references.
- Product-brand-store relationships are available.
- Search can find graph context.
- Object pages can show graph relationships.
- Existing Sprint001-008.5 functions remain working.
- No production SAP connection.
- No automatic unsafe object creation.
- Smoke tests pass.

---

# 10. Codex Instruction

Do not rewrite existing system.

Incremental upgrade only.

Do not build ai.vafox.com.

Do not generate unsupported AI conclusions.

All graph relationships require traceable sources.

Deliver:

```text
SPRINT009_KNOWLEDGE_GRAPH_SUMMARY.md
SPRINT009_KNOWLEDGE_GRAPH_TEST_REPORT.md
```
