# 04 — Short-Term Memory

## 1. Executive Summary

Short-Term Memory (STM) is the conversation and execution working set for a durable thread. In the LangGraph reference model it is managed through **messages** and **checkpointers**. STM answers where the agent is right now—not what the organization knows forever.

## 2. Purpose

Provide recoverable, interruptible execution state without overloading semantic or procedural stores.

## 3. Scope

Thread messages, channel values, checkpoint lifecycle, interrupt/resume/replay as they relate to STM. Semantic facts and skill bodies are out of scope.

## 4. Architecture Overview

Orchestrator owns STM. Checkpoint Store persists snapshots. Clients never write checkpoints directly.

See [../assets/diagrams/04-stm-checkpoint-flow.mmd](../assets/diagrams/04-stm-checkpoint-flow.mmd)

## 5. Core Concepts

- **Messages:** ordered conversational turns and tool results in the thread.
- **Channel values:** typed graph state fields beyond messages.
- **Checkpoint:** versioned durable snapshot keyed by `thread_id` + checkpoint id.
- **Parent checkpoint:** lineage for resume and replay.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| S1 | Postgres (or equivalent ACID store) for checkpointer in production |
| S2 | Single writer: Orchestrator |
| S3 | Do not embed full semantic Memory.md documents into every checkpoint |
| S4 | Interrupt state is first-class in STM |

## 7. Decision Rationale

ACID checkpoints make resume correct after process death. Single writer avoids fork confusion. Keeping semantic content referenced by id keeps checkpoints small and namespaces enforceable.

## 8. Alternatives Considered

| Alternative | Why secondary |
|-------------|---------------|
| In-memory only | Lost on restart; unsuitable for HITL |
| Object storage checkpoints | Weaker transactional semantics |
| Client-held state | Untrusted and non-auditable |

## 9. Tradeoffs

Durable checkpoints add latency and storage. Worth it for enterprise HITL and audit.

## 10. Component Breakdown

### Short-Term Memory Runtime (within Orchestrator)

- **Purpose:** Maintain live thread state and flush checkpoints.
- **Responsibilities:** Append messages, update channels, save/restore checkpoints, expose interrupt markers.
- **Non-responsibilities:** Long-term fact storage; skill versioning.
- **Inputs:** User/tool events, resume payloads.
- **Outputs:** Updated Runtime/Thread State; Checkpoint records.
- **Dependencies:** Checkpoint Store, identity (`thread_id`, `user_id`).
- **Lifecycle:** Created with thread; archived with retention policy.
- **Failure Modes:** Partial write, serialization errors, clock skew.
- **Recovery:** Idempotent save; restore last valid checkpoint; quarantine corrupt snapshots.
- **Security:** Authorize thread access by user/org RBAC.
- **Scalability:** Partition by thread_id; prune old checkpoints per policy.

## 11. Sequence of Operations

1. Create or load thread.
2. Restore latest checkpoint (if any).
3. Assemble context (external to STM write path).
4. Execute node; append messages / channel updates.
5. Save checkpoint.
6. On interrupt: persist awaiting_approval marker; stop scheduling.
7. On resume: load checkpoint; apply Approval/input; continue.

Algorithms: [../programs/checkpoint-save.md](../programs/checkpoint-save.md), [../programs/checkpoint-restore.md](../programs/checkpoint-restore.md)

## 12. State Changes

See [../assets/diagrams/04-stm-state.mmd](../assets/diagrams/04-stm-state.mmd)

| State | Meaning |
|-------|---------|
| empty | New thread |
| running | Active execution |
| checkpointed | Durable snapshot exists |
| awaiting_input | Interrupt |
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
- Define max checkpoint history per thread.

## 16. Anti-patterns

- Using STM as the only CRM/knowledge base.
- Letting the UI patch checkpoint JSON arbitrarily.
- Dual checkpointers for the same thread.

## 17. Common Mistakes

- Forgetting to checkpoint before interrupt.
- Resuming without validating Approval identity.
- Treating message history as unordered.

## 18. Future Evolution

Cross-region checkpoint replication; differential checkpoints; encrypted checkpoint payloads.

## 19. Related Documents

[02-runtime-state-model.md](02-runtime-state-model.md) · [09-checkpoints-interrupt-resume.md](09-checkpoints-interrupt-resume.md) · [08-context-construction.md](08-context-construction.md)
