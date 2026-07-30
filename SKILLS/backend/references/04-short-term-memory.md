# 04 — Short-Term Memory

## 1. Executive Summary

Short-Term Memory (STM) is the conversation and execution working set for a durable thread. In LangGraph it is **graph state** persisted by a **checkpointer**—not by the long-term **Store**. STM answers where the agent is right now—not what the organization knows forever.

## 2. Purpose

Provide recoverable, interruptible execution state without overloading semantic or procedural stores.

## 3. Scope

Thread messages, channel values, checkpoint lifecycle, interrupt/resume/replay as they relate to STM. Semantic facts live in Store ([05](05-semantic-memory.md)); skill bodies are loaded by the Skill Resolver Service ([06](06-procedural-memory-skills.md), [19](19-skill-platform-lifecycle.md)).

## 4. Architecture Overview

Orchestrator runs a LangGraph compiled with `checkpointer=...`. Clients never write checkpoints directly. Optional `store=...` is separate long-term memory.

See [../assets/diagrams/04-stm-checkpoint-flow.mmd](../assets/diagrams/04-stm-checkpoint-flow.mmd) · [langgraph-bindings.md](langgraph-bindings.md)

| Concern | Binding |
|---------|---------|
| STM persistence | Checkpointer (`PostgresSaver` prod) |
| Messages | State channel + reducer (e.g. `add_messages` / `MessagesState`) |
| Cross-thread facts | Store (not checkpointer) |
| Thread key | `configurable.thread_id` |

## 5. Core Concepts

- **Messages:** ordered conversational turns and tool results in the thread state.
- **Channel values:** typed graph state fields beyond messages (with reducers where needed).
- **Checkpoint:** versioned durable snapshot keyed by `thread_id` (+ `checkpoint_id`, optional `checkpoint_ns`).
- **Parent checkpoint:** lineage for resume and time travel.
- **Idempotent nodes:** required because `interrupt()` resume **re-runs the node from the start**.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| S1 | Postgres (or equivalent) checkpointer in production (`PostgresSaver`) |
| S2 | Single writer: compiled LangGraph + checkpointer |
| S3 | Do not embed full semantic `Memory.md` documents into every checkpoint—reference Store keys |
| S4 | Interrupt via `interrupt()`; status projections derived from snapshot |
| S5 | Configure subgraph checkpointing when nested HITL is required |

## 7. Decision Rationale

ACID checkpoints make resume correct after process death. Single writer avoids fork confusion. Keeping semantic content in Store keeps checkpoints small and namespaces enforceable. Idempotent nodes prevent duplicate side effects on resume.

## 8. Alternatives Considered

| Alternative | Why secondary |
|-------------|---------------|
| In-memory only (`InMemorySaver`) | Lost on restart; unsuitable for HITL prod |
| Object storage custom checkpoints | Reinvents checkpointer; weaker integration |
| Client-held state | Untrusted and non-auditable |
| Stuffing LTM into STM | Wrong retention and RBAC model |

## 9. Tradeoffs

Durable checkpoints add latency and storage. Worth it for enterprise HITL and audit. Apply TTL/prune policies.

## 10. Component Breakdown

### Short-Term Memory Runtime (LangGraph + Orchestrator facade)

- **Purpose:** Maintain live thread state and flush checkpoints via LangGraph.
- **Responsibilities:** Invoke/stream graphs; append messages via reducers; expose `get_state` / history; map interrupts.
- **Non-responsibilities:** Long-term fact storage (Store); skill versioning; implementing custom checkpoint SQL.
- **Inputs:** User/tool events, `Command(resume=...)`.
- **Outputs:** Updated snapshots; Checkpoint records in checkpointer backend; DTO projections.
- **Dependencies:** Checkpointer, identity (`thread_id`, `user_id` metadata).
- **Lifecycle:** Created with thread; archived with retention policy.
- **Failure Modes:** Partial write at DB layer, serialization errors.
- **Recovery:** Retry idempotent steps; restore last valid checkpoint via LangGraph.
- **Security:** Authorize thread access by user/org RBAC.
- **Scalability:** Partition by `thread_id`; prune old checkpoints per policy.

## 11. Sequence of Operations

1. Create or load thread (`thread_id`).
2. LangGraph restores latest checkpoint on invoke (if any).
3. Assemble context (reads Store / skill pins; does not replace STM).
4. Execute node; reducers update messages/channels; checkpointer saves.
5. On interrupt: `interrupt(payload)` after any pre-gate logic that is safe to re-run; irreversible effects only after resume.
6. On resume: same `thread_id` + `Command(resume=...)`.

Algorithms: [../programs/checkpoint-save.md](../programs/checkpoint-save.md), [../programs/checkpoint-restore.md](../programs/checkpoint-restore.md)

## 12. State Changes

See [../assets/diagrams/04-stm-state.mmd](../assets/diagrams/04-stm-state.mmd)

| State (projection) | Meaning |
|--------------------|---------|
| empty | New thread |
| running | Active execution (`next` non-empty, no open interrupt) |
| checkpointed | Durable snapshot exists (always after steps with checkpointer) |
| awaiting_input | Open interrupt on snapshot |
| completed | Terminal success |
| failed | Terminal or retryable failure |

## 13. Mermaid Diagrams

Linked in §4 and §12.

## 14. JSON Contracts

- [contracts/runtime-state.json](contracts/runtime-state.json)
- [contracts/thread-state.json](contracts/thread-state.json)
- [contracts/checkpoint.json](contracts/checkpoint.json)

## 15. Best Practices

- Store tool outputs by reference when large; keep digests in messages.
- Record `checkpoint_ns` / graph id for multi-graph platforms.
- Define max checkpoint history / TTL per thread.
- Keep nodes idempotent through `interrupt()`.
- Encrypt checkpoint payloads when required (platform/LangGraph encryption options).

## 16. Anti-patterns

- Using STM as the only CRM/knowledge base.
- Letting the UI patch checkpoint JSON arbitrarily.
- Dual checkpointers / custom writers for the same thread.
- Irreversible side effects before `interrupt()` in the same node without guards.

## 17. Common Mistakes

- Forgetting a checkpointer when using interrupts.
- Resuming without validating Approval identity.
- Re-passing initial state instead of `Command(resume=...)`.
- Treating message history as unordered / omitting reducers.

## 18. Future Evolution

Cross-region checkpoint replication; differential checkpoints; encrypted checkpoint payloads.

## 19. Related Documents

[02-runtime-state-model.md](02-runtime-state-model.md) · [langgraph-bindings.md](langgraph-bindings.md) · [09-checkpoints-interrupt-resume.md](09-checkpoints-interrupt-resume.md) · [05-semantic-memory.md](05-semantic-memory.md)
