# Progress checkpoint format

Read this reference when creating a checkpoint, repairing a malformed checkpoint, or migrating an older shared progress file.

## Required structure

```markdown
OWNER_ROLE: <role-key>
TASK_ID: <task-id or role-key>
STATUS: not_started | in_progress | blocked | complete
SCOPE: <one-sentence responsibility boundary>
EVIDENCE_DIR: <path or none>
LAST_UPDATED: <ISO date/time when available>

## Objective

<Observable outcome>

## Completion criteria

- <Evidence-backed condition>

## Scope boundaries

- In scope: <owned files or responsibilities>
- Out of scope: <work requiring another role or separate authorization>

## Current checkpoint

- Stage:
- Status:
- Last verified action:
- Next action: <exactly one action>
- Verification:

## Completed

- <Result, affected files, and evidence>

## Remaining

- <Unfinished outcome>

## Blockers

- <Cause, needed decision, and resume condition>

## Coordination

- <Cross-role contract or handoff>

## Changed files

- <Path and purpose>

## Verification evidence

- <Command or artifact path and observed result>

## Recovery note

- Interruption point:
- First action after recovery:
```

## Update rules

- Preserve verified history; append or revise the active checkpoint rather than replacing the file wholesale.
- Keep one next action. Split large steps before recording them.
- Pair completion claims with observed evidence. Use `unknown` or a blocker when evidence is unavailable.
- If a command fails, record the failure and the exact safe retry point.
- When a referenced file or result no longer matches the repository, record the drift and reassess only the affected stage.
- Before changing `STATUS` to `complete`, confirm every completion criterion and record the final verification.

## Migrating a shared file

Treat `.agent/progress.md` or another role's progress file as read-only source material:

1. Extract only entries clearly owned by the current role and objective.
2. Validate them against current files, diff, and evidence.
3. Put uncertain entries under blockers or coordination; do not mark them completed.
4. Continue only from the new role-owned progress file.
5. Do not delete or rewrite the old file unless the user separately requests cleanup.
