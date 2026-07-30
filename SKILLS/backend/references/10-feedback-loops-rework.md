# 10 — Feedback Loops & Rework

## 1. Executive Summary

Production agent platforms are loop systems: human approval, rework after revision, evaluation thresholds, and skill promotion. Each loop has explicit entry conditions, state restores, and exit criteria. Hidden retries without state accounting create undetectable drift.

## 2. Purpose

Document the feedback loops architects must design so coding agents implement recoverability and learning without ad-hoc forks.

## 3. Scope

HITL interrupt loop, rework/revise loop, evaluation loop, skill promotion loop. Detailed approval/reflection mechanics in docs 11–12.

## 4. Architecture Overview

See [../assets/diagrams/10-feedback-loops.mmd](../assets/diagrams/10-feedback-loops.mmd)

## 5. Core Concepts

- **HITL loop:** running → awaiting_approval → approve | revise → running.
- **Rework:** restore checkpoint; inject revision; re-enter graph.
- **Eval loop:** scored traces → threshold → gate or alert.
- **Promotion loop:** episodes → proposal → approve → draft skill → soak → production.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| F1 | Revision creates a new checkpoint lineage child, not silent overwrite |
| F2 | Rework preserves prior artifacts for comparison |
| F3 | Skill promotion is a separate loop from run HITL |
| F4 | Automatic model retries are capped and traced |

## 7. Decision Rationale

Lineage preserves audit. Separating promotion from run approval prevents conflating “approve this plan” with “change how the agent works forever.”

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Always restart from thread zero | Wastes work |
| Auto-merge reflection into prod | Unsafe |
| Infinite model self-retry | Cost and loops |

## 9. Tradeoffs

More states to manage; clearer operations and FinOps.

## 10. Component Breakdown

Loops are **cross-cutting behaviors** implemented by Orchestrator + Approval + Reflection + Eval—not a single microservice.

## 11. Sequence of Operations

### HITL approval

1. Graph reaches gate node → Interrupt.
2. Human reviews plan/artifact.
3. Approve → Resume; or Revise → Resume with comments.

### Rework

1. User requests change after a phase.
2. Select checkpoint (phase boundary preferred).
3. Apply revision input; mark prior artifact superseded.
4. Re-run affected subgraph.

### Eval gate

1. Evaluation attaches scores to Episode.
2. If below threshold: block promotion and/or open rework.

### Promotion

1. Reflection emits proposal.
2. Approval creates draft skill version.
3. Staging eval → production label.

See programs under [../programs/](../programs/) for interrupt, resume, reflection, learning-promotion, evaluation, human-approval.

## 12. State Changes

Documented in diagrams; key rule: every loop iteration leaves an Event.

## 13. Mermaid Diagrams

See §4 and [../assets/diagrams/10-rework-sequence.mmd](../assets/diagrams/10-rework-sequence.mmd)

## 14. JSON Contracts

- [contracts/event.json](contracts/event.json)
- [contracts/approval.json](contracts/approval.json)
- [contracts/evaluation.json](contracts/evaluation.json)
- [contracts/reflection.json](contracts/reflection.json)

## 15. Best Practices

- Name loops in runbooks.
- Bound automatic retries (count + wall clock).
- Compare artifact versions on rework.

## 16. Anti-patterns

- Swallowing revise comments.
- Promoting skills on the same button as plan approval.
- Checkpoint restore to arbitrary mid-tool points without safety.

## 17. Common Mistakes

- No event for “revise_requested”.
- Losing skill pin versions across rework.
- Eval without linking to skill version.

## 18. Future Evolution

Policy-driven loop selection; automatic bisect of failing skill versions.

## 19. Related Documents

[09-checkpoints-interrupt-resume.md](09-checkpoints-interrupt-resume.md) · [11-human-approval-governance.md](11-human-approval-governance.md) · [12-reflection-evaluation.md](12-reflection-evaluation.md)
