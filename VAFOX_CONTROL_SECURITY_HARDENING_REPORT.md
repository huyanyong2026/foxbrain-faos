# VAFOX Control Plane 第一阶段安全加固执行报告

> **报告模板：** 用于记录已获批的 `VAFOX_CONTROL_SECURITY_HARDENING_ARTIFACT.md` 实施结果。不得在本报告记录密码、私钥、Token、API Key、恢复密钥或任何其他明文 Secret；只记录脱敏证据、指纹、校验和和受控系统引用。

## 一、报告元数据

| 字段 | 填写内容 |
| --- | --- |
| 报告 ID | `{{REPORT_ID}}` |
| 执行状态 | `{{未开始 / 进行中 / 已完成 / 已停止并回滚}}` |
| 目标系统 | `control.vafox.com`（公网 `114.132.55.178`；内网 `172.16.16.6`） |
| 执行时间（UTC） | 开始：`{{START_UTC}}`；结束：`{{END_UTC}}` |
| 执行人 | `{{EXECUTOR_NAME_AND_ACCOUNT}}` |
| 复核人 | `{{REVIEWER_NAME}}` |
| Artifact ID / 版本 | `VAFOX-CTRL-SEC-HARDENING-P1-001` / `{{ARTIFACT_VERSION}}` |
| 变更单 / 审批编号 | `{{CHANGE_AND_APPROVAL_REFERENCE}}` |
| 执行窗口 | `{{APPROVED_UTC_WINDOW}}` |
| 备份与回滚位置 | `{{APPROVED_ENCRYPTED_BACKUP_URI}}` |
| 备份校验和/清单引用 | `{{BACKUP_MANIFEST_AND_CHECKSUM_REFERENCE}}` |

## 二、执行前检查结果

| 检查项 | 结果（通过/失败/不适用） | 时间（UTC） | 证据引用/说明 |
| --- | --- | --- | --- |
| 服务器身份确认 | `{{RESULT}}` | `{{UTC}}` | `{{EVIDENCE}}` |
| SSH 可用与第二会话 | `{{RESULT}}` | `{{UTC}}` | `{{EVIDENCE}}` |
| 当前用户与授权 | `{{RESULT}}` | `{{UTC}}` | `{{EVIDENCE}}` |
| 磁盘空间 | `{{RESULT}}` | `{{UTC}}` | `{{EVIDENCE}}` |
| 网络状态 | `{{RESULT}}` | `{{UTC}}` | `{{EVIDENCE}}` |
| 备份与读取验证 | `{{RESULT}}` | `{{UTC}}` | `{{EVIDENCE}}` |

## 三、修改内容

| 变更域 | 批准的修改内容 | 实际结果 | 配置/证据引用 |
| --- | --- | --- | --- |
| SSH | `{{APPROVED_CHANGE}}` | `{{ACTUAL_RESULT}}` | `{{EVIDENCE_REFERENCE}}` |
| 管理员与 sudo | `{{APPROVED_CHANGE}}` | `{{ACTUAL_RESULT}}` | `{{EVIDENCE_REFERENCE}}` |
| `vafox-exec` | `{{APPROVED_CHANGE}}` | `{{ACTUAL_RESULT}}` | `{{EVIDENCE_REFERENCE}}` |
| UFW | `{{APPROVED_CHANGE}}` | `{{ACTUAL_RESULT}}` | `{{EVIDENCE_REFERENCE}}` |
| 时间同步 | `{{APPROVED_CHANGE}}` | `{{ACTUAL_RESULT}}` | `{{EVIDENCE_REFERENCE}}` |
| 日志与审计 | `{{APPROVED_CHANGE}}` | `{{ACTUAL_RESULT}}` | `{{EVIDENCE_REFERENCE}}` |
| 变更后备份 | `{{APPROVED_CHANGE}}` | `{{ACTUAL_RESULT}}` | `{{EVIDENCE_REFERENCE}}` |

## 四、验证结果

| 验证项 | 预期结果 | 实际结果 | 结论（通过/失败） | 证据引用 |
| --- | --- | --- | --- | --- |
| SSH 状态 | 密钥认证成功；root、密码与键盘交互认证拒绝 | `{{ACTUAL_RESULT}}` | `{{RESULT}}` | `{{EVIDENCE}}` |
| 用户权限 | 管理员最小权限；`vafox-exec` 不可交互登录且无通用 sudo | `{{ACTUAL_RESULT}}` | `{{RESULT}}` | `{{EVIDENCE}}` |
| 防火墙状态 | 默认拒绝入站；仅批准的 22/80/443 规则；SSH 来源受限 | `{{ACTUAL_RESULT}}` | `{{RESULT}}` | `{{EVIDENCE}}` |
| 日志状态 | 时间同步、journald 持久化、认证/sudo/UFW 日志正常 | `{{ACTUAL_RESULT}}` | `{{RESULT}}` | `{{EVIDENCE}}` |
| 审计状态 | 审计服务 active、规则加载、测试事件可检索 | `{{ACTUAL_RESULT}}` | `{{RESULT}}` | `{{EVIDENCE}}` |
| 备份/回滚就绪 | 加密备份校验和匹配且可读取 | `{{ACTUAL_RESULT}}` | `{{RESULT}}` | `{{EVIDENCE}}` |

## 五、异常、例外与处置

| 编号 | 时间（UTC） | 异常/例外 | 影响评估 | 即时处置 | 审批/风险接受引用 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| `{{ID}}` | `{{UTC}}` | `{{DESCRIPTION}}` | `{{IMPACT}}` | `{{ACTION}}` | `{{REFERENCE}}` | `{{OPEN/CLOSED}}` |

## 六、回滚情况

| 字段 | 填写内容 |
| --- | --- |
| 是否触发回滚 | `{{是 / 否}}` |
| 触发时间与原因 | `{{UTC_AND_REASON}}` |
| 回滚范围 | `{{SSH / sudo / UFW / 系统配置 / 无}}` |
| 使用的备份清单/校验和引用 | `{{REFERENCE}}` |
| 回滚后验证结果 | `{{RESULT}}` |
| 遗留风险与后续行动 | `{{FOLLOW_UP}}` |

## 七、安全验收结论

- [ ] **通过：** 所有必需验证均通过，无未批准高风险例外，变更后备份及回滚路径已验证。
- [ ] **有条件通过：** 已取得书面风险接受，且列明责任人、到期日和整改计划。
- [ ] **不通过：** 已停止后续变更并完成/启动回滚；不得宣布目标环境可上线。

| 角色 | 姓名/标识 | 时间（UTC） | 签署/系统记录引用 |
| --- | --- | --- | --- |
| 执行人 | `{{EXECUTOR}}` | `{{UTC}}` | `{{REFERENCE}}` |
| 系统负责人 | `{{SYSTEM_OWNER}}` | `{{UTC}}` | `{{REFERENCE}}` |
| 安全审批人 | `{{SECURITY_APPROVER}}` | `{{UTC}}` | `{{REFERENCE}}` |
| 复核人 | `{{REVIEWER}}` | `{{UTC}}` | `{{REFERENCE}}` |
