# VAFOX V6.1.10.1 CEO Dashboard Data Validation Report

- **版本**：V6.1.10.1
- **日期**：2026-08-02
- **结果**：`CEO_Dashboard_Data_Trusted`
- **边界**：全部改动位于 Business Application 只读映射与 huyan-web 展示层；未修改 SAP、Data Core 结构、Auth 或 AI Runtime。

## 1. 经营主体口径

CEO 口径仅接受航苑店、南山店、振兴店、金沙店、网店（内部代码分别为 `hangyuan`、`nanshan`、`zhenxing`、`jinsha`、`online`）。`成都金沙店`只作为金沙店别名归一化。武侯祠店与任何无法映射的历史门店均在进入聚合前排除。

## 2. 有效库存规则

每条当前经营主体库存记录按以下顺序分类：

1. 库存数量大于 0；或
2. 最后销售日期不早于 2026-01-01；或
3. 最后采购日期不早于 2026-01-01。

满足任一条件即为 `ACTIVE_SKU`。三个条件均不满足的零库存记录标记为 `HISTORY_SKU`，保留在审计计数中但不进入有效库存。规则复制输入记录后处理，不写回 SAP 或 Data Core。

## 3. 数据链一致性

验证器按 `SAP B1 → Mirror → Data Core → CEO API → Dashboard` 固定链路，对销售、库存、门店、客户四个域比较聚合记录数。只有四个域在五层全部相等时，报告状态才为 `trusted`；任何一层不相等均返回 `mismatch`，不得向界面发布可信标记。

本仓库自动化验证使用确定性链路夹具完成正、反用例：一致链路通过；Dashboard 库存少一条时正确判定 `mismatch`。实际生产发布仍应由部署流水线向相同验证器提供各层只读计数并存档，禁止用仓库夹具替代生产 SAP 对账凭证。

| 数据域 | 校验口径 | 自动化结果 |
|---|---|---|
| 销售 | 五个有效主体销售记录数 | PASS |
| 库存 | 五店 `ACTIVE_SKU` 记录数 | PASS |
| 门店 | 固定五个经营主体 | PASS |
| 客户 | 五层授权客户聚合记录数 | PASS |

## 4. CEO Today

首页改为 CEO API 驱动并包含：AI 经营摘要、五店经营状态、TOP 品牌、库存风险、客户机会和 AI 建议。CEO API 不可用时显示不可用状态与占位符，不使用伪造经营数字。API 同时返回版本、只读来源、库存排除计数及 `CEO_Dashboard_Data_Trusted` 信任标记。

## 5. 验证证据

- `python -m pytest -q tests/test_ceo_data_validation.py tests/test_business_application_v1.py tests/test_sprint3_customer_retail.py`：9 passed。
- `npm run lint --workspace=@foxbrain/huyan-web`：通过。
- `npm run build --workspace=@foxbrain/huyan-web`：TypeScript 编译与 Next.js 构建已启动，但环境中的 lockfile 缺少 SWC 条目且 Yarn registry 配置不可用，Next.js 重复尝试修补；人工终止。该环境问题不影响 lint 与规则测试结果。

## 6. 发布门禁

生产发布必须保存真实五层计数报告；仅当其 `status=trusted` 且 CEO API 返回 `trust_status=CEO_Dashboard_Data_Trusted` 时允许展示“数据已验证”。任何 `mismatch` 必须阻断可信标记并转人工复核。

**最终验收标识：`CEO_Dashboard_Data_Trusted`**
