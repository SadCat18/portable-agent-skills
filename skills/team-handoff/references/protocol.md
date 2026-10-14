# 协议：事实、存储、权限与通信

这些文件是工作约定，不要求特定 agent 或内建 API。沿用项目已有机制，避免重复维护任务真相。

## 角色和存储

在 TEAM.md 登记角色列表、唯一协调者、职责、工作目录、共享文件映射、通信方式和权限边界。
角色名使用安全的文件名；实际角色数量由项目决定。角色协议不是操作系统权限隔离，也不是文件锁。
例如 coordinator、frontend、backend、tester；也可沿用 SERVER-TEST、MINIPROGRAM-FRONTEND、ADMIN-FRONTEND、BACKEND 四角色。示例不是固定要求。

优先使用已确认的交接根目录，没有现成机制时使用项目内 `.agent-handoff/`：
```text
TEAM.md                       # 长期约定和角色登记
CURRENT.md                    # 有效批次、接管与调度状态
TASKS.md                      # 只有有效协调者维护
working/<ROLE>.md             # 只有该角色维护
stages/<BATCH>/INDEX.md        # 快照索引与全部角色回执
stages/<BATCH>/TASKS.md        # 冻结任务状态
stages/<BATCH>/<ROLE>.md       # 每个实际角色一份
stages/<BATCH>/BOOTSTRAP.md    # 新会话启动入口
receipts/<OPERATION>/<ROLE>.md # 角色回执
```
不同 worktree 或机器须明确同步方式；同一个 HEAD 不代表未提交内容相同。
模板在 `../assets/templates/`，只创建所需文件。替换模板占位符时填事实；未知写明未知及局限。

## 状态和控制权

保存状态：DRAFT → WAITING → SEALED；问题标记 BLOCKED。
CURRENT.md 分开记录 latest_sealed_batch 和 preparing_batch，不能提前用草稿替换有效批次。
接管状态：NOT_STARTED → RESTORING → READY_FOR_CONFIRMATION → ACTIVE；问题标记 BLOCKED。
业务派单状态独立为 PAUSED / ACTIVE。这里暂停代理派单和业务变更，不是关闭正常线上服务。
对在途变更确认安全检查点，正常服务和 Worker 保持运行并记录现场。

旧协调者维护保存；新协调者在确认旧组停派单、相关业务写入停止并有接管授权后接手控制文件。
有现成锁或租约就沿用，不声称 Markdown 登记能技术上杜绝并发。
控制权不明时先解决冲突，不能凭最后写文件的人确定。重入操作续用有效操作编号。
封存文件不可变；纠正说明、接管记录及新进度写在批次外，必要时创建修订批次。

## 事实、代码和证据

用户有效指令决定目标和权限；实际代码、配置与运行结果决定实现状态。
旧聊天、日志和交接是证据来源；冲突记录双方来源、时间和影响。
每项完成附对象、方法、结果、时间、版本/环境与未覆盖范围。未运行写未运行。
编译通过不证明业务正确，服务器可连接不证明部署健康。本轮默认引用已有证据。
记录实际目录、分支或 detached HEAD、commit，以及暂存/未暂存/未跟踪重要改动和归属。
可记录非敏感文件校验值；不记录 .env 内容或带凭据的远程 URL，不把文档当代码备份。
只读 Git 检查避免可选锁、外部 diff/textconv；不自动 fetch、checkout、stash 或导出补丁。

## 通信与任务

只登记工具实际返回的 ID 或已核实人工入口，缺失写未知。
消息带项目、批次/操作、发送与目标角色、类型、任务/检查编号。
共享文件没有监听机制时不能承诺自动接单。人工往返通过只能标记人工链路通过。
HANDOFF_ACK：旧角色保存状态并说明停止写入与后台作业。
READY：新角色读取资料并核对现场，带差异和阻塞。
PING/PONG：相同操作编号及唯一标记真实往返，只证明本次通信。
RESULT：任务结果匹配有效登记和任务编号，验收后更新状态。
旧组迟到结果保留原归属，核对后再决定是否接收。

任务带编号、目标/验收条件、负责角色、依赖、范围、状态、交付物、证据和下一步。
建议状态 TODO / IN_PROGRESS / BLOCKED / READY_FOR_REVIEW / VERIFIED / REWORK / CANCELLED。
执行者声明交付不等于验收通过，提交验证不等于 Git commit/push。
共享代码冲突先明确文件归属或执行顺序，不自动改变 worktree 架构。

## 运维和持久入口

仅当团队确有运维职责时，使用 server-extra.template.md 记录环境、实际版本、服务、迁移、作业、故障和回滚引用。
本地版本不冒充线上版本。配置存在、身份可用、连接成功、服务核实分别记录。
共享资料只存必要逻辑环境名与受限记录引用；真实连接元数据按项目保密要求保存在受限位置。
不保存私钥、密码、Token、完整 SSH 日志，不自动分发凭据或关闭主机密钥校验。
记录了连接入口不意味着获准连接或部署。

项目需要时，可按 agents-snippet.template.md 将角色中立入口加入其实际支持的项目指令文件；AGENTS.md 仅为可选示例。
先检查已有规则并保留原文；入口不代替 BOOTSTRAP，也不是封存完成的必要条件。
