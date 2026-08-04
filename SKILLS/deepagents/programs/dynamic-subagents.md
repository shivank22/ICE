# Program: dynamic-subagents

Use interpreter middleware so the agent dispatches subagents from **JavaScript code** (loops, branches, parallel batches) instead of one model-chosen `task` tool call at a time.

Docs: https://docs.langchain.com/oss/python/deepagents/dynamic-subagents  
Interpreters: https://docs.langchain.com/oss/python/deepagents/interpreters

**Beta:** interpreter runtime APIs may change. Needs `langchain-quickjs>=0.2.0` and Python `>=3.11`.

## Inputs

- Configured `subagents=` (custom and/or default general-purpose)
- Work that fans across many independent units / perspectives / recursive slices

## When to use

| Pattern | Prefer |
|---------|--------|
| Single delegation | Normal `task` tool (model tool-call) — [plan-and-decompose.md](plan-and-decompose.md) |
| Many files/tickets, classify→act, fan-out+merge, adversarial check, tournament | **Dynamic subagents** via interpreter `task()` |
| Deterministic loop over N items | Dynamic (JS loop) over N separate model turns |

## Checklist

```
Task Progress:
- [ ] Step 1: Install interpreter deps
- [ ] Step 2: Define named subagents
- [ ] Step 3: Add CodeInterpreterMiddleware
- [ ] Step 4: Prompt with "workflow" when you want code orchestration
- [ ] Step 5: Optional PTC allowlist for tools.* from JS
- [ ] Step 6: Gate eval if HITL needed (interrupt_on does not wrap inner task())
```

### Step 1: Install

```bash
pip install "langchain-quickjs>=0.2.0"
# Python >= 3.11
```

### Step 2–3: Wire agent

```python
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    subagents=[{
        "name": "reviewer",
        "description": "Reviews code for security issues, citing lines and severity",
        "system_prompt": "You are a security-focused code reviewer. Report issues with line numbers and severity.",
    }],
    middleware=[CodeInterpreterMiddleware()],
    # Optional: discover files from JS before fan-out
    # middleware=[CodeInterpreterMiddleware(ptc=["glob", "ls"])],
)
```

GP alone can fan out without custom subagents; custom names/descriptions help the model pick roles.

### Step 4: Trigger

Phrase the request as a **workflow** so the interpreter system prompt opts into code orchestration:

```python
agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Run a workflow that reviews every file in src/routes/ and summarizes the top risks.",
    }]
})
```

For a single plain delegation, phrase without "workflow" and let normal `task` tool-calling apply.

### Step 5: How interpreter `task()` works

From JS inside `eval`:

```js
const review = await task({
  description: "Review src/auth/login.ts for auth issues. Cite line numbers.",
  subagentType: "reviewer",
  responseSchema: { /* optional JSON schema → typed object */ },
});
```

- Holds working set in JS variables (RLM-style)
- Fan-out with `Promise.all` / loops; synthesize in code
- Combine with PTC `tools.*` when enabled

### Step 6: Security notes

- Interpreter `task()` does **not** go through parent `interrupt_on` per dispatch — gate the **`eval`** tool if you need approval before orchestration
- Disable dynamic subagents but keep interpreter: `CodeInterpreterMiddleware(subagents=False)`
- Follow interpreter security/isolation docs

## Common patterns (names only)

1. Classify and act  
2. Fan-out and synthesize  
3. Adversarial verification  
4. Generate and filter  
5. Tournament  
6. Loop until done  

Details: [../references/dynamic-subagents.md](../references/dynamic-subagents.md).

## Failure modes

| Symptom | Fix |
|---------|-----|
| Still one-by-one `task` tool calls | Prompt as a "workflow"; ensure interpreter middleware present |
| No `task` in JS | `subagents=False`? or missing subagents config |
| HITL never fires on fan-out | Interrupt on `eval`, not only on `task` |
| Import errors | `langchain-quickjs` version / Python 3.11+ |

## See also

- [plan-and-decompose.md](plan-and-decompose.md) — standard `task` tool path
- [../examples/dynamic_subagents.py](../examples/dynamic_subagents.py)
- https://docs.langchain.com/oss/python/deepagents/dynamic-subagents
