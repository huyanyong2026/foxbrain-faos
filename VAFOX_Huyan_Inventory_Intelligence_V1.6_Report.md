# VAFOX Huyan Portal V1.6 Inventory Intelligence 交付报告

## 1. 交付结论

在 V1.5 稳定页面基础上新增独立“库存分析”页面，保持 VAFOX CEO OS 的侧栏、留白、橙色强调、卡片、表格和数据溯源视觉规范。未调整 CEO Today、经营分析、商品分析及 SAP B1、SAP Mirror、Data Core、Auth、AI Runtime。

## 2. 四个模块

1. **库存总览**：库存金额、有效 SKU 数、库存数量、品牌库存结构、门店库存结构。
2. **库存健康分析**：按正常库存、高库存、滞销库存、缺货风险切换，展示 SKU、品牌、金额、数量、风险等级和建议。
3. **滞销库存分析**：展示商品、品牌、库存金额、库存数量、最近销售、库龄和建议动作。
4. **补货建议**：按结论、依据、建议输出；依据明确包含销售速度、库存和趋势。

## 3. 真实数据链与口径

页面只请求 `GET /api/business/inventory-analysis`。Business Layer 每次请求即时读取注入的 Core 客户端 `get_products()`、`get_sales()`、`get_inventory()`；方法缺失、上游合同异常或读取失败时返回 `503`，不使用 mock、fixture、faker 或静态数字兜底。

聚合合同声明 `scope.dataset = effective_skus`，并在服务端统一排除：

- 标记为 `HISTORY SKU` / `HISTORY_SKU` 的商品；
- 零库存且 2026 年前无经营记录的商品。

所有汇总、结构、健康分类、滞销清单及建议均基于过滤后的 SKU 集合。

## 4. 成本治理

只有全部库存行均包含可信库存金额或非负单位成本时，接口才返回 `cost_status = trusted` 并展示金额。否则返回 `cost_status = governing`，所有金额位置统一显示“成本数据治理中”，不推测成本。

## 5. 权限与只读保证

新接口沿用 Huyan CEO Portal 的 `VAFOX_CEO + ALL_DATA` 映射和 Business Layer CEO 角色校验。接口仅聚合读取和记录审计事件，不包含 SAP/Core 写入、采购执行、调拨执行或库存修改能力。

## 6. 验证范围

- Python 单元测试验证有效 SKU 排除、四类健康判断与成本治理。
- Node 静态合同测试验证页面仅使用真实库存聚合 API、四模块完整及无 mock/fixture/faker。
- TypeScript 检查验证页面类型与组件编译。
