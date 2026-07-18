# AI Release Installer Offline Update Report

Generated UTC: 2026-07-18
Target: `ai.vafox.com`
Production root: `/opt/ai-vafox`

## Purpose

Codex cannot reach the production server by SSH, so this change adds `ai_release_installer_update_offline.sh`, a self-contained updater that can be copied to and executed directly on the production server.

## Backup Path

- Backup path created by the offline updater: `/opt/ai-vafox/ops/ai_release_tooling_installer.sh.backup`
- The backup preserves mode and timestamps with `cp -p` when the existing installer is present.

## Updated File

- Updated installer path: `/opt/ai-vafox/ops/ai_release_tooling_installer.sh`
- Replacement source: embedded fixed installer payload inside `ai_release_installer_update_offline.sh`
- Checksum verification: the updater verifies the embedded payload SHA256 before install and verifies the installed file SHA256 after install.

## Validation Result

The offline updater performs these validations on the production server:

```bash
bash -n /opt/ai-vafox/ops/ai_release_tooling_installer.sh
```

Expected result: PASS.

The updater also verifies the fixed guard by checking that the installed file contains absolute production-pointer guard logic equivalent to:

```bash
EXPECTED_CURRENT_TARGET="${PROD_ROOT}/releases/fba3c17"
```

and uses absolute symlink resolution with:

```bash
readlink -f
```

## Help Validation

The fixed installer now handles help before payload installation:

```bash
bash /opt/ai-vafox/ops/ai_release_tooling_installer.sh --help
```

Expected result: only display help.

Expected non-effects:

- Does not install payload.
- Does not create a candidate release.
- Does not change `/opt/ai-vafox/current-enterprise-ai`.

## Production Pointer Before/After

The offline updater records and validates:

```bash
readlink -f /opt/ai-vafox/current-enterprise-ai
```

Required before value:

```text
/opt/ai-vafox/releases/fba3c17
```

Required after value:

```text
/opt/ai-vafox/releases/fba3c17
```

If either value differs, the updater exits with failure and writes the report with the observed pointer.

## Safety Confirmation

The offline updater is designed to comply with the requested safety rules:

- No SSH.
- No git command.
- No docker restart.
- No nginx command or nginx config change.
- No database command or database change.
- No release cutover.
- No `current-enterprise-ai` symlink mutation.
- No release directory mutation during the installer `--help` verification.

## Local Test Evidence

Local checks performed in the Codex environment:

```bash
bash -n ai_release_installer_update_offline.sh
```

Result: PASS.

```bash
PROD_ROOT=/tmp/ai-offtest REPORT_PATH=/tmp/ai-offtest/report.md ./ai_release_installer_update_offline.sh
```

Result: PASS in a temporary production-root simulation with `/tmp/ai-offtest/current-enterprise-ai -> /tmp/ai-offtest/releases/fba3c17`.

The temporary directory test confirmed:

- Backup file created.
- Installer replaced.
- Checksum verification passed.
- `bash -n` validation passed.
- Fixed guard validation passed.
- `--help` did not install the payload tool.
- Pointer remained unchanged before and after.
