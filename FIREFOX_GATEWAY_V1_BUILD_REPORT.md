# VAFOX Gateway V1.0 建设报告

## 完成内容

- 建成 VAFOX Outdoor Growth Platform 独立入口。
- 完成全屏 Hero、VAFOX Story、Adventure、Brand Universe、Explorer、Store 六个首发模块。
- 预留 Commerce、AI Outdoor、Explorer Life、Dream Community 四个未来入口，未完成前不跳转到空白页面。
- 增加手机导航、探索方向选择、品牌提示、门店提示和内容弹窗。
- 使用三张定制户外实景图，全部转为 WebP 并控制总体积。
- 增加无障碍跳转、键盘焦点、减少动画偏好和响应式布局。
- 增加静态烟测脚本及 Nginx HTTPS 发布配置模板。

## 修改文件

- `apps/gateway/index.html`
- `apps/gateway/assets/styles.css`
- `apps/gateway/assets/app.js`
- `apps/gateway/assets/images/gateway-hero.webp`
- `apps/gateway/assets/images/adventure-lake.webp`
- `apps/gateway/assets/images/firefox-store.webp`
- `apps/gateway/smoke-test.cjs`
- `apps/gateway/README.md`
- `deploy/nginx/gateway.vafox.com.conf.example`

## 测试结果

- 桌面端 1440 x 900 首屏视觉检查：通过。
- 手机端 390 x 844 响应式检查：通过，无横向溢出。
- 手机菜单打开与关闭：通过。
- Explorer 选择和结果更新：通过。
- Story 弹窗打开：通过。
- JavaScript 语法检查：通过。
- 首页及 5 项静态资源 HTTP 烟测：通过。
- 中文乱码扫描：通过。

## 生产部署

- 域名：`https://gateway.vafox.com`
- 服务器：`1.13.254.217`
- 发布时间：2026-07-13 16:59 CST
- 发布目录：`/var/www/firefox-gateway/releases/20260713-165718`
- 当前版本：`/var/www/firefox-gateway/current`
- 备份目录：`/var/backups/firefox-gateway/20260713-165718`
- Nginx：配置检查通过，服务保持 `active`，使用平滑重载。
- HTTPS：Let's Encrypt 独立证书已签发，2026-10-11 到期，自动续期任务已建立，续期模拟测试通过。
- 隔离结果：没有修改 `ai.vafox.com`、现有容器或 `/var/www/foxbrain`。

## 线上验收

- HTTP 自动跳转 HTTPS：通过。
- HTTPS 证书主机名验证：通过。
- 首页标题和 Hero 内容：通过。
- CSS、JavaScript 和三张 WebP 图片：全部返回 200。
- 桌面端 1440 x 900 线上截图：通过。
- 手机端 390 x 844 布局、菜单与交互：通过。
- 安全响应头和静态资源缓存：通过。
- 旧 VAFOX 登录页不再接管 Gateway 域名。

## 下一步

- 核实四家门店的地址、营业时间和联系方式后开放门店详情。
- 补充真实活动计划后开放 Adventure 列表。
- 品牌资料核实后逐步开放 Brand Universe 详情。
