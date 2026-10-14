# 当前交接与调度状态

- 项目标识：{{PROJECT_ID}}
- 更新时间与时区：{{TIME}}
- 最近已封存批次：{{LATEST_SEALED_BATCH_OR_NONE}}
- 准备中批次：{{PREPARING_BATCH_OR_NONE}}
- 接管操作编号：{{TAKEOVER_ID_OR_NONE}}
- 接管状态：{{NOT_STARTED_RESTORING_READY_FOR_CONFIRMATION_ACTIVE_BLOCKED}}
- 派单状态：{{PAUSED_OR_ACTIVE}}
- 唯一控制文件维护者及依据：{{CONTROLLER_AND_EVIDENCE}}
- 旧组安全停靠证据：{{OLD_GROUP_PAUSE_EVIDENCE}}
- 用户恢复授权及适用范围：{{AUTHORIZATION_OR_NOT_YET}}
- 阻塞：{{BLOCKERS_OR_NONE}}

## 旧组登记

{{OLD_SESSIONS_AND_ACK_REFERENCES}}

## 候选 / 当前新组（每个实际角色一行）

| 角色 | 实际会话入口 / ID | 工作目录 | READY 证据 | 往返检查证据 | 自动 / 人工 / 未验证 |
| --- | --- | --- | --- | --- | --- |
| {{ROLE}} | {{REF}} | {{WORKDIR}} | {{READY}} | {{ROUNDTRIP}} | {{MODE}} |

## 控制权交接、纠正与可选运维状态

{{CONTROL_HISTORY_CORRECTIONS_AND_OPS_STATUS}}
