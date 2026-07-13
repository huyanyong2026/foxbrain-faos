# FoxBrain Enterprise Brain V2.0 建设报告

## 建设结果

FoxBrain Enterprise Brain V2.0 已在现有 FoxBrain Enterprise OS 与 Living Enterprise 基础上完成增量建设。系统没有重建现有 Data Lake、Object、Knowledge Graph、Decision、Memory、CEO Vault 或 AI 模块，而是新增统一 CEO Enterprise Brain 组合层。

核心原则已经落实为系统边界：

> 事实来自 Data Core，智慧来自 Founder Memory，AI 只辅助、不替代决策。

## 已完成模块

### 1. Enterprise Constitution

- 新增企业宪章版本模型。
- 保存使命、愿景、价值观和长期原则。
- 新版本先进入待审核状态。
- 只有老板或管理员人工批准后才能成为现行宪章。
- 旧版本保留并归档，不覆盖历史。

### 2. Founder Memory

- 新增创始人记忆模型。
- 保存当时情况、Founder 判断、经验教训和未来参考。
- 新记录默认待确认。
- 只有老板或管理员可以查看、创建和确认。
- AI 不能代写或自动确认 Founder Memory。

### 3. Enterprise Timeline

- 统一展示有来源的企业事件、Founder 记忆和带 evidence 的 AI 建议。
- 三类信息明确标识，不把 AI 建议伪装成企业事实。
- 无来源时间线记录不会进入 Enterprise Brain 时间轴。

### 4. Enterprise Asset Map

统一盘点：

- 企业数字对象
- Living Enterprise 生命对象
- 企业资料
- CEO Vault 资料
- 企业知识
- 企业记忆
- Founder Memory
- 企业知识关系

每个资产数字都带来源和计数依据。

### 5. CEO Decision Center

- 复用现有 Decision Engine，不建立重复决策系统。
- 只展示具有 evidence 的 AI 建议。
- 同时展示已人工确认的 Founder 判断作为决策参考。
- AI 建议仍需 CEO 复核，未增加自动执行权限。

### 6. CEO Vault

- 继续复用现有 CEO Vault。
- 保持老板与管理员权限隔离。
- 股权、银行、战略、投资和重要合同资料不进入普通用户页面。
- 修复 Vault 页面旧的时间显示函数错误。

## 首页与入口

- 新增 `/enterprise-brain` 统一 CEO 企业大脑入口。
- CEO 首页新增“打开企业大脑”入口。
- 企业资料中心新增“CEO 企业大脑”入口。
- 普通用户不显示 Enterprise Brain 入口。

## 数据库变化

新增两张表：

- `enterprise_constitutions`
- `founder_memories`

两张表都强制保存 `source_type`、`source_id` 和 `source_ref`。缺少来源的记录会在服务层和数据库约束层被拒绝。

现有企业事实、时间线、决策和资产数据继续使用原表，不复制、不迁移、不改写。

## 页面与接口

新增页面：

- `/enterprise-brain`
- `/enterprise-constitution`
- `/founder-memory`
- `/enterprise-timeline`
- `/enterprise-asset-map`
- `/ceo-decision-center`

新增只读接口：

- `GET /api/enterprise-brain`
- `GET /api/enterprise-brain/timeline`
- `GET /api/enterprise-brain/assets`

新增人工输入接口：

- `POST /api/enterprise-brain/constitution`
- `POST /api/enterprise-brain/constitution/activate`
- `POST /api/enterprise-brain/founder-memory`
- `POST /api/enterprise-brain/founder-memory/confirm`

所有写入接口继续使用现有登录、同源请求验证、角色权限和操作日志。

## 数据来源边界

### 企业事实

- 来源：core.vafox.com 企业事实经现有只读副本与 FoxBrain 本地数据链路进入。
- Enterprise Brain 不直接连接生产 SAP。
- Enterprise Brain 不直接写 core.vafox.com。

### AI 分析

- 来源：已经进入 FoxBrain、并带 evidence 的 Decision Insight。
- 预留 ai.vafox.com 分析来源，但本次不修改或部署 ai.vafox.com。
- 无 evidence 的 AI 建议不会被标记为可靠结论。

### Founder 智慧

- 来源：Founder 人工输入。
- 系统保留来源、版本、确认人和确认时间。
- AI 不得自动创建“已确认”的 Founder Memory。

## 安全边界

- 未连接或修改 SAP。
- 未增加 SAP 写权限。
- 未修改 SAP 数据库结构。
- 未在 SAP 服务器安装程序。
- 未开发或部署 ai.vafox.com 页面。
- 未改变现有 AI Agent 执行权限。
- 未增加 AI 自动决策或自动执行能力。
- Enterprise Constitution 与 Founder Memory 仅老板和管理员可访问。

## 修改文件

- `foxbrain_os/enterprise_brain.py`
- `portal_v2.py`
- `tests/test_enterprise_brain.py`
- `tests/test_natural_experience.py`
- `ENTERPRISE_BRAIN_V2_BUILD_REPORT.md`

## 测试结果

- Enterprise Brain 专项测试：7 项通过。
- Enterprise Brain 六个页面隔离渲染：通过。
- Enterprise Brain、Living Enterprise、Brand Life、安全边界和自然中文体验共 46 项测试：全部通过。
- V6 基础烟测：通过。
- Python 编译检查：通过。
- 无来源数据阻断：通过。
- 无 evidence AI 建议隔离：通过。
- 人工批准与确认边界：通过。

## 部署状态

当前代码位于开发分支，尚未部署到 `huyan.vafox.com`。应在 PR 合并到 `main` 后执行生产代码、数据库和文件目录备份，再部署并逐页验证六个入口。

## 下一阶段建议

1. 由 Founder 建立企业宪章第一版，并人工批准。
2. 录入首批真实 Founder Memory，不导入未经确认的 AI 总结。
3. 将 core.vafox.com 的同步新鲜度和对账状态纳入 Enterprise Brain 事实卡片。
4. 将 CEO 已接受决策的执行结果回写企业时间轴与 Founder Memory 候选区，仍需人工确认。
