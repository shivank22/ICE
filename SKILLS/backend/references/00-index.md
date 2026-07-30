# Architecture Knowledge Pack — Index

## Executive Summary

This pack is the reference architecture for designing enterprise **Agentic Orchestrator** backends. It teaches AI coding agents and platform engineers how to make durable decisions about orchestration, the four memory domains, skills, context, checkpoints, feedback loops, governance, security, and deployment—without locking the client to a single cloud vendor.

LangGraph concepts (durable graphs, messages, checkpointers, interrupts) are the **reference orchestration model**. Stack bindings are elicited per project.

## Purpose

Remove ambiguity that causes expensive rework: where state lives, how context is built, how skills are versioned, and how learning is promoted without silent prompt mutation.

## Scope

**In scope:** architecture, contracts, algorithms, diagrams, decision rationale.

**Out of scope:** application source code, vendor SDKs, exploit details, product marketing.

## Document map

| ID | Document | Primary concern |
|----|----------|-----------------|
| 01 | [Architecture Overview](01-architecture-overview.md) | Layers and services |
| 02 | [Runtime & State Model](02-runtime-state-model.md) | Explicit runtime/thread state |
| 03 | [Memory Architecture](03-memory-architecture.md) | Four domains overview |
| 04 | [Short-Term Memory](04-short-term-memory.md) | Messages + checkpoints |
| 05 | [Semantic Memory](05-semantic-memory.md) | Postgres / JWT namespace |
| 06 | [Procedural Memory & Skills](06-procedural-memory-skills.md) | Skill registry |
| 07 | [Episodic Memory](07-episodic-memory.md) | Traces and episodes |
| 08 | [Context Construction](08-context-construction.md) | Assembly order |
| 09 | [Checkpoints, Interrupt, Resume](09-checkpoints-interrupt-resume.md) | Durability & HITL |
| 10 | [Feedback Loops & Rework](10-feedback-loops-rework.md) | Rework paths |
| 11 | [Human Approval & Governance](11-human-approval-governance.md) | Gates and policy |
| 12 | [Reflection & Evaluation](12-reflection-evaluation.md) | Learning proposals |
| 13 | [Observability](13-observability.md) | Traces, quality, cost |
| 14 | [Security](14-security.md) | AuthN/Z, namespaces |
| 15 | [Deployment & Evolution](15-deployment-evolution.md) | Bindings and growth |
| — | [Glossary](glossary.md) | Shared terminology |
| — | [contracts/](contracts/) | Canonical JSON |
| — | [../programs/](../programs/) | Algorithms |
| — | [../assets/diagrams/](../assets/diagrams/) | Mermaid sources |

## Recommended reading order

1. Glossary → Architecture Overview  
2. Runtime & State → Short-Term Memory → Checkpoints  
3. Memory Architecture → Semantic / Procedural / Episodic  
4. Context Construction  
5. Feedback Loops → Approval → Reflection  
6. Observability → Security → Deployment  

## Cross-cutting principles

Modular · Layered · Vendor neutral · Observable · Secure by default · Versioned · Extensible · Testable · Explainable · Human governed

## Related Documents

- [SKILL.md](../SKILL.md) — agent entrypoint  
- Parent ICE ADR (example binding): `docs/adr/ADR-001-vanilla-agentic-platform.md`
