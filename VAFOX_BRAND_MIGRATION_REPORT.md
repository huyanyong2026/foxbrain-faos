# VAFOX Enterprise OS 品牌迁移报告

## 迁移结论

现有企业操作系统的用户可见品牌已统一为 `VAFOX`。域名、数据库、API 路由、服务目录、历史数据和权限体系均保持不变，本次不涉及 SAP 或 Core 业务数据写入。

## 系统名称

| 系统 | 统一名称 | 定位 |
|---|---|---|
| `huyan.vafox.com` | VAFOX Enterprise Brain | 企业大脑 |
| `ai.vafox.com` | VAFOX Enterprise AI Center | 企业智慧中心 |
| `core.vafox.com` | VAFOX Enterprise Data Core | 企业数据核心 |
| `gateway.vafox.com` | VAFOX Gateway | VAFOX 生态入口 |
| `shop.vafox.com` | VAFOX Commerce | 商业交易中心，当前仅保留命名规范 |
| `mail.vafox.com` | VAFOX Mail | 企业通信中心，当前仓库没有独立邮件前端 |
| `www.vafox.com` | VAFOX | 未来公众主站命名规范 |

## 修改范围

- 企业大脑：首页、功能页、标题、系统提示、AI 提示词和版本展示。
- 企业智慧中心：登录页、导航、身份中心、工作台、Agent、经营助手和健康接口。
- 企业数据核心：只读服务名称、README、部署说明和健康状态展示。
- 公众入口：首页 Meta、页头、页脚、Explorer 页面和说明文档。
- 文档体系：README、架构、Sprint、建设报告、部署报告和操作说明中的展示品牌。
- 自动化：部署工作流、服务描述、烟测提示和测试期望中的展示名称。

完整文件清单见 `VAFOX_BRAND_MIGRATION_FILES.txt`。

## 兼容边界

以下技术标识有意保留，以避免破坏生产兼容：

- `foxbrain_os` Python 包和既有模块名。
- `/opt/firefox-*` 服务器目录与现有 systemd 服务名。
- 既有 API 路由、数据库表、字段、Cookie 与插件 ID。
- `X-VAFOX-Service-Token` 内部服务请求头。
- 历史 Git 分支、Commit、SHA 与文件名。

这些标识不会显示在普通用户页面中。

## 页面变化

- 企业大脑统一显示 `VAFOX Enterprise Brain`。
- AI 登录与工作台统一显示 `VAFOX Enterprise AI Center`，原字母标识改为 `V`。
- Core 状态统一显示 `VAFOX Enterprise Data Core`。
- Gateway 浏览器标题显示 `VAFOX Gateway`，页头与页脚主品牌显示 `VAFOX`。
- Explorer 继续使用现有火狐狸图形 Logo，文字品牌统一为 VAFOX。

## 安全检查

- 未修改 SAP。
- 未增加 SAP 权限或写入路径。
- 未修改 Core 数据、数据库结构或令牌权限。
- 未修改域名、Nginx 路由、服务端口或现有登录权限。
- 未重命名内部包、数据库字段或生产目录。

## 测试结果

- 核心 Python 编译检查：通过。
- 品牌迁移专项测试：5 项通过。
- 全项目自动化回归：129 项通过。
- Gateway 静态烟测：首页与 6 项资源全部通过。
- Gateway 桌面视口：标题、页头品牌和页面无旧展示词，横向溢出为 0。
- Gateway 390px 手机视口：标题、页头品牌和 Logo 正常，横向溢出为 0。
- Markdown 展示品牌扫描：通过。
- 用户可见源码残留扫描：通过。
- 全仓残留仅有 2 处既有内部服务请求头，属于明确保留的兼容标识。

## 风险检查

本次涉及大量历史文档的展示名称更新，Git 差异较大但主要为机械文本替换。功能代码只调整展示字符串；内部兼容标识由专门测试锁定，防止误改。
