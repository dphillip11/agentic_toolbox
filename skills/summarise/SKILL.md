---
name: summarise
description: Describes what changed during the current session — which features were worked on, what was implemented, and any decisions made.
---

# Skill: summarise

Use this skill at the end of a session or before a commit. It produces a concise summary of the work done, the state of `FEATURES.md`, and any open questions.

## Usage

```
Load skill summarise for "current session"
```

## Workflow

### Step 1: Gather context

- Read `FEATURES.md` to see which features are marked `[DONE]`
- Review `git diff --stat` (or equivalent) for changed files
- Recall from the conversation which decisions were made

### Step 2: Write the summary

```
## Session summary

Date: <date>
Features completed:
- Feature A — <brief what was implemented>
- Feature B — <brief what was implemented>

Features pending:
- Feature C — <next step if known>

Files changed:
- src/feature-a.ts — new file, implements login
- src/feature-b.ts — modified, adds validation

Key decisions:
- Use JWT for auth tokens
- Test framework: Vitest with co-located tests

Open questions:
- Should we add rate limiting to the login endpoint?
```

### Step 3: Present to user

Ask the user to confirm the summary is accurate. Revise if needed.

## Rules

- Keep it brief — one or two lines per feature
- Do NOT include implementation details that don't affect understanding
- If the user wants a commit, prepare the summary as the commit message body
