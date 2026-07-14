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
- `commerce.vafox.com`、`ai.vafox.com`、Explorer Life 和 Dream Community 仅保留入口，未完成前不会跳转。
- Nginx 站点根目录建议使用 `/var/www/firefox-gateway/current`。
- 发布前必须为 `gateway.vafox.com` 签发并验证独立 TLS 证书。

参考 Nginx 配置：`deploy/nginx/gateway.vafox.com.conf.example`。

公开数据代理默认只监听 `127.0.0.1:8091`。服务器环境变量放在独立权限文件中，至少配置
`CORE_BASE_URL=https://core.vafox.com` 和 `CORE_PUBLIC_API_TOKEN`。Core 端未人工标记为公开的对象不会返回。
