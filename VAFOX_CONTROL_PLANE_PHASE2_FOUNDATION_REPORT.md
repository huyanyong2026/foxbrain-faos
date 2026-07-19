# VAFOX Control Plane Phase 2 基础环境建设执行报告

> **报告状态：Draft Template。** 本模板用于记录已获批准的受控执行结果；不构成执行授权，也不包含服务器操作指令。所有时间使用 UTC，所有 Secret 必须以受控引用替代，严禁写入明文密码、私钥、Token 或恢复密钥。

## 一、报告 Metadata

| 字段 | 内容 |
| --- | --- |
| Report ID | `{{REPORT_ID}}` |
| 报告状态 | `{{DRAFT / COMPLETED / ROLLED_BACK}}` |
| 关联 Artifact | `VAFOX-CONTROL-PLANE-P2-FOUNDATION-001` |
| Artifact 版本 | `{{ARTIFACT_VERSION}}` |
| 关联变更/审批 | `{{CHANGE_AND_APPROVAL_REFERENCE}}` |
| 目标服务器 | `control.vafox.com`（`114.132.55.178` / `172.16.16.6`） |
| 执行时间 | 开始：`{{START_UTC}}`；结束：`{{END_UTC}}` |
| 执行人 | `{{EXECUTION_OWNER}}` |
| 复核人 | `{{REVIEWER}}` |
| 回滚负责人 | `{{ROLLBACK_OWNER}}` |
| 风险结论 | `{{RISK_CONCLUSION}}` |

## 二、执行前门禁结果

| 检查项 | 结果（通过/失败/不适用） | 证据引用 | 确认人/时间（UTC） |
| --- | --- | --- | --- |
| 服务器身份确认 | `{{RESULT}}` | `{{EVIDENCE}}` | `{{OWNER_UTC}}` |
| Phase 1 安全状态 | `{{RESULT}}` | `{{EVIDENCE}}` | `{{OWNER_UTC}}` |
| 磁盘与网络状态 | `{{RESULT}}` | `{{EVIDENCE}}` | `{{OWNER_UTC}}` |
| SSH 与带外恢复路径 | `{{RESULT}}` | `{{EVIDENCE}}` | `{{OWNER_UTC}}` |
| 备份可读与离机留存 | `{{RESULT}}` | `{{EVIDENCE}}` | `{{OWNER_UTC}}` |
| 版本、镜像与配置批准 | `{{RESULT}}` | `{{EVIDENCE}}` | `{{OWNER_UTC}}` |

## 三、安装内容

| 类别 | 批准内容/版本 | 实际结果 | 版本、digest 或配置引用 | 执行时间（UTC） |
| --- | --- | --- | --- |
| Docker Engine | `{{APPROVED_ENGINE_VERSION}}` | `{{RESULT}}` | `{{REFERENCE}}` | `{{UTC}}` |
| Docker Compose v2 | `{{APPROVED_COMPOSE_VERSION}}` | `{{RESULT}}` | `{{REFERENCE}}` | `{{UTC}}` |
| Docker 网络与权限基线 | `{{APPROVED_POLICY}}` | `{{RESULT}}` | `{{REFERENCE}}` | `{{UTC}}` |
| 标准目录初始化 | `/opt/vafox-control/` 及八个子目录 | `{{RESULT}}` | `{{REFERENCE}}` | `{{UTC}}` |
| Agent Registry | `{{APPROVED_RELEASE}}` | `{{RESULT}}` | `{{REFERENCE}}` | `{{UTC}}` |
| Agent Hub | `{{APPROVED_RELEASE}}` | `{{RESULT}}` | `{{REFERENCE}}` | `{{UTC}}` |
| Approval Center | `{{APPROVED_RELEASE}}` | `{{RESULT}}` | `{{REFERENCE}}` | `{{UTC}}` |
| Report Center | `{{APPROVED_RELEASE}}` | `{{RESULT}}` | `{{REFERENCE}}` | `{{UTC}}` |
| Dashboard Backend | `{{APPROVED_RELEASE}}` | `{{RESULT}}` | `{{REFERENCE}}` | `{{UTC}}` |

## 四、验证结果

| 验证域 | 验证结论 | 证据引用 | 复核人/时间（UTC） |
| --- | --- | --- | --- |
| Docker 状态：版本、健康检查、资源限制、重启策略、网络隔离 | `{{PASS / FAIL}}` | `{{EVIDENCE}}` | `{{REVIEWER_UTC}}` |
| 目录状态：完整性、权限、持久化映射、无明文 Secret | `{{PASS / FAIL}}` | `{{EVIDENCE}}` | `{{REVIEWER_UTC}}` |
| 服务状态：依赖顺序、最小授权闭环、无审批绕过 | `{{PASS / FAIL}}` | `{{EVIDENCE}}` | `{{REVIEWER_UTC}}` |
| 日志状态：Docker、Agent、执行、审计、脱敏、轮转、告警 | `{{PASS / FAIL}}` | `{{EVIDENCE}}` | `{{REVIEWER_UTC}}` |
| 备份状态：配置、Artifact、服务配置、校验、离机副本、读取/恢复验证 | `{{PASS / FAIL}}` | `{{EVIDENCE}}` | `{{REVIEWER_UTC}}` |
| 安全状态：SSH/UFW/Fail2Ban、端口、镜像、权限、Secret | `{{PASS / FAIL}}` | `{{EVIDENCE}}` | `{{REVIEWER_UTC}}` |

## 五、异常与处置

| 编号 | 时间（UTC） | 异常/影响 | 即时处置 | 审批或升级引用 | 当前状态 |
| --- | --- | --- | --- | --- | --- |
| `{{ISSUE_ID}}` | `{{UTC}}` | `{{DESCRIPTION}}` | `{{ACTION}}` | `{{REFERENCE}}` | `{{OPEN / RESOLVED}}` |

> 如无异常，填写“无”；不得删除本节。任何安全、备份、审批、网络、健康检查或数据完整性异常均须记录。

## 六、回滚情况

| 字段 | 内容 |
| --- | --- |
| 是否触发回滚 | `{{YES / NO}}` |
| 触发时间与原因 | `{{UTC_AND_REASON}}` |
| 回滚范围 | `{{DOCKER / CONFIG / DIRECTORY / SERVICE}}` |
| 恢复来源 | `{{APPROVED_BACKUP_URI_OR_RELEASE_REFERENCE}}` |
| 实际恢复步骤摘要 | `{{SANITIZED_SUMMARY}}` |
| 回滚后验证 | `{{RESULT_AND_EVIDENCE}}` |
| 遗留风险/后续行动 | `{{FOLLOW_UP}}` |

## 七、最终结论与签署

| 项目 | 内容 |
| --- | --- |
| 最终结论 | `{{PASS / CONDITIONAL_PASS / FAIL / ROLLED_BACK}}` |
| 未决项与风险接受 | `{{NONE_OR_REFERENCE}}` |
| 后续行动与责任人 | `{{ACTION_OWNER_DUE_DATE}}` |
| Artifact 归档位置 | `{{ARTIFACT_ARCHIVE_REFERENCE}}` |
| 备份清单与校验引用 | `{{BACKUP_MANIFEST_REFERENCE}}` |

| 角色 | 姓名/标识 | 签署结论 | 时间（UTC） | 记录引用 |
| --- | --- | --- | --- | --- |
| 执行负责人 | `{{EXECUTION_OWNER}}` | `{{CONCLUSION}}` | `{{UTC}}` | `{{REFERENCE}}` |
| 独立复核人 | `{{REVIEWER}}` | `{{CONCLUSION}}` | `{{UTC}}` | `{{REFERENCE}}` |
| 系统负责人 | `{{SYSTEM_OWNER}}` | `{{CONCLUSION}}` | `{{UTC}}` | `{{REFERENCE}}` |
| 安全审批人 | `{{SECURITY_APPROVER}}` | `{{CONCLUSION}}` | `{{UTC}}` | `{{REFERENCE}}` |

**完成门禁：** 仅当所有适用验证通过、异常已处置或被正式接受、备份与回滚证据归档且上述签署完成后，方可在受控变更流程中关闭本次执行。
