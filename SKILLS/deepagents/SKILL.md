---
name: langchain-deepagents
description: >-
  Write LangChain Deep Agents with create_deep_agent, or reconstruct the same
  harness via create_agent by knowing what happens behind the factory: middleware
  stack, skills progressive disclosure, backends (State/Filesystem/Store/Composite/Sandbox),
  long-term memory (AGENTS.md / MemoryMiddleware), context engineering
  (offload/summarization/runtime context), write_todos planning,
  task/subagent decomposition, dynamic subagents (interpreter/QuickJS),
  human-in-the-loop (interrupt_on / decisions / resume), and
  guardrails (permissions/HITL/PII/limits). Use when building deep agents,
  debugging the deepagents stack, or assembling a deep-agent-like LangGraph agent.
---

# LangChain Deep Agents

You enable writing a **Deep Agent** in two ways:

**Path A — Factory:** call `create_deep_agent(...)` with correct params (model, tools, backend, skills, memory, todos, guardrails, invoke).

**Path B — Internals:** know everything behind `create_deep_agent` well enough to rebuild equivalent behavior with `create_agent` + Deep Agents middleware (or explain/debug any layer).

Both paths produce a LangGraph `CompiledStateGraph`. `create_deep_agent` is a thin factory over LangChain `create_agent` plus an opinionated middleware/backend stack — never a black box.

For ICE platform architecture (skill CI, Thread/Run APIs, Store ownership contracts), defer to [`../backend/`](../backend/).

## Mental model

```text
Agent = Model + Harness
Harness = system prompt + tools + middleware around the ReAct tool-calling loop
Deep Agents = opinionated harness on create_agent + LangGraph runtime
```

`create_agent` **is** the ReAct loop. Do not hand-roll a `while` tool loop.

## Decision

| Situation | Path |
|-----------|------|
| Ship a deep agent quickly | **A** — `create_deep_agent` |
| Fork the stack, teach internals, or debug a layer | **B** — assemble with `create_agent` |
| Graph shape is not an agent loop | Custom LangGraph (optionally as a `CompiledSubAgent`) |

Prefer Path A unless Path B is required.

## Under-the-hood cheat sheet

| Layer | What the factory wires | Symbol |
|-------|------------------------|--------|
| Runtime | ReAct loop on LangGraph | `create_agent` |
| Authored prompt | `USER` → profile `BASE` → `SUFFIX` | `system_prompt`, `HarnessProfile` |
| Skills | Frontmatter index in system prompt; body via `read_file` | `SkillsMiddleware` |
| Filesystem | Built-in FS tools + permissions | `FilesystemMiddleware` |
| Backends | State / disk / Store / Hub / sandbox / LocalShell / Composite | `backend=` |
| Planning | Opt-in todos (v0.7+ not default) | `TodoListMiddleware` |
| Decomposition | Default `task` + general-purpose subagent | `SubAgentMiddleware` |
| Dynamic subagents | Fan-out from interpreter JS via `task()` | `CodeInterpreterMiddleware` (beta) |
| Context | Offload + summarization + isolation + runtime/state schemas | See context-engineering |
| Resume hygiene | Repair dangling tool calls | `PatchToolCallsMiddleware` |
| Memory | Always-loaded memory files (`AGENTS.md`, etc.) | `MemoryMiddleware` + durable backend |
| HITL | Pause tools; approve/edit/reject/respond; resume | `interrupt_on`, `HumanInTheLoopMiddleware` |
| Guardrails | Permissions, HITL, PII, call limits, sandbox | `permissions`, `interrupt_on`, middleware |

Required scaffolding (cannot exclude): `FilesystemMiddleware` + `SubAgentMiddleware`.

Full walk: [programs/under-the-hood.md](programs/under-the-hood.md).

## Progressive disclosure

Read only what the current request needs:

| Concern | Read |
|---------|------|
| Path A factory recipe | [programs/create-deep-agent.md](programs/create-deep-agent.md) |
| What the factory builds | [programs/under-the-hood.md](programs/under-the-hood.md) |
| Path B rebuild with `create_agent` | [programs/assemble-deep-like-agent.md](programs/assemble-deep-like-agent.md) |
| Skills in the system prompt | [programs/skills-progressive-disclosure.md](programs/skills-progressive-disclosure.md) |
| How tasks are planned/broken | [programs/plan-and-decompose.md](programs/plan-and-decompose.md) |
| Long-term memory (`memory=` / AGENTS.md) | [programs/configure-memory.md](programs/configure-memory.md) |
| Context engineering (offload / summarize / runtime) | [programs/context-engineering.md](programs/context-engineering.md) |
| Dynamic subagents (interpreter fan-out) | [programs/dynamic-subagents.md](programs/dynamic-subagents.md) |
| Choose State/FS/Store/Composite/Sandbox | [programs/choose-backend.md](programs/choose-backend.md) |
| Human-in-the-loop (interrupt / resume) | [programs/human-in-the-loop.md](programs/human-in-the-loop.md) |
| Permissions / HITL / PII / limits | [programs/apply-guardrails.md](programs/apply-guardrails.md) |
| Middleware order | [references/harness-middleware-stack.md](references/harness-middleware-stack.md) |
| Skills loading details | [references/skills-loading.md](references/skills-loading.md) |
| Planning + `task` semantics | [references/planning-and-decomposition.md](references/planning-and-decomposition.md) |
| Memory reference | [references/memory.md](references/memory.md) |
| Context engineering reference | [references/context-engineering.md](references/context-engineering.md) |
| Dynamic subagents reference | [references/dynamic-subagents.md](references/dynamic-subagents.md) |
| Backend catalog + security | [references/backends.md](references/backends.md) |
| HITL reference | [references/human-in-the-loop.md](references/human-in-the-loop.md) |
| Guardrails reference | [references/guardrails.md](references/guardrails.md) |
| Prompt / tool description fragments | [references/prompt-fragments.md](references/prompt-fragments.md) |
| API parameter map | [references/api-cheatsheet.md](references/api-cheatsheet.md) |
| Copyable examples | [examples/](examples/) |

## Workflow for agent sessions

```
Deep Agents session:
- [ ] Path A or Path B?
- [ ] Choose backend (Composite if disk or cross-thread memory)
- [ ] Orchestrator prompt: Plan → Context → Delegate → Verify → Synthesize
- [ ] Opt in TodoListMiddleware for multi-step work (recommended)
- [ ] Wire skills/memory paths that exist on the backend
- [ ] Shape context: lean memory, skills for detail, subagents for heavy I/O
- [ ] HITL: interrupt_on + checkpointer; resume with same thread_id
- [ ] Apply guardrails (permissions / interrupt_on / PII / limits)
- [ ] Path A: create_deep_agent(...)  OR  Path B: assemble create_agent stack
- [ ] Invoke with thread_id (+ context / store as needed)
- [ ] Verify: FS tools, skill index, task delegation, optional todos
```

## Hard rules (always)

1. **Never strip** `FilesystemMiddleware` or `SubAgentMiddleware` via `excluded_middleware` — required scaffolding.
2. **Skills need `read_file`** — `SkillsMiddleware` only injects the index; full `SKILL.md` is on-demand.
3. **`TodoListMiddleware` is opt-in** since deepagents v0.7 — pass it explicitly for classic planning.
4. **Wrap disk backends in `CompositeBackend`** — keep `/large_tool_results/` and `/conversation_history/` off project disk (default `StateBackend`).
5. **`virtual_mode=True`** on `FilesystemBackend` — default `False` provides no path sandboxing.
6. **Store backends need namespace factories** for multi-tenant isolation.
7. **Permissions ≠ sandbox safety** — path rules do not contain `execute` / LocalShell.
8. **Enforce boundaries at tool/sandbox level** — do not rely on the model to self-police.
9. **Do not hand-roll a ReAct while-loop** — use `create_agent` / `create_deep_agent`.
10. **Bias against premature subagent splits** — prefer one comprehensive `task` unless work is independent.
11. **Memory ≠ skills** — `memory=` is always loaded; skills are index-then-`read_file`. Scope Store namespaces per user/assistant.
12. **Shared memory is usually read-only** — deny agent writes on org/policy paths to avoid cross-user prompt injection.
13. **Dynamic subagents are beta** — need QuickJS interpreter; gate `eval` for HITL (inner interpreter `task()` bypasses parent `interrupt_on`).
14. **HITL needs a checkpointer** — resume with the same `thread_id`; decisions must match `action_requests` order; use `reject` (not `respond`) to deny side effects.

## Anti-patterns

- Treating Deep Agents as unrelated to `create_agent`
- Assuming `write_todos` is always present without opting in
- Bare `FilesystemBackend` mixing agent internals into the project tree
- Unscoped `StoreBackend` shared across all users
- Expecting StateBackend scratch to persist preferences across threads (use Store `/memories/`)
- Custom subagents expecting inherited `skills=` (they must set `"skills"` themselves)
- Parallel `write_todos` calls in one turn
- Splitting "research X" into overview/techniques/apps without independent aspects
- Using `LocalShellBackend` in multi-tenant production
- Relying on `interrupt_on={"task": True}` to approve interpreter fan-out (it won't)
- Resuming HITL on a different `thread_id` or with mismatched decision count/order
- Using `respond` to deny deletes/emails (model may treat it as success)

## Upstream

- [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)
- [Backends](https://docs.langchain.com/oss/python/deepagents/backends)
- [Memory](https://docs.langchain.com/oss/python/deepagents/memory)
- [Context engineering](https://docs.langchain.com/oss/python/deepagents/context-engineering)
- [Human-in-the-loop](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop)
- [Dynamic subagents](https://docs.langchain.com/oss/python/deepagents/dynamic-subagents)
- [Customization](https://docs.langchain.com/oss/python/deepagents/customization)
- [Build from scratch](https://docs.langchain.com/oss/python/langchain/deep-agent-from-scratch)
- [Going to production](https://docs.langchain.com/oss/python/deepagents/going-to-production)
- [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents)
