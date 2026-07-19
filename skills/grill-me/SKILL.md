---
name: grill-me
description: Asks the user targeted clarifying questions until a shared understanding of the task is reached, before any implementation begins.
---

# Skill: grill-me

Use this skill when the user's request is ambiguous, underspecified, or when implementation requires decisions the user hasn't made yet. Rather than guessing or making assumptions, this skill probes the user with focused questions and only proceeds once both parties agree on what needs to be built.

## Usage

Load this skill early in the conversation, typically right after the user states their request. Pass any known context (e.g. file paths, error messages) as part of the load command.

```
Load skill grill-me for "add a login page"
Load skill grill-me for "fix the slow query" (context: src/lib/db.ts line 200)
```

## Workflow

### Step 1: Restate the request

Summarise what you understand the user wants in 1–2 sentences. This confirms the high-level goal before diving into details.

### Step 2: Identify gaps

Think about what you'd need to know to start implementing:

- **Scope**: What exactly should be included/excluded?
- **Location**: Which file(s) or area(s) of the codebase?
- **Behaviour**: What should happen on success/failure/edge cases?
- **Design**: Any UI/UX preferences, naming conventions, patterns to follow?
- **Dependencies**: Are there existing modules, APIs, or types to reuse?
- **Constraints**: Performance targets, browser support, auth requirements, mobile responsiveness?

### Step 3: Ask one question at a time

Present the single most important clarifying question. Format it clearly:

> **Question **: {question}
>
> {brief context on why this matters}

Wait for the user's answer before asking the next question. Do NOT batch multiple questions — each answer may change what you ask next.

### Step 4: Acknowledge and adapt

After each answer:
1. Confirm you understood correctly
2. Update your mental model of the task
3. Determine the next most important open question
4. Ask it, or if no more questions remain, proceed to Step 5

### Step 5: Summarise shared understanding

Restate the agreed-upon plan in a concise bullet list. Ask the user to confirm before proceeding:

```
**Shared understanding:**
- Build X in file Y
- It does Z on success, W on error
- Follows existing pattern from file V
- Constraints: ...

Confirm? If yes, I'll start implementing.
```

### Step 6: Proceed only on confirmation

Do NOT implement anything until the user explicitly confirms the shared understanding. If they suggest a change, loop back to Step 3.

## Rules

- Ask exactly **one question at a time** — never batch questions
- Start with the question whose answer has the biggest impact on the implementation
- Do NOT skip to implementation until the user confirms the shared understanding (Step 6)
- If the user answers vaguely, ask a follow-up to clarify before moving on
- Keep questions short and specific — avoid hypotheticals or scope creep
- If you already have enough context (very rare), you may skip to Step 5, but still ask for confirmation
