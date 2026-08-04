# Harness middleware stack

Default main-agent middleware order as assembled by `create_deep_agent` (`graph.py`). Prefer this over stale docs that still list `TodoListMiddleware` as default item #1.

## Main agent (first → last)

| # | Middleware | When |
|---|------------|------|
| 1 | `SkillsMiddleware` | If `skills=` |
| 2 | `FilesystemMiddleware` | Always — FS tools + permissions enforcement |
| 3 | `SubAgentMiddleware` | If any sync subagent (incl. auto GP) |
| 4 | `create_summarization_middleware` | Always |
| 5 | `PatchToolCallsMiddleware` | Always |
| 6 | `AsyncSubAgentMiddleware` | If async subagents |
| 7 | Caller `middleware=` | Name-match **replaces**; else spliced after core |
| 8 | Harness profile `extra_middleware` | Model-dependent (e.g. Codex adds todos) |
| 9 | Excluded-tool filtering | If profile `excluded_tools` |
| 10 | Prompt caching (Anthropic / Bedrock) | Always registered; no-op if unsupported |
| 11 | `MemoryMiddleware` | If `memory=` |
| 12 | `HumanInTheLoopMiddleware` | If merged `interrupt_on` non-empty (user map and/or permission `mode="interrupt"`) |

### HITL assembly notes

- Merge: `_merge_fs_interrupt_on(_build_interrupt_on_from_permissions(permissions), interrupt_on)` — **user wins** per tool name; omit middleware if empty
- Hook: `after_model` (LangChain HITL), not inside `FilesystemMiddleware`
- Companion: `PatchToolCallsMiddleware` (always earlier) repairs dangling tool calls on the next `before_agent`
- Details: [human-in-the-loop.md](human-in-the-loop.md#internals-path-b)

## Required scaffolding

Cannot remove via `HarnessProfile.excluded_middleware`:

- `FilesystemMiddleware` — built-in file tools + permission evaluation
- `SubAgentMiddleware` — `task` tool handler

## Synchronous subagent stack

General-purpose and declarative sync subagents get:

- `FilesystemMiddleware` (+ permissions inherit or override)
- `create_summarization_middleware`
- `PatchToolCallsMiddleware`
- `SkillsMiddleware` only if that subagent has `skills` (GP inherits factory `skills=`)
- Profile extras + prompt caching
- **No** nested `SubAgentMiddleware` (only parent exposes `task`)

On subagents, skills middleware is appended **after** Patch (ordering differs from main).

## Merge rules for caller middleware

1. If `.name` matches a default → **replace in place** (full replacement, not deep-merge)
2. Else → insert after last core entry (after Patch / before profile tail)

**FilesystemMiddleware override caveat:** if you replace it, pass `backend` and `permissions` on your instance — they are **not** inherited from `create_deep_agent(...)` kwargs.

## TodoListMiddleware

**Opt-in** since deepagents v0.7. Pass explicitly:

```python
from langchain.agents.middleware import TodoListMiddleware
create_deep_agent(..., middleware=[TodoListMiddleware()])
```

Only some harness profiles (e.g. OpenAI Codex) auto-inject via `extra_middleware`.

## System prompt assembly

```text
Authored:  USER (system_prompt=) → profile BASE → profile SUFFIX
Middleware appends (wrap_model_call): skills fragment, memory fragment, todos fragment (if present), ...
```

Legacy `_LEGACY_BASE_AGENT_PROMPT` is deprecated and not applied by default.

## See also

- [../programs/under-the-hood.md](../programs/under-the-hood.md)
- https://docs.langchain.com/oss/python/deepagents/customization
