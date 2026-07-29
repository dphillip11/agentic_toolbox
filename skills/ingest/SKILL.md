---
name: ingest
description: Ingest new code, specs, or prompts into the knowledge base as atomic elements. Use when new source files are added, when the KB is stale, or when the user supplies requirements/domain knowledge worth persisting. Breaks code into AST symbols via kb_build and captures non-code knowledge as notes.
---

# Ingest

Keeps the knowledge base in sync with reality. Two kinds of input:

## A. Code

For new or modified source files, rebuild just their KB entries:

```sh
python .agentic/scripts/kb_build.py --paths <file> [<file> ...]
```

For anything larger (branch merge, unknown state), check and rebuild:

```sh
python .agentic/scripts/kb_query.py stale
python .agentic/scripts/kb_build.py --since <ref>   # or full: kb_build.py
```

This decomposes each file into its atomic AST elements — functions, classes,
methods, imports, call references — stored under `.agentic/kb/files/`, with
module summaries under `.agentic/kb/modules/` and a global symbol index in
`.agentic/kb/index.json`.

After ingesting, verify with `kb_query.py file <path>` that the symbols you
expect are present.

## B. Prompts, specs, and domain knowledge

Non-code knowledge (requirements, design decisions, constraints, gotchas
learned during a task) goes into `.agentic/kb/notes/` as markdown, one atomic
topic per file:

- Filename: `kebab-case-topic.md`
- Frontmatter: `date`, `source` (user prompt / PR / doc), `related` (list of
  source paths or symbol names it concerns)
- Body: the distilled knowledge — decisions and facts, not conversation
  transcripts. Keep each note under ~40 lines; split rather than bloat.

Before writing a new note, grep existing notes for the topic — update the
existing note instead of duplicating.

## When to run

- A task added/renamed/deleted source files → part A, before committing
- User pastes a spec, brief, or decision worth remembering → part B
- `kb_query.py stale` reports drift → part A
- During `initialise` the full codebase is ingested automatically
