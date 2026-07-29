---
name: initialise
description: Initialise the agentic toolbox in a codebase. Use when the user asks to initialise, set up, or bootstrap AI-assisted development in a repo. Interviews the user about build/run/test commands, writes .agentic/env.json, configures a linter/static analysis if none exists, builds the AST knowledge base from the existing codebase, and generates the GitHub workflow.
---

# Initialise

Sets up a codebase for AI-assisted development. Run this once after copying
the toolbox (`.agentic/`, `skills/`, `opencode.jsonc`) into a repo.

## Outputs

1. `.agentic/env.json` — environment manifest (from the interview)
2. `.agentic/kb/` — AST knowledge base for the whole existing codebase
3. Linter/static-analysis config, if the project lacks one and the user wants it
4. `.github/workflows/agentic.yml` — CI: build, lint, test, KB refresh on push to default branch
5. An `AGENTS.md` section pointing agents at the KB and env manifest

## Step 1 — Inspect before you ask

Do not interview blind. First scan the repo to pre-fill answers:

- Detect languages/frameworks (lockfiles, manifests: `package.json`,
  `pyproject.toml`, `CMakeLists.txt`, `Makefile`, `Cargo.toml`, etc.)
- Detect likely commands (`package.json` scripts, Makefile targets, tox/pytest
  config, existing CI workflows)
- Detect source directories and directories to exclude (generated code,
  vendored deps)
- Detect the default branch (`git symbolic-ref refs/remotes/origin/HEAD` or ask)
- Detect existing linter/static-analysis config (`ruff.toml`/`[tool.ruff]`,
  `.flake8`, `eslint.config.*`/`.eslintrc*`, `biome.json`, `tsconfig.json`,
  `.clang-tidy`, `.clang-format`, `mypy.ini`/`[tool.mypy]`, etc.)

## Step 2 — Interview the user

Use the question tool. Present detected values as recommended defaults and ask
the user to confirm or correct:

- Setup: commands needed on a fresh clone (installs, codegen)
- Build command (or "no build step")
- Run command (how to start the app locally, if applicable)
- Test command, and the command to run a **single** test file
  (use `{path}` as the placeholder, e.g. `pytest {path}`)
- Lint / format / typecheck commands (see step 3 if none exist)
- Source dirs to index and paths to exclude from the KB
- CI runner and setup steps (mirror local setup unless told otherwise)
- Commit/PR conventions (commit style, PR base branch, draft PRs or not)

## Step 3 — Linter / static analysis

The dev loop relies on a fast per-file lint to validate syntax and catch
static errors after every edit, before tests run. If step 1 found existing
linter config, reuse it. If not, offer to set one up (question tool, user may
decline):

| Language | Recommended | lint | lint_single | typecheck |
| --- | --- | --- | --- | --- |
| Python | ruff (+ mypy if typed) | `ruff check .` | `ruff check {path}` | `mypy .` |
| TS/JS | biome (or eslint if ecosystem demands) | `biome check .` | `biome check {path}` | `tsc --noEmit` |
| C/C++ | clang-format + clang-tidy | `clang-tidy` over sources | `clang-tidy {path}` | — |

If the user accepts:

- Install as a dev dependency using the project's package manager
- Generate a **minimal** config (defaults, don't invent style rules) in the
  conventional location
- Run the linter across the codebase once; auto-fix what's safe, report the
  rest — do not go on a refactoring spree
- Note for C/C++: clang-tidy needs `compile_commands.json`
  (`CMAKE_EXPORT_COMPILE_COMMANDS=ON` or bear); skip lint rather than
  half-configure it if the build system can't produce one

Record `lint`, `lint_single` (with `{path}` placeholder), `format`, and
`typecheck` in the manifest. Leave empty only if the user declines.

## Step 4 — Write the manifest

Copy `.agentic/templates/env.json` to `.agentic/env.json` and fill in every
answer. Remove the `$comment` key. Validate that commands actually exist where
cheaply verifiable (e.g. the script names appear in `package.json`).

## Step 5 — Build the knowledge base

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

## Step 6 — Generate the GitHub workflow

Render `.agentic/templates/agentic.yml` to `.github/workflows/agentic.yml`,
replacing:

- `{{PROJECT_NAME}}`, `{{DEFAULT_BRANCH}}`, `{{BUILD_COMMAND}}`, `{{TEST_COMMAND}}`,
  `{{LINT_COMMAND}}` directly from env.json (use `true` for any command the
  project does not have)
- `{{SETUP_STEPS}}` with properly indented YAML steps derived from
  `ci.setup_steps` (e.g. `actions/setup-node`, `pip install`, etc.)

Leave the `${{ ... }}` GitHub expressions untouched — only replace the
`{{UPPERCASE}}` tokens.

## Step 7 — Wire up agent context

Create or append to `AGENTS.md` a short section:

- The commands from env.json (build/run/test/test_single/lint/lint_single)
- Rule: after editing a source file, validate it with `lint_single` (and
  `typecheck` where relevant) before running tests
- How to query the KB: `python .agentic/scripts/kb_query.py {symbol|file|callers|search|imports|stale|stats}`
- Rule: after editing source files, refresh their KB entries with
  `python .agentic/scripts/kb_build.py --paths <files>`
- Rule: for any development task, use the `dev-task` skill; for ingesting new
  code or specs, use the `ingest` skill

## Step 8 — Confirm and commit

Show the user a summary of everything generated. On confirmation, commit:
`chore: initialise agentic toolbox` (include env.json, kb/, workflow,
AGENTS.md, and any new linter config). Do not push unless asked.
