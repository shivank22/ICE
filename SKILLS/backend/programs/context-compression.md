# Algorithm — Context Compression

## Purpose

Fit a Context Package into token budgets without dropping policy or mandatory skill constraints.

## Inputs

- `context_package`
- `budgets`
- `priority_map`

## Outputs

- Compressed `context_package`
- `drops[]` and `summaries[]`

## Preconditions

- Package already ordered.
- Policy section marked non-droppable.

## Postconditions

- Total tokens ≤ global budget.
- Provenance retained for kept blocks.

## Steps

1. Measure tokens per section.
2. If within budget, return unchanged.
3. Compress episodic exemplars first (summarize or drop lowest rank).
4. Compress semantic hits next (keep highest score; summarize Memory.md to bullet claims).
5. Window STM messages (keep latest N + first system).
6. Replace large tool outputs with digests + artifact refs.
7. Never drop policy or mandatory skill constraints; if still over budget → fail with `budget_exhausted`.

## Edge Cases

- Single Memory.md larger than semantic budget → claim extraction summary.
- Empty droppable sections → hard fail.

## Failure Handling

Return structured error; Orchestrator should not call the model with an over-budget package.
