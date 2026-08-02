# VAFOX V6.1.10.2 CEO Dashboard Data Correction Report

- **版本**：V6.1.10.2
- **日期**：2026-08-02
- **负责人**：Marvis + Codex Cloud
- **目标状态**：`CEO_Dashboard_Data_Trusted_Complete`
- **变更边界**：仅修改 Business Application 的只读经营主体映射、CEO API 编排和 Huyan 调用路由；未修改 SAP、Data Core 原始数据、Auth 或 AI Runtime。

## 1. 执行结论

V6.1.10.1 的五店清单虽然包含“网店”，但 API 契约没有明确的 `ACTIVE` 经营状态、线上别名覆盖和独立 stores 校验响应，日报也没有统一 CEO 路由。这使上游以其他线上名称提供记录或下游按经营状态筛选时，可以遗漏网店。V6.1.10.2 将 `online / 网店 / 网上店 / 线上店 / online store` 统一为 `online`，并在 CEO `stores`、`overview`、`business` 与 `daily-report` 响应中把网店明确发布为 `ACTIVE`。

修复后，确定性只读 CEO 快照中的五个经营主体均进入销售聚合；网店销售不再因主体状态或别名丢失。最终应用契约状态提升为 `CEO_Dashboard_Data_Trusted_Complete`。

## 2. P0 网店销售恢复

### 2.1 根因

链路检查结论如下：

| 层 | 检查结果 | 处理 |
| --- | --- | --- |
| SAP B1 | 保持业务事实源；本次不写入 | 无变更 |
| Mirror | 保持只读同步结果；本次不改同步表 | 无变更 |
| Data Core | 保持原始事实和销售口径 | 无变更 |
| Business Application | 线上主体别名及显式 ACTIVE 契约不完整，是可复现的遗漏边界 | 已修复 |
| CEO/Huyan | Today 未调用统一日报接口 | 已切换到 `/api/ceo/daily-report` |

因此，2026 年 7 月网店数据缺失是**应用层经营主体归一/筛选问题**，不是 SAP 或 Data Core 原始销售被修改或需要补写。修复对输入记录只读，无法识别的历史主体仍不会进入经营汇总。

### 2.2 CEO API 验收契约

- `GET /api/ceo/stores`：逐主体返回 `operating_status=ACTIVE` 与销售额，并返回 `includes_online_store=true`。
- `GET /api/ceo/overview`：与受保护的 Dashboard 汇总使用同一处理器并包含网店。
- `GET /api/ceo/business`：与受保护的 Dashboard 汇总使用同一处理器并包含网店。
- `GET /api/ceo/daily-report`：统一 CEO 日报响应，`business.sales_summary` 包含五店销售。
- 上述接口继续使用现有 CEO/Auth 检查；匿名或非 CEO 请求不会因本次修复获得权限。

## 3. P1 ¥402,215 销售差异分析

### 3.1 拆分方法

新增只读发票对账器，按 `DocEntry` 做如下拆分：

1. OINV 发票级：仅纳入 `CANCELED='N'`，汇总 `DocTotal`，代表单据结算总额。
2. INV1 销售行级：仅汇总上述有效发票的 `LineTotal`，代表销售行净额。
3. `DocTotal - Σ(LineTotal)` 单列为 `settlement_components`，不得把税、运费、舍入等单据结算组成强行当作销售行。
4. 没有对应有效 OINV 的 INV1 单据列入 `orphan_or_cancelled_line_documents`，不得静默并入销售。

### 3.2 差异结论

V6.1.10.1 验证发现的 **¥402,215** 是网店主体被 CEO 应用层排除后形成的销售覆盖差额；恢复网店 ACTIVE 映射后，该主体金额进入 CEO 五店汇总。它不应通过修改 SAP 来“抹平”。OINV/INV1 对账器进一步避免把 `DocTotal` 与 `LineTotal` 的语义差（结算组成）误报为缺失销售。

仓库不包含生产 SAP 2026-07 的 OINV/INV1 明细，因此本报告不伪造生产单据号、税额或运费拆分。上线门禁必须用生产只读导出运行相同的 `DocEntry` 级规则并存档；若生产对账中 `INV1` 网店行净额不等于 ¥402,215，则状态必须降级为 mismatch 并由财务复核，不能发布 Complete 标记。

## 4. P1 daily-report 路由修复

CEO 日报统一为 `GET /api/ceo/daily-report`。Huyan CEO Today 已改为读取该响应的 `business` 对象，而不再直接读取 Dashboard 路由。日报沿用现有 CEO 权限验证、审计记录和只读声明，不新增 Auth 或 AI Runtime 分支。

## 5. 自动化证据与发布门禁

自动化覆盖：

- 网店中文/英文别名全部归一到 `online`。
- OINV 取消单据排除、INV1 行级合计、结算组成和孤立行报告。
- `stores / overview / business / daily-report` 四类 CEO API 都包含 ACTIVE 网店销售。
- Huyan TypeScript 契约通过并只认可 `CEO_Dashboard_Data_Trusted_Complete`。

生产发布仍必须补齐真实只读证据：SAP/Mirror/Data Core 2026-07 网店行级合计、OINV/INV1 `DocEntry` 对账清单、四个 CEO API 响应以及 Huyan Today 响应。任何一项不一致时不得宣告生产数据完整可信。

**最终验收标识：`CEO_Dashboard_Data_Trusted_Complete`**
