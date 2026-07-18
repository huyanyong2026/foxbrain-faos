# AI Control Plane Suitability Report

- **Assessment date:** 2026-07-18 (UTC)
- **Target server:** `ai.vafox.com`
- **Target IP:** `1.13.254.217`
- **Target user:** `ubuntu`
- **Assessment mode:** read-only only; no package installation, no service restart, no Docker/Nginx/system/data modification.

## Executive decision

**Decision: B. 不推荐（暂不推荐作为 VAFOX Automation Control Plane）**

The server should **not** be promoted to the VAFOX Automation Control Plane based on the current assessment because the required read-only verification could not be completed from this execution environment:

1. DNS resolution for `ai.vafox.com` failed with `Temporary failure in name resolution`.
2. Direct SSH connectivity to `1.13.254.217:22` failed with `Network is unreachable`.
3. ICMP connectivity from the assessment environment to `1.13.254.217` also failed with `Network is unreachable`.

This is a conservative operational recommendation: a control plane must have verified host capacity, Docker workload profile, AI workload pressure, disk headroom, and network reachability to managed nodes before it is accepted.

## Read-only checks requested

| Check | Result | Evidence / note |
| --- | --- | --- |
| CPU / memory / disk headroom | **Not verified** | SSH access to the server was unavailable from this environment. |
| Current Docker services | **Not verified** | Docker commands were not run because the host could not be reached. |
| Current AI business workload | **Not verified** | Process/container workload could not be inspected. |
| Network to `140.143.207.194` | **Not verified** | Target host could not be reached, so network tests from the target server could not be executed. |
| Network to `139.199.174.36` | **Not verified** | Target host could not be reached, so network tests from the target server could not be executed. |
| Suitability for Ansible Controller | **Not recommended yet** | Requires verified CPU, memory, disk, network, SSH key isolation, and backup policy. |
| Suitability for GitHub Actions Runner | **Not recommended yet** | Requires verified workload isolation, disk headroom, Docker impact, and security posture. |
| Suitability for VAFOX Agent | **Not recommended yet** | Requires verified service compatibility and network paths. |
| Suitability for automated backup jobs | **Not recommended yet** | Requires verified disk capacity, I/O headroom, retention policy, and remote backup path. |

## Commands attempted from the assessment environment

The following commands were attempted without making changes to the target server:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new ubuntu@ai.vafox.com '...read-only inspection commands...'
```

Result:

```text
ssh: Could not resolve hostname ai.vafox.com: Temporary failure in name resolution
```

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new ubuntu@1.13.254.217 '...read-only inspection commands...'
```

Result:

```text
ssh: connect to host 1.13.254.217 port 22: Network is unreachable
```

```bash
getent hosts ai.vafox.com || true
ping -c 2 -W 2 1.13.254.217 || true
```

Result:

```text
ping: connect: Network is unreachable
```

## Required verification before reconsidering

Run the following checks from an environment that can reach `1.13.254.217`, or run them directly on the target server. These commands are read-only.

### 1. Host capacity

```bash
hostname
hostname -I
date -Is
uname -a
nproc
lscpu | egrep 'Model name|CPU\(s\)|Thread|Core|Socket'
free -h
df -hT
uptime
```

Minimum recommended baseline for a combined automation control plane on an existing AI host:

- **CPU:** at least 2 idle vCPU available during normal AI workload; 4+ vCPU preferred.
- **Memory:** at least 4 GiB free/available after AI workload; 8 GiB+ preferred if GitHub Actions jobs build containers or run tests.
- **Disk:** at least 40 GiB free for runners, logs, Ansible artifacts, backups metadata, and rollback space; 100 GiB+ preferred if CI jobs use Docker images.
- **Load:** sustained load average should remain comfortably below available CPU count during normal AI workload.

### 2. Docker and current services

```bash
systemctl is-active docker || true
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || true
docker stats --no-stream 2>/dev/null || true
docker system df 2>/dev/null || true
```

Acceptance indicators:

- Existing AI containers are stable and not frequently restarting.
- Docker disk usage leaves adequate image/layer/log headroom.
- No planned automation workload shares mutable AI data paths without explicit backup/rollback design.

### 3. AI workload pressure

```bash
ps -eo pid,ppid,user,comm,%cpu,%mem --sort=-%cpu | head -20
ps -eo pid,ppid,user,comm,%cpu,%mem --sort=-%mem | head -20
ss -tulpen | head -100
```

Acceptance indicators:

- AI workloads do not routinely consume most CPU and memory.
- Control-plane ports can be assigned without conflict.
- The GitHub Actions runner can be isolated from AI runtime credentials and production data.

### 4. Network from the target server to managed nodes

```bash
ping -c 4 -W 2 140.143.207.194
ping -c 4 -W 2 139.199.174.36
nc -vz -w 5 140.143.207.194 22
nc -vz -w 5 139.199.174.36 22
```

Acceptance indicators:

- Low packet loss to both nodes.
- SSH/TCP port 22 reachable, or the documented management port is reachable.
- Latency is stable enough for Ansible orchestration and backup operations.

## Suitability by component

### Ansible Controller

**Current recommendation:** not approved until host and network checks pass.

Ansible itself is lightweight, but the controller role is operationally critical. It requires reliable outbound SSH to all managed nodes, protected credentials, predictable disk space for logs/inventory/playbooks, and enough CPU/memory headroom not to compete with active AI workloads.

### GitHub Actions Runner

**Current recommendation:** not approved until capacity, Docker, and security checks pass.

A self-hosted runner can consume significant CPU, memory, disk, and Docker resources. On an existing AI server, it should only be added if jobs are tightly scoped, concurrency is limited, runner credentials are isolated, and build artifacts/container caches cannot affect production AI services.

### VAFOX Agent

**Current recommendation:** not approved until service compatibility and network checks pass.

The agent may be acceptable if it is lightweight and isolated. However, it should not be deployed until port usage, process pressure, and managed-node connectivity are verified.

### Automated backup jobs

**Current recommendation:** not approved until disk/I/O and remote backup path checks pass.

Automated backups can create CPU, I/O, network, and storage pressure. They should only be scheduled after confirming free disk, retention requirements, bandwidth, backup target availability, restore testing, and non-overlap with AI peak workload windows.

## Final recommendation

**B. 不推荐** as of this assessment.

This does **not** prove that `ai.vafox.com` is technically incapable of serving as the VAFOX Automation Control Plane. It means the required read-only evidence could not be collected, and therefore the safe decision is to withhold approval.

Reclassify to **A. 推荐作为控制中心** only if the follow-up checks confirm:

1. Adequate CPU, memory, disk, and load headroom.
2. Stable Docker/AI workloads with no resource exhaustion or restart loops.
3. Reliable network reachability from the server to `140.143.207.194` and `139.199.174.36`.
4. Clear isolation for Ansible credentials, GitHub Actions runner workspace, VAFOX Agent runtime, and backup data.
5. Documented rollback and recovery procedures.

Reclassify to **C. 需要扩容后推荐** if the server is reachable but any of the following are observed:

- Memory headroom below 4 GiB during normal AI workload.
- Disk free space below 40 GiB, or Docker disk usage is already high.
- CI/backup jobs would contend with production AI workloads.
- Network is reachable but unstable or insufficient for reliable automation.
