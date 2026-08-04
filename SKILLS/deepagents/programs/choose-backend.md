# Program: choose-backend

Pick and configure the pluggable filesystem (and optional shell) backend for a Deep Agent.

## Inputs

- Persistence needs (thread scratch vs cross-thread vs disk)
- Whether code/shell execution is required
- Multi-tenant vs single-user

## Checklist

```
Task Progress:
- [ ] Step 1: Classify needs
- [ ] Step 2: Select backend pattern
- [ ] Step 3: Configure routes / namespaces
- [ ] Step 4: Align skills/memory paths
- [ ] Step 5: Apply FS permissions / policy hooks
```

### Step 1: Classify needs

| Need | Implication |
|------|-------------|
| Scratch + tool-result offload only | `StateBackend` (default) |
| Real project files | Disk route under Composite |
| Memory across threads | `StoreBackend` route + namespace |
| Shell / pip / tests in prod | Sandbox backend |
| Trusted local CLI only | `LocalShellBackend` + HITL |

### Step 2: Select pattern

**Default (scratch):**

```python
# omit backend=  → StateBackend()
```

**Project files (recommended Composite):**

```python
from deepagents.backends import CompositeBackend, StateBackend, FilesystemBackend

backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/workspace/": FilesystemBackend(
            root_dir="/abs/path/to/project",
            virtual_mode=True,  # required for path sandboxing
        ),
    },
)
```

Never use bare `FilesystemBackend` for most apps — Deep Agents also writes `/large_tool_results/` and `/conversation_history/`; with bare disk those land in `root_dir`.

**Cross-thread memory:**

```python
from deepagents.backends import StoreBackend

backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/memories/": StoreBackend(
            namespace=lambda rt: (rt.server_info.user.identity,),
        ),
    },
)
```

**Production execute:** sandbox backend (LangSmith, E2B, Modal, Daytona, …) — not `LocalShellBackend`.

**LocalShellBackend:** host FS + host shell; **no isolation**. Dev CLIs only; HITL strongly recommended; never multi-tenant prod.

### Step 3: Routes and namespaces

- Composite routes by path prefix; longer/more specific routes win for matching paths
- Store: always set `namespace=` for multi-user (user / assistant+user / org)
- Permissions on Composite with sandbox **default** must be scoped under known non-sandbox route prefixes

### Step 4: Align skills / memory

`skills=` and `memory=` paths are resolved through the **same** backend. Place skill trees under a routed prefix the agent can `ls` / `read_file`.

### Step 5: Permissions / hooks

- `permissions=` — declarative allow/deny/interrupt for **built-in** FS tools only
- Backend **policy hooks** — custom validation (rate limits, audit, content inspection)
- Permissions do not cover custom tools or sandbox `execute`

Details: [../references/backends.md](../references/backends.md), [apply-guardrails.md](apply-guardrails.md).

## Decision quick table

| Backend | Persist | `execute`? | Use when |
|---------|---------|------------|----------|
| `StateBackend` | Thread (checkpointer) | No | Default scratch |
| `FilesystemBackend` | Disk | No | Local/CI files (`virtual_mode=True`) |
| `StoreBackend` | Cross-thread Store | No | Long-term memory |
| `ContextHubBackend` | LangSmith Hub | No | Durable without separate Store |
| Sandbox | Isolated provider | Yes | Prod code exec |
| `LocalShellBackend` | Host | Yes | Trusted local CLI only |
| `CompositeBackend` | Per-route | Per-route | Mix of the above |

## Failure modes

| Symptom | Fix |
|---------|-----|
| Internals polluting project | Composite + State default |
| Path escape | `virtual_mode=True` |
| Shared memory across users | Namespace factory |
| Permissions + sandbox default error | Scope permissions under routed prefixes |

## See also

- Example: [../examples/composite_backend.py](../examples/composite_backend.py)
- Docs: https://docs.langchain.com/oss/python/deepagents/backends
