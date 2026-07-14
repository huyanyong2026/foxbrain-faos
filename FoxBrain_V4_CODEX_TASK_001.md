# VAFOX V4 Enterprise AI Operating System
## CODEX EXECUTION TASK 001
### Project Architecture Upgrade / 企业 AI 操作系统整体升级任务

Repository:

https://github.com/huyanyong2026/foxbrain-v4

---

## 0. Core Principle / 核心原则

This task is NOT a rewrite.

本次任务不是重写项目，不允许推倒重做。

Codex must upgrade the existing VAFOX project based on the current repository.

Must preserve and remain compatible with:

- Existing login system
- Existing role and permission system
- Existing SAP B1 sync logic
- Existing database and existing data
- Existing AI homepage / portal
- Existing APIs
- Existing deployment assumptions
- Existing README and docs

Do not delete existing features.

Do not break SAP B1 sync.

Do not hardcode secrets, passwords, API keys, database credentials, or tokens.

All new features must be modular, maintainable, and backward compatible.

---

## 1. Product Positioning / 产品定位

VAFOX V4 is not a traditional ERP, CRM, or simple knowledge base.

It should be upgraded into:

> VAFOX / 火狐狸 Enterprise AI Operating System

Its long-term goal is to become the digital brain of the company.

Main modules:

- AI CEO / AI 总经理
- Business Overview / 经营总览
- Store Center / 门店中心
- Employee Center / 员工中心
- Brand Center / 品牌中心
- Product Center / 产品中心
- Supplier Center / 供应商中心
- Customer / Member Center / 顾客会员中心
- Inventory & Purchasing / 库存采购
- Finance Center / 财务中心
- Content Center / 内容中心
- Knowledge Center / 知识中心
- AI Agent Center / AI 智能体中心
- Workflow Center / 工作流
- System Management / 系统管理

---

## 2. Task Goal / 本次任务目标

Upgrade the existing project into the first V4 architecture version.

The deliverable should include:

1. A new minimal enterprise dashboard
2. A unified archive framework
3. Six archive modules
4. A document center skeleton
5. A knowledge center skeleton
6. An AI agent center skeleton
7. SAP B1 analysis API placeholders without breaking existing sync
8. Content center skeleton
9. Mobile-first responsive UI
10. Updated README and docs

---

## 3. Dashboard Upgrade / 首页升级

### Requirement

Redesign the homepage.

Style reference:

- Apple
- Notion
- Linear
- ChatGPT
- Arc Browser

UI requirements:

- Minimal
- Premium
- Clean
- Large spacing
- Rounded cards
- Soft shadow
- Mobile-first
- No dense ERP-style tables
- No overloaded charts on homepage
- No excessive numbers on homepage

### Homepage should only show entrance buttons

Use these main buttons/cards:

- AI 总经理
- 经营总览
- 门店中心
- 员工中心
- 品牌中心
- 产品中心
- 供应商中心
- 顾客中心
- 库存采购
- 财务中心
- 内容中心
- 知识中心
- AI 智能体
- 工作流
- 系统管理

Each card should navigate to its detail page.

Do not overload the home page with detailed sales, inventory, or finance data.

The homepage should feel like a CEO command entrance, not an ERP report page.

---

## 4. Unified Archive Framework / 统一档案框架

Create a reusable archive framework that can be used by:

- Store
- Employee
- Brand
- Product
- Supplier
- Customer / Member

All archive modules should support the following features:

- Create
- Edit
- Delete
- Detail page
- Search
- Tags
- Notes
- Timeline
- Related objects
- Attachments
- Upload image
- Upload PDF
- Upload Word
- Upload Excel
- Upload video
- Folder creation
- Drag and drop upload
- Auto archive placeholder
- AI query placeholder
- Full-text search placeholder

The goal is consistency.

All archive pages should share the same layout and components where possible.

---

## 5. Six Archive Modules / 六大档案中心

### 5.1 Store Archive / 门店档案

Add or prepare fields:

- Store name / 门店名称
- Address / 地址
- Photos / 照片
- Area / 面积
- Opening date / 开业时间
- Lease contract / 租赁合同
- Revenue / 营业额
- Rent / 租金
- Property fee / 物业费
- Utilities / 水电
- Management fee / 管理费
- Employees / 员工
- Brands / 品牌
- Renovation history / 历史装修
- Sales history / 历史销售
- Profit / 利润
- Business analysis / 经营分析
- AI suggestions / AI 建议
- Attachments / 附件

### 5.2 Employee Archive / 员工档案

Add or prepare fields:

- Name / 姓名
- Photo / 照片
- Age / 年龄
- Phone / 电话
- Role / 岗位
- Department / 部门
- Entry date / 入职日期
- Leave date / 离职日期
- Salary / 工资
- Performance / 绩效
- Sales history / 销售历史
- Growth record / 成长记录
- Training / 培训
- Rewards and penalties / 奖惩
- Attachments / 附件
- AI evaluation / AI 评价

### 5.3 Brand Archive / 品牌档案

Add or prepare fields:

- Brand name / 品牌名称
- Logo
- Brand introduction / 品牌介绍
- History / 品牌历史
- Owner / 负责人
- Contract / 合同
- Sales / 销售
- Gross margin / 毛利
- Inventory / 库存
- Images / 图片
- Videos / 视频
- Documents / 文档
- Future plan / 未来规划
- AI analysis / AI 分析

### 5.4 Product Archive / 产品档案

Add or prepare fields:

- Product name / 产品名称
- SKU
- Barcode / 条码
- Brand / 品牌
- Category / 分类
- Images / 图片
- Manual / 说明书
- Sales / 销售
- Inventory / 库存
- Profit / 利润
- Attachments / 附件
- AI recommendation / AI 推荐

### 5.5 Supplier Archive / 供应商档案

Add or prepare fields:

- Supplier name / 供应商名称
- Contact person / 联系人
- Phone / 电话
- WeChat / 微信
- Contract / 合同
- Payment terms / 付款方式
- Purchase history / 历史采购
- Attachments / 附件
- AI evaluation / AI 评价

### 5.6 Customer / Member Archive / 顾客会员档案

Add or prepare fields:

- Name / 姓名
- Phone / 电话
- WeChat / 微信
- Birthday / 生日
- Purchase history / 消费记录
- Points / 积分
- Member level / 会员等级
- Historical purchases / 历史购买
- Interests / 兴趣
- Notes / 备注
- Historical interactions / 历史互动
- AI recommendation / AI 推荐

---

## 6. Document Center / 统一文件中心

Create a Document Center skeleton.

Supported file types:

- PDF
- Word
- Excel
- PPT
- Images
- Videos
- Audio
- ZIP
- Contracts

Required skeleton features:

- Upload
- File list
- File detail
- File type
- Related object
- Tags
- Notes
- Created by
- Created time
- Folder
- Search

Prepare placeholders for:

- OCR
- Auto summary
- Keywords
- Auto tags
- Classification
- Embedding
- Vector database
- AI Q&A

Do not implement heavy AI processing if not already supported.

Create clean interface and extension points.

---

## 7. Knowledge Center / AI 知识中心

Create or upgrade Knowledge Center skeleton.

All uploaded documents should eventually support:

- Parsing
- OCR
- Summary
- Keywords
- Vectorization
- Object relation
- AI query

Prepare UI examples for questions:

- 南山店租赁合同在哪里？
- 哪个员工卖 KAILAS 最多？
- 去年利润最高的品牌是什么？
- 库存最大的产品是什么？
- 哪个供应商付款条件最好？

For this task, build the framework and placeholders.

Do not fake real answers unless data exists.

---

## 8. AI Agent Center / AI 智能体中心

Create AI Agent Center page.

Agents:

- AI CEO / AI 总经理
- AI CFO / AI 财务总监
- AI COO / AI 运营总监
- AI Purchasing Manager / AI 采购经理
- AI Inventory Manager / AI 库存经理
- AI Brand Manager / AI 品牌经理
- AI Store Manager / AI 门店经理
- AI Marketing Manager / AI 营销经理
- AI Training Manager / AI 培训经理
- AI Customer Service / AI 客服
- AI Secretary / AI 秘书

Each agent card should include:

- Name
- Role
- Responsibility
- Status
- Entry button
- Future API placeholder

The page should be a framework first.

---

## 9. SAP B1 / SAP B1 数据中台

Do not break existing SAP B1 sync.

Do not modify existing sync logic unless absolutely necessary.

Add new analysis API placeholders or safe endpoints:

- Business analysis API
- Profit analysis API
- Inventory analysis API
- Sales trend API
- AI analysis API

If real SAP data is unavailable in local development, use safe empty states instead of fake data.

---

## 10. Content Center / 内容中心

Create Content Center skeleton.

Channels:

- WeChat Official Account / 公众号
- WeChat Channels / 视频号
- Douyin / 抖音
- Xiaohongshu / 小红书
- Facebook
- Instagram
- TikTok

Future features:

- Unified editor
- Multi-platform rewriting
- Draft management
- One-click publish
- AI content generation

For this task, build the page framework and navigation.

---

## 11. Workflow Center / 工作流中心

Create Workflow Center skeleton if not already existing.

Future workflows:

- Purchase approval
- Payment approval
- Contract approval
- Leave approval
- Recruitment
- Resignation
- Store task assignment
- Content review

For this task, create the framework and placeholders.

---

## 12. Mobile First / 移动端优先

All pages must be responsive.

Must support:

- iPhone screen
- Android screen
- Tablet
- Desktop

Mobile actions should include placeholders for:

- Photo upload
- Camera
- Scan
- Voice input
- AI recognition

Do not create desktop-only pages.

---

## 13. UI Guideline / UI 规范

Avoid:

- ERP-style dense tables
- Overloaded charts
- Too many colors
- Complex menus
- Hard-to-use mobile layout
- Small unreadable text

Use:

- Clean cards
- Large spacing
- Clear hierarchy
- Rounded corners
- Modern typography
- Soft neutral background
- Simple navigation
- Consistent components

---

## 14. Code Requirements / 代码要求

Must follow:

- Modular structure
- Reusable components
- REST API where applicable
- Type safety if stack supports it
- Clear naming
- Logging
- Error handling
- Comments for important logic
- No duplicated large code blocks
- No hardcoded secrets
- No breaking changes

Update docs when adding new structure.

---

## 15. Suggested Directory Structure / 建议目录结构

If compatible with existing project, gradually move toward:

```text
foxbrain-v4/
├── README.md
├── .env.example
├── docs/
│   ├── 00_VISION.md
│   ├── 01_PRODUCT.md
│   ├── 02_ARCHITECTURE.md
│   ├── 03_DATABASE.md
│   ├── 04_UI_GUIDELINE.md
│   ├── 05_AI_AGENTS.md
│   ├── 06_SAP_B1.md
│   ├── 07_WORKFLOW.md
│   ├── 08_API.md
│   ├── 09_DEPLOY.md
│   └── CODEX_TASKS/
│       └── Task001_V4_Architecture_Upgrade.md
├── backend/
├── frontend/
├── ai/
├── knowledge/
├── sap/
├── workflow/
├── deployment/
├── scripts/
└── tests/
```

Do not force this structure if it breaks the current project.

Adopt gradually and safely.

---

## 16. Git / PR Requirements

After completion:

1. Commit changes
2. Push branch
3. Create Pull Request

Recommended PR title:

```text
Task001: VAFOX V4 Architecture Upgrade
```

Recommended PR description:

```text
Task001 Completed

- Enterprise dashboard upgraded
- Unified archive framework added
- Store / Employee / Brand / Product / Supplier / Customer archive skeletons added
- Document Center skeleton added
- Knowledge Center skeleton added
- AI Agent Center skeleton added
- Content Center skeleton added
- Workflow Center skeleton added
- Mobile-first responsive UI improved
- README and docs updated
- Existing login, permissions, SAP B1 sync, and APIs preserved

Ready for review.
```

---

## 17. Required Deliverables / 必须交付

Codex must deliver:

- Updated code
- Updated README
- New or updated docs
- Any database migration script if needed
- Clear PR description
- PC screenshot if possible
- Mobile screenshot if possible
- Suggestions for Task002 and Task003

---

## 18. Absolute Restrictions / 绝对限制

Do NOT:

- Rewrite the whole project
- Delete existing login
- Delete existing permissions
- Break SAP B1 sync
- Delete existing database tables
- Hardcode secrets
- Put real passwords into code
- Replace the project with a completely different stack
- Create fake business data as if it were real
- Make homepage into a dense ERP dashboard

---

## 19. Expected Result / 预期结果

After this task, VAFOX should look and feel like the first version of an enterprise AI operating system.

It should have:

- A clean CEO entrance homepage
- Unified archive module foundation
- Document and knowledge center foundations
- AI agent center foundation
- Content center foundation
- Workflow foundation
- Safe SAP B1 compatibility
- Mobile-first design

This will become the base for Task002, Task003, and future long-term development.
