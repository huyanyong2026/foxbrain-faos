# FireFox Gateway V1.0

FireFox Outdoor Growth Platform 的独立对外入口。

## 本地预览

直接打开 `index.html`，或在当前目录启动任意静态文件服务器。

```powershell
python -m http.server 4173
```

运行基础烟测：

```powershell
node smoke-test.cjs
```

## 发布边界

- 页面不连接 SAP、FoxBrain 数据库或 CEO 系统。
- 公开门店和品牌通过本机 `public_api.py` 代理读取 Core 的 `public:read` 接口；浏览器永远看不到 Core Token。
- `commerce.vafox.com`、`ai.vafox.com` 和 Dream Community 仍为预留入口；Explorer Life 已接入 `/explorer/register`。
- Nginx 站点根目录建议使用 `/var/www/firefox-gateway/current`。
- 发布前必须为 `gateway.vafox.com` 签发并验证独立 TLS 证书。

参考 Nginx 配置：`deploy/nginx/gateway.vafox.com.conf.example`。

公开数据代理默认只监听 `127.0.0.1:8091`。服务器环境变量放在独立权限文件中，至少配置
`CORE_BASE_URL=https://core.vafox.com` 和 `CORE_PUBLIC_API_TOKEN`。Core 端未人工标记为公开的对象不会返回。

## Explorer 身份服务

Explorer 身份服务只监听 `127.0.0.1:8092`，由 Nginx 转发 `/explorer` 和
`/api/explorer/`。部署模板见：

- `deploy/systemd/firefox-explorer-identity.service`
- `deploy/firefox-explorer.env.example`

服务端使用独立的 `explorer:match` Core 令牌匹配已验证手机号对应的购买记录；手机号只以 HMAC 摘要发送，接口不返回顾客目录。公开页面令牌仍然不能读取顾客数据。微信凭据、身份散列密钥、手机号验证密钥和 Core 令牌只放服务器环境文件，不进入 Git。真实微信授权及手机号验证未配置时，页面明确提示暂未开放，不提供绕过验证的测试登录。
