# AI Control Plane Suitability Report

## Executive Summary

- **Target domain:** `ai.vafox.com`
- **Target server IP:** `1.13.254.217`
- **SSH user:** `ubuntu`
- **Current role:** AI Workforce runtime node
- **Proposed future role:** VAFOX Automation Control Plane
- **Audit mode:** Read-only
- **Audit date:** 2026-07-18 UTC
- **Final conclusion:** **不推荐**

This report records a read-only feasibility audit attempt for using `ai.vafox.com` / `1.13.254.217` as the VAFOX Control Plane. The audit could not collect host-level evidence because the execution environment had no network route to the target server. Because CPU, memory, disk, Docker, AI service load, and east-west network checks could not be verified, the server should **not** be promoted to a control-plane role based on the currently available evidence.

## Scope and Constraints

### Requested checks

1. CPU, memory, and disk headroom.
2. Docker container inventory and resource usage.
3. Current AI service load.
4. Network connectivity from `1.13.254.217` to:
   - `140.143.207.194`
   - `139.199.174.36`
5. Suitability for running:
   - Ansible Controller
   - GitHub Actions Runner
   - VAFOX Agent
   - Backup Scheduler

### Explicit prohibitions observed

No system modification was attempted. The audit did not:

- Modify the system.
- Create accounts.
- Install software.
- Modify Docker.
- Modify Nginx.
- Modify databases.

## Access Attempt Results

The audit environment could not reach the server over SSH or basic network probes.

| Check | Command | Result |
| --- | --- | --- |
| SSH reachability | `ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new ubuntu@1.13.254.217 'hostname && date -u'` | Failed: `Network is unreachable` |
| TCP/22 reachability | `nc -vz -w 5 1.13.254.217 22` | Failed: `Network is unreachable` |
| ICMP reachability | `ping -c 3 -W 3 1.13.254.217` | Failed: `Network is unreachable` |
| Local route inspection | `ip route` | Could not run because `ip` command is unavailable in the local execution environment |

## Findings

### 1. CPU / Memory / Disk Headroom

**Status:** Not verified.

The audit could not establish a shell session on `1.13.254.217`, so the following required read-only checks could not be run:

- `uptime`
- `nproc`
- `lscpu`
- `free -h`
- `df -h`
- `du`-based capacity checks for application, Docker, log, and backup paths
- inode availability checks such as `df -ih`

**Control-plane impact:** Unknown capacity creates material risk. A control plane should have predictable headroom for orchestration, scheduled automation, logs, repository checkout/build activity, and emergency maintenance operations.

### 2. Docker Containers and Resource Usage

**Status:** Not verified.

The audit could not run read-only Docker commands such as:

- `docker ps --format ...`
- `docker stats --no-stream`
- `docker system df`
- read-only inspection of container restart counts and exposed ports

**Control-plane impact:** Unknown Docker load is a blocker. If the current AI Workforce runtime already consumes most CPU, memory, disk I/O, GPU, or network resources, adding control-plane duties would increase failure-domain coupling.

### 3. Current AI Service Load

**Status:** Not verified.

The audit could not verify:

- Process-level CPU and memory usage.
- AI service request load.
- Queue depth or worker saturation.
- Log growth rate.
- GPU presence/utilization, if applicable.
- Service restart frequency or error rate.

**Control-plane impact:** The target host currently runs AI Workforce workloads. Without load evidence, it is unsafe to assume spare capacity for orchestration and backup jobs.

### 4. Network Connectivity to Required Nodes

**Status:** Not verified from the server.

Required destination checks from `1.13.254.217` could not be performed:

- `140.143.207.194`
- `139.199.174.36`

Suggested read-only checks for a future successful audit:

```bash
ping -c 5 140.143.207.194
ping -c 5 139.199.174.36
nc -vz -w 5 140.143.207.194 22
nc -vz -w 5 139.199.174.36 22
nc -vz -w 5 140.143.207.194 443
nc -vz -w 5 139.199.174.36 443
```

**Control-plane impact:** Network reachability is mandatory for a control plane. If the server cannot reliably reach managed nodes and external automation endpoints, Ansible, runners, agents, and backups will be unreliable.

## Workload Suitability Assessment

| Proposed workload | Suitability | Reason |
| --- | --- | --- |
| Ansible Controller | **不推荐 / Not currently recommended** | Requires stable network reachability, SSH access to managed nodes, predictable CPU/memory, and reliable disk for inventories, logs, and playbook execution. None could be verified. |
| GitHub Actions Runner | **不推荐 / Not currently recommended** | Can create bursty CPU, memory, disk, and network load. Co-locating with AI runtime workloads is risky without measured headroom and isolation evidence. |
| VAFOX Agent | **不推荐 / Not currently recommended** | Agent feasibility depends on verified service health, network paths, observability, and failure isolation. These are unverified. |
| Backup Scheduler | **不推荐 / Not currently recommended** | Backups are I/O- and network-sensitive. Disk capacity, snapshot strategy, retention paths, and destination reachability were not verified. |

## Risk Assessment

| Risk | Severity | Notes |
| --- | --- | --- |
| No verified administrative access from audit environment | High | Prevented all host-level checks. |
| Unknown resource headroom | High | Control-plane workloads may contend with AI services. |
| Unknown Docker footprint | High | Container resource usage and port conflicts are unknown. |
| Unknown AI service saturation | High | Current role may already be resource-intensive. |
| Unknown network reachability to managed nodes | High | Mandatory for Ansible, agents, and backup workflows. |
| Failure-domain coupling | Medium to High | Combining AI runtime and automation control plane can make incidents harder to isolate. |

## Recommendation

### Final conclusion: **不推荐**

`ai.vafox.com` / `1.13.254.217` is **not recommended** as the VAFOX Automation Control Plane based on the current audit evidence. This is not a finding that the server is technically incapable; it is a finding that suitability could not be proven under the required read-only audit because the server was unreachable from the audit environment.

## Conditions for Reconsideration

The conclusion can be revised to **扩容后推荐** or **推荐** only after a successful read-only audit verifies at minimum:

1. Sustained CPU headroom under normal AI workload.
2. Sufficient memory headroom for concurrent automation jobs.
3. Sufficient disk and inode headroom for Docker layers, logs, repositories, artifacts, and backups.
4. Docker container resource usage and restart health.
5. Current AI service load and peak patterns.
6. Reliable network connectivity from `1.13.254.217` to `140.143.207.194` and `139.199.174.36`.
7. Clear isolation plan between AI runtime workloads and control-plane workloads.
8. Backup retention and restore verification process.

## Suggested Read-Only Follow-Up Command Set

If network access is restored, the following read-only command set can be executed on the server without changing system state:

```bash
hostnamectl
date -u
uptime
nproc
lscpu | sed -n '1,25p'
free -h
df -h
df -ih
ps -eo pid,ppid,comm,%cpu,%mem --sort=-%cpu | head -25
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker stats --no-stream
docker system df
ss -tulpen
ping -c 5 140.143.207.194
ping -c 5 139.199.174.36
nc -vz -w 5 140.143.207.194 22
nc -vz -w 5 139.199.174.36 22
nc -vz -w 5 140.143.207.194 443
nc -vz -w 5 139.199.174.36 443
```
