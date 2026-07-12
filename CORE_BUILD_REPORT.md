# FoxBrain Enterprise Data Core 施工报告

## 服务器配置

- 域名：`core.vafox.com`
- 系统：TencentOS Server 4
- 系统盘：200GB
- 数据盘：1000GB，挂载 `/mnt/datadisk0`，可用约 934GB
- 根目录：`/opt/foxbrain-core`
- 数据、SQL Server、备份和日志目录均绑定到 1000GB 数据盘

## 安全设置

- SSH 仅允许密钥登录，禁止密码和交互式认证
- root 仅允许密钥，默认密码已锁定
- 最大认证重试 3 次，关闭 X11 和 SSH 转发
- 防火墙仅开放 SSH、HTTP、HTTPS
- SQL Server 端口仅监听 `127.0.0.1:11433`，公网不可访问
- SELinux 当前为 Disabled（腾讯云原始状态）

## 数据库配置

- SQL Server 2019 Standard Docker 隔离运行
- 容器：`foxbrain-core-sqlserver`
- 内存上限：8GB
- 数据目录：`/opt/foxbrain-core/sqlserver`
- 密钥：`/opt/foxbrain-core/sap-mirror/mirror.env`，权限 600

## 同步方案

- SAP 生产库使用 `foxbrain_mirror_reader` 专用只读账号
- 已验证 SELECT=1，INSERT/UPDATE/DELETE/ALTER=0
- 目标：pytds 逻辑复制 2120 张 SAP 公司库业务表
- 每表保存批次、断点、行数、校验值和失败记录
- 未完成对账前不允许 Data Core 自动发布给 CEO 系统

## 测试结果

- SSH 新密钥重连：通过
- 防火墙规则：通过
- 1000GB 数据盘绑定：通过
- Docker 服务：通过
- SQL Server 启动：通过
- SQL Server 公网隔离：通过，仅本机监听
- SAP 只读权限：通过
- SAP 全量数据复制：尚未执行
- Dashboard：尚未建设

## 备份方案

- `/opt/foxbrain-core/backup` 位于 1000GB 数据盘
- 首次全量复制完成后生成数据库全量备份和校验清单
- 后续保留每日增量批次、每周全量备份和失败恢复点

## 下一步计划

1. 部署 pytds 逻辑复制器并完成 2120 表首次全量复制
2. 执行表行数、销售、库存、采购、客户、供应商对账
3. 建设只读 SAP Mirror Dashboard
4. 对账通过后人工批准定时同步

Data Core 不安装 AI、Dify 或 Agent。
