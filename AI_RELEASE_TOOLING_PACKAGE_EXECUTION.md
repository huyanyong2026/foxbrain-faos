# AI Release Tooling Package Execution Guide

Target: `ai.vafox.com`
Production root: `/opt/ai-vafox`
Current production pointer: `current-enterprise-ai -> releases/fba3c17`
Tooling script: `scripts/ai_genesis_candidate_build.sh`
Delivery location: `/opt/ai-vafox/ops/`
Execution mode: **candidate-only build tooling delivery**

## Safety Requirements

This guide is limited to safely packaging and delivering the candidate build tooling script.

The following actions are explicitly prohibited:

- **No production cutover.** Do not promote any candidate release to live traffic.
- **No data change.** Do not run migrations, write production records, enqueue production jobs, or alter production storage.
- **No symlink change.** Do not modify `/opt/ai-vafox/current-enterprise-ai`; it must remain `releases/fba3c17`.

Before and after every delivery or execution step, verify the production pointer:

```bash
readlink /opt/ai-vafox/current-enterprise-ai
```

Expected output:

```text
releases/fba3c17
```

## 1. Package Creation

Create the tooling package from a clean repository checkout. The package contains only the candidate build script and supporting package metadata.

Recommended local package workspace:

```bash
mkdir -p /tmp/ai-release-tooling-package
cp scripts/ai_genesis_candidate_build.sh /tmp/ai-release-tooling-package/
chmod 0755 /tmp/ai-release-tooling-package/ai_genesis_candidate_build.sh
```

Create a package manifest:

```bash
cat > /tmp/ai-release-tooling-package/MANIFEST.txt <<'MANIFEST'
ai_genesis_candidate_build.sh
MANIFEST
```

Create the compressed package:

```bash
tar -C /tmp/ai-release-tooling-package \
  -czf /tmp/ai-release-tooling-package/ai-release-tooling-package.tar.gz \
  ai_genesis_candidate_build.sh MANIFEST.txt
```

This package creation step does not touch `/opt/ai-vafox/current-enterprise-ai`, does not write application data, and does not create or promote any release directory.

## 2. File Manifest

Validate the package contents before delivery:

```bash
tar -tzf /tmp/ai-release-tooling-package/ai-release-tooling-package.tar.gz | sort
```

Expected manifest:

```text
MANIFEST.txt
ai_genesis_candidate_build.sh
```

Also verify the manifest file inside the package workspace:

```bash
cat /tmp/ai-release-tooling-package/MANIFEST.txt
```

Expected output:

```text
ai_genesis_candidate_build.sh
```

## 3. SHA256 Checksum

Generate and record the package checksum:

```bash
cd /tmp/ai-release-tooling-package
sha256sum ai-release-tooling-package.tar.gz | tee ai-release-tooling-package.tar.gz.sha256
```

Verify the checksum before production delivery:

```bash
cd /tmp/ai-release-tooling-package
sha256sum -c ai-release-tooling-package.tar.gz.sha256
```

Expected output pattern:

```text
ai-release-tooling-package.tar.gz: OK
```

After copying to production, generate or verify the production-side checksum from `/opt/ai-vafox/ops/`:

```bash
cd /opt/ai-vafox/ops
sha256sum -c ai-release-tooling-package.tar.gz.sha256
```

Expected output pattern:

```text
ai-release-tooling-package.tar.gz: OK
```

## 4. Production Delivery Location

Deliver the package to the production operations directory only:

```bash
sudo mkdir -p /opt/ai-vafox/ops
sudo cp /tmp/ai-release-tooling-package/ai-release-tooling-package.tar.gz /opt/ai-vafox/ops/
sudo cp /tmp/ai-release-tooling-package/ai-release-tooling-package.tar.gz.sha256 /opt/ai-vafox/ops/
```

Extract the package under `/opt/ai-vafox/ops/ai-release-tooling-package/`:

```bash
sudo mkdir -p /opt/ai-vafox/ops/ai-release-tooling-package
sudo tar -C /opt/ai-vafox/ops/ai-release-tooling-package \
  -xzf /opt/ai-vafox/ops/ai-release-tooling-package.tar.gz
```

Do not extract this package into `/opt/ai-vafox/releases/fba3c17`, do not replace any production app files, and do not alter `/opt/ai-vafox/current-enterprise-ai`.

## 5. Permission Setup

Set ownership according to the production operations account used by the host. If the deployment account is `ai-vafox`, use:

```bash
sudo chown -R ai-vafox:ai-vafox /opt/ai-vafox/ops/ai-release-tooling-package
sudo chown ai-vafox:ai-vafox /opt/ai-vafox/ops/ai-release-tooling-package.tar.gz /opt/ai-vafox/ops/ai-release-tooling-package.tar.gz.sha256
```

Set restrictive default permissions and executable script permissions:

```bash
sudo chmod 0750 /opt/ai-vafox/ops/ai-release-tooling-package
sudo chmod 0755 /opt/ai-vafox/ops/ai-release-tooling-package/ai_genesis_candidate_build.sh
sudo chmod 0644 /opt/ai-vafox/ops/ai-release-tooling-package.tar.gz /opt/ai-vafox/ops/ai-release-tooling-package.tar.gz.sha256
```

Confirm permissions:

```bash
stat -c '%A %U:%G %n' \
  /opt/ai-vafox/ops/ai-release-tooling-package \
  /opt/ai-vafox/ops/ai-release-tooling-package/ai_genesis_candidate_build.sh \
  /opt/ai-vafox/ops/ai-release-tooling-package.tar.gz \
  /opt/ai-vafox/ops/ai-release-tooling-package.tar.gz.sha256
```

## 6. Verification Commands

Run these checks after delivery and before any candidate-only execution.

Verify production pointer is unchanged:

```bash
readlink /opt/ai-vafox/current-enterprise-ai
```

Expected output:

```text
releases/fba3c17
```

Verify checksum:

```bash
cd /opt/ai-vafox/ops
sha256sum -c ai-release-tooling-package.tar.gz.sha256
```

Verify extracted file list:

```bash
find /opt/ai-vafox/ops/ai-release-tooling-package -maxdepth 1 -type f -printf '%f\n' | sort
```

Expected output:

```text
MANIFEST.txt
ai_genesis_candidate_build.sh
```

Verify script syntax without executing the candidate build:

```bash
bash -n /opt/ai-vafox/ops/ai-release-tooling-package/ai_genesis_candidate_build.sh
```

Confirm the tool contains the production guard defaults:

```bash
grep -E '^(PROD_ROOT|CURRENT_SYMLINK|EXPECTED_CURRENT_TARGET)=' \
  /opt/ai-vafox/ops/ai-release-tooling-package/ai_genesis_candidate_build.sh
```

Expected values include:

```text
PROD_ROOT="${PROD_ROOT:-/opt/ai-vafox}"
CURRENT_SYMLINK="${CURRENT_SYMLINK:-${PROD_ROOT}/current-enterprise-ai}"
EXPECTED_CURRENT_TARGET="${EXPECTED_CURRENT_TARGET:-releases/fba3c17}"
```

## 7. Candidate-Only Execution

Only run the delivered script when candidate validation is approved. The script is designed to create an isolated candidate release under `/opt/ai-vafox/releases/<candidate_id>` and validate it without changing the production symlink.

Candidate-only dry-run style invocation with explicit guard values:

```bash
cd /opt/ai-vafox/current-enterprise-ai
sudo -u ai-vafox env \
  TARGET_DOMAIN=ai.vafox.com \
  PROD_ROOT=/opt/ai-vafox \
  EXPECTED_CURRENT_TARGET=releases/fba3c17 \
  KEEP_RUNTIME=0 \
  KEEP_FAILED_RELEASE=0 \
  /opt/ai-vafox/ops/ai-release-tooling-package/ai_genesis_candidate_build.sh
```

Execution guardrails:

- The script must fail if `/opt/ai-vafox/current-enterprise-ai` does not point to `releases/fba3c17`.
- The script must archive the source into a new candidate directory under `/opt/ai-vafox/releases/`.
- The script must not replace `current-enterprise-ai`.
- The script must not run production database migrations.
- The script must run preview validation only on a candidate-scoped host and port.
- The script must generate candidate evidence and `AI_GENESIS_CANDIDATE_VALIDATION_REPORT.md`.

Post-execution verification:

```bash
readlink /opt/ai-vafox/current-enterprise-ai
```

Expected output remains:

```text
releases/fba3c17
```

## 8. Cleanup

Remove local temporary package workspace after successful delivery verification:

```bash
rm -rf /tmp/ai-release-tooling-package
```

Remove delivered tooling only when it is no longer needed and after confirming no candidate execution is in progress:

```bash
sudo rm -rf /opt/ai-vafox/ops/ai-release-tooling-package
sudo rm -f /opt/ai-vafox/ops/ai-release-tooling-package.tar.gz /opt/ai-vafox/ops/ai-release-tooling-package.tar.gz.sha256
```

If candidate execution produced a candidate release that must be discarded, remove only that candidate-specific release directory after review:

```bash
sudo rm -rf /opt/ai-vafox/releases/<candidate_id>
```

Never remove or modify:

```text
/opt/ai-vafox/releases/fba3c17
/opt/ai-vafox/current-enterprise-ai
```

Final cleanup verification:

```bash
readlink /opt/ai-vafox/current-enterprise-ai
```

Expected output:

```text
releases/fba3c17
```
