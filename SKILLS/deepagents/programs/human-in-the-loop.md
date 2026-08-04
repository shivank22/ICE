# Program: human-in-the-loop

Pause sensitive tool calls for human approve / edit / reject / respond, then resume the same thread.

Docs: https://docs.langchain.com/oss/python/deepagents/human-in-the-loop

## Inputs

- Which tools (or FS paths) need approval
- Checkpointer available (required)
- UI / API that can show interrupts and collect decisions

## Checklist

```
Task Progress:
- [ ] Step 1: Add checkpointer + stable thread_id
- [ ] Step 2: Configure interrupt_on (and/or permission mode=interrupt)
- [ ] Step 3: Tailor allowed_decisions by risk
- [ ] Step 4: Optional when= predicates for conditional interrupts
- [ ] Step 5: Invoke with version="v2"; detect result.interrupts
- [ ] Step 6: Resume with Command(resume={"decisions": [...]}) same config
- [ ] Step 7: Subagents: per-subagent interrupt_on; gate eval for dynamic fan-out
```

### Step 1: Checkpointer + thread

HITL **requires** a checkpointer. Resume must use the **same** `thread_id`.

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
config = {"configurable": {"thread_id": "hitl-1"}, "recursion_limit": 9999}
```

### Step 2: `interrupt_on`

When set, factory adds `HumanInTheLoopMiddleware`. Values:

| Value | Effect |
|-------|--------|
| `True` | Interrupt; default decisions: approve, edit, reject, respond |
| `False` | No interrupt for that tool |
| `InterruptOnConfig` | Custom `allowed_decisions` and optional `when` |

```python
agent = create_deep_agent(
    model=...,
    tools=[remove_file, fetch_file, notify_email],
    interrupt_on={
        "remove_file": True,
        "fetch_file": False,
        "notify_email": {"allowed_decisions": ["approve", "reject"]},
    },
    checkpointer=checkpointer,
)
```

**Also:** `FilesystemPermission(..., mode="interrupt")` (deepagents≥0.6.8) pauses built-in `write_file` / `edit_file` on matching paths — same interrupt shape; merges with `interrupt_on`.

### Step 3: Decisions by risk

| Decision | Meaning | Use when |
|----------|---------|----------|
| `approve` | Run with original args | Safe as proposed |
| `edit` | Change args, then run | Fix recipient/path before side effect |
| `reject` | Skip tool; feedback to agent | Deny side effects |
| `respond` | Human message becomes tool result | `ask_user`-style tools only |

Do **not** use `respond` to deny side-effecting tools — the model may treat it as a successful result. Prefer `reject` + a clear `message`.

Edit conservatively — large arg changes can make the model re-plan and re-call tools.

### Step 4: Conditional interrupts

Needs `langchain>=1.3.3`. `when(request) -> bool`: `True` pauses, `False` auto-runs (not batched into the interrupt).

```python
from langchain.agents.middleware import ToolCallRequest

def writes_outside_workspace(request: ToolCallRequest) -> bool:
    path = request.tool_call["args"].get("file_path", "")
    return not path.startswith("/workspace/")

interrupt_on = {
    "write_file": {
        "allowed_decisions": ["approve", "edit", "reject"],
        "when": writes_outside_workspace,
    },
}
```

### Step 5–6: Handle and resume

```python
from langgraph.types import Command

result = agent.invoke({"messages": [...]}, config=config, version="v2")

if result.interrupts:
    value = result.interrupts[0].value
    action_requests = value["action_requests"]  # batched if multiple
    # One decision per action, same order
    decisions = [
        {"type": "reject", "message": "Do not delete. Ask which file to archive."},
        # or {"type": "approve"}
        # or {"type": "edit", "edited_action": {"name": "...", "args": {...}}}
    ]
    result = agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config,  # same thread_id
        version="v2",
    )
```

Omit `message` on reject → default “not executed; don’t retry unless user asks.” Prefer domain-specific messages for sensitive tools.

Cancelled / interrupted runs before a tool returns: `PatchToolCallsMiddleware` repairs dangling tool calls in history.

### Step 7: Subagents

1. **Per-subagent `interrupt_on`** — overrides main agent for that subagent’s tools.
2. **`interrupt()` inside a tool** — custom approval payloads; resume with `Command(resume={...})` matching your shape (not necessarily `decisions`).
3. **Dynamic interpreter** — inner `task()` bypasses parent `interrupt_on`; gate **`eval`** instead (see [dynamic-subagents.md](dynamic-subagents.md)).

## Internals (short)

```text
permissions mode=interrupt  →  _build_interrupt_on_from_permissions (when predicates)
user interrupt_on           →  _merge_fs_interrupt_on (user wins per tool name)
                            →  HumanInTheLoopMiddleware (after_model → interrupt())
FilesystemMiddleware        →  allow/deny only (no interrupt())
PatchToolCallsMiddleware    →  before_agent repair if run dies mid-tool
```

- **approve/edit** → revised `AIMessage.tool_calls` then tools run  
- **reject** → `ToolMessage(status="error")`; **respond** → `ToolMessage(status="success")`  
- Full Path B map: [../references/human-in-the-loop.md](../references/human-in-the-loop.md#internals-path-b)

## Hard rules

1. Checkpointer required; same `thread_id` on resume
2. Decisions list length/order must match `action_requests`
3. Use `version="v2"` when reading `result.interrupts` / `result.value` as in current docs
4. `reject` for denials; `respond` only when the human *is* the tool
5. Permission `mode="interrupt"` + `interrupt_on` can appear in one review batch
6. Do not expect `FilesystemMiddleware` alone to pause — interrupts come from HITL middleware after factory merge

## See also

- [../references/human-in-the-loop.md](../references/human-in-the-loop.md)
- [under-the-hood.md](under-the-hood.md)
- [apply-guardrails.md](apply-guardrails.md) — HITL as one guardrail layer
- [../examples/human_in_the_loop.py](../examples/human_in_the_loop.py)
