---
name: dev-task
description: The core development loop for any coding task — feature, bug fix, or refactor. Use when the user gives a development task in an initialised repo. Gathers context from the AST knowledge base, proposes test cases with edge cases, gates on user confirmation, then develops/tests iteratively and finishes with a commit and PR.
---

# Dev Task

Requires an initialised repo (`.agentic/env.json` and `.agentic/kb/` exist —
if not, run the `initialise` skill first). All commands come from
`.agentic/env.json`; never guess build/test commands.

There are exactly **two confirmation gates**: the test plan, and the PR.
Everything between them runs autonomously.

## 1. Receive the task

Restate the task in one or two sentences. If the goal or scope is ambiguous,
ask targeted questions now — not later.

## 2. Gather relevant information

Use the knowledge base before reading files wholesale:

```sh
python .agentic/scripts/kb_query.py search <regex>     # find related symbols
python .agentic/scripts/kb_query.py symbol <name>      # definition + location
python .agentic/scripts/kb_query.py callers <name>     # impact analysis
python .agentic/scripts/kb_query.py imports <path>     # dependency direction
```

Also check `.agentic/kb/notes/` for relevant decisions/constraints, and
`.agentic/kb/modules/` for a structural map of unfamiliar areas. Then read
only the specific line ranges the KB points at. Summarise findings: affected
files, symbols, callers that could break.

## 3. Propose tests — GATE 1

Draft the test plan before writing any implementation:

- Happy-path cases derived from the task
- Edge cases: empty/null inputs, boundaries, invalid types, error paths,
  concurrency/ordering where relevant, and regressions for callers found in
  step 2
- For each case: name, what it asserts, and which file it lives in (follow
  the project's existing test layout and framework from env.json conventions)

Present the plan and **wait for user confirmation**. Incorporate corrections;
re-confirm only if the plan changed materially.

## 4. Develop–test loop

1. Write the agreed tests (they should fail meaningfully first)
2. Implement the change
3. Run the focused tests: `test_single` from env.json with `{path}` substituted
4. On failure: diagnose, fix, rerun. If the *plan* turns out to be wrong
   (not just the code), say so and return to gate 1 with a revised plan
5. When focused tests pass, run the full suite (`test`), plus `lint` /
   `typecheck` / `format` if defined
6. Refresh the KB for every touched source file:
   `python .agentic/scripts/kb_build.py --paths <files>`
7. If the task surfaced durable knowledge (decisions, gotchas), record it via
   the `ingest` skill (notes)

## 5. Commit and PR — GATE 2

- Branch: create one if on the default branch (`<type>/<short-slug>`)
- Stage only intended files (implementation, tests, KB updates, notes);
  review `git status` and `git diff` first
- Commit following env.json `conventions.commit_style`
- Present to the user: branch name, commit summary, diff stats, and the
  proposed PR title/description (task summary, test cases added, KB updates).
  **Wait for confirmation.**
- On confirmation: push and open the PR with `gh pr create` against the base
  branch from env.json. Return the PR URL.

The `agentic.yml` workflow then builds, tests, and refreshes the KB on merge —
do not manually rebuild the full KB as part of the PR.
