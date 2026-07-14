# VAFOX Living Enterprise Data Import V1.0 施工报告

项目编号：FOX-LIFE-IMPORT-001

分支：`firefox-life-import-v1`

完成日期：2026-07-14

## 完成内容

在现有 VAFOX Enterprise OS 上增量增加生命资料导入中心，没有推倒现有生命企业、企业对象或 SAP Mirror 架构。

导入流程已经实现：

文件上传 → 格式检查 → 字段识别 → 字段映射 → 数据预览 → 人工确认 → 正式建立生命对象 → 导入日志 / 安全回滚

系统支持：

- 供应商生命 Supplier Life
- 产品生命 Product Life
- 人才生命 People Life
- 旧版 Excel、XLSX、CSV、GBK/UTF-8/UTF-16 制表符文本
- 原始文件永久保留、文件哈希、行哈希和重复文件提示
- 有错误整批阻断、有警告必须二次确认
- 新对象和已有对象新版本的审计记录
- 精确品牌关系、门店关系及完整来源链
- 管理员导入页面、只读查询接口和批次历史
- 有后续版本或其他来源时阻止危险回滚

## 数据架构

新增数据表：

| 数据表 | 用途 |
|---|---|
| `life_import_batches` | 文件、批次、映射、统计、确认和回滚状态 |
| `life_import_rows` | 原始行、映射行、检查结果和行哈希 |
| `life_import_changes` | 每个生命对象导入前后快照 |
| `life_import_logs` | 上传、确认、回滚审计日志 |

生命对象层新增 `product_life`，已有 `living_objects` 会安全迁移并保留原数据。正式对象继续使用统一的 Identity、Origin、State、Relationship、Timeline、Memory、Decision、Future 结构。

原始文件保存在应用独立的生命导入目录，不进入 Git，不覆盖旧文件。当前 Core API 仍保持只读；本次没有为 Core、SAP 或 Mirror 增加写权限。确认后的生命对象通过现有只读生命对象 API 提供给授权应用使用。

## 页面与接口

新增页面：

- `/admin/import`：上传、字段映射、质量检查、前 80 行预览、人工确认、回滚和历史

新增接口：

- `GET /api/life-import`：批次列表或指定批次详情
- `POST /api/life-import/upload`：仅保存并生成预览
- `POST /api/life-import/mapping`：人工调整字段映射并重新检查
- `POST /api/life-import/approve`：人工确认后建立生命对象
- `POST /api/life-import/rollback`：在安全条件满足时回滚对象变化

现有页面增强：

- `/living-enterprise` 增加产品生命和授权导入入口
- 生命对象列表、详情和 API 增加岗位与门店权限过滤

## 权限模型

- 导入、确认、回滚：仅老板或管理员
- 供应商生命：老板、管理员、采购、财务
- 产品生命：老板、管理员、采购、店长、员工、财务
- 人才生命：老板、管理员；店长仅可查看自己门店
- AI 或其他应用读取时必须继承当前用户权限

## 真实文件验证

| 对象 | 文件行数 | 结果 |
|---|---:|---|
| 供应商 | 121 | 无硬错误，全部因资料不完整等待人工确认 |
| 商品 | 96,011 | 95,858 行通过，153 行缺商品名称，整批阻断 |
| 人员 | 45 | 无硬错误，但缺门店/岗位/状态/入职时间，8 个疑似共用账号 |

详细结论见 `IMPORT_VALIDATION_REPORT.md`。三份文件只在临时数据库完成验证，没有导入生产。

## 测试结果

- 专项与生命企业测试：17 项通过
- 全量自动化回归：114 项通过
- 本地页面烟测：登录、上传、预览、批次 API 均通过
- Python 编译检查：通过
- Git 差异检查：通过
- SAP 写入：0
- 生产数据库写入：0

## 修改文件

- `foxbrain_os/life_import.py`
- `foxbrain_os/living_enterprise.py`
- `portal_v2.py`
- `requirements.txt`
- `scripts/validate_life_import_files.py`
- `tests/test_life_import.py`
- `tests/test_living_enterprise.py`
- `IMPORT_VALIDATION_REPORT.md`
- `FIREFOX_LIFE_IMPORT_V1_REPORT.md`

## 安全检查

- 未连接、修改或回写 SAP
- 未增加 SAP 权限
- 未将连接信息或真实文件提交到 Git
- 未把供应商组名称错误推测为供应商关系
- 未把岗位共用账号自动认定为真实员工
- 所有正式变化都要求人工确认并保留来源

## 后续建议

1. 先修正商品文件 153 条缺少名称的数据，再重新上传。
2. 将员工 SAP 用户清单与真实花名册合并审核，再连接 VAFOX Identity Center。
3. 正式部署后先用小批次完成生产预览、确认和回滚演练。
4. 通过独立、受控的 Core 导入服务承接原始资料归档；继续保持 SAP Mirror 与业务应用只读边界。
