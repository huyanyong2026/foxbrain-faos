# VAFOX Control Plane Phase 1 Readiness Report

Generated UTC: 2026-07-18

## 0. Audit Object

| Item | Value |
| --- | --- |
| Target domain | `ai.vafox.com` |
| Target public IP | `1.13.254.217` |
| Current role | AI Workforce server |
| Proposed additional role | VAFOX Control Plane Phase 1 |
| Proposed control directory | `/opt/vafox-control` |
| Existing AI business directory to protect | `/opt/ai-vafox` |
| Audit mode | Read-only readiness assessment |
| Remote operation policy | Do not deploy, install, restart, edit, prune, migrate, or change any server state |

## 1. Executive Conclusion

**Conclusion: 需要扩容 / 补充实测后再部署。**

The AI server is strategically suitable to become the first VAFOX Control Plane host because the existing architecture already identifies `ai.vafox.com` / `1.13.254.217` as the future control-plane candidate and separates the AI workload under `/opt/ai-vafox` from the proposed control-plane domain under `/opt/vafox-control`.

However, this readiness audit is intentionally read-only and no live server metrics are attached in the repository for the following mandatory checks: CPU saturation, memory pressure, disk headroom, Docker container resource usage, current AI service load, and the actual `/opt/ai-vafox` directory footprint. Because Phase 1 adds an Ansible Controller, GitHub Actions Runner, VAFOX Agent, and Backup Scheduler on top of the current AI Workforce role, the safe decision is **not direct production deployment until capacity is verified**.

Recommended gate:

- **Direct deployment** only if all mandatory thresholds in Section 4 pass.
- **Scale up first** if any CPU, memory, disk, Docker, or AI service load threshold is marginal.
- **Do not deploy** if the AI service is already resource-constrained, the disk has insufficient backup staging capacity, or `/opt/ai-vafox` is not cleanly isolated from automation secrets and runner workspaces.

## 2. Phase 1 Scope Being Evaluated

Phase 1 is assumed to add these capabilities to the AI Workforce server:

| Component | Purpose | Expected footprint | Risk level |
| --- | --- | --- | --- |
| Ansible Controller | Run read-only health checks, deploy orchestration, rollback orchestration against VAFOX nodes | Low CPU except during playbook execution; low steady memory | Medium because it can control other hosts |
| GitHub Actions Runner | Execute CI/CD jobs and controlled automation workflows | Bursty CPU, memory, disk, and network usage | High because unbounded jobs can compete with AI services |
| VAFOX Agent | Local control-plane health, inventory, and telemetry helper | Low steady resource usage | Medium because it may run privileged checks |
| Backup Scheduler | Coordinate scheduled backups and restore-test manifests | Low CPU but potentially high disk and I/O during backup windows | High because backup staging can fill disks |

Phase 1 should be treated as an **operations plane**, not as part of the public AI serving path. It must be isolated by directory, Linux user, systemd unit namespace, secrets, logs, and resource limits.

## 3. Read-only Checks Required Before Deployment

The following commands are safe for an operator to run from an SSH session on `ai.vafox.com` because they inspect state only. They do not install packages, modify files, restart services, prune Docker objects, or change configuration.

### 3.1 CPU

```bash
hostnamectl
nproc
lscpu
uptime
printf '\nTop CPU processes:\n'
ps -eo pid,ppid,user,comm,%cpu,%mem --sort=-%cpu | head -20
printf '\nLoad snapshot:\n'
cat /proc/loadavg
```

Pass criteria:

- 1-minute load average normally stays below `0.70 * vCPU count`.
- 5-minute and 15-minute load averages are stable and not rising during normal AI traffic.
- No AI process is constantly CPU-starved.
- At least 2 vCPU are available for very small Phase 1 usage; 4+ vCPU are recommended if the GitHub runner will build containers or run tests.

### 3.2 Memory

```bash
free -h
cat /proc/meminfo | egrep 'MemTotal|MemAvailable|SwapTotal|SwapFree'
ps -eo pid,ppid,user,comm,%cpu,%mem,rss --sort=-%mem | head -20
```

Pass criteria:

- `MemAvailable` is at least 25% of total memory during normal traffic.
- Absolute available memory is at least 2 GB for lightweight Phase 1.
- 4 GB or more free/available is recommended if the GitHub runner may execute builds, Python dependency installs, browser tests, or Docker image operations.
- Swap is not being heavily used as a substitute for RAM.

### 3.3 Disk

```bash
df -hT
printf '\nInode usage:\n'
df -ih
printf '\nTop /opt directories:\n'
du -xhd1 /opt 2>/dev/null | sort -h
printf '\nDocker disk usage:\n'
docker system df 2>/dev/null || true
```

Pass criteria:

- Root filesystem and `/opt` filesystem, if separate, have at least 30% free capacity.
- At least 20 GB free is recommended before creating `/opt/vafox-control`.
- At least 50 GB free is recommended if backup staging and GitHub runner workspaces live on the same disk.
- Inode usage is below 80%.
- Docker image/container/volume usage is understood before scheduling runner jobs or backup staging.

### 3.4 Docker Containers and Resources

```bash
docker version 2>/dev/null || true
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null || true
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}' 2>/dev/null || true
docker inspect $(docker ps -q 2>/dev/null) --format '{{.Name}} CPU={{.HostConfig.NanoCpus}} Memory={{.HostConfig.Memory}} Restart={{.HostConfig.RestartPolicy.Name}}' 2>/dev/null || true
```

Pass criteria:

- AI-serving containers have explicit or well-understood CPU and memory behavior.
- No container is in a crash loop.
- Docker resource usage leaves enough headroom for transient runner jobs.
- Control-plane containers, if added later, must use explicit resource limits and must not share AI application secrets.

### 3.5 Current AI Service Load

```bash
printf '\nSystemd AI units:\n'
systemctl list-units --type=service --all | egrep -i 'ai|vafox|foxbrain|worker|model|llm' || true
printf '\nListening sockets:\n'
ss -lntup
printf '\nRecent high-level service state:\n'
systemctl --no-pager --failed
printf '\nAI process candidates:\n'
ps -eo pid,ppid,user,comm,args,%cpu,%mem --sort=-%cpu | egrep -i 'ai|vafox|foxbrain|python|node|uvicorn|gunicorn|model|llm|worker' | head -30
```

Pass criteria:

- AI services are healthy before adding the control plane.
- No failed systemd units related to AI workloads.
- No evidence that public AI service latency is already constrained by CPU, memory, I/O, or Docker contention.
- Control-plane scheduled jobs can be placed outside AI traffic peaks.

### 3.6 `/opt/ai-vafox` Structure

```bash
printf '\nDirectory metadata:\n'
stat /opt/ai-vafox 2>/dev/null || true
printf '\nTop-level structure:\n'
find /opt/ai-vafox -maxdepth 2 -mindepth 1 -printf '%M %u %g %p\n' 2>/dev/null | sort | head -200
printf '\nSize summary:\n'
du -xhd2 /opt/ai-vafox 2>/dev/null | sort -h | tail -50
printf '\nSecret-like filenames requiring review, names only:\n'
find /opt/ai-vafox -maxdepth 4 -type f \( -iname '*.env' -o -iname '*secret*' -o -iname '*key*' -o -iname '*token*' \) -printf '%M %u %g %p\n' 2>/dev/null | sort
```

Pass criteria:

- `/opt/ai-vafox` exists and is clearly dedicated to AI business workloads.
- Ownership and permissions are consistent with the AI runtime account.
- AI business secrets are not stored in paths planned for control-plane automation.
- Large model/data directories are accounted for before backup staging is scheduled.

### 3.7 Suitability for `/opt/vafox-control`

```bash
printf '\n/opt metadata:\n'
stat /opt
printf '\nExisting vafox-control check:\n'
stat /opt/vafox-control 2>/dev/null || true
printf '\n/opt capacity:\n'
df -hT /opt
printf '\n/opt top-level ownership:\n'
find /opt -maxdepth 1 -mindepth 1 -printf '%M %u %g %p\n' 2>/dev/null | sort
```

Pass criteria:

- `/opt/vafox-control` is absent or empty before planned creation, unless an existing controlled prototype is documented.
- `/opt` has enough capacity for runner workspaces, Ansible artifacts, logs, and backup manifests.
- Control-plane data can be owned by a dedicated `vafox-exec` account rather than the AI service account or long-running root processes.

## 4. Phase 1 Capacity Decision Matrix

| Area | Direct deployment threshold | Scale-up threshold | Do-not-deploy threshold |
| --- | --- | --- | --- |
| CPU | Load normally below 70% of vCPU count; 4+ vCPU preferred | Sustained load 70-90% or only 2 vCPU with active AI workloads | Sustained load above 90%, CPU steal, or AI latency already CPU-bound |
| Memory | 25%+ available and 4 GB+ available for runner workloads | 10-25% available or less than 4 GB available | Less than 10% available, heavy swap, or OOM history |
| Disk | 30%+ free and 50 GB+ free if staging backups locally | 15-30% free or 20-50 GB free | Less than 15% free, inode pressure, or unknown Docker volume growth |
| Docker | Stable containers and understood resource usage | Some containers lack limits but usage is low | Crash loops, uncontrolled growth, or AI containers already constrained |
| AI load | Normal latency and no failed AI services | Peak-time pressure but off-peak automation is possible | Unstable AI service, failed units, or high production incidents |
| `/opt/ai-vafox` | Cleanly isolated from control-plane secrets and workspaces | Minor permission/structure cleanup required | Mixed secrets, unclear ownership, or no reliable inventory |
| `/opt/vafox-control` | Can be created with dedicated owner and enough disk | Needs disk/account/permission preparation | Cannot isolate from AI runtime or lacks filesystem capacity |

## 5. Component Readiness Assessment

### 5.1 Ansible Controller

**Readiness: Conditionally ready after host metrics pass.**

Ansible itself is lightweight, but its operational authority is high. It is appropriate for Phase 1 if the following controls are implemented:

- Dedicated directory: `/opt/vafox-control/ansible`.
- Dedicated user: `vafox-exec`.
- Separate SSH keys from AI service credentials.
- Ansible Vault or equivalent for secrets.
- Read-only health-check playbooks first; deploy and rollback playbooks gated separately.
- Localhost inventory uses `ansible_connection: local` for AI-node self-checks.

### 5.2 GitHub Actions Runner

**Readiness: Not safe for direct deployment without resource limits.**

The runner is the most resource-variable Phase 1 component. It can run builds, tests, dependency installs, and Docker commands that compete directly with AI services.

Minimum controls before enabling jobs:

- Dedicated runner under `/opt/vafox-control/runner`.
- One runner label scoped to VAFOX control tasks only; do not use broad default labels for arbitrary jobs.
- Concurrency limit of 1 during Phase 1.
- Explicit systemd/cgroup CPU and memory limits.
- Job allowlist and repository allowlist.
- Runner work directory cleanup policy.
- No access to `/opt/ai-vafox` secrets unless a specific deployment workflow requires a narrowly scoped read.

### 5.3 VAFOX Agent

**Readiness: Conditionally ready if implemented as a low-footprint local agent.**

The VAFOX Agent can be added if it only performs local telemetry, inventory, and health reporting during Phase 1.

Required controls:

- Runs as `vafox-exec` or a more restricted service account.
- Read-only default mode.
- No public listener by default.
- Logs to `/opt/vafox-control/logs/agent` or `/var/log/vafox-control`.
- Explicit CPU and memory caps if long-running.

### 5.4 Backup Scheduler

**Readiness: Requires disk and I/O validation before deployment.**

Backup scheduling can be lightweight when it only coordinates manifests, but it can become high-risk if it stages archives locally on the AI server.

Required controls:

- Separate backup manifests under `/opt/vafox-control/backups/manifests`.
- Temporary staging path with hard capacity policy.
- No backup jobs during AI peak traffic.
- Retention policy before first scheduled run.
- Restore-test metadata stored separately from live AI data.
- Alerting when free disk falls below thresholds.

## 6. Proposed `/opt/vafox-control` Phase 1 Layout

```text
/opt/vafox-control/
├── ansible/
│   ├── inventories/
│   ├── playbooks/
│   ├── roles/
│   ├── vault/
│   └── ansible.cfg
├── runner/
│   ├── actions-runner/
│   ├── work/
│   └── hooks/
├── agent/
├── backups/
│   ├── manifests/
│   ├── staging/
│   └── restore-tests/
├── deploy/
│   ├── artifacts/
│   ├── release-manifests/
│   └── locks/
├── secrets/
├── logs/
│   ├── ansible/
│   ├── runner/
│   ├── agent/
│   └── backup/
└── README.md
```

Recommended permissions when deployment is eventually approved:

| Path | Owner | Group | Mode |
| --- | --- | --- | --- |
| `/opt/vafox-control` | `vafox-exec` | `vafox-exec` | `0750` |
| `/opt/vafox-control/secrets` | `vafox-exec` | `vafox-exec` | `0700` |
| `/opt/vafox-control/ansible/vault` | `vafox-exec` | `vafox-exec` | `0700` |
| `/opt/vafox-control/runner/work` | `vafox-exec` | `vafox-exec` | `0750` |
| `/opt/vafox-control/logs` | `vafox-exec` | `adm` | `0750` |

## 7. Deployment Recommendation

### Current recommendation

**需要扩容 / 补充实测后再部署。**

This recommendation is intentionally conservative because the target server is already the AI Workforce server, and the requested audit must not perform server operations. Without live CPU, memory, disk, Docker, AI-load, and `/opt/ai-vafox` evidence, a direct deployment decision would be unsafe.

### When it can become “推荐直接部署”

Approve direct Phase 1 deployment only after all of the following are confirmed from read-only evidence:

1. CPU load is comfortably below the direct-deployment threshold.
2. Memory has enough available headroom for runner bursts.
3. Disk has enough free space for `/opt/vafox-control`, logs, runner workspaces, and backup manifests.
4. Docker containers are stable and not consuming uncontrolled resources.
5. AI service load is healthy and not resource-constrained.
6. `/opt/ai-vafox` is structurally clean and isolated.
7. `/opt/vafox-control` can be created with dedicated ownership, secrets, logs, and resource controls.

### When it should become “不推荐”

Do not deploy Phase 1 on this server if any of the following are true:

- AI service is already unstable or resource-bound.
- Disk space is insufficient for safe runner and backup operation.
- Docker is in a crash-loop or uncontrolled-growth state.
- `/opt/ai-vafox` mixes application runtime data with automation secrets or operator workspaces.
- A dedicated control-plane account and secret boundary cannot be enforced.
- GitHub Actions jobs cannot be constrained to safe labels, concurrency, and resource limits.

## 8. Final Readiness Status

| Decision | Status |
| --- | --- |
| Recommended direct deployment | Not yet |
| Needs scale-up or measured capacity validation | Yes |
| Not recommended | Only if mandatory checks fail |
| Final conclusion | **需要扩容 / 补充实测后再部署** |

