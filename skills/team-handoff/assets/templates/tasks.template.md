# 任务看板 / 阶段任务快照

- 项目标识：{{PROJECT_ID}}
- 看板类型：{{LIVE_OR_SNAPSHOT}}
- 当前批次或接管编号：{{OPERATION_ID}}
- 唯一维护总控：{{CONTROLLER_REF}}
- 记录时间与时区：{{TIME}}

| 任务编号 | 负责角色 | 目标与验收条件 | 状态 | 依赖任务 | 交付物 / 代码路径 | 实际验证证据及缺口 | 下一步 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| {{TASK_ID}} | {{OWNER}} | {{GOAL_AND_ACCEPTANCE}} | {{STATUS}} | {{DEPENDENCIES}} | {{ARTIFACTS}} | {{EVIDENCE}} | {{NEXT}} |

状态约定：TODO / IN_PROGRESS / BLOCKED / READY_FOR_REVIEW / VERIFIED / REWORK / CANCELLED。
区分实现完成、交付总控、本地验证、服务器验证与最终验收。
普通任务回传不等于执行 Git commit；看板状态不代替真实回执。

## 跨端统一约定与阻塞

{{接口字段、协议、共享文件、依赖顺序、需用户确认的动作}}
