# Program: configure-memory

Wire long-term memory for Deep Agents. Memory is **filesystem-backed**: files on a backend, loaded via `memory=` + `MemoryMiddleware`. Distinct from short-term thread state (messages / scratch) and from skills (progressive disclosure).

Docs: https://docs.langchain.com/oss/python/deepagents/memory

## Inputs

- Scope: agent-wide vs per-user vs org policies
- Backend that can persist across threads (`StoreBackend` / disk / Hub)
- Whether the agent may write memory (default) or must stay read-only

## Checklist

```
Task Progress:
- [ ] Step 1: Choose scope + namespace
- [ ] Step 2: Route /memories/ on CompositeBackend
- [ ] Step 3: Pass memory= paths
- [ ] Step 4: Seed initial AGENTS.md / preferences
- [ ] Step 5: Read-only permissions for shared policies
- [ ] Step 6: Verify across two thread_ids
```

### Step 1: Choose scope

| Scope | Namespace idea | Use |
|-------|----------------|-----|
| Agent-scoped | `(assistant_id,)` | Shared persona / learned style for all users |
| User-scoped | `(user_id,)` | Per-user preferences (recommended multi-tenant default) |
| Org / policies | `(org_id,)` | Brand/compliance — usually **read-only** |

Short-term chat history is **not** this — it lives in checkpointer/state. See [context-engineering.md](context-engineering.md) for offload, summarization, and runtime context.

### Step 2: Backend route

```python
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/memories/": StoreBackend(
            namespace=lambda rt: (rt.server_info.user.identity,),
        ),
    },
)
```

Always set a namespace factory for multi-user Store. Pass `store=` to `create_deep_agent` when using StoreBackend.

### Step 3: memory=

```python
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    memory=["/memories/AGENTS.md"],  # or preferences.md, etc.
    backend=backend,
    store=store,
)
```

Unlike skills: memory files are **always loaded** into context at startup (via `MemoryMiddleware`), not index-only.

Skills remain separate: `skills=` for procedural how-to; memory for durable preferences/facts.

### Step 4: Seed + updates

- Seed Store / disk with initial markdown before first invoke
- Agent can `edit_file` / `write_file` memory paths when writable
- Optional: background consolidation between conversations (see reference)

### Step 5: Read-only shared memory

For org policies / shared instructions, deny writes:

```python
from deepagents import FilesystemPermission

permissions = [
    FilesystemPermission(
        operations=["write"],
        paths=["/policies/**", "/memories/org/**"],
        mode="deny",
    ),
]
```

Prevents prompt injection via shared writable memory.

### Step 6: Verify

1. Thread A: user states a preference; agent updates `/memories/...`
2. Thread B (new `thread_id`, same user namespace): agent applies the preference

## Failure modes

| Symptom | Fix |
|---------|-----|
| Memory forgotten next thread | Route `/memories/` to Store (not State-only) |
| User A sees User B prefs | Fix namespace to include user identity |
| Agent rewrites org policy | Deny write on policy paths |
| Memory empty at startup | Seed file; check `memory=` path matches backend |

## See also

- [../references/memory.md](../references/memory.md)
- [choose-backend.md](choose-backend.md)
- [../examples/memory_agent.py](../examples/memory_agent.py)
- Skills vs memory: [skills-progressive-disclosure.md](skills-progressive-disclosure.md)
