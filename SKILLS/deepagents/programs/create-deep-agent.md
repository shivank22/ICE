# Program: create-deep-agent (Path A)

Factory recipe for shipping a Deep Agent with `create_deep_agent`. Prefer this path unless you must fork or explain the stack — then use [assemble-deep-like-agent.md](assemble-deep-like-agent.md).

## Inputs

- Model (`provider:model` or chat model instance)
- Domain tools (optional)
- Backend choice (default State; Composite for disk/memory)
- Optional: skills paths, memory `AGENTS.md`, permissions, HITL, checkpointer/store

## Checklist

```
Task Progress:
- [ ] Step 1: Model + orchestrator prompt
- [ ] Step 2: Backend
- [ ] Step 3: Skills / memory
- [ ] Step 4: Opt in TodoListMiddleware
- [ ] Step 5: Guardrails
- [ ] Step 6: create_deep_agent(...)
- [ ] Step 7: Invoke with thread_id
- [ ] Step 8: Verify behaviors
```

### Step 1: Model + orchestrator prompt

Pass an explicit `model=` (do not rely on deprecated implicit defaults).

Use a Plan → Context → Delegate → Verify → Synthesize system prompt. Copy from [../examples/orchestrator_planning_prompt.md](../examples/orchestrator_planning_prompt.md).

### Step 2: Backend

Follow [choose-backend.md](choose-backend.md). Defaults:

- Scratch only → omit `backend=` (`StateBackend`)
- Project files → `CompositeBackend(default=StateBackend(), routes={"/workspace/": FilesystemBackend(root_dir=..., virtual_mode=True)})`
- Cross-thread memory → add `"/memories/": StoreBackend(namespace=...)`

### Step 3: Skills / memory

- `skills=["/skills/"]` — paths must exist on the backend (or StateBackend `files=` at invoke)
- `memory=["./AGENTS.md"]` or `memory=["/memories/AGENTS.md"]` — always loaded; unlike skills progressive disclosure. For cross-thread persistence see [configure-memory.md](configure-memory.md).

See [skills-progressive-disclosure.md](skills-progressive-disclosure.md).

### Step 4: Opt in planning

Since v0.7, todos are **not** default:

```python
from langchain.agents.middleware import TodoListMiddleware

middleware=[TodoListMiddleware()]
```

Recommended for multi-step deep-like behavior. See [plan-and-decompose.md](plan-and-decompose.md).

### Step 5: Guardrails

Apply as needed via [apply-guardrails.md](apply-guardrails.md):

- `permissions=[FilesystemPermission(...)]`
- `interrupt_on={"write_file": True, "edit_file": True, "execute": True}`
- Extra middleware: `PIIMiddleware`, `ToolCallLimitMiddleware`, `ModelCallLimitMiddleware`

Requires a `checkpointer` when using interrupts.

### Step 6: Create the agent

```python
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[...],  # additive; never removes built-ins
    system_prompt=ORCHESTRATOR_PROMPT,
    backend=backend,  # or omit for StateBackend
    skills=["/skills/"],
    memory=["./AGENTS.md"],
    permissions=permissions,
    interrupt_on=interrupt_on,
    middleware=[TodoListMiddleware()],
    checkpointer=checkpointer,
    store=store,  # when using StoreBackend
)
```

Built-in tools (unless excluded via harness profile): `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute` (sandbox/LocalShell only), `task` (if any sync subagent including default GP).

### Step 7: Invoke

```python
from langchain_core.utils.uuid import uuid7  # or uuid4

config = {"configurable": {"thread_id": str(uuid7())}, "recursion_limit": 9999}
agent.invoke(
    {"messages": [{"role": "user", "content": "..."}]},
    config=config,
    # context=Context(...) when context_schema is set
)
```

### Step 8: Verify

- Filesystem tools work against the chosen backend routes
- Skills appear as an index in the system prompt; `read_file` loads full `SKILL.md`
- `write_todos` available when TodoListMiddleware opted in
- `task` available (default general-purpose subagent)
- HITL pauses when configured

## Failure modes

| Symptom | Fix |
|---------|-----|
| No `write_todos` | Pass `TodoListMiddleware()` |
| No `execute` | Use sandbox or `LocalShellBackend` |
| Skills missing | Check `skills=` paths exist on backend |
| Permission interrupt without resume | Add checkpointer; resume via LangGraph Command |
| Internals on disk | Wrap FS in Composite with State default |

## See also

- Internals: [under-the-hood.md](under-the-hood.md)
- Example: [../examples/minimal_deep_agent.py](../examples/minimal_deep_agent.py), [../examples/guarded_deep_agent.py](../examples/guarded_deep_agent.py)
