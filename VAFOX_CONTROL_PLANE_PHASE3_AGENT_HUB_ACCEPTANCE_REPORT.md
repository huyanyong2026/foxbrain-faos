# VAFOX Control Plane Phase 3 Agent Hub 验收报告

> **模板状态：Draft。** 本报告仅在 `VAFOX_CONTROL_PLANE_PHASE3_AGENT_HUB_ARTIFACT.md` 已获批准、执行完成并收集证据后填写。未完成审批与验证前，不得标记为通过，不得据此授权生产数据接入或业务自动执行。

## 一、报告 Metadata

| 字段 | 内容 |
| --- | --- |
| 报告 ID | `{{ACCEPTANCE_REPORT_ID}}` |
| 关联 Artifact | `VAFOX-CONTROL-PLANE-P3-AGENT-HUB-001` / `{{ARTIFACT_VERSION}}` |
| 目标服务器 | `control.vafox.com`（已核验公网 IP：`{{VERIFIED_PUBLIC_IP}}`；内网 IP：`{{VERIFIED_PRIVATE_IP}}`） |
| 执行窗口（UTC） | `{{APPROVED_CHANGE_WINDOW_UTC}}` |
| 实际执行时间（UTC） | `{{START_UTC}}` — `{{END_UTC}}` |
| 执行负责人 | `{{EXECUTION_OWNER}}` |
| 独立复核人 | `{{REVIEWER}}` |
| 最终状态 | `{{PASS / FAIL / CONDITIONAL}}` |

## 二、部署状态

| 检查项 | 预期 | 实际结果 | 状态 | 证据引用/复核人 |
| --- | --- | --- | --- | --- |
| 审批门禁 | Artifact Approved、窗口和负责人确认均有效。 | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |
| Hub | 仅加载获批最小组件；无未批准公网暴露。 | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |
| Registry | Schema、状态转换和审计可用。 | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |
| Runtime | 隔离、非 root、资源限制和工具策略符合基线。 | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |
| Reports | 来源认证、脱敏和访问控制可用。 | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |

## 三、Agent 注册

| Agent | Agent ID/版本 | 状态 | 权限级别 | 能力范围 | 注册与审计证据 | 结果 |
| --- | --- | --- | --- | --- | --- | --- |
| health-agent | `{{ID_VERSION}}` | `{{STATUS}}` | `{{L0_L4}}` | `{{CAPABILITY}}` | `{{EVIDENCE}}` | `{{PASS_FAIL}}` |
| connectivity-agent | `{{ID_VERSION}}` | `{{STATUS}}` | `{{L0_L4}}` | `{{CAPABILITY}}` | `{{EVIDENCE}}` | `{{PASS_FAIL}}` |
| report-agent | `{{ID_VERSION}}` | `{{STATUS}}` | `{{L0_L4}}` | `{{CAPABILITY}}` | `{{EVIDENCE}}` | `{{PASS_FAIL}}` |
| data-agent | `{{ID_VERSION}}` | `{{STATUS}}` | `{{L0_L4}}` | `{{CAPABILITY}}` | `{{EVIDENCE}}` | `{{PASS_FAIL}}` |
| ceo-agent | `{{ID_VERSION}}` | `{{STATUS}}` | `{{L0_L4}}` | `{{CAPABILITY}}` | `{{EVIDENCE}}` | `{{PASS_FAIL}}` |

验收要求：每项均为唯一登记的获批版本；默认仅 L0/L1；不存在未注册版本、`latest`、生产连接器、SAP/Core 真实数据路径或业务执行能力。

## 四、权限验证

| 验证域 | 通过标准 | 实际结果 | 状态 | 证据 |
| --- | --- | --- | --- |
| RBAC | 每个服务/Agent 仅持有获批最小角色；管理权不等同执行权。 | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |
| ABAC | 环境、数据分类、目标、时间窗、审批引用和所有者属性不匹配时请求被拒绝。 | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |
| Capability | 能力令牌为显式、短时、受众/资源受限；无通配符或共享静态凭据。 | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |
| 越权拒绝 | L2/L3/L4、未登记 Agent、未批准工具和生产数据访问请求均被安全拒绝并审计。 | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |

## 五、健康检查

| 组件 | Liveness | Readiness | Dependency | 版本/配置一致性 | 状态 | 证据 |
| --- | --- | --- | --- | --- | --- |
| Agent Hub | `{{RESULT}}` | `{{RESULT}}` | `{{RESULT}}` | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |
| Registry | `{{RESULT}}` | `{{RESULT}}` | `{{RESULT}}` | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |
| Runtime | `{{RESULT}}` | `{{RESULT}}` | `{{RESULT}}` | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |
| Reports | `{{RESULT}}` | `{{RESULT}}` | `{{RESULT}}` | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |

## 六、日志状态

| 日志类别 | 通过标准 | 实际结果 | 状态 | 证据 |
| --- | --- | --- | --- |
| Agent/Hub 日志 | 含 UTC、Agent ID、版本、请求关联 ID、结果与错误分类；不含 Secret 或真实 payload。 | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |
| Registry 审计 | 注册、状态/权限变更、拒绝与查询操作可追溯且完整。 | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |
| Runtime 日志 | 隔离策略、工具拒绝、资源/健康事件和版本可追溯。 | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |
| Reports 日志 | 来源身份、完整性、脱敏、访问控制和保留/轮转状态已验证。 | `{{RESULT}}` | `{{PASS_FAIL}}` | `{{EVIDENCE}}` |

## 七、回滚状态

| 回滚域 | 备份/恢复来源 | 读取或演练验证 | 当前状态 | 责任人 | 证据 |
| --- | --- | --- | --- | --- | --- |
| Agent 版本回退 | `{{APPROVED_PREVIOUS_RELEASE}}` | `{{RESULT}}` | `{{READY_USED_NOT_NEEDED}}` | `{{ROLLBACK_OWNER}}` | `{{EVIDENCE}}` |
| Registry 恢复 | `{{REGISTRY_BACKUP_URI}}` | `{{RESULT}}` | `{{READY_USED_NOT_NEEDED}}` | `{{ROLLBACK_OWNER}}` | `{{EVIDENCE}}` |
| 配置恢复 | `{{CONFIG_COMPOSE_BACKUP_URI}}` | `{{RESULT}}` | `{{READY_USED_NOT_NEEDED}}` | `{{ROLLBACK_OWNER}}` | `{{EVIDENCE}}` |

如已实际回滚，补充：触发时间、原因、影响范围、恢复版本、实际步骤、验证结果、遗留风险及后续批准结论：`{{ROLLBACK_DETAILS}}`。

## 八、异常、范围确认与结论

| 项目 | 记录 |
| --- | --- |
| 异常/偏差 | `{{EXCEPTIONS_OR_NONE}}` |
| 生产数据/SAP/Core 真实数据接入确认 | `{{CONFIRM_NONE}}` |
| 自动执行业务操作确认 | `{{CONFIRM_NONE}}` |
| 未注册 Agent 或权限扩大确认 | `{{CONFIRM_NONE}}` |
| 遗留风险与整改计划 | `{{RISKS_AND_ACTIONS}}` |
| 最终验收结论 | `{{FINAL_CONCLUSION}}` |

## 九、签署

| 角色 | 姓名/标识 | 结论 | 时间（UTC） | 签署/记录引用 |
| --- | --- | --- | --- |
| 执行负责人 | `{{EXECUTION_OWNER}}` | `{{CONCLUSION}}` | `{{UTC}}` | `{{REFERENCE}}` |
| 回滚负责人 | `{{ROLLBACK_OWNER}}` | `{{CONCLUSION}}` | `{{UTC}}` | `{{REFERENCE}}` |
| 安全审批人 | `{{SECURITY_APPROVER}}` | `{{CONCLUSION}}` | `{{UTC}}` | `{{REFERENCE}}` |
| 独立复核人 | `{{REVIEWER}}` | `{{CONCLUSION}}` | `{{UTC}}` | `{{REFERENCE}}` |
| 系统负责人 | `{{SYSTEM_OWNER}}` | `{{CONCLUSION}}` | `{{UTC}}` | `{{REFERENCE}}` |

**验收限制：** 即使本报告通过，Phase 3 也只表明 Agent Hub 的受控基础能力通过验收；不授权生产数据、SAP、Core 真实数据接入或任何自动业务操作。上述能力均须另行设计、审批、实施和验收。
