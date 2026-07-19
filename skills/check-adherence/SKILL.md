---
name: check-adherence
description: Verifies that the implementation matches the feature plan — checks that all acceptance criteria are covered and no scope creep has occurred.
---

# Skill: check-adherence

Use this skill inside the **develop** loop after tests pass. It compares the implementation against the original feature plan to ensure nothing is missing and nothing extra was added.

## Usage

```
Load skill check-adherence for "add user authentication" (tests passing)
```

## Workflow

### Step 1: Read the plan

Re-read the feature plan produced by **plan-with-me**: scope, acceptance criteria, edge cases.

### Step 2: Read the implementation

Review the source files that were created or modified. Check:

- Do the files match what was planned?
- Are all acceptance criteria met in code?
- Are all edge cases handled?
- Is there any code that goes beyond the agreed scope?
- Are naming, patterns, and conventions consistent with the rest of the codebase?

### Step 3: Report

```
Adherence report for <feature>:
- Acceptance criteria: <N>/<N> covered
- Edge cases: <N>/<N> handled
- Scope creep: <yes/no — if yes, what?>
- Convention violations: <none or list>
- Verdict: ✅ PASS / ❌ FAIL
```

### Step 4: Act on verdict

- **PASS** — report success. The feature is complete.
- **FAIL** — report specific issues. Do NOT fix them here; return them to the **develop** loop.

## Rules

- Be strict about scope creep — even well-intentioned extra code should be flagged
- If acceptance criteria are vague, ask the user for clarification rather than assuming
- Do NOT modify any files during this check
- If the feature depends on other features, verify those are marked `[DONE]` in FEATURES.md
