# FoxBrain Owner OS V1.0 Master Blueprint

## Goal

FoxBrain Owner OS V1.0 is the owner-facing enterprise second brain for `huyan.vafox.com`.

This phase pauses feature-first expansion and establishes the master design baseline before more page work.

## Ecosystem Boundary

- SAP Business One is the System of Record.
- FoxBrain Owner OS is the System of Intelligence.
- FoxBrain Enterprise OS is the System of Execution.

SAP stays independent. Owner OS reads synchronized data, documents and knowledge, but does not create SAP sales, purchase or inventory transactions.

## Fixed Owner Home

The first page has ten fixed centers only:

- Enterprise
- Assets
- Archive
- Knowledge
- AI
- Decision
- Data
- Projects
- Strategy
- System

No more first-level menus should be added. Each center expands as a tree after click-through.

## Product Principles

- Owner OS is not ERP.
- Owner OS is not OA.
- Everything important becomes knowledge.
- Everything important has relationships.
- AI is the default owner entry.

## V1.0 Blueprint Sections

- Product positioning and design principles
- Owner OS information architecture
- Core data models
- Page prototypes and navigation
- Permission system
- SAP read-only synchronization architecture
- AI knowledge base and query flow
- Technical architecture and deployment rules
- Codex development rules

## API Contract

- `/api/owner-os/master-blueprint`
- `/api/owner-os/product-principles`
- `/api/owner-os/v1-blueprint`
- `/api/owner-os/delivery-plan`

## Development Rule

Every future Owner OS change must keep compatibility, preserve SAP independence, update documentation and pass smoke tests.
