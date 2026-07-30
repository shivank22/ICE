# 08 — Context Construction

## 1. Executive Summary

Context is **assembled**, not improvised. The Context Assembler merges identity, policies, short-term state, skills, semantic hits, episodic exemplars, artifacts, and the user request into a **Context Package** with explicit order, priority, conflict rules, and compression.

## 2. Purpose

Make model inputs explainable, budgeted, secure, and reproducible for a given checkpoint and skill pin set.

## 3. Scope

Assembly pipeline, ordering, priority, conflict resolution, compression. Individual memory store internals are in docs 04–07.

## 4. Architecture Overview

See [../assets/diagrams/08-context-assembly.mmd](../assets/diagrams/08-context-assembly.mmd)

### Ordered pipeline (preferred)

1. System guidance / platform policies  
2. Auth identity + entitlements  
3. Restored checkpoint / thread slice (STM)  
4. Selected procedural skills (manifest + constraints)  
5. Semantic retrieval (namespaced)  
6. Episodic exemplars (ranked, budgeted)  
7. Artifacts / tool outputs for this turn  
8. User request  
9. Compression / budget enforcement → **final Context Package**

## 5. Core Concepts

- **Priority:** policy > skill constraint > retrieved memory > model preference.
- **Provenance:** every injected block cites source ids.
- **Budget:** token/char limits per section with drop rules.
- **Conflict resolution:** higher priority wins; log overrides.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| C1 | Single assembler component (logical); deterministic order |
| C2 | Never inject unauthorized semantic namespaces |
| C3 | Prefer references + summaries over raw mega-traces |
| C4 | Record assembly digest on the Trace for replay |

## 7. Decision Rationale

Determinism enables eval and debugging. Authz-before-inject prevents leakage. Digests allow “why did the model see X?” audits.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Free-form prompt concatenation in nodes | Non-reproducible |
| Model-decides-what-to-fetch without budgets | Cost/risk spikes |
| Stuff full Memory.md history always | Context rot |

## 9. Tradeoffs

Assembler complexity vs prompt simplicity. Required at enterprise scale.

## 10. Component Breakdown

### Context Assembler

- **Purpose:** Produce Context Package JSON.
- **Responsibilities:** Fetch, order, conflict-resolve, compress, attest provenance.
- **Non-responsibilities:** Persisting memories; executing tools.
- **Inputs:** Request, JWT claims, thread/checkpoint ids, skill pins, budgets.
- **Outputs:** Context Package; assembly metrics.
- **Dependencies:** STM, semantic, procedural, episodic APIs; policy engine.
- **Lifecycle:** Stateless per invocation (preferred).
- **Failure Modes:** retrieval timeouts, budget overflow, policy deny.
- **Recovery:** Degrade sections by priority; fail closed on authz errors.
- **Security:** Strip secrets; enforce namespace ACL.
- **Scalability:** Parallel retrieval with deadlines; cache skill manifests.

## 11. Sequence of Operations

Detailed algorithm: [../programs/context-assembly.md](../programs/context-assembly.md)  
Compression: [../programs/context-compression.md](../programs/context-compression.md)

## 12. State Changes

Context Package is **ephemeral**. It may be hashed and stored on the Trace; it is not a fifth memory domain.

## 13. Mermaid Diagrams

See §4 and [../assets/diagrams/08-context-priority.mmd](../assets/diagrams/08-context-priority.mmd)

## 14. JSON Contracts

- [contracts/context.json](contracts/context.json)
- [contracts/policy.json](contracts/policy.json)

## 15. Best Practices

- Unit-test assembler order with fixtures.
- Publish per-section token budgets in config.
- Include negative constraints from skills early.

## 16. Anti-patterns

- “Whatever was in the last chat” as context.
- Injecting draft skills into production runs.
- Dropping policy blocks under budget pressure.

## 17. Common Mistakes

- Semantic retrieval without `user_id` filter.
- Putting user request above policies.
- Omitting provenance, making eval impossible.

## 18. Future Evolution

Adaptive budgets by node type; learned compression with guarantees; signed context attestations.

## 19. Related Documents

[03-memory-architecture.md](03-memory-architecture.md) · [02-runtime-state-model.md](02-runtime-state-model.md) · [14-security.md](14-security.md)
