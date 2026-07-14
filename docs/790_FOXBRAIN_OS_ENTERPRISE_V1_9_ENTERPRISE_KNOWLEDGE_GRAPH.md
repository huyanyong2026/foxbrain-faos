# VAFOX Enterprise OS V1.9 Enterprise Knowledge Graph

V1.9 continues from V1.8 without rebuilding the system. It upgrades VAFOX from workflow automation into enterprise relationship understanding with role-based AI permissions.

## Scope

- Enterprise Knowledge Graph
- Entity Center
- AI Digital Employee Management
- AI Permission Engine
- Employee AI Assistant
- Customer AI Assistant
- Business Relationship Analysis
- Knowledge Graph Builder job

## Page and APIs

- Page: `/enterprise-knowledge-graph`
- Main API: `/api/enterprise-knowledge-graph`
- Entity API: `/api/enterprise-knowledge-graph/entities`
- Graph API: `/api/enterprise-knowledge-graph/graph`
- Permission API: `/api/enterprise-knowledge-graph/permissions`
- Employee fit API: `/api/enterprise-knowledge-graph/employee-fit`
- Relationship query API: `/api/enterprise-knowledge-graph/query`

## Database

- `entities`
- `entity_relations`
- `knowledge_graph_nodes`
- `knowledge_graph_edges`
- `digital_employees`
- `ai_permissions`
- `employee_ai_profiles`
- `customer_ai_profiles`
- `business_relationships`

## Guardrails

- SAP remains readonly.
- Knowledge Center, workflow records and task records are compatible sources.
- AI permissions isolate employee, store manager, boss and admin scopes.
- High-risk operations remain approval-gated.
- Mobile access uses existing responsive portal layout.

