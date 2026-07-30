# 07 — Episodic Memory

## 1. Executive Summary

Episodic Memory records **what happened**: traces, successes, failures, scores, and reflections. It is built by collecting execution traces and applying analysis to produce **improvement proposals**. Those proposals may update procedural memory **only** through governed promotion—never by direct automatic mutation of production prompts or skills.

## 2. Purpose

Enable learning and auditability from real runs without compromising production skill integrity.

## 3. Scope

Trace capture, episode records, reflection inputs, retention. Does not own skill registry writes (only proposals).

## 4. Architecture Overview

See [../assets/diagrams/07-episodic-to-promotion.mmd](../assets/diagrams/07-episodic-to-promotion.mmd)

Flow: Run → Trace Store → Episode Record → Reflection Service → Reflection Proposal → Approval → Skill Registry (draft/new version).

## 5. Core Concepts

- **Trace:** span/event timeline for a run/thread.
- **Episode:** curated durable summary linked to traces, outcomes, and artifacts.
- **Reflection Proposal:** suggested change to a skill/policy with evidence links.
- **Promotion gate:** mandatory Approval before production label moves.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| E1 | Dual store: rich traces + queryable episode rows |
| E2 | Reflection outputs proposals, not production writes |
| E3 | Episodes used in context are budgeted exemplars, not full traces |
| E4 | PII redaction policy applied before long-term episode storage |

## 7. Decision Rationale

Full traces are necessary for debug; episodes are necessary for retrieval and learning. Separating proposal from apply preserves human governance. Budgeting prevents context blowups.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Auto-edit production prompts from LLM critique | Silent behavioral drift |
| Store only metrics, no traces | Weak root-cause analysis |
| Replay full traces into every prompt | Cost and leakage |

## 9. Tradeoffs

Storage and pipeline complexity increase. Required for enterprise learning loops.

## 10. Component Breakdown

### Trace / Episodic Store

- **Purpose:** Persist traces and episode records.
- **Responsibilities:** Ingest spans, index by thread/run/user, retain per policy.
- **Non-responsibilities:** Promoting skills; assembling full context alone.
- **Inputs:** Orchestrator/runner telemetry; eval scores.
- **Outputs:** Trace ids, episode records, query results.
- **Dependencies:** Trace backend (e.g. Langfuse or equivalent); Postgres for episodes.
- **Lifecycle:** ingest → index → curate episode → retain/purge.
- **Failure Modes:** ingest lag, partial spans, quota exhaustion.
- **Recovery:** Buffer locally; backfill; mark incomplete episodes.
- **Security:** Tenant isolation; redaction; access by role.
- **Scalability:** Partition by time and tenant; sample high-volume spans.

### Reflection / Learning Promoter

- **Purpose:** Analyze episodes and emit proposals.
- See [12-reflection-evaluation.md](12-reflection-evaluation.md).

## 11. Sequence of Operations

1. Orchestrator emits traces during run.
2. On terminal state, curate Episode (outcome, artifacts, scores).
3. Periodically or on trigger, Reflection selects episode cohorts.
4. Generate Reflection Proposal with evidence + diff suggestion.
5. Route to Approval; on approve, create **draft** skill version.
6. Staging soak → production promotion (separate Approvals as policy requires).

Algorithms: [../programs/reflection.md](../programs/reflection.md) · [../programs/learning-promotion.md](../programs/learning-promotion.md)

## 12. State Changes

| Episode status | Meaning |
|----------------|---------|
| open | Run still active |
| complete | Terminal outcome recorded |
| under_reflection | Selected for analysis |
| proposed | Proposal created |
| closed | No further learning action |

## 13. Mermaid Diagrams

Linked in §4. Also [../assets/diagrams/07-episode-lifecycle.mmd](../assets/diagrams/07-episode-lifecycle.mmd)

## 14. JSON Contracts

- [contracts/episodic-memory.json](contracts/episodic-memory.json)
- [contracts/trace.json](contracts/trace.json)
- [contracts/reflection.json](contracts/reflection.json)
- [contracts/evaluation.json](contracts/evaluation.json)

## 15. Best Practices

- Link episodes to skill version ids actually used.
- Store failure taxonomies for clustering.
- Require dual control for high-risk skill promotions.

## 16. Anti-patterns

- `UPDATE skills SET body = reflection_output`.
- Using raw traces as semantic memory.
- Dropping failed runs from episodic store.

## 17. Common Mistakes

- No linkage between trace and checkpoint id.
- Reflection without evaluation criteria.
- Retaining secrets in spans.

## 18. Future Evolution

Automated cohort detection, causal analysis across skills, regulated retention schedules.

## 19. Related Documents

[06-procedural-memory-skills.md](06-procedural-memory-skills.md) · [11-human-approval-governance.md](11-human-approval-governance.md) · [12-reflection-evaluation.md](12-reflection-evaluation.md) · [13-observability.md](13-observability.md)
