# 02 — Runtime & State Model

## 1. Executive Summary

The platform treats agent execution as an **explicit state machine**. Runtime State and Thread State are canonical JSON-shaped contracts. Implicit chat buffers are insufficient for interrupt, resume, replay, audit, or multi-writer safety.

## 2. Purpose

Define what state exists, who owns it, how it changes, and how it is shown to architects and coding agents via diagrams and JSON.

## 3. Scope

Runtime State, Thread State, Session, User identity binding, and relationships to checkpoints. Memory domain payloads are referenced by id, not inlined as source of truth.

## 4. Architecture Overview

See [../assets/diagrams/02-state-model.mmd](../assets/diagrams/02-state-model.mmd)

```
Session → Thread(s) → Runtime State → Checkpoints (history)
                ↘ Context Package (ephemeral per step)
```

## 5. Core Concepts

- **User:** authenticated principal (`user_id` from JWT).
- **Session:** auth-bound interaction window.
- **Thread:** durable conversation/execution lineage.
- **Runtime State:** current graph status, node, interrupt payload, pointers.
- **Thread State:** messages + channel values.
- **Checkpoint:** durable encoding of Thread/Runtime slice.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| R1 | State is explicit and versioned |
| R2 | Large artifacts stored by reference |
| R3 | Identity always copied from validated token into state metadata |
| R4 | UI may project state but is not the system of record |

## 7. Decision Rationale

Explicit contracts enable multi-agent tooling, tests, and replay. References keep state small. Token-derived identity prevents spoofed ownership.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Stateless request/response agents | No HITL or recovery |
| UI Redux as source of truth | Lost on refresh; untrusted |
| Opaque binary blobs only | Poor explainability |

## 9. Tradeoffs

More schema discipline up front; far less ambiguity later.

## 10. Component Breakdown

### State Owner: Orchestrator

- **Purpose:** Mutate Runtime/Thread State according to graph semantics.
- **Responsibilities:** Transitions, checkpointing, interrupt markers.
- **Non-responsibilities:** Semantic fact curation; skill authoring.
- **Inputs:** Commands, tool results, approvals.
- **Outputs:** New state versions, events.
- **Lifecycle:** Thread create → active → terminal → archive.
- **Failure Modes:** Invalid transition, schema drift.
- **Recovery:** Reject illegal transition; restore checkpoint.
- **Security:** Thread ACL by user/org.
- **Scalability:** Immutable checkpoint history; current pointer.

## 11. Sequence of Operations

1. Create Session from auth.
2. Create Thread with empty Thread State.
3. Each step: load state → assemble context → act → reduce state → checkpoint.
4. Interrupt: set status awaiting_approval; persist payload.
5. Resume: validate Approval; apply input; continue.
6. Complete: terminal status; emit events.

See [../assets/diagrams/02-state-transitions.mmd](../assets/diagrams/02-state-transitions.mmd)

## 12. State Changes

| Field | Updated when |
|-------|--------------|
| status | lifecycle events |
| current_node | graph advance |
| messages | user/tool/model turns |
| interrupt | HITL pause |
| checkpoint_id | after save |
| skill_pins | loader resolve |

## 13. Mermaid Diagrams

Linked in §4 and §11.

## 14. JSON Contracts

- [contracts/runtime-state.json](contracts/runtime-state.json)
- [contracts/thread-state.json](contracts/thread-state.json)
- [contracts/session.json](contracts/session.json)
- [contracts/user.json](contracts/user.json)

## 15. Best Practices

- Include `schema_version` on all state objects.
- Emit domain events on every terminal and interrupt transition.
- Document legal transitions in one state diagram.

## 16. Anti-patterns

- Mutable in-place history without checkpoint ids.
- Storing raw secrets in channel values.
- Divergent “frontend state” and “backend state” without projection rules.

## 17. Common Mistakes

- Reusing one thread across unrelated engagements without reset policy.
- Omitting `user_id` on thread metadata.
- Treating tool failures as silent no-ops in state.

## 18. Future Evolution

Multi-graph parent/child state; time-travel debug UI; verified state hashes.

## 19. Related Documents

[04-short-term-memory.md](04-short-term-memory.md) · [09-checkpoints-interrupt-resume.md](09-checkpoints-interrupt-resume.md) · [08-context-construction.md](08-context-construction.md)
