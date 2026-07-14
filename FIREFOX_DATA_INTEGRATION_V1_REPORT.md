# VAFOX Enterprise Data Integration Layer V1.0

项目编号：`FOX-DATA-INTEGRATION-001`

## 1. 架构

本阶段将企业经营数据入口固定为：

`SAP-PROD -> 22:00只读复制 -> core.vafox.com -> 只读业务对象API -> Huyan / AI / Gateway`

- Core API 只连接本机 `SAP_MIRROR`，不加载 SAP 生产凭据。
- Huyan 的经营摘要优先且默认只读取 Core；旧本地摘要只有显式开启 `ALLOW_LEGACY_LOCAL_DATA=true` 才会使用。
- AI 通过固定 HTTPS 主机和 Bearer Token 读取 Core。
- Gateway 浏览器只访问同源公开代理，Core Token 不进入网页。
- 所有接口拒绝 `POST`、`PUT`、`PATCH`、`DELETE`。

## 2. Business Object API

新增标准对象接口：

| 接口 | 内容 | 权限 |
|---|---|---|
| `/api/v1/objects/stores` | 门店、90日销售、毛利、库存状态 | `objects:read` |
| `/api/v1/objects/products` | SKU、产品、品牌、类别、库存、90日销售、生命周期 | `objects:read` |
| `/api/v1/objects/brands` | 品牌、产品数、销售、库存、合作状态 | `objects:read` |
| `/api/v1/objects/suppliers` | 供应商、合作状态、采购历史摘要 | `objects:read` |
| `/api/v1/objects/customers` | 顾客、消费摘要 | `customers:read` |
| `/api/v1/business/summary` | CEO经营摘要 | `objects:read` 或兼容 `facts:read` |
| `/api/v1/data-health` | 同步状态、对象数量、异常 | `health:read` 或兼容 `facts:read` |
| `/api/v1/public/stores` | 人工批准的公开门店字段 | `public:read` |
| `/api/v1/public/brands` | 人工批准的公开品牌字段 | `public:read` |

原始表兼容接口已收紧为独立 `raw:read`，不得分配给 Huyan、AI 或 Gateway。

## 3. 数据对象与来源

- Store：SAP Mirror 门店、销售、库存；Living Enterprise 可通过服务器端 enrichment 文件补充地址和员工关系。
- Product：SAP Mirror 商品主数据、品牌、类别、库存和销售。
- Brand：SAP Mirror 品牌、商品、库存和销售；Brand Life 可通过 enrichment 文件补充公开介绍。
- Supplier：SAP Mirror 供应商和采购摘要。
- Customer / Explorer：SAP Mirror 顾客和消费摘要，不返回手机号、地址等原始敏感字段。

每个对象响应带只读来源说明和 Data Core 同步时间。业务缓存按数据类型配置：参考资料默认24小时，经营指标默认5分钟，健康状态最长1分钟。

## 4. 权限模型

- CEO：`facts:read`, `objects:read`, `customers:read`, `health:read`
- 管理层 / 采购：按职责配置 `objects:read`, `health:read`
- 店长：`objects:read` + `role=store_manager` + 明确 `store_ids`，只能读取授权门店
- Gateway：只有 `public:read`
- Core 运维兼容访问：单独 `raw:read`

公开对象默认拒绝。只有服务器 enrichment 文件中人工设置 `public: true` 的门店和品牌才会返回。

## 5. 应用接入

- `huyan.vafox.com`：CEO经营摘要改为 Core API 优先，默认关闭旧本地经营数据回退。
- Huyan 原 SAP 连接配置入口已改为 Core 连接状态；Huyan 自身同步触发固定禁用，不再读取 SAP 主机、数据库或接口凭据。
- Huyan 镜像不再包含旧 `sync_sap_b1.py`、`python-tds`、SAP同步数据卷或22:00同步任务；旧同步脚本已从代码库删除，避免误启。
- `ai.vafox.com`：连接器增加业务对象、健康查询和短缓存；现有补货与库存分析仍使用 Core 标准接口。
- `gateway.vafox.com`：新增本机只读公开代理，网页可加载已批准门店；代理仅监听 `127.0.0.1:8091`。

## 6. Data Health Monitor

`GET /api/v1/data-health` 返回：

- 最近同步状态和时间
- 源表完成/失败数量
- 门店、商品、品牌、供应商、顾客对象数量
- 可机器识别的问题代码

`python -m scripts.generate_data_health_report` 可将真实环境快照原子写入 `DATA_HEALTH_REPORT.json`。

## 7. 测试结果

- 全量回归测试：104项通过；其中 Core / AI / Gateway / Enterprise client 定向测试30项通过。
- Gateway静态页面与全部主要资源烟测通过。
- 已验证：Core API 200、Huyan/AI只读客户端、Gateway公开代理、角色权限、店长门店隔离、客户敏感权限。
- 已验证：公众令牌读取经营对象和原始表均被拒绝。
- 已验证：所有写方法返回405。
- 已验证：连接器拒绝 HTTP 和伪造的 `core.vafox.com` 子域。
- Python语法检查通过。

真实服务器的 Core 数据数量和三个域名连通性需要在 PR 合并、服务器环境变量配置后执行；本报告不虚构生产结果。

## 8. 部署与密钥

- 所有 Token 只进入服务器环境变量或受限配置文件，不进入 Git。
- Core enrichment 真实值只放 `/opt/foxbrain-core/api/object-enrichment.json`。
- Gateway 公开代理使用独立 `public:read` Token。
- Huyan 和 AI 不保存、不读取 SAP 生产凭据。

## 9. 下一步

1. 在 Core 服务器配置新的角色化 Token 和人工批准的公开对象。
2. 合并 PR 后先验证 Core `/api/v1/data-health` 和五类对象数量。
3. 依次验证 Huyan经营摘要、AI对象读取、Gateway公开门店。
4. 观察缓存命中率和接口延迟后，再决定是否增加持久化业务对象快照。
