# Agentic Framework — Overall Architecture

Companion to:

- [`01-overall-process.drawio`](01-overall-process.drawio) (in docs)
- [`../ICE.drawio`](../ICE.drawio) (same diagram at the repo root)

Layered layout: FinOps Engine left, Adaption Engine right, five layers/frameworks in between.

## Layers

| Layer | Content |
|-------|---------|
| **FinOps Engine** | Agent cost per run, token/model metering, runner spend, run cost model, budgets, rollups |
| **Connectivity Layer** | Guided Wizard UI, MCP, CLI, Gateway |
| **Context Layer** | Framework skills, Langfuse registry, semantic/episodic memory, knowledge-service, skill-review HITL |
| **Orchestrator Framework** | LangGraph, Deep Agents, Agent Orchestrator, Job Service, **Skill Loader (mount hub)** |
| **Execution Framework** | Sandbox Provisioner + Research / Execution / Reporting runners + skill pipeline |
| **Evaluation Framework** | Langfuse traces, App Insights, artifact integrity, deliverable quality, cost attribution |
| **Adaption Engine** | Engagement tracks, stakeholder email, SLA reminders, deadline nudges |

## Execution pipeline (artifacts, no MR)

| Step | Output |
|------|--------|
| **RESEARCH** | Research Findings Artifact |
| **PLAN** | Plan & Recommendation Artifact |
| **HITL approve** → **EXECUTE** | Execution Report Artifact |
| **REPORT** | Summary Artifact → **Final Deliverable Document** |
| — | **No MR** — the Final Deliverable Document is the deliverable |

Skill Loader mounts centralized skills onto ephemeral runners (via Sandbox Provisioner); agents use mounted skills.

Open in [diagrams.net](https://app.diagrams.net/) or the Draw.io extension.
