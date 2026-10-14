# Server-test mode

Apply this reference only when the resolved role is `server-test` or the user explicitly asks for test execution against a running server.

## Default boundary

The testing agent may inspect application code, configuration, logs, current diffs, and test data needed to understand behavior. It may create or update test artifacts, scripts, progress, and evidence within the user's stated scope. Application fixes require a separate explicit request; diagnosing a failure alone does not authorize changing production code.

Use this evidence directory unless the existing checkpoint names another one:

`.agent/test-evidence/<progress-key>/`

## Safe sequence

Choose only the stages relevant to the objective:

1. Confirm environment identity, target, credentials source, allowed data mutations, and success criteria.
2. Run environment and dependency preflight.
3. Run a small smoke test before broader functional tests.
4. Execute one coherent test group at a time.
5. Cover relevant negative, boundary, authorization, consistency, and regression cases.
6. Run load, stress, destructive, failover, or production-impacting tests only with explicit authorization and stopping conditions.

Do not proceed with data-changing or disruptive tests when the environment is unknown. Never clear databases, alter production data, restart unknown services, or reuse real-user data merely to make a test possible.

## Evidence per test group

Record enough information to reproduce and evaluate the result:

- Environment and version or revision
- Preconditions and test data identifier
- Command, request, or interaction
- Expected result
- Observed result
- Status: `passed`, `failed`, `blocked`, or `skipped`
- Relevant response, logs, database observation, screenshot, or artifact path
- Cleanup status

An HTTP success status alone is not proof of business success. Validate the response contract and any relevant state transition.

## Failure handling

Before proposing a fix:

1. Reproduce the failure when safe.
2. Preserve the smallest useful request, response, log, and state evidence.
3. Classify it as environment, test harness, data, dependency, or application behavior.
4. Record a minimal reproduction and the next diagnostic action.

After an authorized fix, rerun the affected test and the smallest meaningful regression set. Do not restart the entire suite unless the change impact justifies it.
