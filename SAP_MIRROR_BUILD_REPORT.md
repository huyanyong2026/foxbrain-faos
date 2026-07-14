# VAFOX SAP Mirror 施工报告

## 已完成

- 审计 SAP B1 公司数据库：SQL Server 2008 R2 Enterprise、约 5.4 GB、2120 张业务表。
- 确认 VAFOX 服务器剩余空间约 155 GB，具备完整镜像容量。
- 在 SAP 中创建 `foxbrain_mirror_reader` 专用账号。
- 验证专用账号可以读取 2120 张表。
- 验证 `INSERT`、`UPDATE`、`DELETE`、`ALTER` 权限均为 0。
- 密钥仅保存在生产服务器 `/opt/foxbrain-sap-mirror/mirror.env`，权限为 `600 root:root`，未进入 GitHub。
- 新增 SQL Server 2019 Mirror Docker 编排，只绑定 `127.0.0.1:11433`，不公开暴露。
- 保留现有 PostgreSQL `sap-sync-db` 作为分析层；不将其冒充 SAP 原始镜像。
- 现有 SAP 只读同步定时器保持 active，生产门户保持 active。

## 未完成及阻塞

- Microsoft SQL Server 2019/2022 官方容器镜像在生产服务器连续下载超时。
- 国内 Docker 镜像代理对 Microsoft SQL Server 路径返回 403。
- 因目标 SQL Server 镜像尚未取得，首次 BACPAC 导出、导入和全库对账尚未执行。
- 当前不能宣称完整 SAP Mirror 已建成，也不能让 CEO 首页自动改读该镜像。

## 下一步所需

提供以下任意一种条件即可继续：

1. 将 `mcr.microsoft.com/mssql/server:2019-latest` 离线镜像包上传到 VAFOX 服务器；或
2. 提供服务器可访问的 Microsoft SQL Server 2019 Docker 镜像仓库。

镜像可用后继续执行：启动 Mirror、BACPAC 全量复制、2120 表行数与校验对账、只读应用账号、定时增量刷新、人工批准首次发布。

## 安全边界

- 未安装任何程序到 SAP 服务器。
- 未修改 SAP 业务数据和数据库结构。
- 仅新增专用只读安全主体。
- VAFOX AI 不写 SAP，不自动执行经营动作。
