---
name: create-tests
description: Writes test files for a feature per the plan produced by plan-with-me, following the project's existing testing conventions.
---

# Skill: create-tests

Use this skill after `plan-with-me` has produced a confirmed plan. It writes the test files that validate the feature's acceptance criteria.

## Usage

```
Load skill create-tests for "add user authentication" (plan confirmed)
```

## Workflow

### Step 1: Read the plan

Re-read the feature plan (from the conversation). Identify every acceptance criterion and edge case.

### Step 2: Review existing tests

- Find existing test files in the project to understand patterns (test runner, mocking style, setup helpers).
- Look for test fixtures, factories, or utilities used by other tests.

### Step 3: Write tests

For each acceptance criterion and edge case, write a test:

```javascript
describe('feature name', () => {
  it('meets acceptance criterion 1', () => {
    // arrange, act, assert
  })

  it('meets acceptance criterion 2', () => {
    // arrange, act, assert
  })

  it('handles edge case X', () => {
    // arrange, act, assert
  })
})
```

Place tests according to the project convention — co-located next to source files or in a parallel `__tests__` directory.

### Step 4: Verify tests run

Execute the test runner to confirm tests are picked up (they will fail — that's expected at this stage).

```
npm test        # or equivalent
```

## Rules

- Write one test per acceptance criterion
- Write one test per edge case
- Use the project's existing test framework (Vitest, Jest, Playwright, pytest…)
- Mock external dependencies (APIs, databases) per existing patterns
- Do NOT modify source files during this skill
- Confirm with the user before writing tests that require complex mocks or fixtures
