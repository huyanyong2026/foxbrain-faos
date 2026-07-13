# FireFox Living Enterprise V1.0 建设报告

## 建设结果

FireFox Living Enterprise V1.0 已在现有 FoxBrain Enterprise OS 上完成增量建设。系统新增统一 Life Object Framework，把门店、人才、品牌、供应商和探索者从静态资料升级为可持续积累来源、时间轴、关系、记忆、决策与未来事项的生命对象。

本次同时安全带入此前已开发但尚未进入主线的 KAILAS Brand Life Engine，没有重建或替换现有 Object Engine、Knowledge Graph、Memory、Decision、SAP Mirror 或 AI 系统。

## 数据路径

```text
SAP B1（独立、只读边界）
  -> core.vafox.com / SAP Mirror
  -> Data Lake / Business Calibration
  -> 已确认 Enterprise Object
  -> Life Object Framework

Brand Life Engine
  -> Brand Life Profile / Brand Knowledge Vault
  -> Brand Life Object
```

Life Object Framework 不直接连接生产 SAP，也不写 SAP。当前只消费 FoxBrain 本地已确认企业对象和 Brand Life Profile，避免把未经确认的镜像行直接升级为企业生命对象。

## 统一生命模型

八个统一维度：

1. Identity：对象身份与唯一引用。
2. Origin：对象起源及原始来源。
3. Timeline：有发生时间和来源的历史事件。
4. State：当前状态及更新时间。
5. Relationship：对象之间有依据的关系。
6. Memory：已审核企业记忆链接。
7. Decision：带 evidence 的经营决策链接。
8. Future：待验证目标和方向，默认需要人工批准。

第一批生命对象：

- Store Life
- People Life
- Brand Life
- Supplier Life
- Explorer Life

## 数据库变化

新增七张表：

- `living_objects`
- `living_object_sources`
- `living_timeline_events`
- `living_relationships`
- `living_memory_links`
- `living_decision_links`
- `living_future_items`

来源字段在服务层和数据库约束中同时强制。缺少 `source_type`、`source_id` 或 `source_ref` 的对象、事件、关系、记忆、决策和未来事项会被拒绝。

## 现有系统集成

- Enterprise Object：门店、员工、品牌、供应商和顾客对象转换为对应 Life Object。
- Brand Life：KAILAS Brand Life Profile 转换为 Brand Life Object。
- Timeline：只连接同时具有对象引用与来源的时间轴事件。
- Memory：只连接已批准、已生效或已发布的企业记忆。
- Decision：只连接具有 evidence 的 Decision Insight。
- Copilot：页面提供带生命对象上下文的提问入口，但不允许无来源结论。
- SAP Mirror：只通过已确认本地对象间接使用镜像成果，不增加 SAP 连接或写权限。

## 页面与接口

新增页面：

- `/living-enterprise`
- `/living-enterprise/objects/{life_id}`

新增只读接口：

- `GET /api/living-enterprise`
- `GET /api/living-enterprise/objects/{life_id}`

新增人工触发接口：

- `POST /api/living-enterprise/rebuild`

重新同步仅老板和管理员可执行，只更新 FoxBrain 本地数据库，不连接或修改 SAP。

## 同步与幂等

新增 `scripts/sync_living_enterprise.py`：

- 默认 dry-run 并回滚。
- 只有显式传入 `--publish` 才提交本地 Life Object 变化。
- 不接受 SAP 地址、账号或写入参数。
- 相同来源重复同步不会重复创建对象，也不会无意义增加版本。

## 安全边界

- 未修改 SAP。
- 未增加 SAP 写权限。
- 未在 SAP 服务器安装程序。
- 未改变 core.vafox.com 的数据核心定位。
- 未修改现有 AI Agent 的执行权限。
- Future 默认 `approval_required=1`。
- 所有关系和经营上下文必须保留来源。

## 修改文件

- `foxbrain_os/living_enterprise.py`
- `foxbrain_os/brand_life_engine.py`
- `portal_v2.py`
- `scripts/sync_living_enterprise.py`
- `tests/test_living_enterprise.py`
- `tests/test_brand_life_engine.py`
- `scripts/import_brand_life_document.py`
- `BRAND_LIFE_ENGINE_BUILD_REPORT.md`
- `LIVING_ENTERPRISE_V1_BUILD_REPORT.md`

## 测试结果

- Life Object、Brand Life、安全边界和自然中文体验共 38 项测试：全部通过。
- V6 全量基础烟测：通过。
- Python 编译检查：通过。
- 代码差异格式检查：通过。
- SAP 写入检查：没有新增 SAP 写入路径。

## 下一阶段建议

1. 人工确认首批真实门店、人才、品牌、供应商和探索者对象。
2. 通过已确认 Knowledge Graph 关系补充生命对象关系，不自动猜测。
3. 将已批准企业记忆和已接受决策逐步关联到生命时间轴。
4. 在数据量稳定后增加对象生命变化摘要，仍要求 evidence 和人工确认。
