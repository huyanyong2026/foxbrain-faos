# Sprint019.4 生产部署报告

## 部署状态

待代码提交后更新最终提交、备份目录、服务状态和生产验收结果。

## 部署要求

- 备份 `/opt/firefox-portal/portal.py`。
- 使用 SQLite 在线备份接口备份 `portal.db`。
- 备份 `/opt/firefox-portal/uploads`。
- 语法检查通过后替换运行文件。
- 重启 `firefox-portal.service`。
- 不触发 SAP 同步，不修改 SAP。

