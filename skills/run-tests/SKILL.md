---
name: run-tests
description: Executes the project's test runner and reports results in a structured format.
---

# Skill: run-tests

Use this skill inside the **develop** loop after `implement` or whenever test results are needed. It runs the test suite and returns a clear pass/fail summary with details on failures.

## Usage

```
Load skill run-tests for "add user authentication"
```

## Workflow

### Step 1: Determine the test command

Check `AGENTS.md`, `package.json`, or the project's test configuration for the correct runner and flags. Common commands:

- Node/TS: `npm test`, `npx vitest run`, `npx jest`
- Python: `pytest`, `python -m pytest`
- Go: `go test ./...`
- Rust: `cargo test`

### Step 2: Run tests

Execute the test command. Capture the full output.

### Step 3: Report results

Summarise in a structured format:

```
Test results for <feature>:
- Total: <N>
- Passed: <N>
- Failed: <N>
- Skipped: <N>

Failures:
1. test name — error message (file:line)
2. test name — error message (file:line)
```

## Rules

- Always run the full test suite, not just the feature's tests, to catch regressions
- If tests fail, report the failure clearly — do not attempt to fix within this skill; let **develop** or the user decide next steps
- If the test command fails to run (missing deps, config error), report the error and stop
