---
name: develop
description: Iterative loop of implement → run-tests → check-adherence until all acceptance criteria pass and the implementation matches the plan.
---

# Skill: develop

Use this skill after `create-tests` has produced test files for a feature. It runs the tight feedback loop of implementing, testing, and verifying until the feature is complete.

## Usage

```
Load skill develop for "add user authentication" (tests written)
```

## Workflow

### Step 1: Load implement

Load the **implement** skill and follow its workflow to write production code.

### Step 2: Load run-tests

Load the **run-tests** skill to execute the full test suite.

### Step 3: Evaluate

- If all tests pass → proceed to Step 4.
- If any tests fail → go back to Step 1 (implement fixes), then re-run tests.

### Step 4: Load check-adherence

Load the **check-adherence** skill to verify the implementation matches the plan.

### Step 5: Evaluate

- If PASS → feature is complete. Report success.
- If FAIL → go back to Step 1 with the specific issues to fix.

### Keep a counter

Track the iteration number. If the loop exceeds 5 iterations, stop and ask the user for guidance:

```
Iteration <N>: still failing on <reason>. Suggest a different approach?
```

## Rules

- Run the full test suite every time, not just the feature's tests
- Each iteration must make progress — if two consecutive iterations do not reduce failures, raise it with the user
- Do NOT modify test files or the feature plan during this loop
- If the plan is discovered to be incorrect during implementation, stop and ask the user
