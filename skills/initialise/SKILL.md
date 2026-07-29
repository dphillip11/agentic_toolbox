---
name: initialise
description: Initialise the agentic toolbox in a codebase. Use when the user asks to initialise, set up, or bootstrap AI-assisted development in a repo. Interviews the user about build/run/test commands, writes .agentic/env.json, builds the AST knowledge base from the existing codebase, and generates the GitHub workflow.
---

# Initialise

Sets up a codebase for AI-assisted development. Run this once after copying
the toolbox (`.agentic/`, `skills/`, `opencode.jsonc`) into a repo.

## Outputs

1. `.agentic/env.json` — environment manifest (from the interview)
2. `.agentic/kb/` — AST knowledge base for the whole existing codebase
3. `.github/workflows/agentic.yml` — CI: build, test, KB refresh on push to default branch
4. An `AGENTS.md` section pointing agents at the KB and env manifest

## Step 1 — Inspect before you ask

Do not interview blind. First scan the repo to pre-fill answers:

- Detect languages/frameworks (lockfiles, manifests: `package.json`,
  `pyproject.toml`, `CMakeLists.txt`, `Makefile`, `Cargo.toml`, etc.)
- Detect likely commands (`package.json` scripts, Makefile targets, tox/pytest
  config, existing CI workflows)
- Detect source directories and directories to exclude (generated code,
  vendored deps)
- Detect the default branch (`git symbolic-ref refs/remotes/origin/HEAD` or ask)

## Step 2 — Interview the user

Use the question tool. Present detected values as recommended defaults and ask
the user to confirm or correct:

- Setup: commands needed on a fresh clone (installs, codegen)
- Build command (or "no build step")
- Run command (how to start the app locally, if applicable)
- Test command, and the command to run a **single** test file
  (use `{path}` as the placeholder, e.g. `pytest {path}`)
- Lint / format / typecheck commands (optional)
- Source dirs to index and paths to exclude from the KB
- CI runner and setup steps (mirror local setup unless told otherwise)
- Commit/PR conventions (commit style, PR base branch, draft PRs or not)

## Step 3 — Write the manifest

Copy `.agentic/templates/env.json` to `.agentic/env.json` and fill in every
answer. Remove the `$comment` key. Validate that commands actually exist where
cheaply verifiable (e.g. the script names appear in `package.json`).

## Step 4 — Build the knowledge base

```sh
python3 -m venv .agentic/.venv 2>/dev/null || true
.agentic/.venv/bin/pip install -r .agentic/scripts/requirements.txt
.agentic/.venv/bin/python .agentic/scripts/kb_build.py
```

(Plain `pip install` + `python` is fine if the user prefers no venv — ask if
unsure.) Then sanity-check:

```sh
python .agentic/scripts/kb_query.py stats
```

Report file/symbol counts to the user. If a major source dir produced zero
symbols, investigate before continuing.

Ensure `.agentic/.venv/` is in `.gitignore`. The KB itself (`.agentic/kb/`)
**is committed** — do not ignore it.

## Step 5 — Generate the GitHub workflow

Render `.agentic/templates/agentic.yml` to `.github/workflows/agentic.yml`,
replacing:

- `{{PROJECT_NAME}}`, `{{DEFAULT_BRANCH}}`, `{{BUILD_COMMAND}}`, `{{TEST_COMMAND}}`
  directly from env.json (use `true` as the build command if there is no build step)
- `{{SETUP_STEPS}}` with properly indented YAML steps derived from
  `ci.setup_steps` (e.g. `actions/setup-node`, `pip install`, etc.)

Leave the `${{ ... }}` GitHub expressions untouched — only replace the
`{{UPPERCASE}}` tokens.

## Step 6 — Wire up agent context

Create or append to `AGENTS.md` a short section:

- The commands from env.json (build/run/test/test_single/lint)
- How to query the KB: `python .agentic/scripts/kb_query.py {symbol|file|callers|search|imports|stale|stats}`
- Rule: after editing source files, refresh their KB entries with
  `python .agentic/scripts/kb_build.py --paths <files>`
- Rule: for any development task, use the `dev-task` skill; for ingesting new
  code or specs, use the `ingest` skill

## Step 7 — Confirm and commit

Show the user a summary of everything generated. On confirmation, commit:
`chore: initialise agentic toolbox` (include env.json, kb/, workflow, AGENTS.md).
Do not push unless asked.
