# Enterprise Pack 15 - Decision Engine

## Goal

Pack 15 builds the Enterprise Decision Engine for VAFOX OS. It turns business signals
into explainable recommendations with data evidence, knowledge evidence, risk scoring,
confidence and approval gates.

## Core Rule

All business recommendations must be based on:

- Unified data model
- Unified KPI catalog
- Unified metrics service
- Enterprise knowledge
- Enterprise memory

Recommendations must show supporting evidence, risk score and confidence.

## API Contracts

- `/api/decision-engine/framework`
- `/api/decision-engine/risk-scoring`
- `/api/decision-engine/opportunities`
- `/api/decision-engine/recommendations`
- `/api/decision-engine/approval-gate`

## Risk Scoring

Risk scoring covers:

- Inventory
- Cash flow
- Supplier concentration
- Customer churn
- Margin anomalies

Each risk score includes rationale and evidence.

## Opportunity Engine

Opportunity discovery covers:

- Replenishment
- Transfers
- Promotions
- Membership campaigns
- Procurement optimization

Opportunity output remains draft-only until reviewed.

## Explainable Recommendations

Every recommendation includes:

- Data source
- Knowledge source
- Rule or model
- Confidence
- Supporting evidence
- Risk score
- Approval requirement

## Approval Gate

The following high-risk operations must enter manual approval and must not auto execute:

- Price adjustment
- Contract change
- Financial payment
- External publish
- SAP write-back
- HR action
- Customer data export

## Current Delivery

- Added Enterprise Decision Engine framework contract.
- Added risk scoring service.
- Added opportunity engine.
- Added explainable recommendation service.
- Added approval gate contract.
- Connected Enterprise Brain decision payload to the new decision engine.
