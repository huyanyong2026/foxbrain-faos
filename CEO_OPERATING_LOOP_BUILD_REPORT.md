# VAFOX CEO Operating Loop 建设报告

## 建设结果

CEO Operating Loop 已在 VAFOX Enterprise Brain V2.0 基础上完成增量建设，形成以下闭环：

```text
core.vafox.com 企业事实
  -> CEO Morning Brief / Enterprise Question
  -> ai.vafox.com 分析候选
  -> CEO 人工接受或拒绝
  -> Decision Memory
  -> Operating Review
  -> Evidence Chain
```

系统不会把 AI 分析直接当成决策。所有 AI 建议默认进入待人工复核状态，决策和复盘必须再次人工确认。

## 已完成模块

### 1. CEO Morning Brief

- 生成每日 Data Core 事实快照。
- 同一天重复生成不会静默覆盖历史。
- 仅在服务器 AI 地址明确配置为 `ai.vafox.com` 时请求 AI 分析。
- AI 未配置或调用失败时保持“等待 AI 分析”。
- AI 分析完成后进入待 CEO 复核状态。
- CEO 可以接受或拒绝建议。

### 2. Enterprise Question Center

- CEO 输入企业问题时先锁定 Data Core 事实快照。
- 问题、事实、依据、AI 分析来源和人工复核结果完整保存。
- 不允许 AI 改写原始事实快照。
- 未配置 `ai.vafox.com` 时明确等待，不使用其他 AI 来源冒充。

### 3. Decision Memory

- CEO 最终决定写入 `huyan.vafox.com` 本地企业数据库。
- 保存决策事项、最终决定、理由和完整依据。
- 关联 AI 问题时，必须先人工确认该 AI 分析。
- 新决策先进入草稿，人工再次确认后才成为已确认决策。

### 4. Evidence Chain

完整区分：

- Data Core 企业事实
- ai.vafox.com 分析候选
- CEO 人工决策
- 经营复盘结果

每条依据保留目标、来源层、来源类型、来源编号、来源引用和采集时间。没有来源或没有 evidence 的建议不能进入闭环。

### 5. Operating Review

- 只能复盘已经人工确认的 CEO 决策。
- 保存预期结果、实际结果、差异分析、经验教训和下一步行动。
- 复盘默认草稿，人工确认后才进入已确认复盘。
- 复盘同时引用 Data Core 事实与原始 CEO 决策。

## 数据库变化

新增五张表：

- `ceo_morning_briefs`
- `enterprise_questions`
- `ceo_decision_memories`
- `operating_evidence_links`
- `operating_reviews`

## 页面与入口

新增页面：

- `/ceo-operating-loop`
- `/ceo-morning-brief`
- `/enterprise-question-center`
- `/decision-memory`
- `/evidence-chain`
- `/operating-review`

Enterprise Brain 页面新增“CEO 经营闭环”入口。

## API

只读接口：

- `GET /api/ceo-operating-loop`
- `GET /api/ceo-operating-loop/evidence`

人工操作接口：

- `POST /api/ceo-operating-loop/brief/create`
- `POST /api/ceo-operating-loop/brief/review`
- `POST /api/ceo-operating-loop/question/create`
- `POST /api/ceo-operating-loop/question/review`
- `POST /api/ceo-operating-loop/decision/create`
- `POST /api/ceo-operating-loop/decision/confirm`
- `POST /api/ceo-operating-loop/review/create`
- `POST /api/ceo-operating-loop/review/confirm`

所有操作继续受现有登录、同源校验、老板/管理员权限和审计日志保护。

## AI 来源控制

CEO Operating Loop 会检查服务器环境中的 AI 服务地址：

- 只有主机名为 `ai.vafox.com` 或其子域时才允许请求分析。
- API 密钥只从服务器环境变量读取，不进入 GitHub。
- 当前本地测试环境未配置真实 `ai.vafox.com` 凭据，因此测试验证的是“安全等待”状态。
- 未宣称真实 AI 连接已经完成。

## SAP 安全边界

- 未连接生产 SAP。
- 未修改 SAP。
- 未增加 SAP 写权限。
- 未在 SAP 服务器安装任何程序。
- 经营事实只通过现有 Data Core 只读副本链路使用。
- AI 无权修改事实、决策或 SAP 数据。

## 修改文件

- `foxbrain_os/ceo_operating_loop.py`
- `portal_v2.py`
- `tests/test_ceo_operating_loop.py`
- `tests/test_natural_experience.py`
- `CEO_OPERATING_LOOP_BUILD_REPORT.md`

## 测试结果

- CEO Operating Loop 专项测试：8 项通过。
- 六个页面隔离渲染：通过。
- Enterprise Brain、Living Enterprise、Brand Life、安全边界和自然中文体验联合回归：通过。
- 总计 55 项测试：全部通过。
- V6 基础烟测：通过。
- Python 编译检查：通过。
- 代码差异检查：通过。
- 无依据建议阻断：通过。
- 非 ai.vafox.com 分析来源阻断：通过。
- 未经人工确认不能形成关联决策：通过。
- 未确认决策不能进入经营复盘：通过。

## 部署状态

当前代码位于开发分支，尚未部署到 `huyan.vafox.com`。代码合并到 `main` 后，应先备份生产代码、数据库和文件目录，再部署并验证六个页面。

真实启用 ai.vafox.com 分析仍需要在生产服务器安全配置：

- `AI_BASE_URL` 指向 `https://ai.vafox.com` 的兼容接口地址。
- `AI_API_KEY` 存放在服务器环境变量。
- 对应模型名称和访问超时。

上述密钥不得进入 GitHub。
