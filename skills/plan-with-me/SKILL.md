---
name: plan-with-me
description: Takes a single feature from FEATURES.md and uses grill-me to refine it into a concrete implementation plan with acceptance criteria.
---

# Skill: plan-with-me

Use this skill when starting work on a feature from `FEATURES.md`. It turns the one-line feature description into a detailed, actionable plan.

## Usage

```
Load skill plan-with-me for "add user authentication" (from FEATURES.md)
```

## Workflow

### Step 1: Load grill-me

Load the **grill-me** skill to refine the feature. Questions must cover:

- **Scope**: What exactly does this feature include? What is explicitly excluded?
- **Location**: Which files, routes, or modules will change?
- **Behaviour**: What happens on success? On failure? On edge cases (empty state, error state, loading state)?
- **Design**: UI mockups, naming conventions, patterns to follow. Reference existing code.
- **Dependencies**: Does this feature depend on other features?
- **Acceptance criteria**: Bullet list of observable outcomes that define "done".

### Step 2: Write the feature plan

Do NOT write to a file yet. Keep the plan in the conversation. It should include:

```
Feature: <name>
Scope: <what's in, what's out>
Files: <file paths>
Acceptance criteria:
- [ ] Criterion 1
- [ ] Criterion 2
Edge cases:
- <edge case 1>
- <edge case 2>
Dependencies: <none or feature X>
```

### Step 3: Get explicit confirmation

Show the plan and ask:

> **Shared understanding:**
> - Feature: ...
> - Files to touch: ...
> - Acceptance criteria: ...
>
> Confirm? If yes, I'll proceed with creating tests.

## Rules

- Always load grill-me — even if the feature seems simple
- Acceptance criteria must be testable (observable outcomes, not implementation details)
- Do NOT proceed to create-tests or implement without explicit user confirmation
- If the feature has dependencies on other features, flag this and discuss ordering
