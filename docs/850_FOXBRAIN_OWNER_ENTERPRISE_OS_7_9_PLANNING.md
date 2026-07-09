# FoxBrain Owner/Enterprise OS 7.9 Planning

## Goal

The 7.9 package clarifies that FoxBrain should not become one mixed system. It should be planned as one private owner system and one enterprise employee system.

## System 1: FoxBrain Owner OS

Domain: `huyan.vafox.com`

Positioning: boss private enterprise brain.

Primary use:

- Personal business brain
- Private asset database
- Company structure library
- License and contract archive
- Trademark and brand library
- Capital management
- Store asset library
- Decision AI assistant

This system is not for ordinary employees. It stores owner private knowledge, sensitive enterprise assets and high-permission decision material.

## System 2: FoxBrain Enterprise OS

Domain: `ai.vafox.com`

Positioning: employee-facing enterprise operations and collaboration system.

Primary use:

- Employee workspace
- Store operations
- Member points
- Enterprise WeChat
- Training
- Supplier collaboration
- Promotion content
- AI business assistant

This system should be simpler and more suitable for employees, store managers, operations and finance.

## Partial Sync

The two systems are not fully connected. They use partial synchronization only.

Allowed sync domains:

- Store profile data
- Brand profile data
- Supplier profile data
- Contract summaries
- Employee basic profile
- Member operating summary
- Sales operating data
- Rent and fee summary
- Inventory and sales analysis
- Training policy

Blocked sync domains:

- Personal capital
- Equity structure
- Family company data
- Firewall company data
- Core contract original files
- Sensitive finance documents
- Executive decision records
- Owner operating notes

## Data Middle Platform

SAP remains the independent original operating-data server.

Flow:

1. SAP independent server keeps original operating data.
2. Nightly read-only sync.
3. Data middle platform cleans sales, inventory, members, products, employees and suppliers.
4. Owner OS receives decision, asset, contract and structure views.
5. Enterprise OS receives store, employee, member, WeCom and promotion views.

## API

- `/api/owner-enterprise`
- `/api/owner-enterprise/contract`
- `/api/owner-enterprise/sync-policy`
- `/api/owner-enterprise/classify?domain=stores`

## Page

- `/owner-enterprise-plan`

## Guardrails

- Sensitive owner data never syncs to the employee system.
- Contract original files never sync.
- Unknown domains require architecture review.
- Permission changes and sensitive sync policies require human approval.
