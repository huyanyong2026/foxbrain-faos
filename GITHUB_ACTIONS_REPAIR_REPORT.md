# VAFOX GitHub Actions Repair V1.0

## 1. 问题原因

失败的部署任务通过 `appleboy/ssh-action@v1.0.3` 把 YAML 中的 `script: |` 直接交给远程 Bash。只要脚本被中文智能引号、全角括号、翻译后的 Shell 关键字或中文 Python 关键字污染，远程 Bash/Python 就会在执行前产生 `syntax error: invalid syntax`。

检查最新 `main` 后，当前 4 个 Appleboy SSH 脚本块已经全部为 ASCII，没有继续发现中文污染字符。这说明可见污染已在后续提交中被清理，但仓库此前没有自动防护，未来仍可能再次发生。

## 2. 修改文件

- `.github/scripts/check_workflow_scripts.py`
- `.github/workflows/workflow-script-guard.yml`
- `.github/workflows/deploy-ai-replenishment.yml`
- `.github/workflows/deploy-cloud.yml`
- `.github/workflows/deploy.yml`
- `GITHUB_ACTIONS_REPAIR_REPORT.md`

## 3. 修复内容

### 3.1 部署前检查

所有包含 `appleboy/ssh-action@v1.0.3` 的部署流程，在执行 SSH 前运行统一检查器。

检查内容：

- 中文智能双引号和单引号
- 全角括号
- 中文 Shell 关键字
- 中文 Python 关键字
- SSH `script: |` 中的所有非 ASCII 字符
- Bash 语法
- Python heredoc 是否闭合
- Python heredoc 是否能通过标准 Python 编译
- Appleboy SSH Action 与脚本块数量是否一致

### 3.2 PR 防护

新增 `Workflow Script Guard`：

- 修改 workflow 或检查器时自动运行。
- Pull Request 阶段运行，不等到生产部署才发现错误。
- 合并到 `main` 后再次运行。
- 支持手工触发。

### 3.3 安全边界

- 没有修改 SAP。
- 没有增加 SAP 权限。
- 没有修改 Core 数据。
- 没有修改服务器配置或生产服务。
- 本次只修改 GitHub Actions workflow、检查器和报告。

## 4. 本地测试结果

| 测试 | 结果 |
|---|---|
| 扫描全部 workflow | 通过 |
| 识别 Appleboy SSH Action | 4 个 |
| 识别 SSH script 块 | 4 个 |
| Bash `-n` 语法检查 | 通过 |
| Core Python heredoc 编译 | 通过 |
| AI Python heredoc 编译 | 通过 |
| 检查器自身 Python 编译 | 通过 |
| 中文智能引号反向测试 | 正确阻断 |
| 中文关键字反向测试 | 正确阻断 |
| 非 ASCII 脚本反向测试 | 正确阻断 |
| 错误 Python heredoc 反向测试 | 正确阻断 |
| `git diff --check` | 通过 |

## 5. GitHub 与生产验证状态

PR 创建后，`Workflow Script Guard` 可在分支上直接验证。

以下项目必须在 PR 合并到 `main` 后，由生产部署 workflow 验证：

1. Appleboy SSH Action 成功。
2. 远程部署脚本成功。
3. `http://127.0.0.1:8090/healthz` 返回 200。
4. `foxbrain-core-api.service` 状态正常。
5. Core API 生产备份成功。

在实际 Actions 运行完成前，本报告不提前把这些项目标记为通过。

## 6. 后续防护

- 所有远程脚本继续只使用 ASCII。
- 任何 Python heredoc 必须由检查器编译。
- 任何 workflow 修改必须先通过 `Workflow Script Guard`。
- 生产部署仍保持串行，不并发覆盖 Core/AI release。
- GitHub Secrets 继续只通过环境变量传入，不写入仓库。
