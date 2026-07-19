---
name: polish
description: Runs linting, type-checking, and other quality checks across the project. Fixes auto-fixable issues and reports the rest.
---

# Skill: polish

Use this skill after one or more features are complete. It runs all configured quality tools and ensures the project is clean before summarising or preparing for a commit.

## Usage

```
Load skill polish for "current session"
```

## Workflow

### Step 1: Determine quality commands

Check `AGENTS.md`, `package.json`, `tsconfig.json`, `.eslintrc`, etc. for configured quality tools. Common commands:

- Linting: `npm run lint`, `npx eslint .`, `npx prettier --check .`
- Type-checking: `npx tsc --noEmit`, `npx svelte-check`, `mypy .`
- Formatting: `npx prettier --write .`

### Step 2: Run each tool

Run each tool in sequence. For auto-fixable tools (prettier, eslint --fix), run the fix variant first.

### Step 3: Report results

```
Polish report:
- Lint: <pass/fail — details if fail>
- Type-check: <pass/fail — details if fail>
- Format: <pass/fail — details if fail>
- Other: <pass/fail — details if fail>
```

### Step 4: Fix what you can

- Run auto-fix commands (eslint --fix, prettier --write)
- For remaining issues, report them to the user with file paths and line numbers
- Do NOT manually fix issues that require non-trivial refactoring — flag them for the user

## Rules

- Do NOT modify source code logic to satisfy a linter rule without understanding the rule
- If a tool is not configured (e.g. no linter in the project), skip it
- Report the user-facing summary, not raw tool output
