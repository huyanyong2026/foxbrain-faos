# FireFox Gateway V1.0 建设报告

## 完成内容

- 建成 FireFox Outdoor Growth Platform 独立入口。
- 完成全屏 Hero、FireFox Story、Adventure、Brand Universe、Explorer、Store 六个首发模块。
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

## 生产检查

- `gateway.vafox.com` 当前解析到 `1.13.254.217`。
- 当前线上仍为旧 FoxBrain 登录页，并非本次 Gateway 页面。
- 当前 HTTPS 证书与 `gateway.vafox.com` 不匹配，需要重新签发。
- 当前 Codex SSH 公钥尚未被该服务器接受，因此未执行生产文件替换和 Nginx 重载。

## 发布步骤

1. 备份当前 Gateway 站点和 Nginx 配置。
2. 将 `apps/gateway/` 发布到 `/var/www/firefox-gateway/current`。
3. 启用 `deploy/nginx/gateway.vafox.com.conf.example` 对应配置。
4. 为 `gateway.vafox.com` 签发 Let's Encrypt 证书。
5. 检查 Nginx 配置并平滑重载。
6. 验证首页、手机端、静态资源和 HTTPS 证书。

## 下一步

- 核实四家门店的地址、营业时间和联系方式后开放门店详情。
- 补充真实活动计划后开放 Adventure 列表。
- 品牌资料核实后逐步开放 Brand Universe 详情。
