# VAFOX Control Plane Phase 2 Foundation 执行前检查清单

> **文档性质：强制执行前门禁检查清单。** 本文只用于记录核验、审批与放行结论；**不包含服务器操作，不授权或执行任何服务器变更。**

| 项目 | 内容 |
| --- | --- |
| 目标服务器 | `control.vafox.com` |
| 公网 IP | `114.132.55.178` |
| 内网 IP | `172.16.16.6` |
| Artifact | `VAFOX_CONTROL_PLANE_PHASE2_FOUNDATION_ARTIFACT v1.0` |
| 当前审批 | **Approved with Conditions** |
| 门禁结论 | `{{未检查 / 通过 / 不通过}}` |
| 变更/审批引用 | `{{CHANGE_AND_APPROVAL_REFERENCE}}` |
| 核验时间（UTC） | `{{UTC}}` |
| 核验人 | `{{REVIEWER}}` |

## 使用规则

- [ ] 每个适用项目均已填写结果、证据引用、责任人和 UTC 时间。
- [ ] 任一项目不通过、证据缺失、审批过期或执行范围不一致时，停止放行，不得进入执行。
- [ ] 不在本清单中记录密码、私钥、Token、恢复密钥或其他明文 Secret；仅记录受控引用。
- [ ] 本清单全部通过前，审批状态保持 **Approved with Conditions**，不得标记为 **Executing**。

## 一、Phase 1 状态确认

| 检查项 | 必须确认 | 结果 | 证据/记录引用 | 确认人/时间（UTC） |
| --- | --- | --- | --- | --- |
| Phase 1 Security Hardening | 状态为 **Completed**。 | `{{PASS / FAIL}}` | `{{EVIDENCE}}` | `{{OWNER_UTC}}` |
| SSH 安全 | 已完成；仅允许批准的安全访问方式，且无未批准例外。 | `{{PASS / FAIL}}` | `{{EVIDENCE}}` | `{{OWNER_UTC}}` |
| UFW | 已完成并处于批准的安全基线状态。 | `{{PASS / FAIL}}` | `{{EVIDENCE}}` | `{{OWNER_UTC}}` |
| Fail2Ban | 已完成并处于运行/受控状态。 | `{{PASS / FAIL}}` | `{{EVIDENCE}}` | `{{OWNER_UTC}}` |
| 验收报告 | Phase 1 验收报告存在、可访问且与目标服务器对应。 | `{{PASS / FAIL}}` | `{{ACCEPTANCE_REPORT_REFERENCE}}` | `{{OWNER_UTC}}` |

## 二、执行前备份门禁

### 备份完整性确认

| 备份类别 | 必须确认 | 结果 | 备份位置 | 备份时间（UTC） | 恢复方式/证据 |
| --- | --- | --- | --- | --- | --- |
| 系统状态备份 | 当前系统状态已生成受控备份，且可读取/校验。 | `{{PASS / FAIL}}` | `{{BACKUP_LOCATION}}` | `{{UTC}}` | `{{RESTORE_METHOD_REFERENCE}}` |
| 软件包状态备份 | 已记录当前软件包与版本状态，且可用于恢复核对。 | `{{PASS / FAIL}}` | `{{BACKUP_LOCATION}}` | `{{UTC}}` | `{{RESTORE_METHOD_REFERENCE}}` |
| 配置备份 | 已备份相关非敏感配置与配置引用；不含明文 Secret。 | `{{PASS / FAIL}}` | `{{BACKUP_LOCATION}}` | `{{UTC}}` | `{{RESTORE_METHOD_REFERENCE}}` |
| 网络配置备份 | 已备份批准的网络、防火墙与相关配置状态。 | `{{PASS / FAIL}}` | `{{BACKUP_LOCATION}}` | `{{UTC}}` | `{{RESTORE_METHOD_REFERENCE}}` |

- [ ] 备份位置为经批准的受控位置，且不只保留在目标主机。
- [ ] 每份备份均有创建时间、来源、完整性校验和保留期限记录。
- [ ] 恢复方式已经责任人确认，恢复所需权限与受控密钥引用可用。
- [ ] 备份读取或恢复验证通过；仅“备份已生成”不视为通过。

## 三、Docker 版本门禁

| 目标 | 推荐/批准版本 | 兼容性确认 | 镜像策略 | 结果 | 证据/确认人/时间（UTC） |
| --- | --- | --- | --- | --- | --- |
| Docker Engine | `{{APPROVED_ENGINE_VERSION}}` | 与目标操作系统、批准 Compose 版本及运行边界兼容。 | 使用批准来源、固定版本；不使用浮动版本。 | `{{PASS / FAIL}}` | `{{EVIDENCE_OWNER_UTC}}` |
| Docker Compose | `{{APPROVED_COMPOSE_V2_VERSION}}` | 与批准 Docker Engine、Compose 定义和部署模型兼容。 | Compose 定义纳入版本控制；镜像以不可变 digest 或经批准的固定 tag 管理。 | `{{PASS / FAIL}}` | `{{EVIDENCE_OWNER_UTC}}` |

- [ ] Docker Engine 与 Docker Compose 的推荐版本、来源和兼容性已获审批。
- [ ] 镜像来源、所有权、版本/digest、扫描或例外结论已记录并获批准。
- [ ] 不使用 `latest` 或其他浮动镜像标签；不使用未审查安装脚本或镜像来源。

## 四、回滚点确认

**失败时必须能够恢复以下范围：**

| 回滚范围 | 已定义恢复目标与来源 | 结果 | 责任人 | 回滚路径/证据 |
| --- | --- | --- | --- | --- |
| Docker 环境 | 恢复至上一批准的稳定 Docker/Compose 环境与版本清单。 | `{{PASS / FAIL}}` | `{{ROLLBACK_OWNER}}` | `{{ROLLBACK_PATH_REFERENCE}}` |
| 配置 | 恢复至变更前的批准配置快照及 Secret 引用版本。 | `{{PASS / FAIL}}` | `{{ROLLBACK_OWNER}}` | `{{ROLLBACK_PATH_REFERENCE}}` |
| 目录 | 恢复本次范围内的目录结构、属主与最小权限。 | `{{PASS / FAIL}}` | `{{ROLLBACK_OWNER}}` | `{{ROLLBACK_PATH_REFERENCE}}` |
| 服务 | 恢复本次范围内的服务状态或停止异常变更，保留诊断证据。 | `{{PASS / FAIL}}` | `{{ROLLBACK_OWNER}}` | `{{ROLLBACK_PATH_REFERENCE}}` |

- [ ] 回滚责任人已明确、可联系且接受职责。
- [ ] 回滚路径已明确，包括触发条件、恢复来源、验证标准和升级路径。
- [ ] 回滚不会以降低 SSH、UFW、Fail2Ban、审计或 Secret 管理控制作为捷径。

## 五、执行范围确认

### 允许范围

- [ ] Docker 基础环境。
- [ ] Docker Compose。
- [ ] `/opt/vafox-control` 初始化。
- [ ] 日志目录。
- [ ] 备份目录。

### 禁止范围

- [ ] 不部署 Agent Hub。
- [ ] 不正式部署 Dashboard。
- [ ] 不接入 CEO Agent。
- [ ] 不修改 Huyan。
- [ ] 不修改 AI。
- [ ] 不修改 Core。
- [ ] 不访问 SAP。
- [ ] 不进行数据库业务操作。

| 范围核验 | 结果 | 证据/确认人/时间（UTC） |
| --- | --- | --- |
| 允许范围与已批准变更单完全一致。 | `{{PASS / FAIL}}` | `{{EVIDENCE_OWNER_UTC}}` |
| 禁止范围已向执行人、复核人和回滚责任人确认。 | `{{PASS / FAIL}}` | `{{EVIDENCE_OWNER_UTC}}` |

## 六、执行顺序

> 仅在全部执行前门禁通过、处于已批准窗口且获得正式放行后，才可按以下顺序开展受控执行。

| 顺序 | 步骤 | 前置/完成确认 | 结果 | 执行记录引用 |
| ---: | --- | --- | --- | --- |
| 1 | 备份 | 本清单第二部分全部通过。 | `{{PENDING / PASS / FAIL}}` | `{{EXECUTION_REFERENCE}}` |
| 2 | Docker 安装 | 备份、版本门禁和范围确认通过。 | `{{PENDING / PASS / FAIL}}` | `{{EXECUTION_REFERENCE}}` |
| 3 | Docker 验证 | Docker Engine、Compose、来源与版本符合批准清单。 | `{{PENDING / PASS / FAIL}}` | `{{EXECUTION_REFERENCE}}` |
| 4 | 目录初始化 | 仅初始化批准的 `/opt/vafox-control`、日志及备份目录。 | `{{PENDING / PASS / FAIL}}` | `{{EXECUTION_REFERENCE}}` |
| 5 | 权限设置 | 最小权限、属主和可写边界符合批准方案。 | `{{PENDING / PASS / FAIL}}` | `{{EXECUTION_REFERENCE}}` |
| 6 | 日志配置 | 日志目录、轮转、访问控制与审计边界完成验证。 | `{{PENDING / PASS / FAIL}}` | `{{EXECUTION_REFERENCE}}` |
| 7 | 验收 | 本清单第七部分全部通过并完成独立复核。 | `{{PENDING / PASS / FAIL}}` | `{{EXECUTION_REFERENCE}}` |

## 七、验收标准

| 验收域 | 通过标准 | 结果 | 证据/复核人/时间（UTC） |
| --- | --- | --- | --- |
| Docker 状态 | Docker Engine 与 Docker Compose 已按批准版本安装/验证；版本、运行状态和基础安全边界符合批准清单。 | `{{PASS / FAIL}}` | `{{EVIDENCE_REVIEWER_UTC}}` |
| 目录状态 | 批准目录完整；不存在范围外目录变更、业务数据操作或明文 Secret。 | `{{PASS / FAIL}}` | `{{EVIDENCE_REVIEWER_UTC}}` |
| 权限状态 | 目录属主、访问权限和写入边界符合最小权限要求；无不必要的 root 日常运行或宽泛可写权限。 | `{{PASS / FAIL}}` | `{{EVIDENCE_REVIEWER_UTC}}` |
| 日志状态 | 日志目录可用，访问控制、轮转/保留与审计要求已验证；日志不含明文 Secret。 | `{{PASS / FAIL}}` | `{{EVIDENCE_REVIEWER_UTC}}` |
| 备份状态 | 系统、软件包、配置和网络配置备份均可读、可校验、位置受控，恢复方式可用。 | `{{PASS / FAIL}}` | `{{EVIDENCE_REVIEWER_UTC}}` |

## 八、执行报告要求

- [ ] 执行完成后生成 `VAFOX_CONTROL_PLANE_PHASE2_FOUNDATION_ACCEPTANCE_REPORT.md`。
- [ ] 报告包含执行时间。
- [ ] 报告包含执行人。
- [ ] 报告包含 Artifact 版本：`VAFOX_CONTROL_PLANE_PHASE2_FOUNDATION_ARTIFACT v1.0`。
- [ ] 报告包含执行内容。
- [ ] 报告包含验证结果。
- [ ] 报告包含异常；如无异常，明确记录“无”。
- [ ] 报告包含回滚情况；如未回滚，明确记录“未触发”。
- [ ] 报告已关联审批、备份、验证与回滚证据引用，并完成独立复核。

## 九、最终放行条件

| 最终条件 | 结果 | 确认人/时间（UTC） | 证据/记录引用 |
| --- | --- | --- | --- |
| 第一至第八部分所有适用项目均通过。 | `{{PASS / FAIL}}` | `{{OWNER_UTC}}` | `{{EVIDENCE}}` |
| 无未解决异常、无未批准例外、无范围偏离。 | `{{PASS / FAIL}}` | `{{OWNER_UTC}}` | `{{EVIDENCE}}` |
| 回滚责任人、回滚路径和可用备份均已确认。 | `{{PASS / FAIL}}` | `{{OWNER_UTC}}` | `{{EVIDENCE}}` |
| 执行报告要求、执行窗口和责任分工均已确认。 | `{{PASS / FAIL}}` | `{{OWNER_UTC}}` | `{{EVIDENCE}}` |

```text
Approved with Conditions
          ↓
    （全部通过）
          ↓
      Executing
```

- [ ] **最终放行：** 仅当全部最终条件通过并由批准责任人签署后，状态可由 **Approved with Conditions** 变更为 **Executing**。
- [ ] **未放行：** 任一最终条件不通过时，保持 **Approved with Conditions** 或退回审批流程；不得执行。

| 角色 | 姓名/标识 | 放行结论 | 时间（UTC） | 审批/记录引用 |
| --- | --- | --- | --- | --- |
| 执行负责人 | `{{EXECUTION_OWNER}}` | `{{APPROVE / HOLD}}` | `{{UTC}}` | `{{REFERENCE}}` |
| 回滚责任人 | `{{ROLLBACK_OWNER}}` | `{{APPROVE / HOLD}}` | `{{UTC}}` | `{{REFERENCE}}` |
| 独立复核人 | `{{REVIEWER}}` | `{{APPROVE / HOLD}}` | `{{UTC}}` | `{{REFERENCE}}` |
| 审批责任人 | `{{APPROVER}}` | `{{APPROVE / HOLD}}` | `{{UTC}}` | `{{REFERENCE}}` |
