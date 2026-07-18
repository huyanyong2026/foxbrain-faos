# VAFOX 2.0 Unified Identity Gateway Architecture

**文档状态：** Architecture Design / Draft
**统一入口：** `gateway.vafox.com`
**产品定位：** VAFOX Unified Identity Gateway
**设计目标：** 建立 VAFOX 统一身份、认证、授权路由与审计基础。本文件仅定义目标架构与治理规则；不包含服务器、网络、数据库或部署操作。

## 0. 总体架构

`gateway.vafox.com` 是所有人类用户与受管 Agent 进入 VAFOX 业务域的唯一身份入口。Gateway 负责验证主体身份、生成最小权限上下文、执行路由和审计；它不替代下游业务系统的数据授权与业务审批。

```text
用户 / Agent
        |
        v
gateway.vafox.com
VAFOX Unified Identity Gateway
  ├─ Identity Provider / MFA
  ├─ Session & Token Service
  ├─ Policy Decision & Route Service
  ├─ Secret Reference Broker
  └─ Audit Event Gateway
        |
        +-------------------------------+
        |                               |
        v                               v
huyan.vafox.com                    ai.vafox.com
CEO Control Plane                  Employee AI
        |                               |
        +---------------+---------------+
                        v
                 core.vafox.com
             Enterprise Data Brain
```

所有到 `huyan.vafox.com`、`ai.vafox.com`、Agent Hub 及 Core 受保护接口的请求均必须携带由 Gateway 签发或交换得到的可验证身份与权限上下文。下游服务必须再次执行资源级授权；Gateway 的路由决定不等同于数据访问许可。

## 1. Gateway 定位

Gateway 是 VAFOX 2.0 的四合一安全控制点：

| 能力 | Gateway 职责 | 不承担的职责 |
| --- | --- | --- |
| 统一入口 | 提供唯一登录、令牌获取、会话续期和受控 API 入口。 | 不允许各业务域建立独立登录绕过统一身份。 |
| 身份认证 | 验证人类与 Agent 的凭据、MFA 状态、风险等级及身份生命周期。 | 不以邮箱、手机号、员工号或密钥本身作为完整权限结论。 |
| 权限路由 | 根据角色、属性、请求目的和策略，将已授权请求导向正确业务域。 | 不以 URL、前端隐藏项或调用方声明代替授权。 |
| 审计中心 | 生成可关联、可检索、不可抵赖的安全与访问事件。 | 不记录明文密码、令牌、密钥或不必要的敏感原始数据。 |

核心原则：**默认拒绝、最小权限、显式授权、全链路审计、策略优先、职责分离。**

## 2. 身份模型

Gateway 采用不可复用的主体标识（`principal_id`）作为授权锚点。凭据、组织关系、角色和设备是该主体的属性，不可互相替代。一个人可具有多个业务角色，但每次会话必须选择一个明确的活动角色与上下文。

| 身份类型 | 主体定义 | 主要权限边界 | 典型目标域 |
| --- | --- | --- | --- |
| CEO Identity | 经过强认证并由治理流程授予 CEO 职责的自然人身份。 | CEO Private Brain、CEO 决策与审批工作流；不自动取得所有 Core 原始数据权限。 | `huyan.vafox.com` |
| Executive Identity | 经组织任命、具有明确管理范围的高管自然人身份。 | 仅限其职责、部门、数据范围及被授予的管理能力。 | `huyan.vafox.com` 或批准的管理体验 |
| Employee Identity | 与有效雇佣关系绑定的员工自然人身份。 | Employee AI、本人职责范围及部门授权资源。 | `ai.vafox.com` |
| Agent Identity | 已注册、拥有负责人、版本、用途和生命周期状态的非人类工作负载身份。 | 仅限登记的能力、数据契约、环境、受众和有效期；不得继承人类身份权限。 | Gateway API → Agent Hub |

身份生命周期至少包括 `pending`、`active`、`suspended`、`revoked` 和 `expired`。身份状态变化、角色变更、离职、Agent 版本撤销或紧急停止必须触发会话和令牌撤销。

## 3. 认证体系

### 3.1 MFA

- CEO 与 Executive Identity 必须使用抗钓鱼 MFA（优先 FIDO2/WebAuthn 或企业级硬件凭据）；高风险操作必须进行 step-up authentication。
- Employee Identity 至少使用企业 SSO 配合 MFA；异常设备、地点、时间或风险信号触发附加验证。
- Agent Identity 不使用人类密码或共享账号；使用工作负载身份、短期签名凭据、双向 TLS 或经批准的令牌交换。
- MFA 成功仅证明认证强度；仍需完成会话、策略和资源授权检查。

### 3.2 Session

- 会话须绑定 `principal_id`、活动角色、认证强度、策略版本、会话风险与最小上下文版本。
- 使用短空闲超时与绝对过期；CEO、高管和管理操作使用更短的会话寿命。
- 会话标识应使用安全、`HttpOnly`、`Secure`、适当 `SameSite` 的 Cookie 或等效安全机制；禁止在 URL、日志或前端持久化存储中暴露会话机密。
- 角色切换、权限缩减、密码/凭据变更、MFA 重置、身份停用和异常风险事件必须即时撤销或重认证。

### 3.3 Token

- Access Token 短时有效、面向明确受众（`aud`）、最小 scope，并包含发行方、主体、过期时间、唯一标识、活动角色与策略版本等可验证声明。
- Refresh Token 仅用于受控续期、轮换和重放检测；不得跨域、跨客户端或跨主体转授。
- Agent Token 必须绑定 Agent ID、精确版本、调用方、目标服务、能力、环境、目的和极短有效期；禁止通配符受众与长期静态 Token。
- 下游服务必须验证签名、发行方、受众、有效期、撤销状态和所需 scope；不接受自声明角色或未验证 Token。

### 3.4 Secret 管理

- 密钥、证书、OAuth 客户端密钥、数据库凭据及第三方 API Secret 仅可由受控 Secret Manager 保存与轮换。
- Gateway 只向经策略允许的工作负载提供短期凭据或 Secret 引用；不得将明文 Secret 交给浏览器、日志、审计正文或 Agent 提示词。
- Secret 按环境、服务、用途和所有者隔离，遵循最小读取权限、定期轮换、泄露撤销和使用审计。
- 人类用户不得以共享 Secret 认证；Agent 不得使用员工或 CEO 的个人凭据。

## 4. 权限模型

Gateway 的决策采用 **RBAC + ABAC + Capability**：RBAC 给出角色可申请的能力上限，ABAC 根据上下文收窄范围，Agent Capability 将非人类调用限制为已注册的精确能力。任何层未明确允许即拒绝。

### 4.1 RBAC

| 角色 | 可申请的基础能力 | 明确限制 |
| --- | --- | --- |
| CEO | 访问 CEO Private Brain、接收企业级决策洞察、在授权工作流中审批。 | 不绕过 Core 数据策略、审计或双人复核要求。 |
| 高管 | 访问职责范围内的管理洞察、团队/部门授权资源和相应审批。 | 不访问 CEO 私有内容或其他高管的受限范围。 |
| 员工 | 使用 Employee AI，访问本人职责、项目和部门范围内资源。 | 不访问管理层私有洞察、跨部门受限数据或管理操作。 |
| Agent | 执行已登记的观察、分析、建议或经审批的执行能力。 | 不获得人类登录权、无限权限、隐式委派或未注册工具访问。 |

### 4.2 ABAC

每个授权请求至少计算以下属性，并以交集限制资源：

- **数据范围：** 数据分类、资源所有者、字段、记录范围、项目/租户及是否允许聚合或导出。
- **部门：** 组织、部门、汇报关系、岗位、地域及授权委派范围。
- **时间：** Token/审批有效期、工作时间窗、数据新鲜度和临时授权截止时间。
- **环境：** production、staging、development 等环境，网络信任等级、设备风险与目标服务。

授权表达式：

```text
Allow = Active Identity
     ∩ Valid Authentication
     ∩ Role Permission
     ∩ Attribute Policy
     ∩ Resource Policy
     ∩ Approved Purpose
     ∩ (Agent Capability, when non-human)
```

策略必须版本化、可解释并记录决策结果；策略不可用、属性缺失或版本不一致时执行 fail closed。

## 5. 访问与路由规则

| 发起者 | 允许路径 | Gateway 强制校验 | 路由结果 |
| --- | --- | --- | --- |
| CEO | `gateway → huyan` | CEO Identity、强 MFA、CEO 角色、目的与会话风险。 | `huyan.vafox.com` 的 CEO Control Plane。 |
| 高管 | `gateway → huyan` 或经批准管理入口 | Executive Identity、部门/职责范围、MFA 和资源策略。 | 受限管理视图，不继承 CEO 私有范围。 |
| 员工 | `gateway → ai` | Employee Identity、雇佣状态、部门/项目属性和 AI 权限。 | `ai.vafox.com` 的 Employee AI。 |
| Agent | `gateway/API → Agent Hub` | Agent 注册状态、版本、mTLS/工作负载认证、能力、受众、目的、环境和审批。 | 受控 Agent Hub；再由其调用批准的服务。 |

路由规则只授予入口资格。`huyan`、`ai`、Agent Hub 与 `core` 必须在每个资源请求处重新验证 Token 与策略，并仅使用 `core.vafox.com` 提供的受控数据接口。

## 6. 数据隔离

VAFOX 将以下数据与体验域定义为独立安全边界：

| 域 | 可访问主体 | 隔离规则 |
| --- | --- | --- |
| CEO Private Brain | CEO，或经明确、可审计授权的最小支持角色。 | 与 Employee AI 内容、普通管理数据和 Agent 工作区逻辑隔离；不因高管角色自动共享。 |
| Employee AI | 已授权员工及其受策略限制的 AI 服务。 | 不读取 CEO Private Brain；按员工、部门、项目与数据分类收窄上下文。 |
| Core Data | 仅经资源策略允许的服务、人员或 Agent。 | Core 是企业数据权威；禁止通过前端、Gateway 路由或 Agent 绕过数据产品/API 的字段和记录级控制。 |

隔离要求包括独立的访问策略、Token 受众、数据分类、日志访问范围、加密密钥/Secret 范围，以及跨域传递时的显式目的绑定和最小化脱敏。跨域查询必须先由 Core 数据策略允许，再由 Gateway/下游服务审计；不得复制任一域的完整权限到另一域。

## 7. Agent 权限

Agent 身份的能力由注册表和策略共同定义，能力等级由低到高为：

| 能力 | 定义 | 控制要求 |
| --- | --- | --- |
| 观察（Observe） | 读取批准的最小状态、元数据或数据产品。 | 只读、字段/来源白名单、不可访问原始未授权数据。 |
| 分析（Analyze） | 在获准输入上计算、归纳、分类或识别模式。 | 输入输出 schema 校验、敏感数据最小化、结果可追溯。 |
| 建议（Recommend） | 生成供人类审阅的方案、风险提示或下一步建议。 | 明示不确定性、证据来源和人工复核；不得自动改变业务状态。 |
| 执行（Execute） | 对外部系统产生受控动作。 | 默认禁止；仅限显式注册、最小作用域、短期授权、审批、幂等/回滚契约及全程审计。 |

Agent 调用必须经过 `gateway/API → Agent Hub`；Agent Hub 不可视为对 Core、数据库或基础设施的直连授权。每个 Agent 需具备唯一 ID、所有者、版本、状态、用途、允许工具/数据、环境、有效期、速率限制与紧急停止标记。Agent 不得自行创建子 Agent、扩大 scope、转授 Token 或将 Secret 写入提示词与输出。

## 8. 审计体系

Gateway 是审计事件的统一入口与关联点。每条事件使用关联 ID、请求 ID、主体 ID、会话/Token ID（脱敏或散列）和策略版本连接，但不记录明文凭据或不必要的个人/业务敏感内容。

| 审计对象 | 最小记录内容 |
| --- | --- |
| 登录 | 主体类型与 ID、认证方式/MFA 结果、时间、风险信号、设备/网络摘要、结果与失败原因。 |
| 调用 | 调用方、目标服务/资源、目的、Token 受众/scope 摘要、关联 ID、请求结果、延迟和拒绝原因。 |
| 数据访问 | 数据域、分类、资源/字段范围摘要、策略决策、导出/共享标记、返回量级与结果。 |
| 审批 | 发起人、审批人、审批对象、理由、策略/风险上下文、决定、有效期与撤销记录。 |
| 执行 | Agent/人类主体、精确动作、目标、前后状态摘要、审批引用、幂等键、结果、失败与人工介入。 |

审计日志应追加写入受保护存储，实施访问控制、完整性校验、保留期限、告警和独立审查。高风险登录、策略拒绝、权限提升、跨域数据请求、Agent 执行、Secret 访问和异常 Token 使用必须触发安全监测。

## 9. 安全边界与禁止项

以下行为在 VAFOX Unified Identity Gateway 架构中明确禁止：

- **禁止 SSH：** Gateway、Huyan、AI、Core 和 Agent Hub 不是 SSH、远程 Shell 或运维跳板入口。
- **禁止绕过 Gateway：** 人类用户、外部客户端与 Agent 不得通过未受控入口直连受保护业务域或 API。
- **禁止直接访问数据库：** 不向浏览器、人类会话或 Agent 暴露数据库网络凭据；数据必须通过受策略保护的 Core 数据产品/API 获取。
- **禁止绕过权限：** URL 猜测、前端隐藏、共享账号、伪造角色、长期通用 Token 或服务间信任均不能替代资源级策略校验。
- **禁止未授权 Agent 调用：** 未注册、状态非 active、版本/环境不匹配、审批过期、能力越界或无法验证身份的 Agent 请求一律拒绝。

此外，禁止在 Token、审计日志、错误信息、浏览器存储和 Agent Prompt 中泄露 Secret；禁止将 CEO Private Brain 或跨域数据作为默认上下文；禁止在策略系统不可用时降级为允许。

## 10. 未来扩展

Gateway 的身份与策略契约必须面向新入口扩展，而不形成新的身份孤岛：

| 扩展入口 | 接入原则 |
| --- | --- |
| 移动端 | 使用同一 `principal_id`、MFA 与设备/风险属性；采用受众绑定的移动会话和 Token。 |
| 小程序 | 通过 Gateway 的受控授权码/Token 交换接入；平台身份仅是凭据绑定，不替代 VAFOX 主体身份。 |
| 合作伙伴入口 | 建立 Partner Identity、组织关系、合同/租户属性与独立数据边界；默认不继承员工或 CEO 权限。 |
| 外部 API | 采用机器身份、OAuth/OIDC 或等效标准、精确 scope、客户端认证、速率限制、签名/撤销与完整审计。 |

所有新增入口必须复用统一身份模型、Gateway 认证、RBAC + ABAC 决策、数据隔离、审计事件模型和禁止项。新入口、新角色、新数据域或 Agent 能力扩大均须先完成架构评审、策略定义、风险评估与审计验证。

## 11. 架构验收准则

VAFOX 统一身份与权限基础在满足以下条件时具备设计上的完整性：

1. `gateway.vafox.com` 是人类与 Agent 的唯一受控身份入口，且路由不替代下游授权。
2. CEO、Executive、Employee 和 Agent 身份有独立生命周期、认证强度与最小权限边界。
3. MFA、Session、Token 和 Secret 管理均支持短期凭据、撤销、轮换、风险控制与审计。
4. RBAC、ABAC 与 Agent Capability 的交集以默认拒绝方式执行。
5. CEO Private Brain、Employee AI 与 Core Data 在策略、Token、数据范围与审计上严格隔离。
6. Agent 只能通过 Gateway/API 进入 Agent Hub，并被限制在观察、分析、建议或经严格审批的执行能力内。
7. 登录、调用、数据访问、审批和执行均可使用关联 ID 追溯，并遵守敏感信息最小化原则。
8. SSH、Gateway 绕过、数据库直连、权限绕过和未授权 Agent 调用均不存在于允许架构路径中。
