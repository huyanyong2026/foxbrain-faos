# SAP Mirror Engine Phase 2 施工报告

## 已复制表

截至 2026-07-12 19:20，以下表已完成源端与 Mirror 行数一致校验：

- OWHS：12 / 12
- OSLP：59 / 59
- OHEM：0 / 0
- OCRD：143 / 143
- OITM：96,004 / 96,004
- OINV：10,292 / 10,292
- INV1：24,053 / 24,053
- ORIN：904 / 904
- RIN1：1,372 / 1,372
- OPOR：3 / 3
- POR1：44 / 44
- OPCH：1,178 / 1,178
- PCH1：15,544 / 15,544

## 正在复制

- OITW：源端 1,152,048 行，已进入断点复制；报告生成时尚未完成，不能计为成功。

## 未复制表

- 除上述 14 张首批核心表外，其余 SAP 公司库业务表尚未加入复制清单。
- 不能宣称 2120 张表已经完成。

## 同步机制

- 使用 `foxbrain_mirror_reader` 专用只读账号。
- SELECT 可用，INSERT、UPDATE、DELETE、ALTER 权限均为 0。
- 状态库：`/opt/foxbrain-core/sync/mirror-state.db`
- 结构化日志：`/opt/foxbrain-core/logs/sap-mirror.jsonl`
- 服务：`foxbrain-sap-mirror.service`
- 复制批次为每次 1000 行，完成批次后持久化断点。

## 校验结果

- 已完成的 13 张非库存明细表，源端与 Mirror 行数全部一致。
- SQL Server Mirror 仅监听 `127.0.0.1:11433`。
- SAP-PROD 未被修改，未增加任何写权限。

## 错误日志

- 首次运行使用 `OFFSET/FETCH`，SQL Server 2008 R2 不支持，错误已完整记录。
- 已改为兼容 SQL Server 2008 R2 的 `ROW_NUMBER()` 分页并成功重跑。
- 当前无未解释的已完成表行数差异。

## 下一阶段计划

1. 完成 OITW 1,152,048 行复制与行数校验。
2. 为大表升级复合主键 keyset 断点，提升增量同步性能。
3. 增加销售金额、库存数量、采购金额、客户和供应商指标校验。
4. 建设 SAP Mirror Dashboard。
5. 首批对账通过后，再人工批准定时增量同步。
