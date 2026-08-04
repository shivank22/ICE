# Memory

Long-term memory for Deep Agents is **filesystem-backed**. Docs: https://docs.langchain.com/oss/python/deepagents/memory

## What it is / isn’t

| Kind | Mechanism | Lifetime |
|------|-----------|----------|
| Long-term memory | `memory=` files + `MemoryMiddleware` on a durable backend | Across threads/conversations |
| Skills (procedural) | `skills=` progressive disclosure | On-demand how-to |
| Short-term | Messages + StateBackend scratch + checkpointer | Single thread |

## How it works

1. Pass paths to `memory=` (e.g. `/memories/AGENTS.md`)
2. Backend stores the files (`StoreBackend` route recommended for cross-thread)
3. At startup, `MemoryMiddleware` loads those files into the system prompt (always-on — **not** skills-style index-only)
4. Agent may update memory with `edit_file` / `write_file` when writable
5. Optional background consolidation between conversations

## Scoping (namespace)

Backend namespace controls isolation:

| Scope | Example namespace | Notes |
|-------|-------------------|-------|
| Agent | `(assistant_id,)` | Shared across all users of that assistant |
| User | `(user_id,)` | Recommended multi-tenant default |
| Org / policies | `(org_id,)` | Usually read-only; populate from app code |

```python
StoreBackend(namespace=lambda rt: (rt.server_info.user.identity,))
```

Requires `deepagents>=0.5.0` for `rt.server_info` helpers (older: config metadata).

## Typical Composite setup

```python
CompositeBackend(
    default=StateBackend(),
    routes={
        "/memories/": StoreBackend(
            namespace=lambda rt: (rt.server_info.user.identity,),
        ),
    },
)
```

Pass the same paths in `memory=["/memories/AGENTS.md"]` (or `preferences.md`, etc.).

## Read-only vs writable

- **Writable (default):** agent can learn preferences into memory files
- **Read-only:** org policies / compliance — deny writes with `FilesystemPermission` on those paths; write only from application code

Shared writable memory is a **prompt-injection** vector across users.

## Advanced (pointers)

- **Episodic memory** — richer past-experience records beyond AGENTS.md facts (see upstream memory docs)
- **Background consolidation** — update memory between conversations
- **Concurrent writes** — design for single-writer or merge carefully
- **Multiple agents** — separate Store namespaces per assistant

## Contrast with skills

| | Memory | Skills |
|--|--------|--------|
| Param | `memory=` | `skills=` |
| Startup | Full file(s) in prompt | Name/description index only |
| Body load | Already loaded | `read_file` on demand |
| Typical content | Preferences, persona, facts | Workflows, domain procedures |

## See also

- [../programs/configure-memory.md](../programs/configure-memory.md)
- [backends.md](backends.md)
- [skills-loading.md](skills-loading.md)
