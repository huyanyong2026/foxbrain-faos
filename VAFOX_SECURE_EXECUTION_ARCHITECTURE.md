# VAFOX Secure Execution Channel Architecture

## 1. Purpose and Scope

This document defines the proposed **VAFOX Secure Execution Channel** for allowing Codex-driven automation to manage three Tencent Cloud servers without passwords and without broad administrative access.

| Node | Public IP | Role Label | Automation Posture |
| --- | --- | --- | --- |
| Huyan | `140.143.207.194` | Huyan application/runtime node | Managed through controlled SSH execution only |
| AI | `1.13.254.217` | AI service/runtime node | Managed through controlled SSH execution only |
| Core | `139.199.174.36` | Core platform/control node | Managed through controlled SSH execution only |

The architecture is intentionally conservative:

- No password-based SSH access.
- No shared human account for automation.
- No unrestricted root login.
- No direct server mutation by design tooling.
- Every automated action must be planned, logged, attributable, and reversible where practical.

## 2. Security Objectives

The channel must provide the following guarantees:

1. **Strong identity**: Codex automation uses a dedicated cryptographic identity per environment and preferably per node class.
2. **Least privilege**: The execution account can only run approved commands and access approved paths.
3. **Network containment**: SSH is reachable only from trusted control-plane addresses or private overlay network identities.
4. **Auditable execution**: Every action has an immutable record including operator, request, target node, command intent, execution result, timestamp, and artifact checksum when applicable.
5. **No standing secrets in code**: Private keys, deploy tokens, and cloud credentials are not committed to the repository.
6. **Separation of duties**: Architecture, approval, deployment, and audit are separate stages.
7. **Safe rollback**: Deployments must include health checks and a rollback path before promotion.

## 3. High-Level Architecture

```text
+-------------------------+
| Codex / Automation CI   |
| - no passwords          |
| - ephemeral runtime     |
| - signed run metadata   |
+-----------+-------------+
            |
            | SSH over restricted network path
            | Option A: Tencent security group allowlist
            | Option B: Tailscale/VPN private overlay
            v
+-------------------------+        +-------------------------+
| Huyan                   |        | AI                      |
| 140.143.207.194         |        | 1.13.254.217           |
| vafox-exec user         |        | vafox-exec user        |
| command allowlist       |        | command allowlist      |
| audit logging           |        | audit logging          |
+-------------------------+        +-------------------------+
            |
            v
+-------------------------+
| Core                    |
| 139.199.174.36          |
| vafox-exec user         |
| deployment coordinator  |
| audit aggregation       |
+-------------------------+
```

Recommended production pattern:

- Use **Tailscale or an equivalent WireGuard-based VPN** as the default private execution path.
- Retain Tencent Cloud security groups as an outer deny-by-default boundary.
- Expose SSH publicly only as a break-glass option, and only from tightly controlled source IPs.
- Execute automation with a dedicated Linux account such as `vafox-exec`.
- Grant narrow `sudo` rules only for specific deployment and service-management commands.

## 4. SSH Key Scheme

### 4.1 Key Principles

The SSH key design should avoid long-lived shared keys and should support rotation, revocation, and attribution.

Required controls:

- Disable password authentication for automation.
- Disable root SSH login.
- Use Ed25519 keys or SSH certificates.
- Store private keys only in an approved secret manager or CI secret store.
- Never commit private keys or key material to Git.
- Use distinct keys by environment and purpose.
- Prefer short-lived OpenSSH certificates signed by an internal CA for mature environments.

### 4.2 Recommended Key Hierarchy

Preferred model:

```text
VAFOX SSH CA
├── codex-prod executor certificate
├── codex-staging executor certificate
├── human-breakglass certificate
└── emergency-recovery certificate
```

If SSH certificates are not available initially, use static Ed25519 public keys with strict compensating controls:

```text
keys/
├── vafox-codex-prod-huyan.pub
├── vafox-codex-prod-ai.pub
├── vafox-codex-prod-core.pub
└── vafox-breakglass-admin.pub
```

Static-key baseline controls:

- Rotate keys at least every 90 days.
- Revoke keys immediately after role changes or suspected exposure.
- Maintain one key per automation context instead of one universal key.
- Keep a documented fingerprint registry.

### 4.3 Authorized Key Restrictions

For static public keys, use OpenSSH `authorized_keys` options to reduce blast radius.

Recommended restrictions:

```text
from="<trusted-source-cidr>",no-agent-forwarding,no-X11-forwarding,no-pty ssh-ed25519 <public-key> vafox-codex-prod
```

For command-constrained automation accounts, add a forced command wrapper:

```text
command="/usr/local/vafox/bin/vafox-exec-gate",from="<trusted-source-cidr>",no-agent-forwarding,no-X11-forwarding,no-pty ssh-ed25519 <public-key> vafox-codex-prod
```

The forced command wrapper should validate requested actions against an allowlist and write audit records before and after execution.

## 5. Dedicated Execution Account

### 5.1 Account Model

Create a dedicated execution account on each server:

```text
username: vafox-exec
shell: /usr/sbin/nologin or restricted shell where feasible
home: /var/lib/vafox-exec
primary group: vafox-exec
supplementary groups: only when explicitly required
```

The account should not be used by humans. Human operators should use separate named accounts or certificate principals.

### 5.2 Directory Ownership

Recommended managed paths:

| Path | Owner | Purpose |
| --- | --- | --- |
| `/opt/vafox/releases` | `vafox-exec:vafox-exec` | Versioned release artifacts |
| `/opt/vafox/current` | symlink managed through controlled command | Active release pointer |
| `/var/lib/vafox-exec` | `vafox-exec:vafox-exec` | Runtime metadata and deployment state |
| `/var/log/vafox-exec` | root-owned append-only or audit-forwarded | Execution logs |
| `/etc/systemd/system/vafox-*.service` | root-owned | Service units managed only through approved sudo commands |

### 5.3 Login Restrictions

Recommended SSH daemon controls:

```text
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
AllowUsers vafox-exec <named-admin-users>
```

For stricter environments, put automation in a `Match User vafox-exec` block that disables forwarding and TTY allocation.

## 6. Least-Privilege Design

### 6.1 Command Allowlist

Automation should not receive general-purpose root access. Instead, grant only a small command set through a wrapper or sudoers allowlist.

Allowed operation classes:

1. Read service status.
2. Upload release artifact to a staging path.
3. Verify artifact checksum and signature.
4. Install dependencies only from approved package sources, preferably during image build rather than live deployment.
5. Switch release symlink atomically.
6. Restart specific VAFOX services.
7. Run health checks.
8. Roll back to a previous release.
9. Collect bounded logs for troubleshooting.

Explicitly prohibited operation classes:

- Interactive root shell.
- Arbitrary package installation.
- Arbitrary file deletion outside VAFOX-managed paths.
- Modification of SSH daemon configuration by automation.
- Modification of firewall/security-group state by automation.
- Reading unrelated system secrets.
- Disabling audit, monitoring, or endpoint protection.

### 6.2 Sudoers Pattern

Use a dedicated sudoers file such as `/etc/sudoers.d/vafox-exec` with exact command paths.

Conceptual pattern:

```text
vafox-exec ALL=(root) NOPASSWD: /bin/systemctl status vafox-*.service
vafox-exec ALL=(root) NOPASSWD: /bin/systemctl restart vafox-*.service
vafox-exec ALL=(root) NOPASSWD: /bin/systemctl reload vafox-*.service
vafox-exec ALL=(root) NOPASSWD: /usr/local/vafox/bin/promote-release
vafox-exec ALL=(root) NOPASSWD: /usr/local/vafox/bin/rollback-release
```

Implementation warning: sudo wildcard rules must be reviewed carefully because wildcards can unintentionally permit unsafe arguments. A wrapper script with strict argument validation is preferred over broad wildcard sudo access.

### 6.3 Execution Wrapper

All automation should enter through a single gate:

```text
/usr/local/vafox/bin/vafox-exec-gate
```

The gate should:

- Parse a structured request such as JSON.
- Validate target service, action, release ID, checksum, and caller principal.
- Reject unknown commands and unexpected arguments.
- Write a pre-execution audit event.
- Execute only approved internal commands.
- Capture stdout, stderr, exit code, duration, and changed artifact IDs.
- Write a post-execution audit event.
- Return a compact machine-readable result.

## 7. Tailscale / VPN Scheme Evaluation

### 7.1 Option A: Tencent Cloud Security Groups Only

Description: expose SSH on public IPs but allow inbound port 22 only from approved Codex/CI runner egress IPs or an operations bastion.

Advantages:

- Simple to understand.
- Uses native cloud controls.
- No additional overlay network component.

Disadvantages:

- Public SSH surface still exists.
- CI egress IPs can be unstable unless using fixed runners or NAT.
- Harder to express identity-aware policies.
- Emergency allowlist changes can become operationally risky.

Best use:

- Initial bootstrap.
- Temporary fallback.
- Environments with fixed, well-controlled automation egress IPs.

### 7.2 Option B: Tailscale/WireGuard Overlay

Description: each server joins a private tailnet; Codex automation connects through an approved subnet router, ephemeral node, or CI integration using short-lived auth.

Advantages:

- SSH can be closed on the public interface.
- Access policy can be identity-aware.
- Device posture and ACLs can restrict which automation identity reaches which node.
- Easier private addressing and service naming.
- Better fit for ephemeral automation runners.

Disadvantages:

- Adds dependency on the overlay control plane.
- Requires careful ACL design and key expiry.
- Needs operational runbooks for outage and break-glass access.

Best use:

- Recommended default for ongoing VAFOX automation.
- Multi-node private operations.
- Codex or CI jobs with ephemeral identity.

### 7.3 Option C: Traditional VPN or Bastion Host

Description: automation connects to a hardened bastion or VPN gateway, then reaches servers on private network paths.

Advantages:

- Familiar enterprise model.
- Centralized access logging.
- Can integrate with existing SIEM and IAM.

Disadvantages:

- Bastion can become a high-value single point of compromise.
- More manual operational overhead than identity-aware mesh networking.
- Requires careful session recording and account separation.

Best use:

- Organizations already operating a VPN or bastion standard.
- Compliance regimes requiring centralized jump-host recording.

### 7.4 Recommendation

Adopt a two-layer model:

1. **Primary path**: Tailscale or equivalent WireGuard overlay with ACLs that allow only the Codex execution identity to reach SSH on Huyan, AI, and Core.
2. **Outer boundary**: Tencent Cloud security groups that deny public SSH except from emergency break-glass sources.
3. **Break-glass path**: documented human-admin access through named accounts and short-lived SSH certificates.

## 8. Tencent Cloud Security Group Strategy

### 8.1 Baseline Inbound Policy

For each server security group:

| Direction | Protocol/Port | Source | Action | Purpose |
| --- | --- | --- | --- | --- |
| Inbound | TCP/22 | Tailscale/VPN interface or bastion CIDR | Allow | Private automation SSH |
| Inbound | TCP/22 | Emergency admin fixed IPs | Allow only when approved | Break-glass access |
| Inbound | Application ports | Public or load balancer CIDR as required | Allow minimal required set | Product traffic |
| Inbound | All other | `0.0.0.0/0` | Deny | Default deny |

If public SSH must remain temporarily enabled, restrict source CIDRs to fixed trusted IPs only and set a time-bound exception record.

### 8.2 Outbound Policy

Outbound traffic should be limited where operationally feasible:

| Destination | Purpose |
| --- | --- |
| Tencent package mirrors or approved repositories | OS updates and dependencies |
| Artifact registry | Release downloads |
| Observability endpoints | Logs, metrics, traces |
| Tailscale/WireGuard coordination endpoints | VPN operation |
| Required application dependencies | Runtime connectivity |

Avoid broad outbound access for the execution account when host-level egress controls are available.

### 8.3 Security Group Change Control

Security group changes must be treated as infrastructure changes and require:

- Pull request review.
- Explicit ticket or change ID.
- Before/after rule diff.
- Expiry time for temporary rules.
- Post-change verification.

Codex automation should not be allowed to modify Tencent Cloud security groups directly unless a separate infrastructure pipeline with approval gates is implemented.

## 9. Automatic Audit Execution Flow

### 9.1 Audit Event Model

Every automated action should emit an audit event before and after execution.

Minimum fields:

```json
{
  "event_id": "uuid",
  "timestamp_utc": "2026-07-18T00:00:00Z",
  "actor": "codex-prod",
  "request_id": "ci-run-or-task-id",
  "target_node": "huyan|ai|core",
  "target_ip": "node-ip",
  "action": "deploy|restart|healthcheck|rollback|collect_logs",
  "approved_command": "logical-command-name",
  "release_id": "version-or-git-sha",
  "artifact_sha256": "sha256",
  "precheck_result": "passed|failed",
  "exit_code": 0,
  "duration_ms": 1234,
  "result": "success|failure",
  "changed_paths": ["/opt/vafox/current"],
  "rollback_available": true
}
```

### 9.2 Audit Storage

Use at least two destinations:

1. **Local append-only log** on each server, such as `/var/log/vafox-exec/audit.jsonl`.
2. **Central audit sink** from Core or an external logging service.

Recommended hardening:

- Use append-only file permissions where supported.
- Forward logs off-host quickly.
- Include event IDs in CI logs.
- Sign or hash audit batches to detect tampering.
- Keep deployment artifacts and audit records correlated by release ID.

### 9.3 Audit Flow

```text
1. Codex prepares structured execution request.
2. CI signs or annotates request with run metadata.
3. SSH connection authenticates with key or short-lived certificate.
4. vafox-exec-gate receives the request.
5. Gate validates actor, command, arguments, and target service.
6. Gate writes pre-execution audit event.
7. Gate runs the approved command.
8. Gate writes post-execution audit event with result and checksum.
9. CI stores command result and links it to the PR, release, or incident.
10. Central audit pipeline verifies event completeness.
```

### 9.4 Required Automated Checks

Before any mutating operation:

- Confirm target node identity.
- Confirm expected host key fingerprint.
- Confirm release artifact checksum.
- Confirm service name is approved.
- Confirm requested operation has a change ticket or deployment ID.
- Confirm disk, memory, and service dependency readiness.

After any mutating operation:

- Run service health check.
- Run node-local smoke test.
- Verify process owner and listening ports.
- Verify audit event was written.
- Verify rollback pointer exists.

## 10. Automatic Deployment Flow

### 10.1 Release Artifact Flow

```text
1. Build release artifact in CI.
2. Generate SBOM where applicable.
3. Compute SHA-256 checksum.
4. Sign artifact or produce provenance attestation.
5. Upload artifact to approved registry or transfer staging area.
6. Request deployment through vafox-exec-gate.
7. Verify checksum and signature on target.
8. Extract release into /opt/vafox/releases/<release-id>.
9. Run prestart validation.
10. Atomically update /opt/vafox/current symlink.
11. Restart or reload approved service.
12. Run health checks.
13. Mark release healthy or roll back automatically.
```

### 10.2 Progressive Deployment Order

Recommended order for multi-node changes:

1. **AI**: deploy and validate AI-specific runtime behavior.
2. **Huyan**: deploy application-facing runtime changes.
3. **Core**: deploy control-plane or shared coordination changes last unless Core is required first.

For Core-dependent migrations, use an explicit plan:

1. Core compatibility preparation.
2. AI canary.
3. Huyan canary.
4. Core promotion.
5. Full health verification.

### 10.3 Rollback Strategy

Rollback must be available for every deployment:

- Keep at least the last two known-good releases on each node.
- Maintain `/opt/vafox/previous` or equivalent release metadata.
- Roll back by switching symlink and restarting the service.
- Store rollback reason in audit log.
- If database migrations are involved, require forward-compatible migrations or an explicit manual rollback plan.

### 10.4 Health Gates

A deployment is successful only if all relevant gates pass:

- SSH host identity verified.
- Artifact checksum verified.
- Service starts successfully.
- Local health endpoint returns success.
- Critical logs show no startup failure pattern.
- External synthetic check passes where applicable.
- Audit sink receives the deployment event.

## 11. Host Key and Identity Verification

Automation must pin SSH host keys for all three nodes. The host key registry should be stored as a controlled configuration artifact, not discovered opportunistically during deployment.

Host identity registry model:

```text
huyan.vafox.internal 140.143.207.194 ssh-ed25519 <fingerprint>
ai.vafox.internal    1.13.254.217   ssh-ed25519 <fingerprint>
core.vafox.internal  139.199.174.36  ssh-ed25519 <fingerprint>
```

If using Tailscale SSH or private DNS names, pin stable node identities and ensure ACLs map automation identities to exact target nodes.

## 12. Secrets Management

Secrets must be managed outside the repository.

Recommended controls:

- Store private SSH keys or certificate signing access in CI secret manager, Tencent Cloud KMS/Secrets Manager, HashiCorp Vault, or equivalent.
- Use short-lived credentials wherever possible.
- Scope secrets by environment.
- Rotate on schedule and after incidents.
- Do not expose deploy secrets to untrusted pull request contexts.
- Mask secrets in CI logs.
- Deny automation read access to unrelated application secrets unless explicitly required.

## 13. Failure Modes and Controls

| Failure Mode | Control |
| --- | --- |
| Automation key leaked | Short-lived certificates, rapid revocation, source restrictions, audit alerts |
| Codex attempts unsafe command | Forced command wrapper and allowlist rejection |
| Public SSH attacked | Tencent security group restrictions and VPN-only access |
| Deployment breaks service | Health gates and automatic rollback |
| Audit logs tampered | Off-host forwarding and signed audit batches |
| Wrong server targeted | Host key pinning and node identity checks |
| Excessive sudo privilege | Exact sudoers rules and wrapper validation |
| VPN outage | Break-glass path with named users and time-bound approvals |

## 14. Implementation Phases

### Phase 0: Design Approval

- Review this architecture.
- Confirm node roles and service names.
- Confirm preferred network path: Tailscale, bastion, or security-group-only baseline.
- Define the approval workflow for mutating operations.

### Phase 1: Bootstrap Preparation

- Generate automation key or SSH CA design.
- Define host key registry.
- Draft `vafox-exec` account policy.
- Draft sudoers allowlist.
- Draft audit event schema.
- Draft security group desired state.

No server changes should occur in this phase.

### Phase 2: Controlled Server Onboarding

- Create `vafox-exec` account.
- Install public keys or trusted CA.
- Install execution gate.
- Configure sudoers allowlist.
- Configure audit log paths and forwarding.
- Restrict SSH daemon settings.
- Validate with read-only commands first.

This phase must be executed by an authorized operator or approved automation pipeline, not by architecture design alone.

### Phase 3: Read-Only Automation

- Enable status checks.
- Enable health checks.
- Enable bounded log collection.
- Verify complete audit capture.
- Verify no mutating command is accepted.

### Phase 4: Controlled Deployment Automation

- Enable artifact upload.
- Enable checksum verification.
- Enable service restart for approved services.
- Enable symlink-based promotion.
- Enable rollback.
- Require deployment ticket or release ID.

### Phase 5: Continuous Hardening

- Move from static keys to SSH certificates if not already implemented.
- Close public SSH where VPN path is proven.
- Add SIEM alerting for rejected commands and failed logins.
- Add periodic permission drift checks.
- Add disaster-recovery drills.

## 15. Policy Summary

The secure execution channel should be treated as production infrastructure, not a convenience SSH shortcut.

Final recommended baseline:

- **Authentication**: SSH certificates or per-node Ed25519 keys.
- **Account**: dedicated `vafox-exec` account.
- **Privilege**: command-gated least privilege with no general root shell.
- **Network**: Tailscale/WireGuard private path plus Tencent security group deny-by-default.
- **Audit**: pre/post JSON audit events, local and central storage.
- **Deployment**: signed artifacts, checksum verification, atomic promotion, health gates, and rollback.
- **Governance**: PR-reviewed infrastructure changes and time-bound break-glass access.
