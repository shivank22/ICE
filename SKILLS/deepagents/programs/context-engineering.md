# Program: context-engineering

Control what the deep agent sees and how context stays within limits across long runs.

Docs: https://docs.langchain.com/oss/python/deepagents/context-engineering

## Inputs

- Role / system prompt, optional memory + skills
- Per-run data (user id, API keys) vs checkpointed custom state
- Expectation of large tool outputs / long threads

## Checklist

```
Task Progress:
- [ ] Step 1: Map context types needed
- [ ] Step 2: Shape input context (prompt, memory, skills, tools)
- [ ] Step 3: Add runtime context_schema if tools need per-run config
- [ ] Step 4: Add state_schema only for mutable checkpointed fields
- [ ] Step 5: Rely on built-in offload + summarization; optional summarization tool
- [ ] Step 6: Isolate heavy work with task/subagents
- [ ] Step 7: Route /memories/ for cross-thread persistence
```

### Step 1: Map types

| Type | What | Scope |
|------|------|-------|
| Input | system prompt, memory, skills, tool schemas | Every run |
| Runtime | `context=` / `context_schema` | Per invoke; propagates to subagents |
| Compression | Offload large I/O + summarize history | Automatic |
| Isolation | Subagents return one report | Per `task` |
| Long-term | Files on Store/disk via backend | Across threads |

### Step 2: Input context

1. **`system_prompt=`** — role + behavior (static). Use `@dynamic_prompt` middleware only when prompt must depend on `runtime.context` / store.
2. **`memory=`** — always-loaded; keep small. Details: [configure-memory.md](configure-memory.md)
3. **`skills=`** — progressive disclosure. Details: [skills-progressive-disclosure.md](skills-progressive-disclosure.md)
4. **Tools** — unused built-ins still cost tokens; use harness `excluded_tools` for tools the agent must never call

### Step 3: Runtime context

```python
from dataclasses import dataclass

@dataclass
class Context:
    user_id: str
    api_key: str

agent = create_deep_agent(model=..., context_schema=Context)
agent.invoke(
    {"messages": [...]},
    config={"configurable": {"thread_id": "..."}},
    context=Context(user_id="u1", api_key="..."),
)
```

Use for immutable per-run config. Tools get `runtime.context` via `ToolRuntime` without extra middleware.

### Step 4: Custom state

Use `state_schema=` for **mutable** fields that must checkpoint with the thread. Prefer runtime context for IDs/keys/flags.

Declarative `SubAgent` specs inherit parent `state_schema`; `CompiledSubAgent` / async do not.

### Step 5: Compression (built-in)

Every `create_deep_agent` includes offloading + summarization — no extra middleware required for basics.

| Mechanism | Trigger (defaults) | Effect |
|-----------|--------------------|--------|
| Offload inputs/results | ~20k tokens | Write to backend; leave path + short preview |
| Summarization | ~85% of model `max_input_tokens` | Compact older messages; keep ~10% recent |

Optional agent-triggered compaction:

```python
from deepagents.middleware.summarization import create_summarization_tool_middleware

middleware=[create_summarization_tool_middleware(model, backend)]
```

Does not disable automatic summarization. Filter stream tokens with `metadata["lc_source"] == "summarization"` if needed.

### Step 6: Isolation

Delegate output-heavy multi-step work via `task` so the parent only gets the final report. Instruct subagents to return concise summaries; write large artifacts to the filesystem.

See [plan-and-decompose.md](plan-and-decompose.md).

### Step 7: Long-term

Composite `/memories/` → Store (+ `memory=` or prompt the agent to `write_file` there). See [configure-memory.md](configure-memory.md).

## Best practices (upstream)

1. Minimal memory; detailed workflows in skills  
2. Subagents for heavy work  
3. Constrain subagent output size in their system prompts  
4. Prefer files + `read_file`/`grep` over stuffing huge blobs into messages  
5. Document `/memories/` layout in the system prompt  
6. Pass tool config via `context=`

## See also

- [../references/context-engineering.md](../references/context-engineering.md)
- https://docs.langchain.com/oss/python/deepagents/context-engineering
