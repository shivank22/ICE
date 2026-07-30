# 09 — Checkpoints, Interrupt, Resume, Replay

## 1. Executive Summary

LangGraph **checkpointers** make orchestration durable. **`interrupt()`** pauses for human or external input; **`Command(resume=...)`** continues with the same `thread_id`; **time travel** (`get_state_history`, `update_state`) supports audit and branching. Platform Approval/authz and side-effect guards wrap these primitives—they do not replace them.

## 2. Purpose

Specify save/restore semantics, HITL pause points, and recovery so architects bind correctly to LangGraph instead of inventing incompatible durability models.

## 3. Scope

Checkpoint lifecycle and control operations. Semantic/procedural stores are not checkpoint substitutes. See [langgraph-bindings.md](langgraph-bindings.md).

## 4. Architecture Overview

See [../assets/diagrams/09-checkpoint-lifecycle.mmd](../assets/diagrams/09-checkpoint-lifecycle.mmd) and [../assets/diagrams/09-interrupt-resume.mmd](../assets/diagrams/09-interrupt-resume.mmd)

| Operation | LangGraph API |
|-----------|----------------|
| Save | Automatic with checkpointer on graph steps |
| Restore / continue | Invoke with `thread_id` (latest) |
| Interrupt | `interrupt(payload)` inside node |
| Resume | `Command(resume=value)` + same `thread_id` |
| Inspect history | `get_state` / `get_state_history` |
| Fork | `update_state` then continue (new branch) |

Docs: [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) · [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) · [Time travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel)

## 5. Core Concepts

- **Checkpoint id / parent id:** lineage chain in checkpointer.
- **Interrupt payload:** JSON-serializable value passed to `interrupt()`; projected to clients as `InterruptPayload`.
- **Resume payload:** Approval or revision input via `Command(resume=...)`.
- **Node re-entry:** on resume, the interrupted **node restarts from the beginning**—code before `interrupt()` runs again.
- **Replay mode:** read-only history vs forked re-execution with side-effect guards.
- **Static breakpoints:** `interrupt_before` / `interrupt_after` for debug—not preferred for production HITL.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| K1 | Use LangGraph checkpointer; no parallel checkpoint writer |
| K2 | Production HITL uses `interrupt()`; static breakpoints for debug/test |
| K3 | Resume requires authz + matching open interrupt; then `Command(resume=...)` |
| K4 | Replay of external side effects is gated / simulated / forked by default |
| K5 | Irreversible tools only after successful path past `interrupt()`; nodes idempotent |

## 7. Decision Rationale

Enterprise HITL needs durable pauses. Authz on resume prevents hijack. Side-effect replay without guards double-charges APIs. Idempotency matches LangGraph resume semantics.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Restart thread from scratch on every approval | Loses work; poor UX |
| Store only final answers | No recovery mid-graph |
| Automatic replay of all tools | Dangerous |
| Custom “awaiting_approval” DB as SoR | Diverges from snapshot interrupts |

## 9. Tradeoffs

More checkpoint volume vs recoverability. Prefer retention policies over skipping durability.

## 10. Component Breakdown

### Checkpoint Store (LangGraph checkpointer backend)

- **Purpose:** Persist and fetch snapshots for the runtime.
- **Responsibilities:** Atomic write (via LangGraph), list history, fetch by id, TTL/prune.
- **Non-responsibilities:** Graph logic; approvals; semantic Store.
- **Inputs:** Serialized graph state from runtime.
- **Outputs:** Checkpoints accessible via `get_state` / history.
- **Dependencies:** ACID database preferred (`PostgresSaver`).
- **Lifecycle:** write → read → expire/archive.
- **Failure Modes:** serialization failure, disk full, split brain if multi-writer.
- **Recovery:** Quarantine bad rows; restore prior id via history.
- **Security:** Encrypt at rest; ACL by thread at API layer.
- **Scalability:** Partition by `thread_id`; blob offload for large channels.

### Approval gate (platform)

- Validates roles, records Approval, maps decision to resume value, then calls LangGraph resume.

## 11. Sequence of Operations

### Save
See [../programs/checkpoint-save.md](../programs/checkpoint-save.md)

### Restore
See [../programs/checkpoint-restore.md](../programs/checkpoint-restore.md)

### Interrupt
See [../programs/interrupt.md](../programs/interrupt.md)

### Resume
See [../programs/resume.md](../programs/resume.md)

### API lifecycle (any frontend)
See [16-api-surface-interrupt-resume.md](16-api-surface-interrupt-resume.md) · [../programs/api-run-lifecycle.md](../programs/api-run-lifecycle.md)

### Replay
See [../programs/replay.md](../programs/replay.md)

## 12. State Changes

| Op | Precondition | Postcondition |
|----|--------------|---------------|
| save | running step | checkpoint advanced (LangGraph) |
| interrupt | running node hits `interrupt()` | snapshot has interrupt; client sees awaiting_approval |
| resume | open interrupt + valid Approval | `Command(resume)` continues; node re-enters |
| replay | historical checkpoint | debug view or guarded fork re-exec |

## 13. Mermaid Diagrams

Linked in §4.

## 14. JSON Contracts

- [contracts/checkpoint.json](contracts/checkpoint.json)
- [contracts/approval.json](contracts/approval.json)
- [contracts/runtime-state.json](contracts/runtime-state.json) — projection
- [contracts/interrupt-payload.json](contracts/interrupt-payload.json) — projection of interrupt value

## 15. Best Practices

- Place mandatory `interrupt()` before irreversible execution skills.
- Include human-readable summary in interrupt payload.
- Index/prune checkpoints by thread and timestamp.
- Document idempotency requirements on every gated node.
- Subgraphs with nested interrupts: enable subgraph checkpointing.

## 16. Anti-patterns

- Interrupt implemented as “stop the container and hope.”
- Resume without verifying interrupt still open / authz.
- Unlimited checkpoint retention with PII.
- Re-passing initial invoke state to “resume.”
- Using only `interrupt_before` for production human approval workflows.

## 17. Common Mistakes

- Side effects before `interrupt()` without idempotent guards.
- Multiple services writing the same thread’s checkpoints.
- Replaying payments/emails without dry-run/fork mode.
- Passing `checkpoint_id` on normal resume (accidental time travel).

## 18. Future Evolution

Branching checkouts for what-if; merkle proofs for audit; cross-region sync.

## 19. Related Documents

[04-short-term-memory.md](04-short-term-memory.md) · [langgraph-bindings.md](langgraph-bindings.md) · [10-feedback-loops-rework.md](10-feedback-loops-rework.md) · [11-human-approval-governance.md](11-human-approval-governance.md) · [16-api-surface-interrupt-resume.md](16-api-surface-interrupt-resume.md) (Thread/Run HTTP scaffold)
