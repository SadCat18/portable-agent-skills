# {{BATCH_ID}} 交接索引

- 项目标识：{{PROJECT_ID}}
- 保存操作编号：{{OPERATION_ID}}
- 创建 / 封存时间与时区：{{CREATED_AND_SEALED_TIME}}
- 状态：{{DRAFT_WAITING_BLOCKED_SEALED}}
- 发起协调者实际入口：{{OLD_CONTROLLER_REF}}
- 前一封存批次：{{PREVIOUS_BATCH_OR_NONE}}
- 本批次目录：{{BATCH_PATH}}

## 目标与全局摘要

{{GOAL_VERIFIED_SCOPE_LIMITS_AND_NEXT_ACTION}}

## 登记角色交接（按 TEAM.md 全部实际角色展开）

| 角色 | 交接文件 | 实际旧会话入口 | HANDOFF_ACK 证据 | 停止相关业务写入 | 缺口 / 冲突 |
| --- | --- | --- | --- | --- | --- |
| {{ROLE}} | {{ROLE}}.md | {{REF}} | {{ACK}} | {{QUIESCENCE}} | {{GAPS}} |

## 核对证据和能力边界

{{WORKDIR_CODE_TASK_INTERFACE_JOBS_ACCESS_PRIVACY_AND_TRANSPORT_CHECKS}}

## 接手入口

- 任务快照：TASKS.md
- 新会话提示词：BOOTSTRAP.md
- 长期规则和当前状态：{{TEAM_PATH}} / {{CURRENT_PATH}}
- 需要保留的代码现场：{{WORKDIRS}}
- 缺失材料与待验证事项：{{GAPS_OR_NONE}}

缺少任一登记角色回执或关键现场核对时不得标 SEALED。
