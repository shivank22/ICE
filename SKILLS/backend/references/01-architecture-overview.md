# 01 — Architecture Overview

## 1. Executive Summary

An enterprise Agentic AI platform is a modular control plane: authenticated clients submit work; an orchestrator runs durable graphs; memory and skills supply context; execution produces artifacts; evaluation and governance close the loop. This document defines layers, services, and interaction boundaries.

## 2. Purpose

Establish a shared topology so teams and coding agents do not invent conflicting ownership for state, memory, skills, or approval.

## 3. Scope

Covers logical layers and architectural services. Does not prescribe a single cloud, language, or monorepo layout. LangGraph is the reference orchestration model.

## 4. Architecture Overview

### Layers

| Layer | Purpose | Key concerns |
|-------|---------|--------------|
| Access | Single edge: auth, RBAC, APIs, streams | Gateway, identity |
| Orchestration | Job lifecycle and durable agent graphs | Orchestrator, checkpoints |
| Memory & Skills | Semantic, procedural, episodic knowledge | Knowledge, registry, loader |
| Execution | Tools / runners that act | Sandbox optional |
| Evaluation | Traces, scores, cost | Observability, FinOps |
| Governance | Approvals, policy, promotion | Approval gate, reflection |

See diagram: [../assets/diagrams/01-context-layers.mmd](../assets/diagrams/01-context-layers.mmd)

### Container view

See diagram: [../assets/diagrams/01-container-overview.mmd](../assets/diagrams/01-container-overview.mmd)

## 5. Core Concepts

- **Explicit state** over chat-history improvisation
- **Four memory domains** with separate stores and lifecycles
- **Skills as packages**, not prompt blobs
- **Deterministic context assembly**
- **Human-governed learning**

## 6. Design Decisions

| Decision | Choice |
|----------|--------|
| D1 | Separate orchestration from memory stores |
| D2 | Skill loader is sole resolve/mount authority for procedural content |
| D3 | Checkpoint store has a single writer: the orchestrator |
| D4 | Semantic namespaces default to JWT `user_id` |
| D5 | Episodic learning never writes production skills directly |

## 7. Decision Rationale

Coupling memory writes into the orchestrator creates untestable side effects. A single checkpoint writer prevents divergent thread histories. Namespace isolation prevents cross-user leakage. Gated promotion preserves auditability.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Monolithic “agent service” owning all stores | Hard to scale, observe, and govern |
| Prompt-only “memory” in the system message | No lifecycle, retrieval, or tenancy |
| Auto-updating prompts from traces | Silent drift; compliance risk |

## 9. Tradeoffs

More services increase operational surface. The gain is independent scaling, clearer RBAC, and replaceable vendors behind contracts.

## 10. Component Breakdown

### Gateway / Identity

- **Purpose:** Authenticate and authorize every request; forward identity.
- **Responsibilities:** JWT validation, RBAC, rate limits, routing, SSE/WebSocket edge.
- **Non-responsibilities:** Graph execution, memory retrieval logic.
- **Inputs:** HTTP/SSE/MCP/CLI requests with bearer tokens.
- **Outputs:** Authorized calls with identity headers/claims.
- **Dependencies:** IdP (OIDC).
- **Lifecycle:** Always-on control plane.
- **Failure Modes:** IdP outage, expired tokens, misconfigured audiences.
- **Recovery:** Fail closed; retry IdP; clear client re-auth.
- **Security:** Audience/issuer checks; no secrets in responses.
- **Scalability:** Stateless replicas behind LB.

### Agent Orchestrator

- **Purpose:** Run durable agent graphs.
- **Responsibilities:** STM, checkpoints, interrupt/resume, invoke context assembler, call tools.
- **Non-responsibilities:** Owning semantic/episodic stores; skill authoring.
- **Inputs:** Job/thread commands, resume payloads.
- **Outputs:** State transitions, tool calls, artifacts events, interrupts.
- **Dependencies:** Checkpoint store, context assembler, skill loader, LLM.
- **Lifecycle:** Always-on; threads long-lived.
- **Failure Modes:** LLM timeouts, checkpoint write failures, poison state.
- **Recovery:** Retry idempotent steps; restore last good checkpoint; dead-letter bad threads.
- **Security:** Runs with service identity; never trusts client-supplied `user_id` over JWT.
- **Scalability:** Shard by thread_id; externalize checkpoints.

### Context Assembler

- **Purpose:** Build the Context Package deterministically.
- **Responsibilities:** Ordered merge, budgets, conflict resolution, compression.
- **Non-responsibilities:** Persisting memory; executing tools.
- **Inputs:** Request, identity, checkpoint slice, retrieval queries.
- **Outputs:** Context Package JSON.
- See [08-context-construction.md](08-context-construction.md).

### Knowledge / Semantic Memory Service

- **Purpose:** Persist and retrieve user/org facts (`Memory.md`).
- See [05-semantic-memory.md](05-semantic-memory.md).

### Skill Registry + Loader

- **Purpose:** Version and mount procedural skills.
- See [06-procedural-memory-skills.md](06-procedural-memory-skills.md).

### Checkpoint Store

- **Purpose:** Durable graph snapshots.
- See [09-checkpoints-interrupt-resume.md](09-checkpoints-interrupt-resume.md).

### Trace / Episodic Store

- **Purpose:** Capture what happened.
- See [07-episodic-memory.md](07-episodic-memory.md).

### Reflection / Learning Promoter

- **Purpose:** Propose skill improvements from episodes.
- See [12-reflection-evaluation.md](12-reflection-evaluation.md).

### Approval / Policy Gate

- **Purpose:** Gate irreversible actions and promotions.
- See [11-human-approval-governance.md](11-human-approval-governance.md).

## 11. Sequence of Operations (happy path)

1. Client authenticates at Gateway.
2. Job/thread created; Orchestrator starts or resumes graph.
3. Context Assembler builds Context Package.
4. Model/tools execute; STM checkpointed.
5. Optional interrupt for approval.
6. Artifacts persisted; traces written.
7. Optional reflection proposals queued for review.

See [../assets/diagrams/01-request-sequence.mmd](../assets/diagrams/01-request-sequence.mmd)

## 12. State Changes

| From | Event | To |
|------|-------|----|
| none | thread.create | running |
| running | checkpoint.save | running (durable) |
| running | interrupt | awaiting_approval |
| awaiting_approval | approve/revise | running |
| running | complete | succeeded |
| * | fail | failed / recoverable |

## 13. Mermaid Diagrams

Referenced above under Architecture Overview and Sequence.

## 14. JSON Contracts

- [contracts/runtime-state.json](contracts/runtime-state.json)
- [contracts/session.json](contracts/session.json)
- [contracts/user.json](contracts/user.json)
- [contracts/event.json](contracts/event.json)

## 15. Best Practices

- Keep control plane credentials off data-plane runners when sandboxes are used.
- Version every skill and policy.
- Document stack bindings separately from topology.

## 16. Anti-patterns

- Orchestrator directly editing production skill text.
- Multiple services writing checkpoints.
- Context built ad hoc inside prompts with no contract.

## 17. Common Mistakes

- Equating “chat history” with the full memory architecture.
- Skipping HITL before irreversible tools.
- Using org-wide semantic namespace for personal facts.

## 18. Future Evolution

Add multi-agent fabrics, policy-as-code engines, and multi-region checkpoint replication without changing layer boundaries.

## 19. Related Documents

[00-index.md](00-index.md) · [02-runtime-state-model.md](02-runtime-state-model.md) · [03-memory-architecture.md](03-memory-architecture.md) · [15-deployment-evolution.md](15-deployment-evolution.md)
