# FoxBrain SAP Mirror 施工报告

## 已完成

- 审计 SAP B1 公司数据库：SQL Server 2008 R2 Enterprise、约 5.4 GB、2120 张业务表。
- 确认 FoxBrain 服务器剩余空间约 155 GB，具备完整镜像容量。
- 在 SAP 中创建 `foxbrain_mirror_reader` 专用账号。
- 验证专用账号可以读取 2120 张表。
- 验证 `INSERT`、`UPDATE`、`DELETE`、`ALTER` 权限均为 0。
- 密钥仅保存在生产服务器 `/opt/foxbrain-sap-mirror/mirror.env`，权限为 `600 root:root`，未进入 GitHub。
- 新增 SQL Server 2019 Mirror Docker 编排，只绑定 `127.0.0.1:11433`，不公开暴露。
- 已通过本机断点下载生成 505 MB OCI 离线包，SHA-256 校验后上传服务器并成功导入。
- SQL Server 2019 Mirror 容器已启动，生产端口仅为 `127.0.0.1:11433`。
- 保留现有 PostgreSQL `sap-sync-db` 作为分析层；不将其冒充 SAP 原始镜像。
- 现有 SAP 只读同步定时器保持 active，生产门户保持 active。

## 未完成及阻塞

- 最新 SqlPackage 无法与 SQL Server 2008 R2 完成 BACPAC 登录；隔离启用兼容 TLS 后仍在 post-login 阶段超时，未生成数据包。
- Linux SQL Server 2019 不提供 Linked Server 所需 OLE DB Provider，无法使用服务器内原生跨库复制。
- 首次 2120 表逻辑复制和全库对账尚未执行。
- 当前不能宣称完整 SAP Mirror 已建成，也不能让 CEO 首页自动改读该镜像。

## 下一步所需

提供以下任意一种条件即可继续：

建设基于 `pytds` 的只读逻辑复制器：读取源表结构与数据，按批次写入 Mirror，记录每表行数、校验值、断点和错误；完成 2120 表后再执行全库对账、只读应用账号、定时增量刷新和首次人工批准。

## 安全边界

- 未安装任何程序到 SAP 服务器。
- 未修改 SAP 业务数据和数据库结构。
- 仅新增专用只读安全主体。
- FoxBrain AI 不写 SAP，不自动执行经营动作。
