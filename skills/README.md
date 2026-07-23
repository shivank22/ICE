# Implementation Skills — Vanilla Agentic Framework

These are **Cursor-style Agent Skills** that help someone reading this repository **build** the architecture in [`ARCHITECTURE.md`](../ARCHITECTURE.md) using **their own tools**.

They are **not** the runtime procedural skills (Research / Planning / Execution / Reporting) that agents mount at execution time. Those are a separate seed catalog created during Phase 2+.

## How to invoke

In Cursor (or any agent that can load repo skills), ask explicitly, for example:

- “Use the **agentic-framework-bootstrap** skill and interview my stack”
- “Use **phase-1-access-and-research** and implement Phase 1 against `.stack.md`”

Optional: copy any skill folder into your project’s `.cursor/skills/` if you want Cursor auto-discovery. This repo keeps them under `skills/` only (not `~/.cursor`).

## Order

| Order | Skill | Purpose |
|------:|-------|---------|
| 0 | [`agentic-framework-bootstrap`](agentic-framework-bootstrap/SKILL.md) | Stack interview → monorepo skeleton → write `framework/.stack.md` |
| 1 | [`phase-1-access-and-research`](phase-1-access-and-research/SKILL.md) | Gateway, job-service, Engagement, wizard, Docker runner, Skill 1 |
| 2 | [`phase-2-planning-hitl-skills`](phase-2-planning-hitl-skills/SKILL.md) | Planning, HITL approve, skill-loader, skill registry |
| 3 | [`phase-3-execution-reporting-deliverable`](phase-3-execution-reporting-deliverable/SKILL.md) | Execution + Reporting, managed runners, Final Deliverable Document |
| 4 | [`phase-4-knowledge-and-clients`](phase-4-knowledge-and-clients/SKILL.md) | Knowledge memory, skill-review HITL, MCP + CLI parity |
| 5 | [`phase-5-finops-and-adaption`](phase-5-finops-and-adaption/SKILL.md) | FinOps Engine, Adaption Engine, dashboards |

Always start with **bootstrap** unless `.stack.md` already exists and the user names a phase.

## Opinionated (do not renegotiate)

- Microservice map and six layers from the architecture
- Engagement ID as the unit of work; engagement-centric gateway routes
- Artifact-first pipeline → **Final Deliverable Document**; **no merge request**
- HITL after Planning; **skill-loader** mounts skills onto ephemeral runners
- FinOps and Adaption as independent services
- Build order Phase 1 → 5

## Flexible (always ask before coding)

- Backend language / framework per service (FastAPI, Spring, Nest, Axum, Go, …)
- Guided wizard frontend (React, Vue, Svelte, HTMX, …)
- Orchestration stack (prefer LangGraph + Deep Agents when Python; document equivalents otherwise)
- Skill registry + traces (Langfuse default; OpenTelemetry + prompt store OK)
- Datastore (Postgres + pgvector default)
- Runner backend (Docker first; K8s / ACI later)
- Auth, message bus, email transport, cloud bindings

## Source of truth

- Architecture: [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
- Diagrams: [`../docs/`](../docs/)
- Blueprint PDF: [`../blueprint/agentic-framework-guide.pdf`](../blueprint/agentic-framework-guide.pdf)
