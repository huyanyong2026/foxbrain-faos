# FireFox Production Readiness Audit V1.0

## 1. 审计结论

- 审计时间：2026-07-14 09:20-09:45（Asia/Shanghai）
- 审计对象：`huyan.vafox.com`、`ai.vafox.com`，并核验 `core.vafox.com`、`gateway.vafox.com` 及 SAP 只读数据链路
- 审计方式：安全只读检查
- 综合结论：**有条件运行，暂不建议宣布“全面生产就绪”**
- 生产可用性：四个域名均可访问，核心服务正常运行，TLS 证书有效
- 数据安全边界：当前运行链路符合 `SAP -> core -> ai/huyan/gateway`；未发现 `ai` 或 `huyan` 运行进程直接访问 SAP
- 主要阻塞项：历史 SAP 配置未完全退场、生产文件权限过宽、AI 主机网络规则过宽、Core 容量与独立数据盘不符合既定目标、密钥治理和服务最小权限仍需收口

本次审计没有修改代码、数据库、SAP、Core 数据、配置或服务；没有重启、部署、迁移、删除文件，也没有触发同步任务。

## 2. 关键证据摘要

| 检查项 | 结果 | 证据 |
|---|---|---|
| SAP 来源权限 | 通过 | 来源账号不是 `sa`，属于 `db_datareader`；`SELECT=1`，`INSERT/UPDATE/DELETE/ALTER/CONTROL=0`，非 `sysadmin` |
| 22:00 镜像任务 | 通过 | `foxbrain-sap-mirror.timer` 已启用，每日 22:00 执行 |
| 最近镜像结果 | 通过 | 2026-07-13 22:00:01 至 22:04:16，2,120/2,120 表成功，失败 0 |
| 行级复制校验 | 通过 | 2,134 个进度记录全部完成；来源与副本均为 4,937,789 行 |
| 业务对账 | 通过 | 商品、库存、客户、供应商、销售单据/金额、采购单据/金额全部一致 |
| Core 数据库暴露 | 通过 | SQL Server 仅监听 `127.0.0.1:11433`，公网探测不可达 |
| Core API 认证 | 通过 | 无令牌访问返回 401；`ai`、`huyan`、`gateway` 使用独立只读作用域 |
| Huyan 运行链路 | 通过 | 运行进程配置 `core.vafox.com`；无运行时 `SAP_HOST`/SAP API；同步调度关闭 |
| AI 运行链路 | 通过 | 容器配置 `core.vafox.com`；运行时 `SAP_*` 键数量为 0；Core 状态读取 200 |
| Gateway 运行链路 | 通过 | `/api/core/status` 代理 Core 公共只读状态，返回 200 |
| 防止直连 SAP | 通过但需清理 | `huyan`、`ai` 均有到 SAP 公网地址的出站拒绝规则；历史配置仍存在 |

## 3. 生产可用性

| 系统 | 入口状态 | 服务状态 | 备注 |
|---|---|---|---|
| `huyan.vafox.com` | 首页 GET 200；受保护页面重定向登录 | `firefox-portal.service` active | HEAD 请求返回 501，GET 正常 |
| `ai.vafox.com` | 登录页 200；健康接口 200 | `vafox-auth` healthy，任务 Worker 运行 | 当前真实经营分析历史仍较少 |
| `core.vafox.com` | 未授权状态接口 401，符合预期 | Core API active，镜像定时器 active | API 仅通过 Nginx 对外，数据库仅本机 |
| `gateway.vafox.com` | 首页 200；Core 状态接口 200 | Nginx 正常 | 公共接口只提供脱敏状态 |

TLS 到期时间：

- `huyan.vafox.com`：2026-09-29
- `ai.vafox.com`：2026-10-06
- `core.vafox.com`：2026-10-11
- `gateway.vafox.com`：2026-10-11

## 4. 数据链路审计

```text
SAP-PROD
  |  专用只读账号：仅 SELECT
  |  每日 22:00 逻辑镜像
  v
core.vafox.com / SQL Server Mirror
  |  独立只读令牌与作用域
  +--> huyan.vafox.com   facts:read
  +--> ai.vafox.com      facts:read
  +--> gateway.vafox.com public:read
```

### 4.1 SAP 到 Core

- 来源账号为专用只读账号，非 `sa`，非系统管理员。
- 数据库角色只有 `db_datareader`。
- 权限查询确认无法插入、更新、删除、修改结构或控制数据库。
- 镜像服务为一次性任务，定时器每日 22:00 调用。
- 最近一次任务退出码为 0，执行约 4 分 15 秒。
- 2,120 张来源表全部完成，无缺表、无额外表、无行数差异。
- 最终业务对账报告 `all_passed=true`。

### 4.2 Core 到应用

- Core API 使用专用系统账号 `foxcore` 运行，启用了 `NoNewPrivileges`、`ProtectSystem=strict`、`ProtectHome=yes`、`PrivateTmp=yes`。
- Core 数据库端口只绑定本机，防火墙仅开放 SSH、HTTP、HTTPS。
- 令牌按应用拆分：AI 与 Huyan 为 `facts:read`，Gateway 为 `public:read`。
- Huyan 和 AI 的运行环境均指向 `core.vafox.com`，未发现运行时 SAP 连接键。
- Gateway 仅代理 Core 的公共状态接口，不暴露业务事实接口。

### 4.3 数据新鲜度

- 最近同步完成：2026-07-13 22:04:16。
- 下一次计划同步：2026-07-14 22:00。
- 当前同步模式仍为全量复制；随着数据增长，需要评估执行窗口、增量策略和失败回滚演练。

## 5. 风险与问题

### P1：上线前应优先处理

1. **Huyan 历史 SAP 连接能力尚未完全退场。**
   - 运行进程当前没有 SAP 主机/API 配置，正式调度也已关闭，这是正确状态。
   - 但磁盘仍保留直接 SAP/旧同步相关环境键、旧同步目录、本地 SQL Mirror 和同步数据库容器。
   - 风险：未来误启旧任务可能绕过 Core 单一数据入口。
   - 建议：在备份和回滚方案确认后，先停用并归档旧连接配置，再删除密钥；本次审计未执行。

2. **Huyan 生产数据库和部分备份权限过宽。**
   - `portal.db`、WAL 及多份完整数据库备份为 0644。
   - `/opt/backups` 约 25GB、12,193 个文件，其中至少 129 个普通文件对其他本机用户可读。
   - 风险：主机内低权限账号可能读取经营数据、会话或历史资料。
   - 建议：备份目录 0700、数据库和敏感备份 0600，并由独立服务账号持有。

3. **AI 主机的防火墙与容器暴露策略不一致。**
   - UFW 允许公网访问 3000-3100 和 9443；多个容器绑定 `0.0.0.0`。
   - 外部实测这些端口当前被云侧安全组阻断，但主机策略本身仍过宽。
   - 风险：云安全组调整后，Dify、Portainer 等管理面可能意外暴露。
   - 建议：主机防火墙和容器都只保留 22/80/443，对内部服务改为 localhost 或私有网络绑定。

4. **AI 旧 Compose 文件包含密钥默认值。**
   - 发现 16 类非空默认凭据配置，文件同时为组可写。
   - 本报告不记录任何密钥值。
   - 建议：迁移到 0600 环境文件或密钥管理服务，删除默认值并轮换相关凭据。

5. **Core 未达到既定 1000GB 独立数据盘目标。**
   - 当前 `/opt` 与根分区共用约 200GB 系统盘，已用约 5%，没有独立 1000GB 数据挂载。
   - 当前约 493 万行可以运行，但全库历史增长、备份与索引会持续占用空间。
   - 建议：上线容量评审、独立数据盘、空间告警和恢复演练完成后，再声明长期生产就绪。

### P2：近期治理

1. Huyan Portal 以 root 运行，未启用 `NoNewPrivileges`、`ProtectSystem`、`ProtectHome`、`PrivateTmp` 等系统服务保护。
2. Huyan 与 AI 仍允许 SSH 密码认证；AI 允许 root 使用密钥登录，建议统一为普通运维账号加 sudo，并关闭密码认证。
3. AI Nginx 报告 `worker_connections 4096` 高于进程文件描述符上限 1024，应统一限制配置。
4. Huyan 对 HEAD 请求返回 501，影响部分监控、CDN 和可用性探针。
5. Huyan 实际运行目录为 `/opt/firefox-portal`，仓库位于 `/opt/foxbrain-faos` 且提交版本与运行文件没有强绑定，部署追溯性不足。
6. Core 镜像状态库和多份历史状态备份为 0644；虽然不包含生产业务全量数据，也应收紧为 0600。
7. Core 目前没有 Swap，内存充足但在大批量复制时缺少突发保护；应结合 SQL Server 内存上限评估。
8. AI 经营任务数据库中真实分析记录仍少，技术链路已通但业务使用量不足，需通过受控真实任务验证长期稳定性。
9. 安全响应头存在重复配置，建议在 Nginx 单层统一，避免维护漂移。

### P3：优化项

1. 为四个域名增加证书到期、接口延迟、镜像时长、表差异和磁盘容量告警。
2. 将全量复制逐步升级为可验证的增量复制，但保留周期性全量对账。
3. 建立版本化部署清单，记录仓库提交、构建产物哈希、数据库迁移和回滚点。
4. 统一备份保留周期，避免 `.bak`、旧 release 和日志无限增长。

## 6. 内容分类

### 6.1 生产内容

**Huyan**

- `/opt/firefox-portal/portal.py`
- `/opt/firefox-portal/portal.db`、WAL 及上传目录
- `firefox-portal.service`
- Huyan Nginx 站点配置
- `/opt/foxbrain-faos`：源代码仓库，但不是当前直接运行目录
- 每日备份定时器

**AI / Gateway**

- 当前 AI release、`vafox-auth`、经营任务 Worker
- AI 共享环境文件、身份数据库、业务数据库
- Dify、n8n、PostgreSQL、Redis 等当前依赖服务
- Gateway 静态资源和 Nginx 配置

**Core**

- `/opt/foxbrain-core/api`
- `/opt/foxbrain-core/sync`
- Core SQL Server 容器及数据目录
- `foxbrain-core-api.service`
- `foxbrain-sap-mirror.service/timer`
- 镜像状态库、对账报告和当前配置

### 6.2 归档内容

- 各次部署前的代码、数据库和环境文件备份
- 已完成迁移前后的镜像状态库快照
- 旧 release、旧 Portal 文件和历史日志
- 已签字或已确认的只读权限、对账和发布记录

归档前应记录来源、时间、用途和保留期限，并对敏感文件加密或限制为 0600；本次未移动任何文件。

### 6.3 废弃候选（仅列出，未删除）

**Huyan**

- 旧 SAP 同步目录与环境文件
- 本机 `foxbrain-sap-mirror-sql`、`sap-sync-db` 容器
- 已停用的 SAP 同步 timer/service 备份
- Portal 中不再使用的 SAP 直连代码路径

**AI**

- `/opt/ai-vafox/sap-sync` 旧代码与日志
- 已被 release 镜像替代的旧 `auth-service` 源目录
- 无引用的旧 Compose 备份和过期 release

**Core**

- 已完成迁移且不再用于回滚的中间状态库快照
- 过期调试日志与重复对账报告

所有废弃候选都必须先核对运行引用、建立备份和回滚点，并由负责人批准后再处理。

## 7. 建议整改顺序

1. 收紧 Huyan 数据库/备份权限，收紧 AI 主机防火墙和容器绑定。
2. 轮换并迁移 AI Compose 中的默认密钥；核对所有环境文件权限。
3. 完成 Huyan 旧 SAP 直连能力退场，确保 Core 是唯一事实入口。
4. 为 Huyan Portal 建立专用系统账号和 systemd 沙箱保护。
5. 为 Core 增加独立数据盘、容量告警、备份恢复演练。
6. 建立统一部署版本记录，让运行产物可追溯到 Git commit。
7. 完成一次受控灾难恢复演练和一次镜像失败恢复演练。
8. 整改后重复本审计，目标为 P1 清零后转为“生产就绪”。

## 8. 审计边界与证明

- 只执行了 HTTP GET/HEAD、系统状态读取、文件权限读取、进程环境键名检查、SQLite 只读查询、SQL 权限查询和只读业务对账读取。
- 没有读取或记录密码、令牌、私钥的具体值。
- 没有进行写权限破坏性测试；SAP 写权限结论来自 SQL Server 权限元数据查询。
- 没有修改 SAP、Core 数据、Huyan/AI 数据库或任何生产配置。
- 没有重启服务、执行部署、运行迁移、触发同步或删除文件。

## 9. 最终判定

FireFox 当前核心数据链路已经达到可验证的安全只读结构：SAP 只读复制到 Core，应用通过分权 Core API 读取，最近一次全库同步和业务对账均成功。生产服务当前稳定可用。

但在主机权限、历史直连能力、密钥治理、网络收口、Core 容量和部署追溯方面仍有 P1 风险，因此本次结论为：**允许现状受控运行，不建议扩大开放范围；完成 P1 整改并复审后，再确认全面生产就绪。**
