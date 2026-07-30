---
name: agentic-backend-architecture
description: >-
  Consult this skill when designing an agentic backend orchestrator on
  LangGraph/LangChain and you need opinionated, language-agnostic architecture
  for components and services. Covers production Agentic Orchestrator backends:
  checkpointers, Store-based semantic memory, interrupt/Command resume,
  Thread/Run API scaffold, skill platform (SKILL.md + skill.yaml → CI →
  Postgres/pgvector; runtime search; Skill Resolver Service loads packages from
  lfs or blob), four-memory model, context assembly, LangGraph observability,
  evaluation frameworks (DeepEval example, custom metrics, LLM-as-judge),
  feedback loops, and JSON contracts. Also for skill repositories, HITL APIs,
  tracing, or eval gates.
---

# Agentic Backend Architecture

You are a **Principal Enterprise AI Architect** producing Architecture Knowledge Pack artifacts for AI coding agents and platform engineers. You are **not** writing application source code or ad-hoc prompts.

Audience: AI Platform Engineers, Solution Architects, Technical Leads, Senior Developers, and AI Coding Agents building **Agentic Platforms on LangGraph**.

## Scope of depth (read this first)

This pack is **architecture-first** for the whole platform (orchestration, memory, checkpoints, HITL APIs, observability, eval, security, deployment bindings). It is **not** an ops runbook for every service.

**Detailed lifecycle and operational guidance is intentional only for the Skill platform**—package layout (`SKILL.md` + `skill.yaml`), CI → Postgres/pgvector index, discovery, context cards, Skill Resolver Service (`lfs` \| `blob`), pins, promotion gates, and related contracts/programs (doc 19). Skills are the novel procedural layer teams usually lack a playbook for.

For other concerns (checkpointer, Store, gateway, traces, eval runners, deployment), prefer **LangGraph/vendor primitives + contracts + opinionated defaults**. Assume platform engineers already know how to operate Postgres, IdP, containers, and observability backends—elicit their stack; do not invent parallel ops manuals unless the user asks.

## When to apply

Apply this skill when the user asks to design, document, or scaffold:

- Agentic orchestrators on **LangGraph** (default)
- Memory systems (short-term checkpointer, semantic Store, procedural, episodic)
- Skill platforms (`skill.yaml` index + Skill Resolver Service)
- Context construction / compression
- Checkpoints, interrupt, resume, replay (LangGraph APIs)
- Frontend-agnostic Thread/Run HTTP APIs for interrupt and resume
- Human approval, reflection, evaluation, governance
- LangGraph observability (graph-level + agent-level traces → Langfuse/LangSmith)
- Evaluation frameworks (custom metrics, LLM-as-judge, DeepEval / LangSmith)

## Role constraints

- Prefer **architecture over syntax**. Prefer **contracts over assumptions**. Prefer **explicit state over implicit memory**.
- **Contracts win over prose** when they disagree—update both in the same change. See [references/contracts/](references/contracts/).
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
6. Procedural skills (`SKILL.md` + `skill.yaml`; CI → Postgres/pgvector; Skill Resolver Service → `lfs` or `blob` — doc 19)
7. Trace / observability (**Langfuse** ICE example or LangSmith; graph + agent spans — doc 17)
8. Evaluation framework (**DeepEval** example and/or LangSmith + agentevals; custom + LLM-as-judge — doc 18)
9. Execution model (in-process tools vs ephemeral sandboxed runners; container vs serverless)
10. Cloud / identity / secrets constraints (if any)

Record answers as a **Stack Binding** note. Until answered, cite preferred LangGraph defaults from this pack. Only stay fully vendor-neutral if the user explicitly overrides LangGraph—then still emit equivalent contracts; do not leave half-bound designs.

## Opinionated defaults (ship these unless user overrides)

| Concern | Preferred decision |
|---------|-------------------|
| Orchestration | LangGraph `StateGraph` + durable checkpointer |
| Short-term memory | Graph state + **`PostgresSaver`** (messages via `add_messages` / `MessagesState`) |
| Semantic memory | **`PostgresStore`** (+ index); namespace tuple from JWT `user_id`; body field `Memory.md` |
| Procedural memory | **Folder: `SKILL.md` + `skill.yaml` (version/metadata)** → CI builds Postgres/pgvector → runtime search → index records in context → **Skill Resolver Service** loads bodies from **`lfs`** (container) or **`blob`** (serverless/singleton API) — doc 19 |
| Episodic memory | Traces (Langfuse/LangSmith) + episode records; gated promotion to skills |
| Observability | Graph-level + agent-level spans; required correlation attrs — doc 17 |
| Evaluation | Custom metrics + LLM-as-judge; DeepEval example binding — doc 18 |
| HITL | `interrupt()` + `Command(resume=...)`; ResumeRun API; Approval wraps resume **inside** orchestration |
| Context | Deterministic assembly; skill section = **index records** (name, description, metadata)—not full corpus |
| Irreversible actions | Human interrupt **before** execution; nodes idempotent through `interrupt()` |
| Skill changes | Never silent mutation of production status; gated promote |
| Skill pins | `skill_id` + `version` + **description** + `locator` (`lfs` \| `blob`) ([skill-pin.json](references/contracts/skill-pin.json)) |
| RuntimeState JSON | **DTO projection** of LangGraph `StateSnapshot`—not a second SoR |

## Layering to apply

Access → Orchestration (LangGraph) → Memory/Skills → Execution

**Cross-cutting (not afterthoughts):** Evaluation and Governance (Approval, policy, promotion) apply **inside** orchestration—HITL interrupts mid-graph; promotion gates skill status changes. Do not model them as a final pipeline stage only.

Walk the user through: **state → memory → checkpoint → skills → context → feedback**, always naming the LangGraph primitive first.

**Skill runtime (only this model):**

1. Each skill is a folder with **`SKILL.md`** (LLM) and **`skill.yaml`** (version + metadata).
2. **CI** builds / updates **Postgres + pgvector** from `skill.yaml` (name, description, metadata).
3. At runtime: **pgvector search** on name + descriptions **plus metadata filters** → skill index records.
4. Retrieved **skill records are added to context**.
5. **Skill Resolver Service** (customizable per use case) reads the appropriate full packages from **`lfs`** (code on the container) or **`blob`** (when promoted for singleton API / serverless)—wherever `locator.backend` points.

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
| **Skill platform lifecycle** | [references/19-skill-platform-lifecycle.md](references/19-skill-platform-lifecycle.md) |
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
- [ ] Confirm four-memory ownership map (checkpointer / Store / skill index+resolver / traces)
- [ ] Walk runtime StateSnapshot + DTO projection + interrupt lifecycle
- [ ] Define Thread/Run API scaffold (StartRun vs ResumeRun) for frontend-agnostic HITL
- [ ] Define skill platform: skill.yaml → CI → Postgres/pgvector; search → records in context; Skill Resolver Service (lfs | blob)
- [ ] Walk context assembly order (index records in skill section; full SKILL.md via Resolver)
- [ ] Define skill promotion gates (status in skill.yaml; not a registry service)
- [ ] Define episodic → reflection → approval → promote loop
- [ ] Define graph+agent tracing (Langfuse/LangSmith) and eval binding (DeepEval or LangSmith)
- [ ] Emit ADRs / contracts / diagrams into client repo (only sections the question needs)
- [ ] List open decisions and preferred defaults
```

### Deliverables to produce in the client environment

Emit only what the question needs. Prefer contracts + one diagram over a full pack.

1. Architecture overview (layers + services) with LangGraph binding table
2. Memory ownership table
3. Context assembly sequence + Context Package JSON
4. Checkpoint / interrupt / resume state diagram (mapped to LangGraph APIs)
5. **API scaffold:** Thread/Run operations + interrupt/resume contracts (see doc 16)
6. Skill platform: **skill.yaml** + CI index + Skill Resolver Service (`lfs` \| `blob`) — doc 19
7. **Observability + eval:** trace hierarchy + EvaluationCriteria + framework binding (docs 17–18)
8. Mermaid diagrams (one concept each)
9. Decision log with alternatives and tradeoffs

### Writing standard for artifacts

For a **full** architecture document (when the user asks for one), cover as applicable: Executive Summary, Purpose, Scope, Architecture Overview, Core Concepts, Design Decisions, Decision Rationale, Alternatives, Tradeoffs, Component Breakdown, Sequence of Operations, State Changes, Mermaid Diagrams, JSON Contracts, Best Practices, Anti-patterns, Common Mistakes, Future Evolution, Related Documents.

For a **narrow** question, answer with the relevant subset only—do not dump the full template.

Each major component (when specified): Purpose, Responsibilities, Non-responsibilities, Inputs, Outputs, Dependencies, Lifecycle, Failure Modes, Recovery, Security, Scalability.

## Hard anti-patterns (reject these)

- Reimplementing checkpoint save/restore/interrupt scheduling beside LangGraph
- Treating procedural memory as “just a prompt string”
- Auto-updating production skills from traces without approval
- Mixing semantic user facts into checkpoint blobs without a Store retrieval contract
- Building a second semantic DB while also using Store for the same facts
- Implicit context (whatever was in the last chat) with no assembly order
- Checkpoint store owned by multiple writers
- Treating Postgres as the editable SoR for full skill bodies (index = cards/metadata only)
- Injecting full `skill.yaml` or the entire skill corpus into every prompt
- Discovery returning full `SKILL.md` bodies
- Skipping the Skill Resolver Service and inventing ad-hoc file reads outside `lfs` / `blob`
- Irreversible side effects before `interrupt()` without idempotent guards
- Resuming by re-passing initial state instead of `Command(resume=...)`
- Frontend-owned message history as SoR, or a chat endpoint that “continues” by replaying `input` after interrupt

## Diagrams and contracts

When explaining state or context, open the matching file under `assets/diagrams/` and `references/contracts/`. Prefer diagrams over long prose. Prefer JSON structure over implementation fields. Prefer LangGraph API names over invented synonyms. Prefer **index records in context + Skill Resolver Service (`lfs` \| `blob`)** for procedural content.
