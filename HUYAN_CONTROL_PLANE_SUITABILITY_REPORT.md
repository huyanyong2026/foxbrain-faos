# HUYAN Control Plane Suitability Report

- 审计对象：`huyan.vafox.com`
- 服务器 IP：`140.143.207.194`
- 服务器用户：`ubuntu`
- 目标定位：VAFOX Control Plane / 机器人控制中心
- 审计时间：2026-07-18 UTC
- 审计模式：只读审计；未安装软件、未修改系统、未修改 Docker、未修改 Nginx、未修改数据库、未重启服务。

## 0. 执行摘要

本次审计尝试通过 SSH 以只读方式连接 `ubuntu@140.143.207.194`，用于采集 CPU、内存、磁盘、服务、Docker、Nginx 以及从 Huyan 到目标节点 `1.13.254.217`、`139.199.174.36` 的网络连通性。当前执行环境到目标服务器的 22 端口返回：`Network is unreachable`，因此无法进入服务器执行只读采集命令。

由于关键服务器侧事实无法验证，本报告不能把 Huyan 判定为“推荐”。在当前证据下，Huyan 作为 VAFOX Robot Control Plane 的结论为：**不推荐**。

> 说明：该“不推荐”不是证明服务器能力不足，而是因为控制平面上线前必须完成的容量、服务、Docker、Nginx、网络路径审计均未能从服务器侧验证。若后续在具备 SSH/VPN/堡垒机访问的环境完成只读复核，并满足资源与隔离条件，结论可重新评估为“推荐”或“扩容后推荐”。

## 1. 审计边界与禁止项核对

| 项目 | 状态 |
| --- | --- |
| 修改系统 | 未执行 |
| 安装软件 | 未执行 |
| 修改 Docker | 未执行 |
| 修改 Nginx | 未执行 |
| 修改数据库 | 未执行 |
| 重启服务 | 未执行 |
| 写入服务器文件 | 未执行 |

本地仅新增本报告文件，用于记录只读审计结果。

## 2. 访问性检查

| 检查项 | 结果 | 影响 |
| --- | --- | --- |
| SSH 到 `ubuntu@140.143.207.194` | 失败：`Network is unreachable` | 无法采集服务器侧资源与运行态。 |
| HTTPS 到 `https://huyan.vafox.com` | 失败：代理返回 `CONNECT tunnel failed, response 403` | 当前执行环境无法验证线上 Huyan Web/Nginx/TLS 状态。 |
| 本地到 `140.143.207.194` ping | 失败：`Network is unreachable` | 当前执行环境无法验证公网 ICMP 连通性。 |
| 本地到 `1.13.254.217` ping | 失败：`Network is unreachable` | 不能替代服务器侧网络审计。 |
| 本地到 `139.199.174.36` ping | 失败：`Network is unreachable` | 不能替代服务器侧网络审计。 |

## 3. CPU / 内存 / 磁盘

| 资源项 | 审计结果 | 风险 |
| --- | --- | --- |
| CPU 核数、型号、负载 | 未能采集 | 无法确认是否可承载 Ansible Controller、GitHub Actions Runner、VAFOX Agent 与备份调度。 |
| 内存总量、可用内存、Swap | 未能采集 | 无法评估控制平面与现有 Huyan 业务的内存隔离和峰值余量。 |
| 根分区与 `/opt` 磁盘、inode | 未能采集 | 无法确认日志、Runner 工作目录、备份索引、Docker 数据增长空间。 |

### 建议最低资源基线

若 Huyan 需要同时作为机器人控制中心与控制平面，建议至少满足以下基线后再推荐：

| 组件组合 | 建议最低基线 |
| --- | --- |
| 轻量控制平面 | 4 vCPU、16 GiB RAM、100 GiB 可用磁盘空间 |
| 含 GitHub Actions Runner 与备份调度 | 8 vCPU、32 GiB RAM、200 GiB 可用磁盘空间 |
| 与生产 Huyan Web/API 同机共存 | 需要 cgroup/容器资源限制、日志限额、独立目录、磁盘告警与备份保留策略 |

## 4. 当前服务

服务器侧 `systemctl`、监听端口、进程列表均未能采集。

上线控制平面前必须确认：

- Huyan 当前 Web/API/Worker 服务的进程、端口与启动方式。
- 是否已有高 CPU/高内存业务进程。
- 22、80、443 以及内部控制端口是否存在冲突。
- 是否存在定时任务、备份任务、AI 推理服务或数据库本地实例。

## 5. Docker 情况

Docker CLI、Docker daemon、容器列表、镜像、volume、网络、资源占用均未能采集。

上线控制平面前必须确认：

- Docker 是否已安装且运行稳定。
- 当前是否有 Huyan 或 VAFOX 生产容器。
- Docker root dir 磁盘剩余空间。
- 容器是否已有 restart loop、unhealthy 状态或高资源占用。
- 是否允许新增控制平面容器；若允许，必须在维护窗口内规划，不应在审计阶段修改。

## 6. Nginx 情况

Nginx 版本、进程状态、站点配置、证书路径、反向代理 upstream 均未能采集。

上线控制平面前必须确认：

- `huyan.vafox.com` 当前是否由 Nginx 承载。
- 现有 server block、TLS 证书、反向代理路径。
- 是否可安全增加控制平面路径或子域名。
- 控制平面应避免与现有 Huyan 页面/API 路径冲突。

## 7. 网络检查

目标要求检查从 Huyan 到以下节点的网络：

1. `1.13.254.217`
2. `139.199.174.36`

由于无法 SSH 到 Huyan，未能从服务器侧执行 `ping`、`ip route get`、`nc`/`curl` 等只读网络检查。当前执行环境本地对这些地址的网络检查也失败，但这只说明本审计环境的网络受限，不能证明 Huyan 到目标节点不可达。

上线前必须从 Huyan 服务器侧完成：

```text
ping -c 4 1.13.254.217
ping -c 4 139.199.174.36
ip route get 1.13.254.217
ip route get 139.199.174.36
```

如有明确服务端口，还应只读检查 TCP 连通性，例如：

```text
nc -vz 1.13.254.217 <port>
nc -vz 139.199.174.36 <port>
```

## 8. 组件适配性评估

| 目标组件 | 当前结论 | 原因 |
| --- | --- | --- |
| Ansible Controller | 暂不适合上线 | 无法验证 CPU、内存、磁盘、Python/SSH 环境、到被控节点网络。 |
| GitHub Actions Runner | 暂不适合上线 | Runner 可能引入构建负载、工作目录膨胀与凭据风险；服务器容量与隔离状态未验证。 |
| VAFOX Agent | 暂不适合上线 | 无法确认与现有服务、端口、Docker/Nginx、系统权限模型的兼容性。 |
| Backup Scheduler | 暂不适合上线 | 无法确认磁盘空间、备份目标、数据库/文件路径与现有定时任务冲突。 |

## 9. 风险清单

- **访问风险**：当前环境无法 SSH 到服务器，无法完成服务器侧事实采集。
- **容量风险**：CPU、内存、磁盘、inode、负载均未知。
- **运行态风险**：当前服务、端口、Docker 容器、Nginx 配置均未知。
- **网络风险**：Huyan 到两个目标节点的路径未验证。
- **安全风险**：GitHub Actions Runner 与控制平面通常需要凭据和执行权限，若与生产 Web/API 同机部署，必须有隔离与审计策略。
- **可恢复性风险**：Backup Scheduler 未验证前，不应假设该节点可承担备份编排职责。

## 10. 后续只读复核建议

在具备服务器访问的网络环境中，建议仅执行以下只读命令采集事实：

```text
hostname; date -Is; uptime
nproc; lscpu | sed -n '1,25p'
free -h
df -hT; df -ih
systemctl --type=service --state=running --no-pager --no-legend
ss -tulpen
docker version
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker system df
nginx -v
systemctl is-active nginx
find /etc/nginx -maxdepth 2 -type f \( -name '*.conf' -o -path '*/sites-enabled/*' \) -print
ping -c 4 1.13.254.217
ping -c 4 139.199.174.36
ip route get 1.13.254.217
ip route get 139.199.174.36
```

仍需保持：不安装、不修改、不重启、不写服务器文件。

## 11. 最终结论

**结论：不推荐。**

在当前只读审计环境无法访问 Huyan 服务器的情况下，无法验证控制平面上线所需的关键条件。建议先解决 SSH/VPN/堡垒机访问路径，完成服务器侧只读复核；若复核显示资源充足、Docker/Nginx 运行态健康、网络可达、并能为 Runner/Agent/Backup 提供隔离与限额，则可重新评估为“推荐”或“扩容后推荐”。
