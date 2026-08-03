# VAFOX Huyan V1.4 CEO Authorization Report

## 1. 结论

Huyan Portal 与 Business Aggregation API 的 CEO 授权已对齐。经 Gateway 验证的 Huyan JWT 只有同时满足以下三项时，才会在三个 V1.4 经营分析接口上获得 Business API 所需的 `ceo` 角色：

- `portal = huyan.vafox.com`
- `roles`（或 `role_scopes`）包含 `VAFOX_CEO`
- `data_scope = ALL_DATA`

映射发生在 Gateway 的 Huyan 专用授权适配层。JWT 本身不被浏览器或前端改写，Auth 核心的签发与验签实现也未修改。

## 2. 权限映射

| Huyan 已验证声明 | Business 内部声明 | 约束 |
| --- | --- | --- |
| `portal=huyan.vafox.com` | 保留来源校验 | 其他 Portal 不可复用映射 |
| `VAFOX_CEO` | 追加 `ceo` | 仅在完整条件匹配后追加 |
| `ALL_DATA` | `X-VAFOX-Data-Scope: ALL_DATA` | 三个接口继续强制校验全量数据范围 |

Gateway 仅转发经服务端验签的声明，并新增 `/api/business` 到 Business 服务的显式路由。Business 服务对销售、会员、客户三个聚合接口同时检查 CEO 角色和 `ALL_DATA`，未降低原权限要求。

## 3. 获授权接口

- `GET /api/business/sales-analysis`
- `GET /api/business/member-analysis`
- `GET /api/business/customer-analysis`

错误 Portal、错误角色、非 `ALL_DATA` 范围均不会产生 `ceo` 映射。即使调用方已经拥有内部 `ceo` 角色，上述三个接口缺少 `ALL_DATA` 时仍返回 `403 all_data_scope_required`。

## 4. 供应商隔离

`GET /api/business/supplier-analysis` 不在 Huyan CEO 映射白名单中。供应商接口保持既有独立授权路径，不会因为 `VAFOX_CEO + ALL_DATA` 的 Huyan 映射而自动取得 `ceo` 角色。

## 5. 安全边界

- 未修改 `packages/vafox_foundation/auth.py`，Auth 核心保持原状。
- 未在 Huyan Web 中生成、补写或伪造角色/数据范围。
- 映射依赖 Gateway 已验签声明，浏览器请求头不能触发该映射。
- 映射采用三个精确路径的白名单，不扩展到供应商或其他 Business API。
- Business API 保留并显式执行 `ceo + ALL_DATA` 双重校验。

## 6. 自动化验证

自动化测试覆盖：三个目标接口的正确映射、错误 Portal/角色/范围拒绝、供应商接口隔离，以及 Business 服务对非 `ALL_DATA` CEO 请求返回 `403`。验证命令与最终结果记录在本次变更的交付摘要中。
