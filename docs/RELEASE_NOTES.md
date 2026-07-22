# FoxBrain Release Notes

## Release policy

FoxBrain uses semantic version tags in the form `vMAJOR.MINOR.PATCH`. The
current production baseline is **`v1.0.0`** and is exposed to deployed runtime
services through `FOXBRAIN_VERSION`.

Pushing a matching tag starts the Release GitHub Actions workflow. It derives
the changes since the prior tag, creates the GitHub release, and publishes
these auditable records:

- `release-metadata.json` — version, source commit, repository, prior tag, and
  publication timestamp.
- `CHANGELOG.md` — commit-subject changelog for the release range.
- `deployment-record.json` — immutable workflow-run reference and
  release-created status.

Production deployment remains a separate, protected action on `main`; creating
a tag does not bypass environment approval or trigger an SSH deployment.

## Security

Release records must contain only version and source-control information. Do
not place `.env` contents, production passwords, SAP credentials, API tokens,
or SSH private keys in release notes, generated assets, commits, or logs.
