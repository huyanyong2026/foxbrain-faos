# 15 Deployment / 部署

## 本地启动

```bash
python3 portal_v2.py
```

默认监听：

```text
127.0.0.1:8088
```

## 生产建议

- Ubuntu 服务器
- systemd 管理服务
- Nginx/Caddy HTTPS 反向代理
- `.env` 保存真实配置
- 定时任务执行 SAP B1 同步

## 安全

不要提交真实密码、API Key、数据库连接和服务器私密信息。

