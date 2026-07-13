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

- 这是纯静态站点，不连接 SAP、FoxBrain 数据库或 CEO 系统。
- `commerce.vafox.com`、`ai.vafox.com`、Explorer Life 和 Dream Community 仅保留入口，未完成前不会跳转。
- Nginx 站点根目录建议使用 `/var/www/firefox-gateway/current`。
- 发布前必须为 `gateway.vafox.com` 签发并验证独立 TLS 证书。

参考 Nginx 配置：`deploy/nginx/gateway.vafox.com.conf.example`。
