# Program: assemble-deep-like-agent (Path B)

Rebuild a Deep Agent–equivalent stack with `create_agent` + Deep Agents middleware. Use when forking, teaching, or debugging. Prefer [create-deep-agent.md](create-deep-agent.md) for normal shipping.

## Inputs

- Same as Path A (model, tools, backend, skills, guardrails)
- Understanding of [under-the-hood.md](under-the-hood.md)

## Checklist

```
Task Progress:
- [ ] Step 1: Backend
- [ ] Step 2: Orchestrator prompt + TodoListMiddleware
- [ ] Step 3: Build GP subagent middleware
- [ ] Step 4: Build main middleware (factory order)
- [ ] Step 5: create_agent(...)
- [ ] Step 6: High recursion_limit + invoke
- [ ] Step 7: Verify parity with create_deep_agent
```

### Step 1: Backend

Same rules as Path A — [choose-backend.md](choose-backend.md). One backend instance shared by main agent and general-purpose subagent.

### Step 2: Prompt + planning

Use [../examples/orchestrator_planning_prompt.md](../examples/orchestrator_planning_prompt.md).

Opt in planning:

```python
from langchain.agents.middleware import TodoListMiddleware
```

### Step 3: General-purpose subagent stack

Match factory GP middleware (no nested `SubAgentMiddleware`):

```python
from deepagents.middleware import (
    FilesystemMiddleware,
    SkillsMiddleware,
    PatchToolCallsMiddleware,
)
from deepagents.middleware.summarization import create_summarization_middleware
from deepagents.middleware.subagents import GENERAL_PURPOSE_SUBAGENT

gp_middleware = [
    FilesystemMiddleware(backend=backend),
    create_summarization_middleware(model, backend),
    PatchToolCallsMiddleware(),
]
if skills:
    gp_middleware.append(SkillsMiddleware(backend=backend, sources=skills))

gp = {
    **GENERAL_PURPOSE_SUBAGENT,
    "model": model,
    "tools": tools or [],
    "middleware": gp_middleware,
}
```

For declarative path permissions + HITL without forking FS middleware internals, prefer Path A (`create_deep_agent(..., permissions=..., interrupt_on=...)`). Path A runs `_build_interrupt_on_from_permissions` + `_merge_fs_interrupt_on` for you. On Path B, append `HumanInTheLoopMiddleware(interrupt_on=...)` yourself after Patch; recreate FS `when` predicates only if you need `mode="interrupt"` without the factory (see [../references/human-in-the-loop.md](../references/human-in-the-loop.md#internals-path-b)). When overriding `FilesystemMiddleware` yourself, pass a fully configured instance (backend, tools allowlist, etc.) — name-matched overrides replace the default and do not inherit factory kwargs.

### Step 4: Main middleware (factory order)

```python
from deepagents.middleware import SubAgentMiddleware

main_middleware = []
if skills:
    main_middleware.append(SkillsMiddleware(backend=backend, sources=skills))
main_middleware.extend([
    FilesystemMiddleware(backend=backend),
    SubAgentMiddleware(backend=backend, subagents=[gp]),
    create_summarization_middleware(model, backend),
    PatchToolCallsMiddleware(),
    TodoListMiddleware(),  # recommended for deep-like planning
    # optional: PIIMiddleware, ToolCallLimitMiddleware, HumanInTheLoopMiddleware, ...
])
```

Order details: [../references/harness-middleware-stack.md](../references/harness-middleware-stack.md).

### Step 5: create_agent

```python
from langchain.agents import create_agent

agent = create_agent(
    model,
    tools=tools or [],
    system_prompt=ORCHESTRATOR_PROMPT,
    middleware=main_middleware,
    checkpointer=checkpointer,
    # store=store when StoreBackend used
)
```

### Step 6: Invoke

```python
config = {
    "configurable": {"thread_id": thread_id},
    "recursion_limit": 9999,  # deepagents uses a very high default
}
agent.invoke({"messages": [{"role": "user", "content": "..."}]}, config=config)
```

### Step 7: Verify parity

| Behavior | Expectation |
|----------|-------------|
| FS tools | Present and routed via backend |
| Skills index | In system prompt when `SkillsMiddleware` configured |
| Skill body | Via `read_file` on listed path (`limit=1000`) |
| `task` | Launches GP (or custom) subagent |
| `write_todos` | Present when TodoListMiddleware opted in |
| Summarization | Long threads compress without manual trim |

If parity is hard to maintain, switch back to Path A unless the fork is intentional.

## Failure modes

| Symptom | Fix |
|---------|-----|
| No `task` tool | Include `SubAgentMiddleware` with ≥1 subagent |
| Skills index without bodies | Ensure FS `read_file` available |
| Stack drift from factory | Diff against [under-the-hood.md](under-the-hood.md) order |
| Early recursion stop | Raise `recursion_limit` |

## See also

- Example: [../examples/assemble_deep_like_agent.py](../examples/assemble_deep_like_agent.py)
- From-scratch guide: https://docs.langchain.com/oss/python/langchain/deep-agent-from-scratch
