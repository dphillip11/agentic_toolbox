---
name: implement
description: Writes production code for a feature per the plan, making tests pass while following project conventions.
---

# Skill: implement

Use this skill after `create-tests` has produced the test files. It writes the source code needed to make those tests pass.

## Usage

```
Load skill implement for "add user authentication" (tests written)
```

## Workflow

### Step 1: Read the plan and tests

Re-read the feature plan (acceptance criteria, edge cases, file list) and the test files. Understand exactly what behaviour the implementation must satisfy.

### Step 2: Read existing code

Read neighbouring files and any referenced modules to match style, patterns, and conventions.

### Step 3: Implement

Write the minimum production code needed to satisfy the tests. Follow these priorities:

1. **Correctness** — meets all acceptance criteria
2. **Convention** — matches existing code structure, naming, error handling
3. **Cleanliness** — readable, no dead code, no over-engineering

### Step 4: Run tests

Execute the test runner to confirm tests pass:

```
npm test        # or equivalent
```

If tests fail, debug and fix until they pass.

## Rules

- Write the minimum code to pass the tests — no gold-plating
- Do NOT modify test files during this skill
- If you discover the plan is wrong or incomplete, stop and raise it with the user
- Follow the project's conventions from AGENTS.md (naming, error handling, logging)
- Do NOT commit files — stage only if user explicitly asks
