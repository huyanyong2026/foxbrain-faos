# FoxBrain SAP Lab Phase 2 Business Object Mapping Report

## 一、施工边界

- 本阶段只建立 SAP 到 FoxBrain 的业务理解层。
- 数据依据来自 Phase 1 生成的 SAP Business Dictionary：2,113 张表、70,403 个字段。
- 未修改 SAP Lab 数据，未写入 SAP，未连接生产 SAP。
- 映射配置不自动创建 FoxBrain 对象；正式发布仍需人工批准。

## 二、25条 Object Mapping 确认结果

经真实字段字典核验，25条建议已全部确认并保留来源记录：

| 业务范围 | 已确认SAP表 | 确认用途 |
| --- | --- | --- |
| 企业 | OADM | 企业基础档案 |
| 产品 | OITM、ITM1、OITW | 商品主数据、价格、分仓库存 |
| 品牌 | OMRC | 制造商/品牌候选档案 |
| 门店 | OWHS | 仓库/门店候选档案 |
| 客户 | OCRD | `CardType='C'` 的客户档案 |
| 供应商 | OCRD | `CardType='S'` 的供应商档案 |
| 员工 | OHEM、OSLP | 员工与销售员档案 |
| 销售 | OINV、INV1、ORIN、RIN1 | 销售发票与退货单据、明细 |
| 采购 | OPOR、POR1、OPCH、PCH1 | 采购订单与采购发票、明细 |
| 库存 | OITW、OIVL、OILM | 分仓余额、估值、库存流水 |
| 财务 | OJDT、JDT1 | 会计凭证与分录 |
| 合同 | OOAT、OAT1 | 总括协议与协议明细 |

确认状态写入 `config/sap_business_object_mappings.json`。每条确认只表示理解关系成立，不代表自动发布数据或自动生成对象。

## 三、优先 Business Object 定义

### 1. Product Object（产品对象）

- 主来源：`OITM`；补充来源：`ITM1`、`OITW`。
- 源身份：`OITM.ItemCode`。
- 业务含义：可销售、采购或库存的商品，SAP商品编码始终作为可追溯源身份。
- 核心字段：商品名称、外文名、条码、商品组、品牌编码、首选供应商、默认仓库、价格、分仓现货、占用量、在途量、平均成本。
- 关系：归属品牌、首选供应商、在门店/仓库有库存。
- AI可查询：商品身份、名称、品牌、供应商、价格、库存、成本和最近采购信息。

### 2. Brand Object（品牌对象）

- 主来源：`OMRC`；产品关系来源：`OITM.FirmCode`。
- 源身份：`OMRC.FirmCode`。
- 业务含义：SAP制造商主数据形成品牌候选，再与FoxBrain现有品牌档案人工归一。
- 核心字段：品牌编码、品牌名称、关联商品编码。
- 关系：一个品牌可关联多个商品。
- AI可查询：品牌编码、名称、关联商品。

### 3. Store Object（门店对象）

- 主来源：`OWHS`；库存和销售关系来源：`OITW`、`INV1`。
- 源身份：`OWHS.WhsCode`。
- 业务含义：SAP仓库形成门店候选；配送仓、退货仓和虚拟仓不得自动认定为零售门店。
- 核心字段：仓库编码、名称、锁定状态、城市、区域、地址、商品、库存数量、销售单据。
- 关系：库存商品、履约销售。
- AI可查询：门店候选身份、名称、区域、库存商品、库存数量和销售证据。
- 人工校准：必须通过仓库别名和门店属性确认后才能发布为门店对象。

### 4. Customer Object（客户对象）

- 主来源：`OCRD`，过滤条件 `CardType='C'`；销售关系来源：`OINV`。
- 源身份：`OCRD.CardCode`。
- 业务含义：用于销售、会员和客户经营分析的客户型业务伙伴。
- 核心字段：客户编码、名称、分组、币种、余额、信用额度、折扣、销售负责人、地区和有效状态。
- 关系：产生销售单据、由销售员工服务。
- AI可查询：经过授权的客户经营字段。
- 默认受限：电话、手机、邮箱、详细地址、证照和银行信息。

### 5. Supplier Object（供应商对象）

- 主来源：`OCRD`，过滤条件 `CardType='S'`；采购关系来源：`OPOR`、`OPCH`。
- 源身份：`OCRD.CardCode`。
- 业务含义：用于采购、合同和供应关系分析的供应商型业务伙伴。
- 核心字段：供应商编码、名称、分组、币种、余额、信用额度、折扣、地区、有效状态、采购订单和采购发票。
- 关系：接收采购订单、开具采购发票、作为商品首选供应商。
- AI可查询：经过授权的供应经营字段。
- 默认受限：电话、手机、邮箱、详细地址、证照和银行信息。

## 四、关系模型

```text
Brand (OMRC.FirmCode)
  -> Product (OITM.FirmCode)

Product (OITM.ItemCode)
  -> Inventory by Store (OITW.ItemCode + OITW.WhsCode)
  -> Preferred Supplier (OITM.CardCode)

Store Candidate (OWHS.WhsCode)
  -> Inventory (OITW.WhsCode)
  -> Sales Rows (INV1.WhsCode)

Customer (OCRD.CardCode, CardType='C')
  -> Sales Invoice (OINV.CardCode)
  -> Sales Employee (OCRD.SlpCode -> OSLP.SlpCode)

Supplier (OCRD.CardCode, CardType='S')
  -> Purchase Order (OPOR.CardCode)
  -> Purchase Invoice (OPCH.CardCode)
  -> Preferred Product Supplier (OITM.CardCode)
```

所有未来对象关系必须附带：源数据库、源表、源字段、源主键、同步批次和提取时间。

## 五、AI查询边界

- AI只查询配置中明确列出的 `ai_query_fields`。
- 客户和供应商敏感联系方式、证照和银行字段默认受限。
- AI结论必须引用SAP源字段和同步批次证据。
- AI不得因字段缺失推断品牌、门店或对象关系。
- AI不得自动创建、合并或发布业务对象。

## 六、代码与配置

- `config/sap_business_object_mappings.json`：25条确认记录及五个优先对象定义。
- `scripts/validate_sap_object_mapping.py`：使用SAP Dictionary校验来源表、来源字段、AI字段和确认数量。
- `tests/test_sap_object_mapping.py`：安全边界、确认数量和对象完整性测试。

## 七、验证结果

- 确认映射：25/25。
- 优先对象：5/5。
- 来源表检查：通过。
- 来源字段检查：通过。
- AI查询字段检查：通过。
- 安全配置：SAP写入关闭、自动创建对象关闭。
- 映射测试：2项通过。
- Phase 1 Lab测试：3项通过。
- 既有安全边界测试：5项通过。

首轮校验发现 `OCRD` 的真实字段名为 `validFor`，已按SAP Dictionary修正，未采用文档猜测字段。

## 八、下一步建议

下一阶段先在FoxBrain本地建立对象预览和匹配队列，不直接发布：

1. 生成80,446个产品候选、品牌候选、12个门店/仓库候选以及客户和供应商候选。
2. 对品牌名称、仓库门店属性和现有FoxBrain对象进行别名匹配。
3. 由人工确认“关联现有对象”或“创建新对象”。
4. 发布前执行对象数量、源主键唯一性、关系完整性和敏感字段权限审计。
