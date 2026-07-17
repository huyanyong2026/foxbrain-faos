# Production Deploy Trigger Fix Report

## Before

- `.github/workflows/production-deploy.yml` was audited for production deployment governance.
- The production deployment path required explicit operational controls so that a merge to `main` can promote the release without relying only on a manual emergency dispatch path.
- Manual deployment remains necessary for emergency recovery, but it must not be the only production activation mechanism.

## Root cause

- Production deploy governance did not fully codify the release path from a merged `main` commit through deploy and verification.
- Without a controlled `push` trigger on `main`, merged Genesis changes could remain in the repository without an automatic production deployment.
- The workflow also needed explicit pre-deploy release guards, public runtime verification, rollback behavior, and failure reporting in the same production workflow.

## Changes

- Kept `workflow_dispatch` for manual emergency production deployment.
- Added and retained a controlled automatic trigger for pushes to `main`:

  ```yaml
  on:
    push:
      branches:
        - main
    workflow_dispatch:
  ```

- Added a pre-deploy release commit guard that verifies the checked-out commit exactly matches `github.sha`, confirms the worktree is clean, and prints the release commit.
- Added release tests before deployment:
  - `tests/test_ai_os_v6.py`
  - `tests/test_core_readonly_api.py`
- Renamed deployment metadata generation to release metadata generation and added JSON validation plus a commit match check for `deployment.json`.
- Preserved Docker Compose validation before SSH deployment.
- Strengthened remote deployment rollback by preserving the previous checked-out release and keeping the rollback trap active through public runtime verification.
- Added automatic post-deploy public runtime verification for:
  - `https://gateway.vafox.com/health/runtime`
  - `https://ai.vafox.com/health/runtime`
  - `https://huyan.vafox.com/health/runtime`
- Added GitHub Actions failure reporting to the step summary with the failed commit, workflow run URL, and rollback behavior.

## After verification

- A merge to `main` now starts the production deployment workflow automatically.
- Manual `workflow_dispatch` remains available for emergency deployment.
- Deployment is blocked before production changes when the release commit does not match the workflow SHA, the worktree is dirty, release tests fail, release metadata is invalid, or Docker Compose validation fails.
- If remote deployment or runtime verification fails before completion, the remote rollback trap restores the previous release commit and restarts the production Compose stack.
- The workflow reports deployment failures in the GitHub Actions step summary.

END
