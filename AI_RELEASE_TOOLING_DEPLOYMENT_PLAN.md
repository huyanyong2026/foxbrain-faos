# AI Release Tooling Deployment Plan

## Purpose

This plan defines a safe, non-cutover method to deliver AI release-candidate tooling to the production host for `ai.vafox.com` when the production server is not a Git checkout and does not already contain `scripts/ai_genesis_candidate_build.sh`.

The procedure is limited to installing and verifying migration/build tooling and running an isolated release-candidate build. It does **not** activate the candidate, migrate data, or change production routing.

## Mandatory Guardrails

- **NO PRODUCTION CUTOVER.** Do not promote the candidate release.
- **NO DATA CHANGE.** Do not run database migrations, seeders, destructive scripts, or writes against production data stores.
- **NO SYMLINK CHANGE.** Do not modify `/opt/ai-vafox/current-enterprise-ai`.
- Preserve the existing production pointer exactly:

```text
/opt/ai-vafox/current-enterprise-ai -> releases/fba3c17
```

Any step that observes a different production pointer must stop immediately and require a separate incident review.

## Target Production Layout

The production root remains:

```text
/opt/ai-vafox
├── ops/
│   └── release-tooling/
│       └── ai-genesis/
│           └── <tooling-package-id>/
├── releases/
│   ├── fba3c17/
│   └── <candidate-id>/
└── current-enterprise-ai -> releases/fba3c17
```

### 1. Tooling Location

Use three distinct locations so tooling delivery, candidate assembly, and production runtime stay separated.

#### Ops Directory

Tooling packages are unpacked under:

```text
/opt/ai-vafox/ops/release-tooling/ai-genesis/<tooling-package-id>/
```

Contents:

- `scripts/ai_genesis_candidate_build.sh`
- `TOOLING_MANIFEST.txt`
- `TOOLING_MANIFEST.txt.sha256`
- optional operator notes or checksum evidence

The ops directory is for operational tooling only. It is not served by the application and is not the production runtime target.

#### Release Directory

The existing production release remains untouched:

```text
/opt/ai-vafox/releases/fba3c17/
```

The active symlink must remain:

```text
/opt/ai-vafox/current-enterprise-ai -> releases/fba3c17
```

Do not copy tooling into `releases/fba3c17/`. Do not edit files below the active release.

#### Candidate Directory

The candidate build script creates an isolated candidate directory under:

```text
/opt/ai-vafox/releases/<candidate-id>/
```

The candidate directory is for validation only. It may contain candidate source, manifests, evidence, logs, and preview-runtime scratch files. It is not activated and must not become the target of `current-enterprise-ai` during this procedure.

## 2. How to Package Tooling

Package only the release-candidate tooling needed to run the candidate build from a clean, trusted Git checkout outside production.

Recommended package name:

```text
ai-release-tooling-<git-short-sha>-<YYYYMMDD-HHMMSS>.tar.gz
```

Create a staging directory with the script and manifest:

```bash
TOOLING_ID="ai-release-tooling-$(git rev-parse --short HEAD)-$(date -u +%Y%m%d-%H%M%S)"
STAGING_DIR="/tmp/${TOOLING_ID}"
mkdir -p "${STAGING_DIR}/scripts"
cp scripts/ai_genesis_candidate_build.sh "${STAGING_DIR}/scripts/"
chmod 0755 "${STAGING_DIR}/scripts/ai_genesis_candidate_build.sh"
(
  cd "${STAGING_DIR}"
  find . -type f -print0 | sort -z | xargs -0 sha256sum > TOOLING_MANIFEST.txt
  sha256sum TOOLING_MANIFEST.txt > TOOLING_MANIFEST.txt.sha256
)
tar -C /tmp -czf "/tmp/${TOOLING_ID}.tar.gz" "${TOOLING_ID}"
sha256sum "/tmp/${TOOLING_ID}.tar.gz" > "/tmp/${TOOLING_ID}.tar.gz.sha256"
```

Transfer both files to the production host using the approved secure channel:

```bash
scp "/tmp/${TOOLING_ID}.tar.gz" "/tmp/${TOOLING_ID}.tar.gz.sha256" ai.vafox.com:/tmp/
```

## 3. How to Verify Checksum

On the production host, verify the archive checksum before unpacking:

```bash
cd /tmp
sha256sum -c "${TOOLING_ID}.tar.gz.sha256"
```

Expected result:

```text
<TAR_FILE>: OK
```

Create the ops tooling directory and unpack there only:

```bash
sudo mkdir -p /opt/ai-vafox/ops/release-tooling/ai-genesis
sudo tar -C /opt/ai-vafox/ops/release-tooling/ai-genesis -xzf "/tmp/${TOOLING_ID}.tar.gz"
```

Verify the internal manifest after unpacking:

```bash
cd "/opt/ai-vafox/ops/release-tooling/ai-genesis/${TOOLING_ID}"
sha256sum -c TOOLING_MANIFEST.txt.sha256
sha256sum -c TOOLING_MANIFEST.txt
```

Confirm script permissions and content identity:

```bash
stat -c '%a %n' scripts/ai_genesis_candidate_build.sh
grep -n 'never changes the production current symlink' scripts/ai_genesis_candidate_build.sh
```

Do not execute the script if any checksum verification fails.

## 4. How to Execute Candidate Build Without Touching Production

Before execution, confirm the production pointer exactly:

```bash
readlink /opt/ai-vafox/current-enterprise-ai
```

Expected output:

```text
releases/fba3c17
```

Run the candidate build from the unpacked ops tooling directory with explicit guardrail environment variables:

```bash
cd "/opt/ai-vafox/ops/release-tooling/ai-genesis/${TOOLING_ID}"
sudo env \
  TARGET_DOMAIN=ai.vafox.com \
  PROD_ROOT=/opt/ai-vafox \
  RELEASES_DIR=/opt/ai-vafox/releases \
  CURRENT_SYMLINK=/opt/ai-vafox/current-enterprise-ai \
  EXPECTED_CURRENT_TARGET=releases/fba3c17 \
  PREVIEW_HOST=127.0.0.1 \
  PREVIEW_PORT=18086 \
  KEEP_RUNTIME=0 \
  KEEP_FAILED_RELEASE=0 \
  scripts/ai_genesis_candidate_build.sh
```

The candidate build is safe because it must:

- assert `/opt/ai-vafox/current-enterprise-ai -> releases/fba3c17` before candidate creation;
- create candidate artifacts under `/opt/ai-vafox/releases/<candidate-id>/`;
- run preview validation on `127.0.0.1:18086`;
- write evidence and logs inside the candidate directory;
- assert the production pointer again after validation;
- avoid any command that changes `/opt/ai-vafox/current-enterprise-ai`.

If source code is also required on production because the host is not a Git checkout, deliver it as a separate immutable source archive into the candidate directory or a temporary staging directory. Do not convert production into a Git checkout and do not overlay source files onto `current-enterprise-ai` or `releases/fba3c17`.

## 5. How to Preserve `current-enterprise-ai -> releases/fba3c17`

Preservation checks are required before, during, and after tooling execution.

### Pre-Run Check

```bash
if [ "$(readlink /opt/ai-vafox/current-enterprise-ai)" != "releases/fba3c17" ]; then
  echo "ABORT: production pointer is not releases/fba3c17" >&2
  exit 10
fi
```

### Runtime Rule

Do not run any of these commands during this plan:

```bash
ln -sfn /opt/ai-vafox/releases/<candidate-id> /opt/ai-vafox/current-enterprise-ai
ln -sfn releases/<candidate-id> /opt/ai-vafox/current-enterprise-ai
rm /opt/ai-vafox/current-enterprise-ai
mv /opt/ai-vafox/current-enterprise-ai /opt/ai-vafox/current-enterprise-ai.*
```

### Post-Run Check

```bash
if [ "$(readlink /opt/ai-vafox/current-enterprise-ai)" != "releases/fba3c17" ]; then
  echo "CRITICAL: production pointer changed" >&2
  exit 99
fi
```

Record the final pointer in the validation evidence:

```bash
readlink /opt/ai-vafox/current-enterprise-ai | tee /opt/ai-vafox/ops/release-tooling/ai-genesis/${TOOLING_ID}/final-current-enterprise-ai.txt
```

## 6. Rollback and Cleanup

Because this plan forbids cutover, rollback means removing delivered tooling and candidate-only artifacts while leaving production unchanged.

### Stop Preview Runtime

If the candidate script leaves a preview process running because `KEEP_RUNTIME=1` was used, stop only that preview process. Match on the preview port or candidate ID before killing anything:

```bash
sudo lsof -iTCP:18086 -sTCP:LISTEN -n -P
sudo kill <preview-pid>
```

### Remove Candidate Runtime Scratch Data

Remove only candidate-specific runtime scratch directories, logs, or failed build artifacts after evidence is collected:

```bash
sudo rm -rf /opt/ai-vafox/releases/<candidate-id>/runtime
```

If the entire candidate is no longer needed:

```bash
sudo rm -rf /opt/ai-vafox/releases/<candidate-id>
```

Never remove `/opt/ai-vafox/releases/fba3c17`.

### Remove Delivered Tooling Package

After checksums, logs, and reports are archived, remove the unpacked tooling package and temporary transfer files:

```bash
sudo rm -rf "/opt/ai-vafox/ops/release-tooling/ai-genesis/${TOOLING_ID}"
rm -f "/tmp/${TOOLING_ID}.tar.gz" "/tmp/${TOOLING_ID}.tar.gz.sha256"
```

### Final Safety Verification

Run the final no-change verification:

```bash
readlink /opt/ai-vafox/current-enterprise-ai
```

Expected output:

```text
releases/fba3c17
```

Also confirm the active release directory still exists:

```bash
test -d /opt/ai-vafox/releases/fba3c17
```

## Completion Criteria

This plan is complete only when all of the following are true:

- tooling archive checksum verified successfully;
- internal tooling manifest verified successfully;
- candidate build executed only in candidate/preview mode, or was safely aborted before execution;
- no production data migration or data write was performed;
- `/opt/ai-vafox/current-enterprise-ai` still resolves to `releases/fba3c17`;
- rollback/cleanup removed only candidate-specific or tooling-specific files.
