# Changelog

## v1.0.0-core-release

- Core Data API v2.0.
- Five Business Domains: Product, Inventory, Customer, Store, and Sales.
- Evidence Layer for governed, attributable runtime responses.
- RBAC and data-scope enforcement.
- SAP Read Only Boundary: application requests use the SAP Mirror and have no
  SAP production write path.

## [v1.0.0] - 2026-07-22

### Added
- Production-ready V1 monorepo entrypoints for Gateway, AI Workspace, and Huyan.
- Shared UI and API client packages, repository validation, frontend builds, and Docker build coverage.
- Release governance, migration, deployment, pilot, and production-baseline documentation.

### Changed
- Standardized the production `FOXBRAIN_VERSION` release identity to `v1.0.0` across runtime metadata generation, runtime governance, and the production deployment workflow.

### Security
- Retained explicit repository exclusions for environment files, credentials, tokens, and local dependencies.
