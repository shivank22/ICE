# ICE Overall Architecture

Companion to:

- [`01-overall-process.drawio`](01-overall-process.drawio) (in docs)
- [`../ICE.drawio`](../ICE.drawio) (same diagram next to `DSE.drawio` for easy comparison)

Layout inspired by [`../DSE.drawio`](../DSE.drawio): layered fabrics with FinOps left, Adaption Engine right.

## Layers (ICE terminology)

| Layer | ICE content |
|-------|-------------|
| **FinOps Engine** | Agent cost per run, token/model metering, runner spend, TCO, budgets, rollups |
| **Connectivity Fabric** | Guided Wizard UI, MCP, CLI, Gateway |
| **Context Fabric** | ICE Skills, Langfuse registry, semantic/episodic memory, knowledge-service, skill-review HITL |
| **Orchestrator Framework** | LangGraph, Deep Agents, Agent Orchestrator, Job Service, **Skill Loader (mount hub)** |
| **Execution Framework** | Sandbox Provisioner + Discovery / Onboarding / Procure runners + skill pipeline |
| **Evaluation Framework** | Langfuse traces, App Insights, artifact integrity, ADD quality, cost attribution |
| **Adaption Engine** | Engagement tracks, owner email, SLA reminders, EoL nudges (replaces DSE Campaign Module) |

## Execution pipeline (replaces Scan / Implement / Validate / MR)

| DSE (reference) | ICE |
|-----------------|-----|
| SCAN | **DISCOVERY** → Inventory Artifact |
| IMPLEMENT | **RECOMMEND** → Readiness Artifact |
| HITL → Commit + MR | **HITL approve** → **ONBOARD** → Blueprint Artifact |
| AUDIT | **PROCURE** → Manifest Artifact → **Architecture Design Document** |
| GitLab / GitHub MR | **No MR** — ADD is the final deliverable |

Skill Loader mounts centralized skills onto ephemeral runners (via Sandbox Provisioner); agents use mounted skills.

Open in [diagrams.net](https://app.diagrams.net/) or the Draw.io extension.
