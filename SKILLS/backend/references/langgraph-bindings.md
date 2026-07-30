# LangGraph Bindings (default stack)

## Executive Summary

This pack’s **default orchestration binding is LangGraph**. Platform layers (skill index + Skill Resolver Service, context assembly, approval, episodic reflection) build **on top** of LangGraph primitives. Do not reimplement checkpointers, stores, interrupt/resume, or time travel.

Official docs:

- [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) — checkpointer vs store
- [Checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers)
- [Stores](https://docs.langchain.com/oss/python/langgraph/stores)
- [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [Time travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel)
- [Long-term memory](https://docs.langchain.com/oss/python/langchain/long-term-memory)
- [Graph API / reducers](https://docs.langchain.com/oss/python/langgraph/graph-api)

## Binding table

| Platform concern | LangGraph / LangChain primitive | Typical prod class | Build on top? |
|------------------|----------------------------------|--------------------|---------------|
| Short-term / thread state | Checkpointer | `PostgresSaver` | No — configure |
| Messages channel | State + reducer | `MessagesState` / `add_messages` | Schema only |
| Semantic / cross-thread facts | Store | `PostgresStore` (+ `index=`) | Thin RBAC facade OK |
| HITL pause | `interrupt(value)` | — | Approval UI/authz + API RunResult |
| HITL continue | `Command(resume=...)` | — | ResumeRun API (`command.resume`); map Approval → resume |
| HTTP scaffold (optional product) | Agent Server Thread/Run APIs | LangSmith Deployment | Or self-host same semantics — see [16-api-surface-interrupt-resume.md](16-api-surface-interrupt-resume.md) |
| Inspect / resume latest | `get_state`, invoke + `thread_id` | — | GetThreadState / ACL gateway |
| History / replay | `get_state_history` | — | Side-effect policy |
| Fork / branch | `update_state` | — | Audit + fork thread ids |
| Debug breakpoints | `interrupt_before` / `interrupt_after` | — | Not prod HITL |
| Procedural skills | — | `skill.yaml` → Postgres/pgvector; Discovery → records in context | **Yes** — doc 19; [../programs/skill-runtime-pipeline.md](../programs/skill-runtime-pipeline.md) |
| Skill materialize | — | **Skill Resolver Service** `lfs` \| `blob` | Customizable per use case |
| Skill execution | — | LangGraph nodes/tools using resolved `SKILL.md` | Same pin/locator contract |
| Context Package | — | Assembler; skill section = **index records** | **Yes** |
| Episodic / traces | — | LangSmith / Langfuse + episodes | **Yes** — see [17-langgraph-observability.md](17-langgraph-observability.md) |
| Evaluation runners | — | DeepEval / LangSmith + agentevals | **Yes** — see [18-evaluation-frameworks.md](18-evaluation-frameworks.md) |
| Skill promotion | — | Approval + `skill.yaml` status + CI re-index (+ blob publish when used) | **Yes** |

## Compile pattern (reference)

```text
checkpointer = PostgresSaver.from_conn_string(...)  # setup() as required
store = PostgresStore.from_conn_string(..., index=IndexConfig(...))  # setup() as required
graph = builder.compile(checkpointer=checkpointer, store=store)
config = {"configurable": {"thread_id": "<uuid>"}}
```

Dev may use `InMemorySaver` / `InMemoryStore`. Production must use durable backends.

## Hard rules (reject deviations)

1. **Single checkpoint writer** — the compiled graph + checkpointer. No parallel checkpoint tables for the same `thread_id`.
2. **Semantic memory defaults to Store** — `put` / `get` / `search` with JWT-derived namespace tuples. `Memory.md` is a **value field**, not a reason to invent a second SoR.
3. **Resume correctly** — same `thread_id` + `Command(resume=...)` via ResumeRun API. Do not re-pass initial graph input to continue. Do not set `checkpoint_id` unless time-traveling. Clients must not POST full message history to “continue.”
4. **Idempotent gated nodes** — resume re-executes the node from the start. Irreversible side effects only **after** `interrupt()` returns.
5. **HITL vs debug** — production approvals use `interrupt()`; static `interrupt_before`/`after` are for debugging/stepping.
6. **RuntimeState JSON is a DTO** — project from `StateSnapshot`; do not treat it as the durability layer.
7. **Subgraphs** — enable subgraph checkpointing when nested interrupts must resume correctly (`checkpoint_ns`).
8. **Retention** — prune/TTL checkpoints and Store items; unbounded history is an ops failure mode.
9. **Never auto-mutate production skills** from traces — reflection proposes; Approval promotes (platform).

## Ownership map (four memories)

| Domain | Owner primitive | Notes |
|--------|-----------------|-------|
| Short-term | Checkpointer | Thread-scoped |
| Semantic | Store | Cross-thread; namespace = JWT `user_id` (+ org/engagement) |
| Procedural | **skill.yaml → Skill Index**; Skill Resolver Service (`lfs` \| `blob`) | Discover → context records → Resolve → Execute — doc 19 |
| Episodic | Trace/episode platform | Feeds reflection; not a checkpointer substitute |

## What agents should emit for client repos

When scaffolding a LangGraph platform from this skill:

1. Stack Binding noting `PostgresSaver` + `PostgresStore` (or approved alternatives).
2. Graph state schema with reducers.
3. Interrupt gate nodes with idempotency notes.
4. Store namespace conventions.
5. DTO mapping: `StateSnapshot` → `RuntimeState`.
6. Skill platform + promotion policy (`skill.yaml` status + CI index; blob publish when used).
7. Context assembly order with skill **index records** (platform).
8. Skill pin authz + locator (`lfs` \| `blob`) requirements.

## Related Documents

[00-index.md](00-index.md) · [02-runtime-state-model.md](02-runtime-state-model.md) · [04-short-term-memory.md](04-short-term-memory.md) · [05-semantic-memory.md](05-semantic-memory.md) · [09-checkpoints-interrupt-resume.md](09-checkpoints-interrupt-resume.md) · [../SKILL.md](../SKILL.md)
