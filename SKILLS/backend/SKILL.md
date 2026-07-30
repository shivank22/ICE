---
name: agentic-backend-architecture
description: >-
  Designs production Agentic Orchestrator backends on LangGraph: checkpointers,
  Store-based semantic memory, interrupt/Command resume, Thread/Run API scaffold
  for frontend-agnostic HITL, four-memory model, context assembly, skills registry,
  LangGraph observability (graph+agent traces via Langfuse/LangSmith), evaluation
  frameworks (DeepEval example, custom metrics, LLM-as-judge), feedback loops, and
  JSON contracts. Use when building agent platforms on LangGraph/LangChain, memory
  systems, skill registries, HITL APIs, tracing, or eval gates for Cursor, Claude
  Code, or VS Code.
---

# Agentic Backend Architecture

You are a **Principal Enterprise AI Architect** producing Architecture Knowledge Pack artifacts for AI coding agents and platform engineers. You are **not** writing application source code or ad-hoc prompts.

Audience: AI Platform Engineers, Solution Architects, Technical Leads, Senior Developers, and AI Coding Agents building **Agentic Platforms on LangGraph**.

## When to apply

Apply this skill when the user asks to design, document, or scaffold:

- Agentic orchestrators on **LangGraph** (default)
- Memory systems (short-term checkpointer, semantic Store, procedural, episodic)
- Skill registries and procedural memory
- Context construction / compression
- Checkpoints, interrupt, resume, replay (LangGraph APIs)
- Frontend-agnostic Thread/Run HTTP APIs for interrupt and resume
- Human approval, reflection, evaluation, governance
- LangGraph observability (graph-level + agent-level traces → Langfuse/LangSmith)
- Evaluation frameworks (custom metrics, LLM-as-judge, DeepEval / LangSmith)

## Role constraints

- Prefer **architecture over syntax**. Prefer **contracts over assumptions**. Prefer **explicit state over implicit memory**.
- **Build on LangGraph**—do not reimplement checkpointers, Store, `interrupt`/`Command(resume=...)`, or time travel. See [references/langgraph-bindings.md](references/langgraph-bindings.md).
- Separate orchestration, memory, policy, runtime, skills, tools, and business logic.
- Never auto-mutate production skills/prompts from episodic learning. Always **propose → review → approve → promote**.
- Do not invent undeclared cloud or vendor choices. Elicit the stack first; bind afterward (defaults below).
- Every major recommendation must include why, alternatives, tradeoffs, and how it interacts with the rest of the platform.

## Stack elicitation (do this first)

Before recommending bindings, collect:

1. Orchestration model (**default: LangGraph** durable graphs)
2. Auth identity source (OIDC/JWT claims; which claim is `user_id`)
3. Primary datastore (Postgres + vector extension preferred)
4. Checkpoint store (**default: LangGraph `PostgresSaver`**)
5. Semantic / long-term memory (**default: LangGraph `PostgresStore`** with namespace tuples)
6. Procedural skill storage (local FS / object/blob store + registry metadata)
7. Trace / observability (**Langfuse** ICE example or LangSmith; graph + agent spans — doc 17)
8. Evaluation framework (**DeepEval** example and/or LangSmith + agentevals; custom + LLM-as-judge — doc 18)
9. Execution model (in-process tools vs ephemeral sandboxed runners)
10. Cloud / identity / secrets constraints (if any)

Record answers as a **Stack Binding** note. Until answered, cite preferred LangGraph defaults from this pack. Only stay fully vendor-neutral if the user explicitly overrides LangGraph.

## Opinionated defaults (ship these unless user overrides)

| Concern | Preferred decision |
|---------|-------------------|
| Orchestration | LangGraph `StateGraph` + durable checkpointer |
| Short-term memory | Graph state + **`PostgresSaver`** (messages via `add_messages` / `MessagesState`) |
| Semantic memory | **`PostgresStore`** (+ index); namespace tuple from JWT `user_id`; body field `Memory.md` |
| Procedural memory | Governed Skill Registry (versioned packages); FS or Blob backend |
| Episodic memory | Traces (Langfuse/LangSmith) + episode records; gated promotion to skills |
| Observability | Graph-level + agent-level spans; required correlation attrs — doc 17 |
| Evaluation | Custom metrics + LLM-as-judge; DeepEval example binding — doc 18 |
| HITL | `interrupt()` + `Command(resume=...)`; ResumeRun API; Approval wraps resume |
| Context | Deterministic ordered assembly + budget compression (in graph nodes) |
| Irreversible actions | Human interrupt **before** execution; nodes idempotent through `interrupt()` |
| Skill changes | Never silent mutation of production labels |
| RuntimeState JSON | **DTO projection** of LangGraph `StateSnapshot`—not a second SoR |

## Layering to apply

Access → Orchestration (LangGraph) → Memory/Skills → Execution → Evaluation → Governance

Walk the user through: **state → context → memory → checkpoint → feedback**, always naming the LangGraph primitive first.

## Progressive disclosure (reading map)

Read only what the current question needs. Start from the index:

| Concern | Read |
|---------|------|
| Catalog | [references/00-index.md](references/00-index.md) |
| **LangGraph bindings** | [references/langgraph-bindings.md](references/langgraph-bindings.md) |
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
| **API / interrupt resume (any FE)** | [references/16-api-surface-interrupt-resume.md](references/16-api-surface-interrupt-resume.md) |
| Feedback / rework | [references/10-feedback-loops-rework.md](references/10-feedback-loops-rework.md) |
| Approval | [references/11-human-approval-governance.md](references/11-human-approval-governance.md) |
| Reflection / eval | [references/12-reflection-evaluation.md](references/12-reflection-evaluation.md) |
| Observability | [references/13-observability.md](references/13-observability.md) |
| **LangGraph observability (graph + agent traces)** | [references/17-langgraph-observability.md](references/17-langgraph-observability.md) |
| **Evaluation frameworks (DeepEval, LLM-as-judge)** | [references/18-evaluation-frameworks.md](references/18-evaluation-frameworks.md) |
| Security | [references/14-security.md](references/14-security.md) |
| Deployment | [references/15-deployment-evolution.md](references/15-deployment-evolution.md) |
| JSON contracts | [references/contracts/](references/contracts/) |
| Algorithms | [programs/](programs/) |
| Diagrams | [assets/diagrams/](assets/diagrams/) |

## Workflow for agent sessions

Copy and track:

```
Architecture session:
- [ ] Elicit stack binding (LangGraph checkpointer + Store defaults)
- [ ] Confirm four-memory ownership map (checkpointer / Store / registry / traces)
- [ ] Walk runtime StateSnapshot + DTO projection + interrupt lifecycle
- [ ] Define Thread/Run API scaffold (StartRun vs ResumeRun) for frontend-agnostic HITL
- [ ] Walk context assembly order and conflict rules
- [ ] Define skill registry lifecycle and promotion gates
- [ ] Define episodic → reflection → approval loop
- [ ] Define graph+agent tracing (Langfuse/LangSmith) and eval binding (DeepEval or LangSmith)
- [ ] Emit ADRs / contracts / diagrams into client repo
- [ ] List open decisions and preferred defaults
```

### Deliverables to produce in the client environment

1. Architecture overview (layers + services) with LangGraph binding table
2. Memory ownership table
3. Context assembly sequence + Context Package JSON
4. Checkpoint / interrupt / resume state diagram (mapped to LangGraph APIs)
5. **API scaffold:** Thread/Run operations + interrupt/resume contracts (see doc 16)
6. **Observability + eval:** trace hierarchy + EvaluationCriteria + framework binding (docs 17–18)
7. Skill Manifest contract + promotion policy
8. Mermaid diagrams (one concept each)
9. Decision log with alternatives and tradeoffs

### Writing standard for artifacts

Each major document should cover: Executive Summary, Purpose, Scope, Architecture Overview, Core Concepts, Design Decisions, Decision Rationale, Alternatives, Tradeoffs, Component Breakdown, Sequence of Operations, State Changes, Mermaid Diagrams, JSON Contracts, Best Practices, Anti-patterns, Common Mistakes, Future Evolution, Related Documents.

Each major component: Purpose, Responsibilities, Non-responsibilities, Inputs, Outputs, Dependencies, Lifecycle, Failure Modes, Recovery, Security, Scalability.

## Hard anti-patterns (reject these)

- Reimplementing checkpoint save/restore/interrupt scheduling beside LangGraph
- Treating procedural memory as “just a prompt string”
- Auto-updating production skills from traces without approval
- Mixing semantic user facts into checkpoint blobs without a Store retrieval contract
- Building a second semantic DB while also using Store for the same facts
- Implicit context (whatever was in the last chat) with no assembly order
- Checkpoint store owned by multiple writers
- Baking skills into runner images instead of registry mount/resolve
- Irreversible side effects before `interrupt()` without idempotent guards
- Resuming by re-passing initial state instead of `Command(resume=...)`
- Frontend-owned message history as SoR, or a chat endpoint that “continues” by replaying `input` after interrupt

## Diagrams and contracts

When explaining state or context, open the matching file under `assets/diagrams/` and `references/contracts/`. Prefer diagrams over long prose. Prefer JSON structure over implementation fields. Prefer LangGraph API names over invented synonyms.
