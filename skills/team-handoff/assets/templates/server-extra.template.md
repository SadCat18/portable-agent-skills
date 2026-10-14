## 运维 / 测试职责专项补充（仅适用角色填写）

### 调度现场

{{已派发任务、执行中任务、已回传待验收、返工、跨端依赖、下一阶段验证顺序；引用任务看板}}

### 环境与部署现场（脱敏）

| 逻辑环境 | 测试 / 生产 | 当前实际版本及证据 | 部署 / 服务 / 日志资料引用 | 核实时间 | 未验证项 |
| --- | --- | --- | --- | --- | --- |
| {{ENV_NAME}} | {{ENV_TYPE}} | {{VERSION_OR_UNKNOWN}} | {{SAFE_REFERENCE}} | {{TIME}} | {{GAPS}} |

- 本地代码与服务器版本的差异：{{DIFFERENCES}}
- 服务/进程/容器与健康检查位置：{{SAFE_SERVICE_INFO}}
- 已执行与待执行的数据库迁移及依据：{{MIGRATIONS}}
- Worker/异步任务、不能重复执行的操作：{{JOBS_AND_NON_IDEMPOTENT_ACTIONS}}
- 已知故障、临时措施、回滚资料位置：{{INCIDENTS_AND_ROLLBACK_REFS}}
- 尚未进行的服务器验证：{{SERVER_GAPS}}

### 安全连接入口

- 受限运维记录位置或由用户安全提供的方式：{{RESTRICTED_OPS_REFERENCE}}
- 本次配置检查 / 权限检查 / 连接检查 / 服务检查的分别状态：{{SEPARATE_CHECK_STATUSES}}
- 新环境还需申请的权限：{{APPROVALS}}
- 凭据未安全持久化或不可用的阻塞：{{CREDENTIAL_BLOCKERS}}

此共享交接段落不填真实私钥、密码、Token、完整 .env；实际地址、用户、端口、Host 别名及私钥路径等需要时放在受限本地记录，不自动进 Git。
