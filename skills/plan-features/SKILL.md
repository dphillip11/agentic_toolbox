---
name: plan-features
description: Creates or updates FEATURES.md — a high-level list of features with status markers, ordered by priority.
---

# Skill: plan-features

Use this skill after `init-project` to define the feature roadmap. Produces or updates `FEATURES.md`, a living document that the user may edit freely.

## Usage

```
Load skill plan-features for "list all features for the CLI tool"
```

## Workflow

### Step 1: Load grill-me

Load the **grill-me** skill to enumerate and prioritise features. Questions should cover:

- **Core features**: What must the first working version do?
- **Enhancements**: What comes after?
- **User flow**: Walk through the main user journey — what features does it touch?
- **Priorities**: Which features are blockers for others?
- **Non-features**: What will NOT be built (at least not yet)?

### Step 2: Write FEATURES.md

Produce `FEATURES.md` with this structure:

```markdown
# Features

Features listed below. Mark with `[DONE]` when complete. User may add, remove, reorder at any time.

- Feature one — brief description
- Feature two — brief description
- Feature three — brief description
- [DONE] Already completed feature
```

Features without a `[DONE]` marker are considered pending. Order reflects priority (top = next).

### Step 3: Present for approval

Show the list and ask the user to confirm, reorder, or amend.

## Rules

- Keep each feature description to one line — detail belongs in feature plans
- If `FEATURES.md` already exists, read it first, then discuss additions/reorderings with the user
- Do NOT mark any feature `[DONE]` except by explicit user confirmation
