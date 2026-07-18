# AI Release Tooling Package Transfer Report

Date (UTC): 2026-07-18
Target: `ai.vafox.com`
Production server: `1.13.254.217`
User: `ubuntu`
Production root: `/opt/ai-vafox`
Delivery directory: `/opt/ai-vafox/tooling-packages`
Package: `ai-release-tooling-installer-package.tar.gz`

## Before State

The requested production pointer verification could not be completed because this execution environment could not reach the production host.

Commands attempted:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new ubuntu@ai.vafox.com 'hostname && readlink /opt/ai-vafox/current-enterprise-ai'
```

Result:

```text
ssh: Could not resolve hostname ai.vafox.com: Temporary failure in name resolution
```

Fallback command attempted against the provided production IP:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new ubuntu@1.13.254.217 'hostname && readlink /opt/ai-vafox/current-enterprise-ai'
```

Result:

```text
ssh: connect to host 1.13.254.217 port 22: Network is unreachable
```

Expected pointer remains:

```text
/opt/ai-vafox/releases/fba3c17
```

## Transfer Status

Status: **Not transferred**.

The package was prepared locally at:

```text
/tmp/ai-release-tooling-installer-package.tar.gz
```

No production delivery command succeeded because SSH connectivity to both `ai.vafox.com` and `1.13.254.217` failed before authentication or remote command execution.

The following production-side actions were therefore **not performed**:

- Creation of `/opt/ai-vafox/tooling-packages`.
- Upload of `ai-release-tooling-installer-package.tar.gz`.
- Production-side checksum verification.
- Production-side package extraction.
- Production-side extracted-file verification.

## Package Checksum

Local package SHA256:

```text
c14e3b07c701855e19023aa1d17716fbbe6e19d22e30d061b528ae00ec21f9ad  /tmp/ai-release-tooling-installer-package.tar.gz
```

Package member checksums recorded in `SHA256SUMS`:

```text
b4db67e29fb1c2af73e08128781d79333d3882a1c6d89247b67a6a5b1abe51d7  ai_release_tooling_installer.sh
3b4115c47573d2af093a9d79d331bd6f4e193c03de4425266178033493a7af1a  ai_genesis_candidate_build.sh
5a603e3129df8d59406981e2db1c92c107bddaba4d96665fc01940fde92ee479  MANIFEST.txt
```

## Extracted Files

Local package contents were verified with `tar -tzf` and match the expected package layout:

```text
MANIFEST.txt
SHA256SUMS
ai_genesis_candidate_build.sh
ai_release_tooling_installer.sh
```

Production extraction was **not performed** because the production host was unreachable.

## Production Pointer Before / After

| Check | Status | Observed value |
| --- | --- | --- |
| Before transfer | Not verified: host unreachable | N/A |
| After transfer | Not verified: host unreachable | N/A |

Required value:

```text
/opt/ai-vafox/releases/fba3c17
```

## Safety Verification

The required safety rules were preserved from this environment:

- No production cutover was performed.
- No production data was changed.
- No Docker restart was performed.
- `/opt/ai-vafox/current-enterprise-ai` was not modified.
- `/opt/ai-vafox/releases/fba3c17` was not modified.
- The installer was not executed.
- The candidate build script was not executed.

## Follow-up Required

Run the delivery again from a network path that can resolve `ai.vafox.com` and reach SSH on `1.13.254.217`, then re-run the before and after pointer checks exactly as requested before extracting or preparing the tooling package on production.
