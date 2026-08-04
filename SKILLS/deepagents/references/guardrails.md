# Guardrails

Production safety layers for Deep Agents. Docs: [going to production](https://docs.langchain.com/oss/python/deepagents/going-to-production), [permissions](https://docs.langchain.com/oss/python/deepagents/permissions), [HITL](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop).

## Principle

Deep Agents follow a **"trust the LLM"** security model: the agent can do anything its tools allow. Enforce boundaries at the **tool / sandbox / middleware** layer — not by expecting the model to self-police via prompts.

## Layers

| Layer | Mechanism | Covers |
|-------|-----------|--------|
| Path ACL | `FilesystemPermission` via `permissions=` | Built-in FS tools |
| Human approval | `interrupt_on` + HITL middleware; permission `mode="interrupt"` | Named tool calls |
| Loop limits | `ToolCallLimitMiddleware`, `ModelCallLimitMiddleware` | Runaway ReAct |
| Privacy | `PIIMiddleware` | Inputs/outputs (email, cards, custom) |
| Isolation | Sandbox backends | Code/shell execution |
| Custom policy | Backend policy hooks, `@wrap_tool_call` | App-specific rules |
| Resilience | Retry / fallback middleware | Transient API failures |

## Permissions

```python
from deepagents import FilesystemPermission

FilesystemPermission(
    operations=["read" | "write"],
    paths=["/workspace/**"],
    mode="allow" | "deny" | "interrupt",
)
```

- Evaluated in declaration order; **first match wins**
- No match → **allowed** (permissive default)
- `read` → `ls`, `read_file`, `glob`, `grep`
- `write` → `write_file`, `edit_file`, `delete`
- Does **not** apply to custom/MCP tools or sandbox `execute`
- Subagents inherit parent permissions unless they set their own (replacement, not merge)
- Specific denies (e.g. `.env`) must appear **before** broad `/workspace/**` allows

## HITL

```python
create_deep_agent(
    ...,
    interrupt_on={"edit_file": True, "execute": True},
    checkpointer=checkpointer,  # required to pause/resume
)
```

Resume with `Command(resume={"decisions": [...]})` on the same `thread_id`. Permission `mode="interrupt"` merges into the same path.

Details (decision types, conditional `when`, batched actions, subagents, factory/`after_model` internals): [human-in-the-loop.md](human-in-the-loop.md).

## PII

```python
from langchain.agents.middleware import PIIMiddleware

PIIMiddleware("email", strategy="redact", apply_to_input=True)
# strategies: redact | mask | hash | block
```

## Call limits

```python
from langchain.agents.middleware import ToolCallLimitMiddleware, ModelCallLimitMiddleware

ToolCallLimitMiddleware(thread_limit=50, run_limit=25)
ModelCallLimitMiddleware(run_limit=40)
```

Exit behaviors include error vs end-run (see LangChain middleware docs).

## Sandbox vs LocalShell

| | Sandbox | LocalShellBackend |
|--|---------|-------------------|
| Isolation | Provider container/VFS | None (host) |
| Production | Yes | No |
| HITL | Recommended | Strongly recommended |
| Path permissions | Insufficient alone | Insufficient alone |

## Middleware hooks for custom guardrails

| Hook | Use |
|------|-----|
| `before_model` | Trim history, catch PII before LLM |
| `wrap_model_call` | Retries, dynamic tools, caching |
| `after_model` | HITL before tools run |
| `wrap_tool_call` | Gate/inspect tool execution |
| `before_agent` / `after_agent` | Session setup/teardown |

## See also

- [../programs/apply-guardrails.md](../programs/apply-guardrails.md)
- [../programs/human-in-the-loop.md](../programs/human-in-the-loop.md)
- [human-in-the-loop.md](human-in-the-loop.md)
- [../examples/guarded_deep_agent.py](../examples/guarded_deep_agent.py)
- [../examples/human_in_the_loop.py](../examples/human_in_the_loop.py)
- https://docs.langchain.com/oss/python/langchain/middleware/built-in
