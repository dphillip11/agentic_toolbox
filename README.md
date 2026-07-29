# Agentic Toolbox

A portable set of tools for AI-assisted development that can be dropped into
any codebase, regardless of language or stack. It gives a coding agent three
things it usually lacks:

1. **An environment manifest** (`.agentic/env.json`) — the project's real
   build/run/test/lint commands, gathered by interviewing you once.
2. **An AST-derived knowledge base** (`.agentic/kb/`) — every source file
   decomposed into atomic elements (functions, classes, methods, imports,
   call references) via tree-sitter, plus a symbol index, per-module
   summaries, and freeform knowledge notes. Committed to the repo and kept
   fresh by CI.
3. **A disciplined dev loop** — gather context from the KB, propose tests
   (with edge cases), confirm with you, develop/test until green, then
   commit and open a PR.

## Layout

```
.agentic/
  scripts/
    kb_build.py       # build/refresh the knowledge base (tree-sitter)
    kb_query.py       # query it: symbol, file, callers, search, imports, stale, stats
    requirements.txt
  templates/
    env.json          # environment manifest template
    agentic.yml       # GitHub workflow template (build, test, KB refresh on push)
  kb/                 # generated: files/, modules/, notes/, index.json
skills/
  initialise/         # interview -> env.json, full KB build, workflow, AGENTS.md
  ingest/             # ingest new code (AST atoms) or specs/decisions (notes)
  dev-task/           # the dev loop: context -> tests -> confirm -> develop -> PR
install.sh            # copy the toolbox into a target repo
```

## Usage

```sh
./install.sh /path/to/your/repo
```

Then open your agent (opencode) in that repo and say "initialise this repo"
— the `initialise` skill interviews you, indexes the existing codebase, and
generates `.github/workflows/agentic.yml`.

From then on, give it tasks normally; the `dev-task` skill drives the loop:

- **Gather** — queries the KB instead of reading the codebase wholesale
- **Test plan** — proposes test cases and edge cases; *you confirm*
- **Develop** — implement, run focused tests, iterate until the suite is green
- **Ship** — *you confirm* the commit/PR, then it pushes and opens the PR

On merge to the default branch, CI builds, tests, and recompiles changed
files into the knowledge base, committing the update back with `[skip ci]`.

## Language support

Dedicated AST extraction for Python, TypeScript/JavaScript (incl. TSX/JSX),
and C/C++. Go, Rust, Java, Kotlin, Ruby, PHP, C#, Swift, Lua and shell fall
back to a generic extractor. Requires Python 3.10+ and
`pip install -r .agentic/scripts/requirements.txt`.
