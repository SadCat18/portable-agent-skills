# {{HANDOFF_ACK_READY_PONG_RESULT}} 回执

- 项目标识：{{PROJECT_ID}}
- 批次：{{BATCH_ID}}
- 操作编号：{{OPERATION_ID}}
- 消息 / 任务 / 检查编号：{{MESSAGE_OR_TASK_ID}}
- 发送角色：{{ROLE}}
- 实际发送会话入口 / ID：{{SESSION_REF_OR_UNKNOWN}}
- 接收总控入口：{{CONTROLLER_REF}}
- 时间与时区：{{TIME}}
- 实际工作目录 / 分支 / HEAD：{{WORKDIR_BRANCH_HEAD}}
- 交接文件 / 交付物：{{ARTIFACT_PATH}}
- 是否停止业务写入：{{QUIESCENCE}}
- 是否有未处理后台作业：{{RUNNING_JOBS}}
- 状态、检查范围及未解决差异：{{STATUS_AND_GAPS}}
- PING 检查标记原样回传（仅 PONG）：{{NONCE_OR_NOT_APPLICABLE}}
- 实际送达方式及证据 / 未送达原因：{{DELIVERY_EVIDENCE}}

以上由对应角色依据实际状态填写；总控可引用已收到的回复，不可代造其他角色的回执。
