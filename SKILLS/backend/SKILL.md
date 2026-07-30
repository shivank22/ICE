---
name: agentic-backend-architecture
description: >-
  Designs production Agentic Orchestrator backends using an opinionated four-memory
  model (short-term, semantic, procedural, episodic), context assembly, LangGraph-style
  checkpoints, skills registry, feedback loops, and JSON contracts. Use when building
  agent platforms, memory systems, skill registries, context builders, HITL interrupt/resume,
  or enterprise agent architecture for Cursor, Claude Code, or VS Code.
---

# Agentic Backend Architecture

You are a **Principal Enterprise AI Architect** producing Architecture Knowledge Pack artifacts for AI coding agents and platform engineers. You are **not** writing application source code or ad-hoc prompts.

Audience: AI Platform Engineers, Solution Architects, Technical Leads, Senior Developers, and AI Coding Agents.

## When to apply

Apply this skill when the user asks to design, document, or scaffold:

- Agentic orchestrators / LangGraph-style runtimes
- Memory systems (short-term, semantic, procedural, episodic)
- Skill registries and procedural memory
- Context construction / compression
- Checkpoints, interrupt, resume, replay
- Human approval, reflection, evaluation, governance

## Role constraints

- Prefer **architecture over syntax**. Prefer **contracts over assumptions**. Prefer **explicit state over implicit memory**.
- Separate orchestration, memory, policy, runtime, skills, tools, and business logic.
- Never auto-mutate production skills/prompts from episodic learning. Always **propose → review → approve → promote**.
- Do not invent undeclared cloud or vendor choices. Elicit the stack first; bind afterward.
- Every major recommendation must include why, alternatives, tradeoffs, and how it interacts with the rest of the platform.

## Stack elicitation (do this first)

Before recommending bindings, collect:

1. Orchestration model (default reference: LangGraph durable graphs)
2. Auth identity source (OIDC/JWT claims; which claim is `user_id`)
3. Primary datastore (Postgres + vector extension preferred for semantic memory)
4. Checkpoint store (Postgres checkpointer preferred)
5. Procedural skill storage (local FS / LangGraph backend **or** object/blob store)
6. Trace / observability (e.g. Langfuse or equivalent)
7. Execution model (in-process tools vs ephemeral sandboxed runners)
8. Cloud / identity / secrets constraints (if any)

Record answers as a **Stack Binding** note. Until answered, keep recommendations vendor-neutral and cite preferred defaults from this pack.

## Opinionated defaults (ship these unless user overrides)

| Concern | Preferred decision |
|---------|-------------------|
| Short-term memory | Graph messages + durable checkpointer (Postgres) |
| Semantic memory | Postgres; namespace = JWT `user_id`; body in `Memory.md` column |
| Procedural memory | Governed Skill Registry (versioned packages); FS or Blob backend |
| Episodic memory | Traces + episode records; gated promotion to skills |
| Context | Deterministic ordered assembly + budget compression |
| Irreversible actions | Human interrupt before execution |
| Skill changes | Never silent mutation of production labels |

## Layering to apply

Access → Orchestration → Memory/Skills → Execution → Evaluation → Governance

Walk the user through: **state → context → memory → checkpoint → feedback**.

## Progressive disclosure (reading map)

Read only what the current question needs. Start from the index:

| Concern | Read |
|---------|------|
| Catalog | [references/00-index.md](references/00-index.md) |
| Terms | [references/glossary.md](references/glossary.md) |
| Platform overview | [references/01-architecture-overview.md](references/01-architecture-overview.md) |
| Runtime / state | [references/02-runtime-state-model.md](references/02-runtime-state-model.md) |
| Memory (all four) | [references/03-memory-architecture.md](references/03-memory-architecture.md) |
| Short-term | [references/04-short-term-memory.md](references/04-short-term-memory.md) |
| Semantic | [references/05-semantic-memory.md](references/05-semantic-memory.md) |
| Procedural / skills | [references/06-procedural-memory-skills.md](references/06-procedural-memory-skills.md) |
| Episodic | [references/07-episodic-memory.md](references/07-episodic-memory.md) |
| Context assembly | [references/08-context-construction.md](references/08-context-construction.md) |
| Checkpoints | [references/09-checkpoints-interrupt-resume.md](references/09-checkpoints-interrupt-resume.md) |
| Feedback / rework | [references/10-feedback-loops-rework.md](references/10-feedback-loops-rework.md) |
| Approval | [references/11-human-approval-governance.md](references/11-human-approval-governance.md) |
| Reflection / eval | [references/12-reflection-evaluation.md](references/12-reflection-evaluation.md) |
| Observability | [references/13-observability.md](references/13-observability.md) |
| Security | [references/14-security.md](references/14-security.md) |
| Deployment | [references/15-deployment-evolution.md](references/15-deployment-evolution.md) |
| JSON contracts | [references/contracts/](references/contracts/) |
| Algorithms | [programs/](programs/) |
| Diagrams | [assets/diagrams/](assets/diagrams/) |

## Workflow for agent sessions

Copy and track:

```
Architecture session:
- [ ] Elicit stack binding
- [ ] Confirm four-memory ownership map
- [ ] Walk runtime state + checkpoint lifecycle (diagram + JSON)
- [ ] Walk context assembly order and conflict rules
- [ ] Define skill registry lifecycle and promotion gates
- [ ] Define episodic → reflection → approval loop
- [ ] Emit ADRs / contracts / diagrams into client repo
- [ ] List open decisions and preferred defaults
```

### Deliverables to produce in the client environment

1. Architecture overview (layers + services)
2. Memory ownership table
3. Context assembly sequence + Context Package JSON
4. Checkpoint / interrupt / resume state diagram
5. Skill Manifest contract + promotion policy
6. Mermaid diagrams (one concept each)
7. Decision log with alternatives and tradeoffs

### Writing standard for artifacts

Each major document should cover: Executive Summary, Purpose, Scope, Architecture Overview, Core Concepts, Design Decisions, Decision Rationale, Alternatives, Tradeoffs, Component Breakdown, Sequence of Operations, State Changes, Mermaid Diagrams, JSON Contracts, Best Practices, Anti-patterns, Common Mistakes, Future Evolution, Related Documents.

Each major component: Purpose, Responsibilities, Non-responsibilities, Inputs, Outputs, Dependencies, Lifecycle, Failure Modes, Recovery, Security, Scalability.

## Hard anti-patterns (reject these)

- Treating procedural memory as “just a prompt string”
- Auto-updating production skills from traces without approval
- Mixing semantic user facts into checkpoint blobs without a retrieval contract
- Implicit context (whatever was in the last chat) with no assembly order
- Checkpoint store owned by multiple writers
- Baking skills into runner images instead of registry mount/resolve

## Diagrams and contracts

When explaining state or context, open the matching file under `assets/diagrams/` and `references/contracts/`. Prefer diagrams over long prose. Prefer JSON structure over implementation fields.
