---
name: project-checkpoint
description: Manage long-running project work through role-isolated progress files and evidence-backed checkpoints. Use when the user asks an agent to start, resume, continue, or hand off a coding or testing task incrementally across chats, especially after naming a role such as frontend, backend, or server test. Do not use for quick one-turn questions that do not benefit from persistent project state.
---

# Project Checkpoint

Turn the user's role and objective into a durable, resumable project workflow. Treat repository files as persistent memory and the chat as temporary context.

## How to invoke

Load this SKILL.md using the host tool's skill mechanism, or ask the agent to read this file and follow it. `$project-checkpoint` below is shorthand only for hosts that support it; it is not a universal command. Then state the role and task in ordinary language.

Use this minimal pattern:

```text
$project-checkpoint 你是【角色】，负责【具体任务】。
```

Examples:

```text
$project-checkpoint 你是前端，负责会员中心页面开发。
$project-checkpoint 你是后端，负责订单接口和数据库逻辑。
$project-checkpoint 你是服务器测试，负责测试落地和回归验证，默认不修改业务代码。
```

To separate multiple active tasks owned by the same role, add a stable task ID:

```text
$project-checkpoint 你是前端，TASK_ID=member-center，负责会员中心改版。
```

To continue in a fresh chat, open the same local workspace/worktree and invoke the same role and task ID or objective:

```text
$project-checkpoint 你是前端，TASK_ID=member-center，继续之前的任务。
```

The old transcript is optional. Recover from the matching progress file, current Git state, and referenced evidence. If the user invokes the skill with only a role and no usable objective, ask for the objective once. If an existing role checkpoint has a different active objective, ask whether to resume it or use a task ID.

Expected behavior after invocation:

1. Resolve the role, objective, and optional task ID.
2. Select a role-isolated progress file.
3. Resume from that checkpoint when it exists; otherwise initialize it after minimal discovery.
4. Work one verifiable step at a time and keep the checkpoint current.
5. Report the progress path and single next action on every handoff.

Do not use this workflow for a quick explanation, one-off review, or other task that has no useful persistent state.

## Establish the task identity

Extract these inputs from the invocation:

- **Role**: what this chat is responsible for.
- **Objective**: the concrete outcome it should achieve.
- **Task ID**: optional stable identifier supplied by the user.
- **Completion evidence**: tests, checks, or artifacts that prove success when stated.

If role or objective is genuinely missing, ask one concise question before writing files. Do not scan the repository broadly just to guess them.

Normalize common roles as follows:

| User wording | Role key | Default boundary |
| --- | --- | --- |
| 前端, frontend | `frontend` | UI, components, styles, client state, client API adapters, frontend tests |
| 后端, backend, API | `backend` | server code, APIs, data access, migrations, auth, backend tests |
| 服务器测试, 测试落地, server test | `server-test` | test planning, execution, evidence, reproduction, regression; application code is read-only unless a fix is explicitly requested |
| Other clear role | concise lowercase kebab-case | derive the narrowest boundary from the user's objective |

Use the role key as the progress key unless the user supplies a task ID. With a task ID, use `<role-key>-<task-id>`. Sanitize path separators and reserved filename characters; do not invent opaque IDs.

Reuse an existing project checkpoint directory when configured. Otherwise the progress file is:

`.agent/progress/<progress-key>.md`

If the default role file already exists but its active scope materially differs from the new objective, do not overwrite it. Ask whether to resume it or use a short task ID.

## Start or resume

First determine whether the progress file exists.

### Existing checkpoint

Recover with the smallest useful read set:

1. Read the matching progress file.
2. Read `git status --short` when this is a Git repository.
3. Inspect only diffs and files named by the current checkpoint or needed for its next action.
4. Read only the newest relevant evidence referenced by the checkpoint.
5. Validate that claimed completed work still exists; record inconsistencies instead of resetting the task.
6. Summarize the recovered state in at most 10 lines, then execute only the recorded next action.

Do not redo project-wide discovery, regenerate the whole plan, or rerun unchanged passing checks. Expand discovery only when the checkpoint is missing required facts or the repository has materially changed; state the reason first.

### New checkpoint

Perform one minimal discovery pass limited to the stated role and objective. Identify acceptance evidence and the first small action, then create the progress file using [references/progress-format.md](references/progress-format.md). Do not front-load a speculative full-project plan.

For a `server-test` role, also read and follow [references/server-test.md](references/server-test.md) before executing tests.

## Work incrementally

- Keep exactly one **next action** in the active checkpoint.
- Prefer a step that can be implemented and verified before moving on.
- Update the checkpoint after a meaningful code change, completed test group, decision, discovered blocker, or interruption point.
- Record observed evidence, commands, results, and affected files. Do not mark assumptions as completed work.
- Preserve existing user and other-agent changes. Inspect relevant diffs before editing shared files; never revert unrelated work.
- Write only this task's progress file. Other `.agent/progress/*.md` files are read-only unless the user explicitly changes this task's ownership.
- Record cross-role needs under coordination items rather than silently taking over another role's work.
- A new worktree does not inherit uncommitted changes from another checkout. When resuming, verify that the current workspace/worktree contains the expected checkpoint and diff.

This skill does not authorize deployments, production changes, destructive data operations, credential use, commits, pushes, or other external mutations. Obtain the authorization those actions normally require.

## Finish and hand off

Mark the task complete only when its stated objective and verification criteria are actually satisfied. A turn ending, a service interruption, or a nearly exhausted context window is not completion.

At each handoff or final response, report:

```text
角色：<role-key>
任务：<task-id or role-key>
当前阶段：
本轮完成：
当前阻塞：
下一步唯一动作：
进度文件：.agent/progress/<progress-key>.md
```

In a fresh chat, invoking `$project-checkpoint` with the same role and objective should recover from this file, current repository state, and referenced evidence rather than requiring the old transcript.
