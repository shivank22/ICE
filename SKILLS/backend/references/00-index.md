# Architecture Knowledge Pack — Index

## Executive Summary

This pack is the reference architecture for designing enterprise **Agentic Orchestrator** backends **on LangGraph**. It teaches AI coding agents and platform engineers how to make durable decisions about orchestration, the four memory domains, skills, context, checkpoints, feedback loops, governance, security, and deployment—**binding to LangGraph primitives first**, then adding platform layers (skills, context assembly, promotion).

LangGraph concepts (durable graphs, messages, checkpointers, Store, interrupts, time travel) are the **default orchestration model**. See [langgraph-bindings.md](langgraph-bindings.md). Stack overrides are elicited per project.

## Purpose

Remove ambiguity that causes expensive rework: where state lives, how context is built, how skills are versioned, and how learning is promoted without silent prompt mutation—without reinventing what LangGraph already provides.

## Scope

**In scope:** architecture, contracts, algorithms, diagrams, decision rationale, LangGraph bindings.

**Out of scope:** application source code dumps, exploit details, product marketing, alternate orchestrators unless the user explicitly overrides LangGraph.

## Document map

| ID | Document | Primary concern |
|----|----------|-----------------|
| — | [LangGraph Bindings](langgraph-bindings.md) | Checkpointer, Store, interrupt, time travel |
| 01 | [Architecture Overview](01-architecture-overview.md) | Layers and services |
| 02 | [Runtime & State Model](02-runtime-state-model.md) | StateSnapshot + DTO projections |
| 03 | [Memory Architecture](03-memory-architecture.md) | Four domains overview |
| 04 | [Short-Term Memory](04-short-term-memory.md) | Messages + checkpointers |
| 05 | [Semantic Memory](05-semantic-memory.md) | Store / JWT namespace |
| 06 | [Procedural Memory & Skills](06-procedural-memory-skills.md) | Skill packages (`SKILL.md` + `skill.yaml`) |
| 19 | [Skill Platform Lifecycle](19-skill-platform-lifecycle.md) | CI→pgvector, Discovery→context records→Skill Resolver (`lfs`\|`blob`) |
| 07 | [Episodic Memory](07-episodic-memory.md) | Traces and episodes |
| 08 | [Context Construction](08-context-construction.md) | Assembly order |
| 09 | [Checkpoints, Interrupt, Resume](09-checkpoints-interrupt-resume.md) | Durability & HITL |
| 10 | [Feedback Loops & Rework](10-feedback-loops-rework.md) | Rework paths |
| 11 | [Human Approval & Governance](11-human-approval-governance.md) | Gates and policy |
| 12 | [Reflection & Evaluation](12-reflection-evaluation.md) | Learning proposals |
| 13 | [Observability](13-observability.md) | Traces, quality, cost |
| 14 | [Security](14-security.md) | AuthN/Z, namespaces |
| 15 | [Deployment & Evolution](15-deployment-evolution.md) | Bindings and growth |
| 16 | [API Surface: Interrupt & Resume](16-api-surface-interrupt-resume.md) | Thread/Run HTTP scaffold, any-FE HITL |
| 17 | [LangGraph Observability](17-langgraph-observability.md) | Graph + agent traces, Langfuse/LangSmith |
| 18 | [Evaluation Frameworks](18-evaluation-frameworks.md) | DeepEval, custom metrics, LLM-as-judge |
| — | [Glossary](glossary.md) | Shared terminology |
| — | [contracts/](contracts/) | Canonical JSON |
| — | [../programs/](../programs/) | Algorithms |
| — | [../assets/diagrams/](../assets/diagrams/) | Mermaid sources |

## Recommended reading order

1. LangGraph Bindings → Glossary → Architecture Overview  
2. Runtime & State → Short-Term Memory → Checkpoints  
3. Memory Architecture → Semantic / Procedural (**+ doc 19 Skill Platform**) / Episodic  
4. Context Construction  
5. Feedback Loops → Approval → Reflection  
6. **API Surface (doc 16)** — Thread/Run/Resume for any frontend  
7. Observability (13) → **LangGraph tracing (17)** → **Eval frameworks (18)** → Security → Deployment  

**Skill runtime phases:** Discover → Assemble (index records) → Skill Resolver Service (`lfs`\|`blob`) → Execute — [../programs/skill-runtime-pipeline.md](../programs/skill-runtime-pipeline.md)

## Cross-cutting principles

Modular · Layered · **LangGraph-first** · Observable · Secure by default · Versioned · Extensible · Testable · Explainable · Human governed · **Contracts win over prose**

## Related Documents

- [SKILL.md](../SKILL.md) — agent entrypoint  
- Parent ICE ADR (example binding): `docs/adr/ADR-001-vanilla-agentic-platform.md`
