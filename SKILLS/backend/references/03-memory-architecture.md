# 03 — Memory Architecture

## 1. Executive Summary

Memory is four independent architectural domains: **Short-Term**, **Semantic**, **Procedural**, and **Episodic**. Each has its own store, lifecycle, security boundary, and failure modes. Treating them as one “memory module” causes leakage, silent drift, and unrecoverable state.

## 2. Purpose

Define ownership, interfaces, and promotion rules across memory domains so context construction and learning remain governable.

## 3. Scope

Cross-domain model and interactions. Domain detail lives in docs 04–07.

## 4. Architecture Overview

See [../assets/diagrams/03-memory-domains.mmd](../assets/diagrams/03-memory-domains.mmd) and [../assets/diagrams/03-memory-lifecycle.mmd](../assets/diagrams/03-memory-lifecycle.mmd).

| Domain | Holds | Preferred store | Primary owner |
|--------|-------|-----------------|---------------|
| Short-Term | Messages, channel values, execution cursor | LangGraph **checkpointer** (`PostgresSaver`) | Orchestrator / LangGraph |
| Semantic | Durable facts (`Memory.md` in values) | LangGraph **Store** (`PostgresStore`) | Store + optional RBAC facade |
| Procedural | Skills (packages) | Registry + FS or Blob | Skill registry/loader (platform) |
| Episodic | Traces, outcomes, scores | Trace store + episode table | Evaluation / observability (platform) |

## 5. Core Concepts

- **Independence:** domains do not share write paths.
- **Promotion:** episodic → procedural only via Reflection Proposal + Approval.
- **Namespace:** semantic isolation by identity (default JWT `user_id`).
- **Budget:** episodic and semantic retrieval are always budgeted into Context Package.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| M1 | Four domains, not three (STM is first-class via checkpointer) |
| M2 | STM (checkpointer) never substitutes for semantic facts (Store) |
| M3 | Procedural memory is a Skill Registry, not prompt strings |
| M4 | Episodic never auto-mutates production skills |
| M5 | Context Assembler is the only merger of domains into model input |
| M6 | Semantic defaults to LangGraph Store namespaces—not a parallel SoR |

## 7. Decision Rationale

STM answers “where are we in this thread?” Semantic answers “what do we know?” Procedural answers “how should we act?” Episodic answers “what happened before?” Collapsing these questions into one store loses retention policy, RBAC, and explainability.

## 8. Alternatives Considered

| Alternative | Tradeoff |
|-------------|----------|
| Three-memory model (no STM) | Leaves durability/interrupt undocumented |
| Vector DB for everything | Weak transactional guarantees for checkpoints/skills |
| Fine-tune instead of episodic reflection | Costly, slow, hard to govern per change |

## 9. Tradeoffs

Four stores increase integration work. Benefit: independent scaling, clearer audits, safer learning loops.

## 10. Component Breakdown

Cross-domain **Memory Router** (logical): maps retrieval intents to the correct domain API. Prefer implementing this inside Context Assembler rather than as a fifth datastore.

## 11. Sequence of Operations

1. Identify retrieval intents from graph node / skill manifest.
2. Load STM from LangGraph snapshot / checkpointer (`get_state` or in-node state).
3. Query semantic via Store `search`/`get` by authorized namespace tuples.
4. Resolve procedural skills by id/version/label (registry).
5. Select episodic exemplars under token budget.
6. Merge via Context Assembler.

Algorithm: [../programs/memory-retrieval.md](../programs/memory-retrieval.md)

## 12. State Changes

| Domain | Create | Update | Retire |
|--------|--------|--------|--------|
| STM | checkpoint save | newer checkpoint | TTL / thread archive |
| Semantic | insert Memory.md | versioned update | soft-delete / archive |
| Procedural | draft skill | new version | deprecate label |
| Episodic | trace/episode write | enrich scores | retention purge |

## 13. Mermaid Diagrams

See assets linked in §4.

## 14. JSON Contracts

- [contracts/memory-record.json](contracts/memory-record.json)
- [contracts/semantic-memory.json](contracts/semantic-memory.json)
- [contracts/procedural-memory.json](contracts/procedural-memory.json)
- [contracts/episodic-memory.json](contracts/episodic-memory.json)

## 15. Best Practices

- Document retention per domain.
- Emit provenance: which memory ids entered a Context Package.
- Test retrieval isolation with cross-user adversarial cases.

## 16. Anti-patterns

- Writing semantic facts only into the latest checkpoint.
- Storing skill bodies inside episode blobs as “source of truth.”
- Shared writable “memory” table without domain discriminators.

## 17. Common Mistakes

- Using conversation summary as the only long-term store.
- Namespace = email string that can change.
- Skipping org vs user namespace distinction.

## 18. Future Evolution

Hierarchical namespaces (user → team → org), memory quarantine workflows, and differential privacy for episodic aggregates.

## 19. Related Documents

[04-short-term-memory.md](04-short-term-memory.md) · [05-semantic-memory.md](05-semantic-memory.md) · [06-procedural-memory-skills.md](06-procedural-memory-skills.md) · [07-episodic-memory.md](07-episodic-memory.md) · [langgraph-bindings.md](langgraph-bindings.md) · [08-context-construction.md](08-context-construction.md)
