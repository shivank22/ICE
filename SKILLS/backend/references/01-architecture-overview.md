# 01 — Architecture Overview

## 1. Executive Summary

An enterprise Agentic AI platform is a modular control plane on **LangGraph**: authenticated clients submit work; an orchestrator runs durable graphs with **checkpointers** and **Store**; skills and episodic systems supply platform context; execution produces artifacts; evaluation and governance close the loop. This document defines layers, services, and interaction boundaries. See [langgraph-bindings.md](langgraph-bindings.md).

## 2. Purpose

Establish a shared topology so teams and coding agents do not invent conflicting ownership for state, memory, skills, or approval.

## 3. Scope

Covers logical layers and architectural services. Does not prescribe a single cloud, language, or monorepo layout. **LangGraph is the default orchestration binding**—configure its primitives; do not reimplement them.

## 4. Architecture Overview

### Layers

| Layer | Purpose | Key concerns |
|-------|---------|--------------|
| Access | Single edge: auth, RBAC, APIs, streams | Gateway, identity |
| Orchestration | Job lifecycle and durable LangGraph graphs | Orchestrator, checkpointer |
| Memory & Skills | Store (semantic), procedural, episodic | Store facade, Skill Index, Discovery, Skill Resolver Service |
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
| D1 | Separate orchestration from long-term memory (checkpointer ≠ Store) |
| D2 | Skill Resolver Service is sole authority for loading full skill packages (`lfs` \| `blob`) |
| D3 | Checkpoints have a single writer: compiled LangGraph + checkpointer |
| D4 | Semantic memory defaults to LangGraph Store; namespaces from JWT `user_id` |
| D5 | Episodic learning never writes production skills directly |
| D6 | RuntimeState / client JSON are projections of `StateSnapshot` |

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
- **Responsibilities:** JWT validation, RBAC, rate limits, routing, SSE/WebSocket edge; Thread/Run/Resume API scaffold ([16-api-surface-interrupt-resume.md](16-api-surface-interrupt-resume.md)).
- **Non-responsibilities:** Graph execution, memory retrieval logic; owning STM (checkpointer does).
- **Inputs:** HTTP/SSE/MCP/CLI requests with bearer tokens.
- **Outputs:** Authorized calls with identity headers/claims; RunResult / RuntimeState DTOs.
- **Dependencies:** IdP (OIDC).
- **Lifecycle:** Always-on control plane.
- **Failure Modes:** IdP outage, expired tokens, misconfigured audiences.
- **Recovery:** Fail closed; retry IdP; clear client re-auth.
- **Security:** Audience/issuer checks; no secrets in responses.
- **Scalability:** Stateless replicas behind LB.

### Agent Orchestrator (LangGraph runtime + facade)

- **Purpose:** Run durable LangGraph agent graphs.
- **Responsibilities:** Compile with checkpointer (+ optional Store); STM; `interrupt`/`Command(resume)`; invoke context assembler; call tools; project `StateSnapshot` → RuntimeState DTO.
- **Non-responsibilities:** Reimplementing checkpointers; owning episodic SoR; skill authoring.
- **Inputs:** Job/thread commands, `Command(resume=...)`, approvals.
- **Outputs:** State transitions, tool calls, artifact events, interrupts.
- **Dependencies:** Checkpointer, Store, context assembler, Skill Resolver Service, LLM.
- **Lifecycle:** Always-on; threads long-lived.
- **Failure Modes:** LLM timeouts, checkpointer failures, poison state.
- **Recovery:** Retry idempotent steps; resume from last good snapshot; dead-letter bad threads.
- **Security:** Runs with service identity; never trusts client-supplied `user_id` over JWT.
- **Scalability:** Shard by `thread_id`; durable checkpointer backend.

### Context Assembler

- **Purpose:** Build the Context Package deterministically (platform layer inside nodes/helpers).
- **Responsibilities:** Ordered merge, budgets, conflict resolution, compression.
- **Non-responsibilities:** Persisting memory; executing tools; replacing LangGraph state.
- **Inputs:** Request, identity, snapshot slice, Store retrieval, skill pins.
- **Outputs:** Context Package JSON.
- See [08-context-construction.md](08-context-construction.md).

### Semantic Memory (LangGraph Store + optional facade)

- **Purpose:** Persist and retrieve user/org facts (`Memory.md` in Store values).
- See [05-semantic-memory.md](05-semantic-memory.md).

### Skill Discovery + Skill Resolver Service (procedural platform)

- **Purpose:** Search the Skill Index and load full packages (doc 19).
- **Responsibilities:** Discovery = pgvector + metadata → **index records** for context; Skill Resolver Service = load appropriate packages from **`lfs`** (container) or **`blob`** (serverless/singleton API)—customizable per use case.
- **Non-responsibilities:** Injecting skill.yaml into the LLM; semantic user facts; running Discovery or Resolve inside Context Assembler.
- See [06-procedural-memory-skills.md](06-procedural-memory-skills.md) · [19-skill-platform-lifecycle.md](19-skill-platform-lifecycle.md).

### Checkpointer backend

- **Purpose:** Durable graph snapshots via LangGraph checkpointer.
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
- Multiple services writing checkpoints (bypassing LangGraph checkpointer).
- Parallel semantic DB for the same facts as Store.
- Context built ad hoc inside prompts with no contract.
- Custom interrupt FSM that disagrees with `StateSnapshot` interrupts.

## 17. Common Mistakes

- Equating “chat history” with the full memory architecture.
- Skipping HITL before irreversible tools.
- Using org-wide semantic namespace for personal facts.

## 18. Future Evolution

Add multi-agent fabrics, policy-as-code engines, and multi-region checkpoint replication without changing layer boundaries.

## 19. Related Documents

[00-index.md](00-index.md) · [langgraph-bindings.md](langgraph-bindings.md) · [02-runtime-state-model.md](02-runtime-state-model.md) · [03-memory-architecture.md](03-memory-architecture.md) · [15-deployment-evolution.md](15-deployment-evolution.md) · [16-api-surface-interrupt-resume.md](16-api-surface-interrupt-resume.md)
