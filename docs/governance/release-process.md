# Release Governance

A pull request requires passing CI, reviewer approval, and a green deployment validation before it can enter a protected release branch. Production deployment requires an environment approver. Secrets belong in GitHub/environment secret stores and must never be written to source, logs, or release notes.
