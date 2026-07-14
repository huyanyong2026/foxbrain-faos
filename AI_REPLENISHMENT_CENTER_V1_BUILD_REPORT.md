# FoxBrain AI补货中心 V1.0 建设报告

## 实际完成

- 在现有 `apps/ai` 上增量建设 AI 补货中心，没有改写登录、Dify、n8n 或 CEO Brain。
- 增加南山店、航苑店、振兴店的统一补货页面、筛选、历史批次和 Excel 导出。
- 增加管理员真实 SAP 导出 CSV/XLSX 导入通道与空白模板。
- 增加 Core 标准只读接口 `GET /api/v1/replenishment/input`，数据仅来自 SAP mirror。
- 增加管理员、采购员、店长权限；店长通过 `auth_users.store_code` 仅访问本店。
- 增加补货批次、补货明细和审计日志表。

## 规则版本

`replenishment-v1.0`

- 当前库存可销售天数低于 15 天进入补货建议。
- 目标库存为 30 天。
- 低于 7 天为紧急；销量增长可提高优先级。
- 近 60 天无销售时建议数量固定为 0。
- 负库存和负净销量保留数据警告，计算不产生负补货量。

## 数据边界

- AI 服务不连接 SAP-PROD。
- Core API 只连接本机 SAP mirror 只读账号。
- Core 接口只允许认证 GET，未增加写接口。
- Core 尚未配置时，页面明确要求管理员上传真实文件，不展示模拟业务数字。

## 生产配置待办

1. 在 Core 服务器设置三店真实 SAP 仓库编码 `CORE_STORE_MAP_JSON`。
2. 确认 `CORE_API_TOKEN` 的 `facts:read` 权限。
3. 运行 AI 服务数据库初始化，建立补货表及 `auth_users.store_code` 字段。
4. 给采购员设置角色 `purchaser`；给店长设置 `store_manager` 和对应门店编码。
5. 先用匿名化的真实格式文件完成预发布验收，再切入每日 22:30 自动生成。

## 测试

- 补货专项测试覆盖阈值边界、增长优先级、60天无销售、负数据、三店中文导入、重复 SKU、缺少字段和 Excel 工作表。
- 全量自动化回归必须在合并前再次执行并记录结果。
