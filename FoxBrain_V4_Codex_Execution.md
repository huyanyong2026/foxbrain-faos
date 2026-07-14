# VAFOX V4 企业 AI 操作系统 — Codex 执行文件

> 项目：VAFOX / 火狐狸 AI 企业经营系统
> 执行对象：Codex  
> 执行原则：在现有代码基础上继续升级，不推倒重做。  
> 当前基础：已有 `portal_v2.py`、`sync_sap_b1.py`、`sap_b1_sync_page.md`、`wiki_ai_plan_content.json`、`.env.example` 等文件。  
> 当前状态：已完成登录/注册/审核、角色权限、移动端适配、V3 入口型首页、AI 总经理晨报页面、SAP B1 同步脚本、经营摘要接口、档案模块基础框架。

---

## 一、总目标

将现有 VAFOX V3 升级为 **VAFOX V4 企业 AI 操作系统**。

VAFOX 不是普通后台，也不是简单知识库，而是火狐狸公司的统一 AI 经营入口。

最终目标：

1. 老板每天打开系统，可以看到公司经营状态。
2. 员工可以用手机上传图片、合同、文档、销售资料。
3. 每个门店、员工、品牌、产品、供应商、顾客都有独立档案。
4. 所有文档、图片、Excel、PDF 都能自动归档。
5. 所有资料都可以被 AI 查询。
6. SAP B1 数据可以同步到系统，用于经营分析。
7. 系统支持 AI 总经理、AI 财务、AI 采购、AI 库存、AI 内容、AI 门店经理等智能体。
8. 后续支持公众号、视频号、小红书、抖音、小程序等内容发布。

---

## 二、重要开发原则

### 1. 不要推倒重做

必须基于现有文件继续升级：

- `portal_v2.py`
- `sync_sap_b1.py`
- `sap_b1_sync_page.md`
- `wiki_ai_plan_content.json`
- `.env.example`

允许拆分模块，但不要破坏现有功能。

### 2. 首页必须极简

首页不要显示大量数据表格。

首页只保留核心入口按钮：

1. AI 总经理
2. 经营总览
3. 门店档案
4. 员工档案
5. 品牌档案
6. 产品档案
7. 供应商档案
8. 顾客/会员档案
9. 财务中心
10. 库存采购中心
11. 内容发布中心
12. 知识中心
13. AI 智能体查询
14. 任务中心
15. 系统管理

点击按钮后进入详细页面。

### 3. 所有模块都要支持统一能力

以下模块必须统一支持：

- 新建
- 编辑
- 删除
- 查看详情
- 上传图片
- 上传 PDF
- 上传 Word
- 上传 Excel
- 上传其他附件
- 建立文件夹
- 自动归档
- AI 查询
- 时间轴
- 操作日志
- 标签
- 关联对象

适用对象：

- 门店
- 员工
- 品牌
- 产品
- 供应商
- 顾客/会员
- 合同
- 项目
- 任务
- 内容
- 知识文档

---

## 三、页面结构要求

### 1. 首页 / 总入口

页面名称：`/dashboard` 或 `/`

设计要求：

- 移动端优先
- 简洁大按钮
- 圆角卡片
- 类似 Apple / Notion / ChatGPT 风格
- 不要密集表格
- 支持深色模式预留
- 每个入口有图标、标题、简短说明

首页入口示例：

```text
AI 总经理
今天公司情况、风险提醒、经营建议

经营总览
销售、利润、库存、现金流

门店档案
南山店、振兴店、航苑店等

员工档案
员工信息、销售、收入、成长记录

品牌档案
KAILAS、Mammut、OSPREY、Deuter 等

产品档案
产品说明、库存、销售历史

供应商档案
合同、付款、供货记录

顾客/会员档案
消费记录、标签、贡献

内容发布中心
公众号、小红书、抖音、视频号

AI 智能体查询
直接问公司经营问题
```

---

## 四、六大核心档案系统

### 1. 门店档案

字段：

- 门店名称
- 地址
- 面积
- 开业时间
- 店铺照片
- 店铺介绍
- 租赁合同
- 租金
- 水电费
- 管理费
- 杂费
- 历史营业额
- 历史毛利
- 库存金额
- 员工列表
- 关联品牌
- 关联供应商
- 经营问题
- 改造计划
- AI 分析记录

页面功能：

- 门店详情页
- 门店图片墙
- 门店文件夹
- 门店时间轴
- 门店经营分析
- 门店 AI 问答

示例问题：

```text
南山店租赁合同在哪里？
南山店今年销售下降原因是什么？
振兴店和航苑店是否重叠？
哪个店库存风险最大？
```

### 2. 员工档案

字段：

- 姓名
- 年龄
- 手机
- 岗位
- 所属门店
- 入职时间
- 历史销售
- 历史毛利
- 历史收入
- 提成记录
- 培训记录
- 发展空间
- 奖惩记录
- 合同/证件附件
- 照片
- AI 评价

示例问题：

```text
哪个员工销售最好？
哪个员工毛利贡献最高？
谁适合做店长？
南山店员工工资是否合理？
```

### 3. 品牌档案

字段：

- 品牌名称
- 品牌介绍
- 品牌照片
- 代理商
- 负责人
- 合同
- 折扣政策
- 历史销售
- 历史毛利
- 库存金额
- 返点政策
- 风险说明
- 关联供应商
- 关联产品
- AI 分析

重点品牌：

- KAILAS
- Mammut
- OSPREY
- Deuter
- Gregory
- Salomon
- VAFOX

示例问题：

```text
KAILAS 今年销售怎么样？
OSPREY 62 折还有利润吗？
Mammut 是否适合开专卖店？
哪个品牌库存压力最大？
```

### 4. 产品档案

字段：

- 产品名称
- 品牌
- 品类
- 货号
- 图片
- 说明
- 吊牌价
- 进货价
- 当前折扣
- 库存数量
- 库存金额
- 历史销售
- 历史毛利
- 适合人群
- 搭配建议
- 关联内容
- AI 推荐话术

示例问题：

```text
哪些产品卖得最好？
哪些产品库存太多？
哪些产品适合做小红书？
哪些产品适合做套装？
```

### 5. 供应商档案

字段：

- 供应商名称
- 联系人
- 电话
- 微信
- 地址
- 合同
- 付款方式
- 账期
- 供货品牌
- 历史采购
- 应付金额
- 返点政策
- 风险记录
- 附件
- AI 评价

示例问题：

```text
哪个供应商账期最长？
哪个供应商风险最大？
今年应付多少钱？
哪些合同快到期？
```

### 6. 顾客/会员档案

字段：

- 姓名
- 手机
- 微信
- 年龄
- 性别
- 所属门店
- 来源
- 标签
- 历史消费
- 历史毛利
- 购买品牌
- 购买品类
- 活动参与
- 社群归属
- 备注
- AI 推荐

示例问题：

```text
哪些顾客贡献最高？
哪些顾客适合邀请进户外社群？
哪些顾客适合推荐 KAILAS？
哪些顾客沉睡超过一年？
```

---

## 五、文件上传与自动归档

### 1. 上传类型

必须支持：

- 图片：jpg、jpeg、png、webp
- PDF
- Word：doc、docx
- Excel：xls、xlsx、csv
- 文本：txt、md
- 视频：mp4、mov
- 音频：mp3、m4a、wav

### 2. 上传后自动处理

上传后系统应自动：

1. 保存原始文件
2. 生成文件记录
3. 识别文件类型
4. 绑定所属对象
5. 提取文本
6. 生成摘要
7. 自动标签
8. 写入知识库
9. 建立向量索引预留
10. 记录上传人、上传时间

### 3. 归档结构

建议目录：

```text
/uploads
  /stores
  /employees
  /brands
  /products
  /suppliers
  /customers
  /contracts
  /finance
  /inventory
  /content
  /knowledge
```

---

## 六、AI 知识库与问答

### 1. 知识库目标

所有经营资料都进入知识库，AI 可以查询。

包括：

- 门店合同
- 员工资料
- 品牌资料
- 产品资料
- 供应商合同
- 顾客记录
- 财务数据
- 销售数据
- 库存数据
- 会议纪要
- 图片说明
- 经营方案
- 内容文案

### 2. AI 查询入口

页面：`/ai-query`

功能：

- 输入问题
- 选择范围：全公司 / 门店 / 员工 / 品牌 / 产品 / 供应商 / 顾客
- 返回答案
- 显示引用来源
- 显示相关文件
- 显示下一步建议

### 3. 预留模型接口

`.env.example` 增加：

```env
OPENAI_API_KEY=
DEEPSEEK_API_KEY=
AI_PROVIDER=deepseek
AI_BASE_URL=
AI_MODEL=
EMBEDDING_MODEL=
```

必须支持：

- DeepSeek
- OpenAI
- 自定义 API endpoint

---

## 七、AI 智能体矩阵

新增页面：`/agents`

智能体列表：

1. AI 总经理
2. AI 财务总监
3. AI 采购经理
4. AI 库存经理
5. AI 品牌经理
6. AI 门店经理
7. AI 人事经理
8. AI 内容经理
9. AI 客服
10. AI 法务
11. AI 数据分析师
12. AI 投资助手

每个智能体需要：

- 名称
- 角色说明
- 可查询数据范围
- Prompt 模板
- 常用问题
- 输出格式

示例：

```text
AI 总经理：
你是火狐狸公司的 AI 总经理，负责根据销售、库存、财务、门店、员工、品牌、供应商、顾客数据，给老板提供经营判断、风险预警和行动建议。
```

---

## 八、SAP B1 数据同步升级

当前已有 `sync_sap_b1.py`，继续升级。

目标：

- 从 SAP B1 SQL Server 同步到本地 PostgreSQL
- 支持定时同步
- 支持手动同步
- 支持同步日志
- 支持错误提示
- 支持经营摘要生成

同步数据：

- 销售单
- 退货单
- 库存
- 商品
- 品牌
- 会员
- 供应商
- 采购
- 应收
- 应付
- 毛利
- 门店
- 员工销售

新增页面：`/sap-sync`

页面功能：

- 查看同步状态
- 手动执行同步
- 查看最后同步时间
- 查看同步错误
- 查看经营摘要

---

## 九、经营总览中心

页面：`/business-overview`

展示：

- 今日销售
- 本月销售
- 本月毛利
- 本月费用
- 本月利润预估
- 门店排名
- 品牌排名
- 员工排名
- 库存金额
- 库存风险
- 现金流预警
- AI 建议

注意：首页不要直接显示这些详细数据，要点击“经营总览”后进入。

---

## 十、内容发布中心

页面：`/content-center`

目标：一次编辑，多平台改写。

支持平台：

- 微信公众号
- 视频号
- 小红书
- 抖音
- 朋友圈
- 小程序
- 官网

功能：

- 新建内容
- 上传图片
- 选择产品
- 选择门店
- 选择品牌
- AI 生成标题
- AI 生成文案
- AI 改写为不同平台版本
- 保存草稿
- 发布记录

内容类型：

- 产品推荐
- 门店活动
- 户外知识
- 品牌介绍
- 会员福利
- 新品上市
- 清仓促销
- 社群活动

---

## 十一、任务中心

页面：`/tasks`

功能：

- 新建任务
- 指派人员
- 关联门店/品牌/产品/供应商/顾客
- 设置截止时间
- 设置优先级
- 设置状态
- 上传附件
- AI 生成任务建议
- 完成记录

任务状态：

- 未开始
- 进行中
- 等待确认
- 已完成
- 已取消

---

## 十二、数据库建议

建议使用 PostgreSQL。

核心表：

```text
users
roles
permissions
stores
employees
brands
products
suppliers
customers
files
folders
documents
knowledge_chunks
ai_agents
ai_conversations
sap_sync_logs
business_snapshots
tasks
task_comments
operation_logs
tags
object_relations
content_posts
```

### 关键通用字段

每张核心表建议包含：

```text
id
name/title
description
status
created_at
updated_at
created_by
updated_by
is_deleted
```

### 文件表 files

字段建议：

```text
id
original_name
stored_name
file_path
file_type
mime_type
file_size
object_type
object_id
folder_id
summary
extracted_text
tags
uploaded_by
created_at
```

### 关联表 object_relations

用于把门店、员工、品牌、产品、供应商、顾客、文件、任务等连接起来。

字段：

```text
id
source_type
source_id
target_type
target_id
relation_type
note
created_at
```

---

## 十三、权限要求

角色：

1. 超级管理员
2. 老板/总经理
3. 店长
4. 员工
5. 财务
6. 采购
7. 内容运营
8. 只读访客

权限控制：

- 页面访问权限
- 数据查看权限
- 新建/编辑/删除权限
- 文件上传权限
- AI 查询权限
- SAP 同步权限
- 系统管理权限

---

## 十四、UI 设计要求

整体风格：

- 简洁
- 高级
- 移动端友好
- 卡片式
- 大按钮
- 圆角
- 留白
- 不要传统 ERP 复杂表格感

推荐风格：

- Apple
- Notion
- Linear
- ChatGPT

颜色：

- 主色：深蓝 / 黑灰 / 橙红点缀
- 背景：浅灰白
- 卡片：白色
- 字体：清晰大号

移动端：

- 按钮要大
- 表单要简洁
- 上传要方便
- 支持手机拍照上传

---

## 十五、API 路由建议

```text
GET  /
GET  /dashboard
GET  /business-overview
GET  /stores
POST /stores
GET  /stores/<id>
POST /stores/<id>/edit
POST /stores/<id>/delete
POST /stores/<id>/upload

GET  /employees
GET  /brands
GET  /products
GET  /suppliers
GET  /customers

GET  /knowledge
POST /knowledge/upload
POST /ai-query
GET  /agents
GET  /tasks
POST /tasks
GET  /content-center
POST /content-center/create
GET  /sap-sync
POST /sap-sync/run
GET  /settings
```

---

## 十六、开发优先级

### 第一阶段：V4.0 基础升级

必须完成：

1. 首页入口型设计优化
2. 六大档案模块完整 CRUD
3. 文件上传系统
4. 文件夹系统
5. 附件与对象绑定
6. AI 查询页面基础版
7. AI 智能体页面基础版
8. SAP 同步页面优化
9. 经营总览页面基础版
10. 移动端优化

### 第二阶段：V4.1 知识库增强

完成：

1. PDF 文本提取
2. Word 文本提取
3. Excel 文本提取
4. 图片 OCR 预留
5. 自动摘要
6. 自动标签
7. 知识分块
8. AI 引用来源
9. 向量数据库预留

### 第三阶段：V4.2 经营分析增强

完成：

1. 销售分析
2. 毛利分析
3. 库存分析
4. 门店分析
5. 员工分析
6. 品牌分析
7. 供应商分析
8. 顾客分析
9. AI 经营日报
10. AI 风险预警

### 第四阶段：V4.3 内容中心

完成：

1. 内容草稿
2. 多平台文案改写
3. 图片管理
4. 产品关联
5. 门店关联
6. 发布记录

---

## 十七、验收标准

Codex 完成后，需要满足：

1. 系统可以正常启动。
2. 原有登录和权限不丢失。
3. 首页变成入口型首页。
4. 门店/员工/品牌/产品/供应商/顾客都可以新建、编辑、删除、查看。
5. 每个档案可以上传文件。
6. 文件可以绑定到对应档案。
7. 可以查看文件列表。
8. AI 查询页面可以打开。
9. AI 智能体页面可以打开。
10. SAP 同步页面可以打开。
11. 经营总览页面可以打开。
12. 手机端访问布局正常。
13. `.env.example` 不包含真实密码。
14. 不要在代码里写死真实 API Key、数据库密码、服务器密码。
15. README 需要更新为 V4 说明。

---

## 十八、安全要求

严禁：

- 把真实密码写进 GitHub
- 把 API Key 写进代码
- 把数据库密码写进代码
- 把服务器密码写进代码
- 把用户隐私数据暴露在页面

必须：

- 使用 `.env`
- `.env` 加入 `.gitignore`
- `.env.example` 只放空模板
- 上传文件限制大小
- 上传文件限制类型
- 后台接口必须校验登录
- 删除操作需要确认

---

## 十九、建议目录结构

```text
foxbrain/
  portal_v2.py
  sync_sap_b1.py
  sap_b1_sync_page.md
  wiki_ai_plan_content.json
  .env.example
  requirements.txt
  README.md
  /templates
  /static
    /css
    /js
    /icons
  /uploads
    /stores
    /employees
    /brands
    /products
    /suppliers
    /customers
    /knowledge
  /modules
    auth.py
    dashboard.py
    stores.py
    employees.py
    brands.py
    products.py
    suppliers.py
    customers.py
    files.py
    knowledge.py
    ai_agents.py
    sap_sync.py
    business.py
    content.py
    tasks.py
  /db
    models.py
    migrations
```

如果现有代码暂时不方便拆分，可以先保持 `portal_v2.py`，但代码内部必须分区清晰。

---

## 二十、给 Codex 的直接执行命令

请按以下步骤执行：

```text
1. 阅读当前项目全部文件，尤其是 portal_v2.py、sync_sap_b1.py、README.md、.env.example。
2. 不要推倒重写，在现有基础上升级。
3. 优先完成 V4.0 基础升级。
4. 保留原有登录、权限、移动端适配、SAP 同步能力。
5. 把首页改为入口型首页。
6. 完成门店、员工、品牌、产品、供应商、顾客六大档案模块。
7. 为每个档案模块增加文件上传、文件列表、详情页、编辑页、删除功能。
8. 增加知识中心、AI 查询、AI 智能体中心、任务中心、内容发布中心页面。
9. 增加统一文件表和对象关联能力。
10. 更新 README 为 VAFOX V4 说明。
11. 检查安全，不要提交真实密码、API Key、数据库连接。
12. 完成后给出变更摘要、启动方式、测试账号、测试步骤。
```

---

## 二十一、最终目标一句话

把 VAFOX 从一个内部管理门户，升级为火狐狸自己的 **AI 总经理 + 企业知识库 + 经营数据中台 + 智能体系统 + 内容发布中心**。

