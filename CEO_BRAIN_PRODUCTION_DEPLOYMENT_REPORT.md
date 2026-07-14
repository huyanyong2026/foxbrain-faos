# VAFOX Enterprise Brain 生产部署报告

状态：已完成。

## 部署信息

- 生产运行目录：`/opt/firefox-portal`
- 生产代码仓库：`/opt/foxbrain-faos`
- 部署分支：`phoenix-ceo-brain-product-build-v1`
- 部署提交：`611fbfd3bdaff7b03b174fa48a7b9730b9ae283e`
- 服务：`firefox-portal.service`，状态正常运行

## 备份与回滚

备份目录：`/opt/backups/ceo-brain-product-v1-20260711-201925`

- 数据库：750 MB
- 生产代码：1.7 MB
- 上传目录压缩包：1.3 MB
- 私有配置：已备份，未提交 GitHub

## 线上逐页验证

| 页面 | 状态 | 响应时间 |
|---|---:|---:|
| 今天 | 200 | 0.113 秒 |
| 企业 | 200 | 0.008 秒 |
| 企业资料 | 200 | 0.011 秒 |
| 企业数字档案 | 200 | 0.009 秒 |
| AI 助手 | 200 | 0.008 秒 |
| 行动中心 | 200 | 0.109 秒 |
| 系统 | 200 | 0.004 秒 |

公网 HTTPS 首页状态 200，响应约 0.207 秒。服务重启后未发现新的程序异常、数据库异常或堆栈。

未连接 SAP 写权限，未修改生产 SAP，未部署 `ai.vafox.com`。
