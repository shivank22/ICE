# Program: plan-and-decompose

How Deep Agents plan and break work. There is **no hard-coded planner** — the LLM chooses when to plan and when to delegate, guided by tools + prompts.

## Inputs

- Multi-step user goal
- Whether `TodoListMiddleware` is opted in
- Available subagent types (default: general-purpose)

## Checklist

```
Task Progress:
- [ ] Step 1: Decide whether to plan
- [ ] Step 2: write_todos (if needed)
- [ ] Step 3: Choose execution mode per step
- [ ] Step 4: Delegate with task (if needed)
- [ ] Step 5: Update todos; synthesize
```

### Step 1: Decide whether to plan

| Goal complexity | Action |
|-----------------|--------|
| Fewer than 3 trivial steps | Act directly — skip `write_todos` |
| 3 or more distinct steps / non-trivial | Opt in `TodoListMiddleware` and plan |
| Pure Q&A | No todos, no `task` |

Wire planning (Path A or B):

```python
from langchain.agents.middleware import TodoListMiddleware
middleware=[TodoListMiddleware()]
```

### Step 2: write_todos

Rules the middleware teaches the model (encode in orchestrator prompt too):

- Break into **specific, actionable** items
- Mark first item(s) `in_progress` immediately
- Keep ≥1 `in_progress` until done (unless all completed)
- Mark `completed` immediately — do not batch
- **One** `write_todos` call per model turn (replaces entire list)
- Final user answer is a **separate message after** the last todo update

State: `todos: [{content, status}]` with `pending | in_progress | completed`.

Todos do **not** propagate to subagents (`todos` excluded from subagent I/O).

### Step 3: Choose execution mode per step

| Step type | Mode |
|-----------|------|
| Local FS / simple tools / synthesis | Main agent tools |
| Heavy, multi-step, context-heavy, uncertain search | `task(subagent_type=..., description=...)` |
| Independent comparisons / facets | Parallel `task` calls in **one** turn |

### Step 4: Delegate with task

`task` tool guidance:

- Put **full context** in `description` — subagent is stateless; only sees that prompt
- State exactly what to return (subagent report is a `ToolMessage`; **not** shown to the user)
- Bias to **one comprehensive** subagent; avoid premature splits of "research X" into overview/techniques/apps
- Parallelize only for explicit comparisons or clearly independent aspects
- Parent **relays/summarizes** results to the user

Default GP description: researching, searching files/content, multi-step tasks — same tools as main when factory-built.

### Step 5: Update and synthesize

Canonical flow (research example pattern):

1. **Plan** — `write_todos`
2. **Context** — explore / save request to scratch files
3. **Delegate** — `task(...)` for heavy slices
4. **Act** — main agent finishes local steps
5. **Verify** — reconcile todos against original ask
6. **Synthesize** — parent writes the user-facing answer

Copyable prompt: [../examples/orchestrator_planning_prompt.md](../examples/orchestrator_planning_prompt.md).

## Failure modes

| Symptom | Fix |
|---------|-----|
| Agent never plans | Opt in TodoListMiddleware; strengthen system prompt |
| Parallel write_todos errors | One call per turn |
| Empty subagent results | Richer `description`; ask for complete final answer |
| Token blow-up from many subagents | Bias to single comprehensive task |

## See also

- [../references/planning-and-decomposition.md](../references/planning-and-decomposition.md)
- [../references/prompt-fragments.md](../references/prompt-fragments.md)
- Many independent units / JS fan-out: [dynamic-subagents.md](dynamic-subagents.md)
