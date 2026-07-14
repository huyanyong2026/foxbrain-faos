# VAFOX Explorer Identity V1.0 建设报告

## 1. 建设结论

本阶段已完成 Explorer 顾客数字身份基础，并将 Gateway 的 Explorer Life 从预留入口升级为可部署的真实登记入口。系统采用独立身份库，不把顾客身份写回 SAP；购买记录仅通过 `core.vafox.com` 的受保护只读接口匹配。

真实微信授权和手机号验证必须在服务器配置正式凭据后才能开放。未配置时系统会明确显示“尚未开放”，不会使用模拟登录或未经验证的手机号匹配购买记录。

## 2. 数据模型

| 数据表 | 用途 | 隐私边界 |
|---|---|---|
| `explorer_identities` | Explorer ID、显示名、城市、生命周期状态 | OpenID、手机号仅保存 HMAC 摘要，手机号只显示末四位 |
| `explorer_interest_tags` | 徒步、登山、越野跑、露营、摄影、旅行兴趣 | 仅本人选择 |
| `explorer_purchase_links` | 本人与 Core 顾客及购买记录的确认关联快照 | 不保存原始手机号，不向其他 Explorer 开放 |
| `explorer_journey_events` | 活动、路线、旅行、故事、社群记录 | V1 默认 `private` |
| `explorer_oauth_states` | 一次性微信授权状态与同意记录 | 十分钟失效且只能消费一次 |
| `explorer_sessions` | 登录会话 | 只保存会话令牌摘要，30 天到期，可撤销 |
| `explorer_audit_logs` | 登录、匹配、资料更新和退出审计 | IP、浏览器信息仅保存摘要 |

## 3. 页面与用户流程

- `GET /explorer/register`：微信扫码登记、兴趣选择、隐私同意。
- `GET /explorer/auth/wechat/callback`：校验一次性状态并创建或登录 Explorer 身份。
- `GET /explorer`：我的探索人生首页。
- 我的装备：展示本人已匹配的购买记录。
- 我的积分：保留 Explorer Value 说明，不虚构积分。
- 我的探索：记录活动、路线、旅行和故事。
- 我的社群、我的故事：明确显示尚未接入及开放条件。
- `GET /explorer/privacy`：中文隐私说明。

Gateway 首页新增“创建我的 Explorer 身份”及 Explorer Life 真实入口，保留原有户外内容和交互。

## 4. API

### Explorer 同源接口

- `GET /api/explorer/me`
- `GET /api/explorer/equipment`
- `GET /api/explorer/journey`
- `POST /api/explorer/profile`
- `POST /api/explorer/phone/verify`
- `POST /api/explorer/journey`

所有 Explorer API 必须带本人安全会话。写请求执行同源校验；`PUT`、`PATCH`、`DELETE` 均拒绝。

### Core 只读接口

- `GET /api/v1/explorer/customer-match?phone_hash=...`
- `GET /api/v1/objects/customers/{customer_id}/purchases`（CEO 等授权场景保留）

Explorer 匹配接口要求独立的 `explorer:match`，只接收以服务令牌为密钥生成的手机号 HMAC，不接收明文手机号、不返回顾客目录。购买明细接口要求 `customers:read`。Gateway 的 `public:read` 令牌、CEO 令牌和一般 AI 令牌都不能调用 Explorer 匹配接口；浏览器不接触任何 Core 令牌。

## 5. 权限与安全

- Explorer 只能通过会话中的 Explorer ID 查询自己的资料、装备和探索记录。
- 当前没有顾客列表或跨顾客查询页面，员工和 CEO 管理视图留待 Identity Center 权限连接后建设。
- 微信 OpenID、手机号、会话、OAuth state、IP 和 User-Agent 均以用途隔离的 HMAC 摘要存储。
- 手机号必须经外部验证凭据确认，才允许调用 Core 购买匹配。
- Core 仍为只读业务对象 API；未新增 SAP 连接、SAP 写权限或 SAP 写操作。
- 密钥仅通过 `/etc/firefox-explorer.env` 注入，示例文件不包含真实值。
- systemd 服务启用文件系统保护，仅允许写 `/var/lib/firefox-explorer`。

## 6. 测试范围

自动化覆盖：

- 微信授权启动、回调、身份创建和 OAuth state 防重放。
- 手机号验证后购买匹配及“我的装备”展示。
- 两个 Explorer 之间的数据隔离。
- 未登录拒绝、跨站请求拒绝、非允许 HTTP 方法拒绝。
- OpenID 和完整手机号不以明文写入身份数据库。
- Core 顾客和购买接口的敏感权限隔离。
- Gateway 公开令牌无法读取顾客对象和购买记录。
- 未配置微信凭据时拒绝创建虚假授权地址。

最终结果：全仓 `122` 项测试全部通过；Explorer/Core/权限定向测试 `21` 项全部通过；Gateway 首页与五项静态资源烟测全部通过。

## 7. 部署说明

本分支按要求提交 PR，不直接修改 `main`，也不在 PR 合并前部署生产。合并后上线需：

1. 备份 Gateway 代码、Nginx 配置和现有数据。
2. 创建 `/var/lib/firefox-explorer` 并授予 `www-data`。
3. 从模板创建 `/etc/firefox-explorer.env`，权限设为仅 root 可读。
4. 在 Core token policy 中创建 Explorer 专用令牌，仅授予 `explorer:match`。
5. 安装并启动 `firefox-explorer-identity.service`。
6. 合并 Nginx Explorer 路由，先执行配置检查再平滑重载。
7. 完成真实微信回调域名校验、手机号验证和一位授权顾客的人工验收。

## 8. 下一步

1. 接入企业认证的微信公众号网页授权和合规手机号验证服务。
2. 与 VAFOX Identity Center 连接，增加员工服务范围和 CEO 脱敏汇总权限。
3. 建设数据更正、撤回同意、账号注销和保留期限管理。
4. 在用户再次明确授权后接入 Dream Community、活动和个性化 AI 服务。
5. Explorer Partner 与生态贡献机制需单独完成合规、财务和隐私评审后再开发。
