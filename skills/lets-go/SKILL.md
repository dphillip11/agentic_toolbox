---
name: lets-go
description: Master orchestrator that walks through the entire SDLC — init if needed, check FEATURES.md, then work through each feature with plan-with-me → create-tests → develop → polish → summarise.
---

# Skill: lets-go

Use this skill to kick off a development session. It is the entry point that orchestrates all other skills.

## Usage

```
Load skill lets-go
```

## Workflow

### Step 1: Check for AGENTS.md

If `AGENTS.md` does not exist in the project root:
  1. Load **init-project** and follow its workflow
  2. Once confirmed, proceed to Step 2

If `AGENTS.md` exists, proceed to Step 2.

### Step 2: Read FEATURES.md

Read the current `FEATURES.md`.

- If it does not exist, load **plan-features** to create it.
- If it exists, present it to the user and ask:
  > Here's the current feature list. Do you want to add, remove, or reorder anything before we start?

### Step 3: Identify next feature

Find the first feature in `FEATURES.md` that does NOT have a `[DONE]` marker. If none, report all features complete.

### Step 4: Execute feature

For the selected feature, run these skills in sequence:

1. **plan-with-me** — refine into a plan with acceptance criteria
2. **create-tests** — write tests per the plan
3. **develop** — iterative loop of implement → run-tests → check-adherence

### Step 5: Mark complete

When the feature passes check-adherence:

1. Update `FEATURES.md` — add `[DONE]` to the feature line
2. Report to the user:
   > Feature "<name>" is complete.

### Step 6: Continue?

Ask the user:

> Do you want to continue with the next feature, or take a break?
> - Continue → go to Step 3
> - Break → run **polish**, then **summarise**

### Step 7: Polish and summarise

Before ending:
1. Load **polish** — run quality checks
2. Load **summarise** — describe what changed

## Rules

- Always check with the user before starting a new feature
- Never skip polish and summarise at the end of a break
- If any skill raises a blocker (incorrect plan, dependency not met), stop and ask the user
- Respect the user's pace — if they say break, break
