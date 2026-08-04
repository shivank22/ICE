# Dynamic subagents

Dispatch Deep Agents subagents from **interpreter (QuickJS) code** instead of one-at-a-time model tool calls.

Docs: https://docs.langchain.com/oss/python/deepagents/dynamic-subagents  
Related: https://docs.langchain.com/oss/python/deepagents/interpreters · https://docs.langchain.com/oss/python/deepagents/subagents

## Status

- Interpreter runtime is **beta**
- Requires `langchain-quickjs>=0.2.0`, Python `>=3.11`

## Standard task vs dynamic task

| | Standard `task` tool | Dynamic (interpreter) |
|--|----------------------|------------------------|
| Who schedules | Model chooses each tool call | JS loops / `Promise.all` / branches |
| Best for | One or few delegations | Many independent units, workflows |
| Trigger | Normal user ask | Often phrase as a **"workflow"** |
| HITL | `interrupt_on={"task": ...}` can apply | Inner `task()` **bypasses** parent tool HITL — gate `eval` |

## Setup

```python
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    subagents=[{
        "name": "reviewer",
        "description": "Reviews code for security issues...",
        "system_prompt": "...",
    }],
    middleware=[CodeInterpreterMiddleware()],
    # middleware=[CodeInterpreterMiddleware(ptc=["glob"])],  # optional PTC
    # middleware=[CodeInterpreterMiddleware(subagents=False)],  # interpreter without dynamic task()
)
```

## Interpreter `task()` API

```js
await task({
  description: "...",      // full prompt for the child
  subagentType: "reviewer",
  responseSchema: { ... }, // optional → typed object result
});
```

Orchestration pattern: keep working set in JS variables → slice → `task()` → synthesize in code (RLM-style). Can combine with programmatic tool calling (`tools.*`) when PTC allowlisted.

## Pattern catalog

| Pattern | Idea |
|---------|------|
| Classify and act | Route each item to the right specialist |
| Fan-out and synthesize | Parallel same-role work, then merge |
| Adversarial verification | Producer vs critic / checker |
| Generate and filter | Many proposals → score → keep best |
| Tournament | Pairwise or multi-round comparison |
| Loop until done | Iterate until a stop condition |

## Security

1. `task()` from inside `eval` does **not** honor parent `interrupt_on` per subagent dispatch
2. Approve/gate the **`eval`** tool when orchestration must be human-reviewed
3. Disable with `CodeInterpreterMiddleware(subagents=False)` if you want interpreter without dynamic subagents
4. Follow interpreter isolation docs for sandboxing the QuickJS runtime

## See also

- [../programs/dynamic-subagents.md](../programs/dynamic-subagents.md)
- [planning-and-decomposition.md](planning-and-decomposition.md) — standard `task` path
- [../examples/dynamic_subagents.py](../examples/dynamic_subagents.py)
