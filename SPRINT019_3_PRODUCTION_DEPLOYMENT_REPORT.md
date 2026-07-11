# Sprint019.3 生产部署报告

状态：已部署并验证通过。

## 部署信息

- 部署时间：2026-07-11 11:24 CST。
- 运行目录：`/opt/firefox-portal`。
- 服务：`firefox-portal.service`。
- 部署后状态：`active (running)`。
- 本机健康检查：HTTP 200。
- 公网健康检查：HTTP 200。

## 生产备份

- 代码：`/opt/firefox-portal/portal.py.bak.sprint0193.20260711-112220`。
- 数据库：`/opt/firefox-portal/portal.db.bak.sprint0193.20260711-112220`，729MB。
- 文件目录：`/opt/firefox-portal/uploads.bak.sprint0193.20260711-112220.tgz`。
- 文件清单：`/opt/firefox-portal/uploads.inventory.sprint0193.20260711-112220`。
- 四项备份均完成非空校验。

## 页面验证

以下生产页面均使用真实登录态验证：

- `/`：200，五个一级入口完整。
- `/business-overview`：200。
- `/business-health`：200。
- `/decision`：200。
- `/inventory-intelligence`：200。
- `/brand-intelligence`：200。
- `/store-intelligence`：200。
- `/daily-intelligence`：200。
- `/drive`：200。
- `/copilot`：200。
- `/action-center`：200。
- 不存在页面：404，中文友好说明可用。

核心页面扫描未发现接口按钮、英文引擎标题、原始请求路径、异常堆栈或英文无数据提示。

本次部署未连接或修改生产 SAP，未增加 SAP 写权限，未开发 ai.vafox.com。
