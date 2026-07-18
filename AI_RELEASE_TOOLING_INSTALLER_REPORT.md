# AI Release Tooling Installer Report

Target: `ai.vafox.com` production
Installer: `ai_release_tooling_installer.sh`
Installed tooling: `/opt/ai-vafox/ops/ai_genesis_candidate_build.sh`
Required production pointer invariant: `current-enterprise-ai -> releases/fba3c17`

## Purpose

This change adds an offline, standalone installer for production hosts that are not Git checkouts and cannot receive repository files automatically.

The installer embeds the release candidate build tooling payload directly in `ai_release_tooling_installer.sh`, writes it to `/opt/ai-vafox/ops/ai_genesis_candidate_build.sh`, verifies the embedded and installed SHA256 checksum, sets executable permissions, runs only the tooling help command, and verifies the production pointer before and after installation.

## Installer Behavior

When run on the production host, the installer performs only these actions:

1. Verifies `/opt/ai-vafox/current-enterprise-ai` points to `releases/fba3c17`.
2. Creates `/opt/ai-vafox/ops` if missing.
3. Installs `ai_genesis_candidate_build.sh` into `/opt/ai-vafox/ops`.
4. Verifies the SHA256 checksum before and after installation.
5. Sets the installed script mode to `755`.
6. Runs only:

   ```bash
   bash /opt/ai-vafox/ops/ai_genesis_candidate_build.sh --help
   ```

7. Re-verifies `/opt/ai-vafox/current-enterprise-ai` points to `releases/fba3c17`.

## Safety Guarantees

The installer is intentionally limited to tooling installation and help validation.

Explicitly prohibited and not performed:

- No production cutover.
- No data change.
- No Docker restart.
- No symlink change.
- No release promotion.
- No execution of the candidate build workflow.

## Usage

Copy `ai_release_tooling_installer.sh` to the production host and run it with appropriate privileges to write under `/opt/ai-vafox`:

```bash
bash ai_release_tooling_installer.sh
```

Optional environment overrides for non-production rehearsal only:

```bash
PROD_ROOT=/tmp/ai-vafox-test bash ai_release_tooling_installer.sh
```

## Validation Performed in Repository

Repository-side validation confirmed that:

- The installer shell syntax is valid.
- The installed tooling help path is safe and exits before candidate-build execution.
- The installer can complete against a temporary fake production root with `current-enterprise-ai -> releases/fba3c17`.
- The installer writes the embedded tooling with mode `755`.
- The installed tooling checksum matches the embedded checksum.

## Final Status

Ready for offline transfer to `ai.vafox.com` production.

No production execution was performed from this repository environment.
