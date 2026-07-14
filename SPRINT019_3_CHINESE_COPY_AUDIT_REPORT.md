# Sprint019.3 中文文案审计报告

## 升级前盘点

- 源码路由判断约 719 处，页面函数 31 个，包含大量历史兼容接口与多代页面。
- 主要问题包括英文模块标题、英文状态值、接口按钮、内部字段说明、无说明的英文空状态和旧系统入口。
- 历史模块继续作为后台兼容能力保留，不再全部暴露在日常导航。

## 重点替换

| 升级前 | 升级后 |
|---|---|
| Dashboard | 经营首页 |
| Enterprise Copilot | AI助手 |
| Decision Engine | 经营决策 |
| Business Health | 企业健康 |
| Daily Intelligence | 每日经营简报 |
| Inventory Intelligence | 库存分析 |
| Brand Intelligence | 品牌分析 |
| Store Intelligence | 门店分析 |
| Evidence | 依据 |
| Rebuild / Analyze | 重新分析 |
| Pending / Success / Failed | 待处理 / 已完成 / 处理失败 |

## 技术信息治理

- 普通主要页面不再显示接口按钮和请求路径。
- 文件详情不再显示文件哈希；版本显示为“第 N 版”。
- AI助手不再显示内部上下文模块名和接口清单，改为企业数据、档案、关系、规则、决策记录、记忆和每日简报。
- 错误页不显示堆栈或内部异常，改为影响说明、可重试动作和 AI 入口。

正式品牌名、SAP B1、VAFOX 和用户上传文件原文按规范保留。
