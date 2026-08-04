# API cheatsheet

Compact map of public surfaces for Path A and Path B. Prefer official API reference for full signatures: https://reference.langchain.com/python/deepagents/

## create_deep_agent (Path A)

```python
from deepagents import create_deep_agent

create_deep_agent(
    model=...,                 # str | BaseChatModel (explicit recommended)
    tools=...,                 # additive domain tools
    system_prompt=...,         # USER authored instructions
    middleware=...,            # merge/replace into default stack
    subagents=...,             # SubAgent | CompiledSubAgent | AsyncSubAgent
    skills=...,                # list of source paths
    memory=...,                # list of AGENTS.md paths
    permissions=...,           # list[FilesystemPermission]
    backend=...,               # default StateBackend()
    interrupt_on=...,          # tool name → bool | InterruptOnConfig
    response_format=...,
    state_schema=...,
    context_schema=...,
    checkpointer=...,
    store=...,
    debug=False,
    name=...,
    cache=...,
) -> CompiledStateGraph
```

## create_agent (Path B core)

```python
from langchain.agents import create_agent

create_agent(
    model,
    tools=...,
    system_prompt=...,
    middleware=...,
    checkpointer=...,
    # ... response_format, context_schema, etc.
)
```

## Key imports

```python
from deepagents import create_deep_agent, FilesystemPermission, HarnessProfile
from deepagents.backends import (
    StateBackend,
    FilesystemBackend,
    StoreBackend,
    CompositeBackend,
    LocalShellBackend,
)
from deepagents.middleware import (
    FilesystemMiddleware,
    SkillsMiddleware,
    SubAgentMiddleware,
    PatchToolCallsMiddleware,
)
from deepagents.middleware.summarization import create_summarization_middleware
from deepagents.middleware.subagents import GENERAL_PURPOSE_SUBAGENT
from langchain.agents.middleware import (
    TodoListMiddleware,
    PIIMiddleware,
    ToolCallLimitMiddleware,
    ModelCallLimitMiddleware,
    HumanInTheLoopMiddleware,
)
```

## FilesystemPermission

```python
FilesystemPermission(
    operations=["read", "write"],
    paths=["/workspace/**"],
    mode="allow",  # allow | deny | interrupt
)
```

## Invoke shape

```python
config = {
    "configurable": {"thread_id": "..."},
    "recursion_limit": 9999,
}
agent.invoke(
    {"messages": [{"role": "user", "content": "..."}]},
    config=config,
    context=Context(...),  # if context_schema set
)
```

HITL resume: `Command(resume={"decisions": [...]})` with same `thread_id` and `version="v2"`.

## HITL (quick)

| Knob | Notes |
|------|-------|
| `interrupt_on` | tool → `True` \| `False` \| `{allowed_decisions, when?}` |
| Decisions | `approve` \| `edit` \| `reject` \| `respond` (ask_user only) |
| FS pause | `FilesystemPermission(..., mode="interrupt")` ≥0.6.8 |
| Conditional | `when: (ToolCallRequest) -> bool` (langchain≥1.3.3) |
| Batch | One interrupt for all gated tools in a turn; match order |
| Factory | `_merge_fs_interrupt_on` + `HumanInTheLoopMiddleware.after_model` |
| Reject vs respond | `ToolMessage` status `error` vs `success` |

Details / Path B: [human-in-the-loop.md](human-in-the-loop.md).

## Built-in tools

| Tool | Notes |
|------|-------|
| `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep` | Via FilesystemMiddleware |
| `execute` | Sandbox / LocalShell only |
| `task` | SubAgentMiddleware when sync subagents present |
| `write_todos` | TodoListMiddleware only |
| Interpreter `eval` / dynamic `task()` | `CodeInterpreterMiddleware` (beta; see dynamic-subagents) |

## Memory vs skills

| | `memory=` | `skills=` |
|--|-----------|-----------|
| Middleware | `MemoryMiddleware` | `SkillsMiddleware` |
| Startup | Full file content in prompt | Index only |
| Persist across threads | Needs Store/disk route | Same (files on backend) |

## Context engineering (quick)

| Knob | API |
|------|-----|
| Per-run config | `context_schema=` + `context=` |
| Checkpointed custom fields | `state_schema=` |
| Large tool I/O | Built-in offload (~20k tokens) → backend paths |
| Long history | Built-in summarization (~85% window) |
| Agent-triggered compact | `create_summarization_tool_middleware(model, backend)` |
| Isolate heavy work | `task` / subagents |

Details: [context-engineering.md](context-engineering.md).

## Send / map-reduce (quick)

| Knob | Notes |
|------|-------|
| Import | `from langgraph.types import Send` |
| Shape | `Send("worker_node", {"item": x})` |
| Wire | Conditional edge returns `list[Send]`; list allowed destinations |
| Fan-in | `Annotated[list[T], operator.add]` (or `add_messages`) |
| Under deep agent | `CompiledSubAgent(runnable=compiled_graph)` |

Not part of Path A factory — custom `StateGraph`. Details: [send-api.md](send-api.md).

## Graph engineering (quick)

| Idea | Prefer |
|------|--------|
| Open-ended tool agent | Path A `create_deep_agent` |
| Fixed stages + hard gates | Explicit `StateGraph` |
| Runtime N workers | `Send` map-reduce |
| Risk HITL / revise loops | Routes in code + checkpointer |

Details: [graph-engineering.md](graph-engineering.md).

## Version notes (from docs)

| Feature | Approx. version |
|---------|-----------------|
| Permissions | `deepagents>=0.5.2` |
| Permission `interrupt` mode | `>=0.6.8` |
| `delete` tool / FS tools allowlist | `>=0.7` |
| TodoListMiddleware default | **Removed** in v0.7 (opt-in) |
| `rt.server_info` namespaces | `>=0.5.0` |

## Upstream links

- https://docs.langchain.com/oss/python/deepagents/overview
- https://docs.langchain.com/oss/python/deepagents/customization
- https://docs.langchain.com/oss/python/deepagents/backends
- https://docs.langchain.com/oss/python/deepagents/memory
- https://docs.langchain.com/oss/python/deepagents/context-engineering
- https://docs.langchain.com/oss/python/deepagents/human-in-the-loop
- https://docs.langchain.com/oss/python/deepagents/dynamic-subagents
- https://docs.langchain.com/oss/python/langgraph/use-graph-api#map-reduce-and-the-send-api
- https://www.analyticsvidhya.com/blog/2026/07/graph-engineering/
- https://docs.langchain.com/oss/python/langchain/deep-agent-from-scratch
- https://github.com/langchain-ai/deepagents
