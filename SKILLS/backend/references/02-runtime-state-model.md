# 02 — Runtime & State Model

## 1. Executive Summary

The platform treats agent execution as an **explicit state machine** backed by LangGraph. **`StateSnapshot`** from `graph.get_state` / `get_state_history` is the system of record for in-flight thread execution. **`RuntimeState` and `ThreadState` JSON contracts are API projections (DTOs)** over that snapshot plus platform metadata—not a second checkpoint store.

## 2. Purpose

Define what state exists, who owns it, how it changes, and how it is shown to architects and coding agents via diagrams and JSON—without inventing a parallel durability layer beside LangGraph.

## 3. Scope

Runtime State (projection), Thread State (projection of channel values / messages), Session, User identity binding, and relationships to LangGraph checkpoints. Memory domain payloads are referenced by id, not inlined as source of truth.

## 4. Architecture Overview

See [../assets/diagrams/02-state-model.mmd](../assets/diagrams/02-state-model.mmd) · [langgraph-bindings.md](langgraph-bindings.md)

```
Session → Thread(s) → LangGraph StateSnapshot (checkpointer)
                ↘ RuntimeState / ThreadState DTOs (API projection)
                ↘ Context Package (ephemeral per step)
```

## 5. Core Concepts

- **User:** authenticated principal (`user_id` from JWT).
- **Session:** auth-bound interaction window.
- **Thread:** durable conversation/execution lineage (`thread_id` in LangGraph config).
- **StateSnapshot (LangGraph):** `values`, `next`, `config`, `tasks` / interrupts, `metadata`, `parent_config`.
- **Runtime State (DTO):** status, interrupt projection, skill pins, identity metadata for clients.
- **Thread State (DTO):** messages + channel values projected from `snapshot.values`.
- **Checkpoint:** durable encoding owned by the **checkpointer**; lineage via parent configs.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| R1 | LangGraph checkpointer is SoR; RuntimeState is a versioned projection |
| R2 | Large artifacts stored by reference in graph state |
| R3 | Identity always copied from validated token into config/metadata—never trust client `user_id` alone |
| R4 | UI may project state but is not the system of record |
| R5 | Prefer reducers (e.g. `add_messages`) for concurrent channel updates; document channel schemas |

## 7. Decision Rationale

Explicit contracts enable multi-agent tooling, tests, and replay. Projections keep APIs stable if LangGraph snapshot fields evolve. Token-derived identity prevents spoofed ownership. Reducers prevent lost updates on parallel nodes.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Stateless request/response agents | No HITL or recovery |
| UI Redux as source of truth | Lost on refresh; untrusted |
| Custom RuntimeState DB written beside checkpointer | Dual writers; fork confusion |
| Opaque binary blobs only | Poor explainability |

## 9. Tradeoffs

More schema discipline up front; far less ambiguity later. Projection mapping code must stay thin and tested.

## 10. Component Breakdown

### State Owner: Orchestrator (LangGraph runtime)

- **Purpose:** Execute graphs; persist via checkpointer; expose snapshots.
- **Responsibilities:** Transitions via graph edges; `interrupt` / resume; project DTOs; attach identity metadata.
- **Non-responsibilities:** Semantic fact curation (Store); skill authoring.
- **Inputs:** Commands, tool results, `Command(resume=...)`, approvals.
- **Outputs:** New checkpoints; events; DTO projections.
- **Lifecycle:** Thread create → active → terminal → archive.
- **Failure Modes:** Invalid transition, schema drift, checkpointer outage.
- **Recovery:** Reject illegal client updates; resume from last good snapshot.
- **Security:** Thread ACL by user/org.
- **Scalability:** Immutable checkpoint history; shard by `thread_id`.

## 11. Sequence of Operations

1. Create Session from auth.
2. Create Thread; first invoke with `thread_id` (empty or initial state).
3. Each step: LangGraph loads checkpoint → node runs (optional context assembly) → reducers update state → checkpointer saves.
4. Interrupt: node calls `interrupt(payload)`; snapshot shows interrupts; project `awaiting_approval`.
5. Resume: validate Approval; `Command(resume=...)` with same `thread_id`.
6. Complete: terminal status; emit events.

See [../assets/diagrams/02-state-transitions.mmd](../assets/diagrams/02-state-transitions.mmd)

## 12. State Changes

| Field (DTO) | Updated when |
|-------------|--------------|
| status | Derived from snapshot (`next`, interrupts, errors) + platform terminal markers |
| current_node | From snapshot `next` / task metadata |
| messages | From `values` (messages channel) |
| interrupt | Mapped from LangGraph interrupt values |
| checkpoint_id | From snapshot `config.configurable` |
| skill_pins | Platform metadata from Discovery / Resolver (`skill_id` + `version` + description + `locator`) |

## 13. Mermaid Diagrams

Linked in §4 and §11.

## 14. JSON Contracts

- [contracts/runtime-state.json](contracts/runtime-state.json) — projection
- [contracts/thread-state.json](contracts/thread-state.json) — projection of `values`
- [contracts/session.json](contracts/session.json)
- [contracts/user.json](contracts/user.json)

## 15. Best Practices

- Include `schema_version` on DTO projections.
- Document graph state TypedDict / pydantic schema separately from DTOs.
- Emit domain events on every terminal and interrupt transition.
- Use `MessagesState` / `add_messages` patterns unless a deliberate alternative exists.

## 16. Anti-patterns

- Mutable in-place history without checkpoint ids.
- Storing raw secrets in channel values.
- Divergent “frontend state” and checkpointer state without projection rules.
- Writing a custom checkpoint table for the same `thread_id`.

## 17. Common Mistakes

- Reusing one thread across unrelated engagements without reset policy.
- Omitting `user_id` on thread metadata.
- Treating tool failures as silent no-ops in state.
- Re-passing full prior state as invoke input when intending to resume.

## 18. Future Evolution

Multi-graph parent/child state (`checkpoint_ns`); time-travel debug UI on `get_state_history`; verified state hashes.

## 19. Related Documents

[langgraph-bindings.md](langgraph-bindings.md) · [04-short-term-memory.md](04-short-term-memory.md) · [09-checkpoints-interrupt-resume.md](09-checkpoints-interrupt-resume.md) · [08-context-construction.md](08-context-construction.md)
