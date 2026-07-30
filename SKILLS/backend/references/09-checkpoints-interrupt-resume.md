# 09 — Checkpoints, Interrupt, Resume, Replay

## 1. Executive Summary

Checkpoints make orchestration durable. **Interrupt** pauses for human or external input; **Resume** continues from a checkpoint with new input; **Replay** inspects or re-drives history for audit and debugging. These are core Short-Term Memory operations owned by the Orchestrator.

## 2. Purpose

Specify save/restore semantics, HITL pause points, and recovery so architects do not invent incompatible durability models.

## 3. Scope

Checkpoint lifecycle and control operations. Semantic/procedural stores are not checkpoint substitutes.

## 4. Architecture Overview

See [../assets/diagrams/09-checkpoint-lifecycle.mmd](../assets/diagrams/09-checkpoint-lifecycle.mmd) and [../assets/diagrams/09-interrupt-resume.mmd](../assets/diagrams/09-interrupt-resume.mmd)

## 5. Core Concepts

- **Checkpoint id / parent id:** lineage chain.
- **Interrupt payload:** what is being asked of the human/system.
- **Resume payload:** Approval or revision input.
- **Replay mode:** read-only vs re-execution with side-effect guards.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| K1 | Checkpoint before and after side-effecting tool calls (policy) |
| K2 | Interrupt is explicit graph state, not a crashed process |
| K3 | Resume requires authz + matching interrupt id |
| K4 | Replay of external side effects is gated / simulated by default |

## 7. Decision Rationale

Enterprise HITL needs durable pauses. Authz on resume prevents hijack. Side-effect replay without guards double-charges APIs or duplicates actions.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Restart thread from scratch on every approval | Loses work; poor UX |
| Store only final answers | No recovery mid-graph |
| Automatic replay of all tools | Dangerous |

## 9. Tradeoffs

More checkpoint volume vs recoverability. Prefer retention policies over skipping durability.

## 10. Component Breakdown

### Checkpoint Store

- **Purpose:** Persist and fetch snapshots.
- **Responsibilities:** Atomic write, list history, fetch by id, TTL.
- **Non-responsibilities:** Graph logic; approvals.
- **Inputs:** Serialized state; thread key.
- **Outputs:** Checkpoint records.
- **Dependencies:** ACID database preferred.
- **Lifecycle:** write → read → expire/archive.
- **Failure Modes:** serialization failure, disk full, split brain if multi-writer.
- **Recovery:** Quarantine bad rows; restore prior id.
- **Security:** Encrypt at rest; ACL by thread.
- **Scalability:** Partition by thread_id; blob offload for large channels.

## 11. Sequence of Operations

### Save
See [../programs/checkpoint-save.md](../programs/checkpoint-save.md)

### Restore
See [../programs/checkpoint-restore.md](../programs/checkpoint-restore.md)

### Interrupt
See [../programs/interrupt.md](../programs/interrupt.md)

### Resume
See [../programs/resume.md](../programs/resume.md)

### Replay
See [../programs/replay.md](../programs/replay.md)

## 12. State Changes

| Op | Precondition | Postcondition |
|----|--------------|---------------|
| save | running | checkpoint_id advanced |
| interrupt | running | awaiting_approval + interrupt payload |
| resume | awaiting_approval + valid Approval | running |
| replay | historical checkpoint | debug view or guarded re-exec |

## 13. Mermaid Diagrams

Linked in §4.

## 14. JSON Contracts

- [contracts/checkpoint.json](contracts/checkpoint.json)
- [contracts/approval.json](contracts/approval.json)
- [contracts/runtime-state.json](contracts/runtime-state.json)

## 15. Best Practices

- Place mandatory interrupt before irreversible execution skills.
- Include human-readable summary in interrupt payload.
- Index checkpoints by thread and timestamp.

## 16. Anti-patterns

- Interrupt implemented as “stop the container and hope.”
- Resume without verifying interrupt still open.
- Unlimited checkpoint retention with PII.

## 17. Common Mistakes

- Checkpointing after the irreversible tool already ran.
- Multiple services writing the same thread’s checkpoints.
- Replaying payments/emails without dry-run mode.

## 18. Future Evolution

Branching checkouts for what-if; merkle proofs for audit; cross-region sync.

## 19. Related Documents

[04-short-term-memory.md](04-short-term-memory.md) · [10-feedback-loops-rework.md](10-feedback-loops-rework.md) · [11-human-approval-governance.md](11-human-approval-governance.md)
