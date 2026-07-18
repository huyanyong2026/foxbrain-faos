#!/usr/bin/env bash
set -u

SERVER_NAME="Huyan"
SERVER_IP="140.143.207.194"
EXPECTED_USER="ubuntu"

readonly_section() {
  printf '\n===== %s =====\n' "$1"
}

run_readonly() {
  local description="$1"
  shift
  printf '\n--- %s ---\n' "$description"
  "$@" 2>&1 || printf '[WARN] command failed: %s\n' "$*"
}

readonly_section "VAFOX ${SERVER_NAME} READ-ONLY AUDIT"
printf 'Server: %s\nIP: %s\nExpected user: %s\nStarted at: %s\n' "$SERVER_NAME" "$SERVER_IP" "$EXPECTED_USER" "$(date -Is)"
printf 'Safety: read-only checks only; no system changes, no deletes, no service restarts, no database writes.\n'

readonly_section "Identity"
run_readonly "hostname" hostname
run_readonly "current user" whoami
run_readonly "user id" id
run_readonly "kernel" uname -a
run_readonly "os release" cat /etc/os-release
run_readonly "uptime" uptime

readonly_section "SSH Access Clues"
run_readonly "ssh daemon process" pgrep -a sshd
run_readonly "ssh effective config" sshd -T
run_readonly "authorized_keys metadata" find "$HOME/.ssh" -maxdepth 1 -type f -name 'authorized_keys' -printf '%p %m %u %g %s bytes\n'

readonly_section "System Resources"
run_readonly "cpu and memory" bash -lc 'nproc && free -h'
run_readonly "disk usage" df -hT
run_readonly "block devices" lsblk -f
run_readonly "top processes" ps aux --sort=-%mem | head -20

readonly_section "Network"
run_readonly "listening tcp/udp ports" ss -lntup
run_readonly "ip addresses" ip addr show
run_readonly "routes" ip route show

readonly_section "Docker"
run_readonly "docker version" docker version
run_readonly "docker info" docker info
run_readonly "running containers" docker ps --no-trunc
run_readonly "all containers" docker ps -a --no-trunc
run_readonly "images" docker images --digests
run_readonly "networks" docker network ls
run_readonly "volumes" docker volume ls
run_readonly "compose files under common paths" find /opt /srv "$HOME" -maxdepth 5 -type f \( -name 'docker-compose.yml' -o -name 'compose.yml' -o -name 'docker-compose.yaml' -o -name 'compose.yaml' \) -print

readonly_section "Nginx"
run_readonly "nginx version" nginx -v
run_readonly "nginx service status" systemctl status nginx --no-pager
run_readonly "nginx config test" nginx -t
run_readonly "nginx sites" find /etc/nginx -maxdepth 3 \( -type f -o -type l \) -print
run_readonly "nginx full config" nginx -T

readonly_section "Scheduling and Backups"
run_readonly "system timers" systemctl list-timers --all --no-pager
run_readonly "current user crontab" crontab -l
run_readonly "cron directories" find /etc/cron.d /etc/cron.daily /etc/cron.hourly /etc/cron.weekly /etc/cron.monthly -maxdepth 1 -type f -print
run_readonly "backup path clues" find /opt /srv /var/backups "$HOME" -maxdepth 4 \( -iname '*backup*' -o -iname '*bak*' -o -iname '*dump*' \) -print

readonly_section "Application Clues"
run_readonly "common app directories" find /opt /srv /var/www "$HOME" -maxdepth 3 -type d -print
run_readonly "environment file metadata only" find /opt /srv /var/www "$HOME" -maxdepth 5 -type f \( -name '.env' -o -name '*.env' \) -printf '%p %m %u %g %s bytes\n'

readonly_section "Report Template"
cat <<'REPORT'
# VAFOX 服务器只读审计执行报告

## 基本信息
- 服务器：Huyan
- IP：140.143.207.194
- 执行用户：
- 执行时间：
- 审计脚本：server_audit_huyan.sh
- 脚本 Git Commit：

## 只读约束确认
- [ ] 未修改系统配置
- [ ] 未删除文件
- [ ] 未重启服务
- [ ] 未修改数据库
- [ ] 未执行写入型部署命令

## 审计摘要
| 项目 | 结果 | 风险等级 | 备注 |
| --- | --- | --- | --- |
| 系统版本 |  |  |  |
| SSH 接入 |  |  |  |
| Docker |  |  |  |
| Nginx |  |  |  |
| 端口监听 |  |  |  |
| 定时任务 |  |  |  |
| 磁盘容量 |  |  |  |
| 备份线索 |  |  |  |
| 数据目录 |  |  |  |

## 发现的问题
1.
2.
3.

## 建议动作
1.
2.
3.
REPORT

printf '\nCompleted at: %s\n' "$(date -Is)"
