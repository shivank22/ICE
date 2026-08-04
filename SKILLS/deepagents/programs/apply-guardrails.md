# Program: apply-guardrails

Layer production guardrails on a Deep Agent. Boundaries live at **tools / sandbox / middleware** — not in prompts alone.

## Inputs

- Sensitivity of tools (writes, execute, network)
- PII / compliance needs
- Whether HITL is available (checkpointer required)

## Checklist

```
Task Progress:
- [ ] Step 1: Filesystem permissions
- [ ] Step 2: HITL interrupt_on
- [ ] Step 3: Call / tool limits
- [ ] Step 4: PII and privacy middleware
- [ ] Step 5: Isolation (sandbox vs LocalShell)
- [ ] Step 6: Custom policy hooks / wrap_tool_call
```

### Step 1: Filesystem permissions

```python
from deepagents import FilesystemPermission, create_deep_agent

permissions = [
    FilesystemPermission(operations=["read", "write"], paths=["/workspace/**"], mode="allow"),
    FilesystemPermission(operations=["write"], paths=["/workspace/.env", "/secrets/**"], mode="deny"),
    FilesystemPermission(operations=["read", "write"], paths=["/**"], mode="deny"),
]
```

- First-match-wins; put specific rules before broad ones
- `mode="interrupt"` pauses for approval (needs checkpointer)
- Covers built-in FS tools only — not custom MCP/FS tools, not sandbox shell

### Step 2: HITL

```python
agent = create_deep_agent(
    ...,
    permissions=permissions,
    interrupt_on={
        "write_file": True,
        "edit_file": True,
        "delete": True,
        "execute": True,
    },
    checkpointer=checkpointer,
)
```

Permission `interrupt` modes merge with `interrupt_on`. Resume with LangGraph `Command(resume={"decisions": [...]})` on the same `thread_id`.

Full flow (decisions, conditional `when`, subagents, FS interrupts): [human-in-the-loop.md](human-in-the-loop.md).

### Step 3: Call limits

```python
from langchain.agents.middleware import ToolCallLimitMiddleware, ModelCallLimitMiddleware

middleware=[
    ToolCallLimitMiddleware(thread_limit=50, run_limit=25),
    ModelCallLimitMiddleware(run_limit=40),
]
```

Prevents runaway ReAct loops.

### Step 4: PII

```python
from langchain.agents.middleware import PIIMiddleware

middleware=[
    PIIMiddleware("email", strategy="redact", apply_to_input=True),
    PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
]
```

Strategies: `redact`, `mask`, `hash`, `block`. Custom detectors supported.

### Step 5: Isolation

| Environment | Choice |
|-------------|--------|
| Production code exec | Sandbox backend |
| Trusted local CLI | `LocalShellBackend` + HITL |
| No shell needed | State / Composite without sandbox |

Path permissions cannot contain shell (`execute`). Treat sandbox policy and secrets carefully.

### Step 6: Custom policies

- Backend **policy hooks** for path/content validation beyond declarative permissions
- `@wrap_tool_call` / custom `AgentMiddleware` for app-specific gates
- Fault tolerance: model retry / fallback middleware (see LangChain built-ins)

## Hard rules

1. Trust the LLM model of security: **bound tools**, don't prompt-police
2. Permissions ≠ custom tools ≠ `execute`
3. Interrupts need a checkpointer
4. Specific permission rules before `/**` deny/allow

## See also

- [human-in-the-loop.md](human-in-the-loop.md)
- [../references/guardrails.md](../references/guardrails.md)
- [../references/human-in-the-loop.md](../references/human-in-the-loop.md)
- Examples: [../examples/guarded_deep_agent.py](../examples/guarded_deep_agent.py), [../examples/human_in_the_loop.py](../examples/human_in_the_loop.py)
- https://docs.langchain.com/oss/python/deepagents/going-to-production
- https://docs.langchain.com/oss/python/deepagents/permissions
- https://docs.langchain.com/oss/python/deepagents/human-in-the-loop
