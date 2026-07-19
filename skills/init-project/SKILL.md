---
name: init-project
description: Scaffolds a new project by creating AGENTS.md with high-level philosophy, constraints, conventions, and folder structure.
---

# Skill: init-project

Use this skill at the start of a new project. It produces `AGENTS.md` — the single source of truth for how the AI should approach the project.

## Usage

Load after the user describes a new project idea. It is also loaded automatically by **lets-go** when no `AGENTS.md` exists.

```
Load skill init-project for "a CLI tool for managing DNS records"
```

## Workflow

### Step 1: Load grill-me

Load the **grill-me** skill to refine the project description into concrete decisions. Questions should cover:

- **Purpose**: What does this project do? Who is it for?
- **Framework/Language**: Which runtime, language, framework, build tool?
- **Deployment**: Where does it run? (Cloudflare, AWS, Vercel, self-hosted, CLI…)
- **Storage**: Database, cache, file storage — which ones and why?
- **Auth**: Does it need authentication? What model? (OAuth, JWT, session, API key…)
- **Testing**: Preferred test framework, co-located or separate directory?
- **Patterns**: State management, error handling, logging patterns.
- **Folder structure**: monorepo? packages? feature-based or type-based grouping?
- **Non-goals**: What is explicitly out of scope?

### Step 2: Write AGENTS.md

Produce `AGENTS.md` using this template. Fill in the decisions from Step 1.

````markdown
# Project name

One-line description.

## Philosophy

- **Plan before you code.** Every feature starts with a written plan agreed with a human.
- **Verify after you build.** Tests and adherence checks run before anything is considered done.
- **Human in the loop.** The AI proposes, the human disposes.
- **Iterate in small loops.** Implement → test → verify. Repeat until the feature is solid.

## Development lifecycle

This project uses the skills from [agentic-toolbox](https://github.com/dphillip11/agentic_toolbox).

1. **plan-features** — define the feature roadmap in `FEATURES.md`
2. For each feature:
   a. **plan-with-me** — refine the feature into a concrete plan
   b. **create-tests** — write tests per the plan
   c. **develop** — loop of implement → run-tests → check-adherence
3. **polish** — lint, type-check, quality checks
4. **summarise** — describe what changed

See `skills/` for detailed instructions on each step.

## Constraints

- **Language/Framework**: {decided}
- **Runtime**: {decided}
- **Deployment**: {decided}
- **Storage**: {decided}
- **Auth**: {decided}
- **Testing**: {decided}

## Conventions

- **Naming**: {camelCase / kebab-case / PascalCase …}
- **Error handling**: {pattern}
- **Testing**: {framework, co-located or `__tests__` dir}
- **Commits**: {style}

## Folder structure

```
project/
├── src/
│   ├── lib/
│   └── routes/
├── tests/
└── FEATURES.md
```
````

### Step 3: Present for approval

Show the generated `AGENTS.md` and ask the user to confirm. Revise as needed.

## Rules

- Do NOT skip grill-me — every project has unique constraints
- Keep AGENTS.md concise (under 100 lines when possible)
- Only include decisions the user explicitly agrees to
- Reference the toolbox skills by name so the AI knows which skill to load at each stage
