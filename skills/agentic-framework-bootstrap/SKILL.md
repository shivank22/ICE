---
name: agentic-framework-bootstrap
description: >-
  Interviews the user's stack and scaffolds the Vanilla Agentic Framework monorepo
  from ARCHITECTURE.md without inventing a different topology. Use when the user
  wants to implement, scaffold, or bootstrap this agentic architecture, start Phase 0,
  or choose languages/tools for gateway, orchestrator, runners, FinOps, or Adaption.
disable-model-invocation: true
---

# Agentic Framework Bootstrap

Help the user start implementing the **Vanilla Agentic Framework** described in this repo.

## Before anything else

1. Read [`ARCHITECTURE.md`](../../ARCHITECTURE.md) (Goal, microservice map, build order).
2. Skim diagrams index: [`docs/README.md`](../../docs/README.md).
3. Do **not** invent a different service topology, add an MR/PR step, or skip the HITL gate after Planning.

## Opinionated vs flexible

**Fixed (never ask to change):**
- Engagement ID as unit of work; engagement-centric routes
- Microservices behind a single gateway
- Artifact-first pipeline → Final Deliverable Document; **no MR**
- skill-loader mounts centralized skills onto ephemeral runners
- FinOps Engine + Adaption Engine as separate services
- Build phases 1 → 5

**Flexible (interview):** language, frontend, auth, DB, skill registry, bus, runners, cloud.

## Stack interview

Ask only for answers not already in `framework/.stack.md`. Prefer short numbered questions.

Capture at least:

| Topic | Examples |
|-------|----------|
| Monorepo root name | `framework/` (default from architecture) |
| Backend language(s) | FastAPI, Spring Boot, NestJS, Axum, Go, … |
| Same language for all services? | yes / mixed (list per service) |
| Guided wizard UI | React, Vue, Svelte, HTMX, … |
| Auth | Entra ID (default), Auth0, Keycloak, none-for-local |
| Datastore | Postgres + pgvector (default), other |
| Skill registry + traces | Langfuse (default), OTel + prompt store |
| Orchestration | LangGraph + Deep Agents if Python; else name equivalent |
| Local runners | Docker available? yes/no |
| Message bus | Service Bus, NATS, RabbitMQ, Redis streams, in-process for Phase 1 |
| Target cloud | Azure (default mapping), AWS, GCP, local-only |

## Persist choices

Write or update `framework/.stack.md`:

```markdown
# Stack choices (Vanilla Agentic Framework)

Updated: <ISO date>

## Languages / frameworks
- gateway:
- job-service:
- knowledge-service:
- agent-orchestrator / skill-loader:
- sandbox-provisioner:
- finops-engine:
- adaption-engine:
- web (guided wizard):
- mcp:
- cli:

## Platforms
- auth:
- datastore:
- skill_registry_traces:
- orchestration:
- message_bus:
- runner_backend_phase1: docker | other
- runner_backend_phase3: k8s | aci | other
- cloud:
- email_transport:  # Phase 5

## Notes
- <constraints, existing repos, team conventions>
```

## Scaffold monorepo (skeleton only)

Create empty/stub layout matching architecture (adjust root name from `.stack.md`):

```
framework/
├── apps/
│   ├── web/
│   ├── cli/
│   └── mcp/
├── services/
│   ├── gateway/
│   ├── knowledge/
│   ├── job/
│   ├── orchestrator/      # agent-orchestrator + skill-loader
│   ├── sandbox/           # sandbox-provisioner
│   ├── finops/
│   └── adaption/
├── runners/
├── infra/
├── docs/                  # symlink or copy from repo docs/ if separate
├── skills/                # seed runtime SKILL.md content (later phases)
└── .stack.md
```

Rules for this skill:
- Create directories + minimal README stubs per service (“owned by Phase N”).
- Do **not** implement production business logic here.
- Do **not** start Phase 1 code unless the user explicitly asks in the same turn.

## Hand off

Tell the user:

1. Stack is recorded in `framework/.stack.md`.
2. Next: invoke **`phase-1-access-and-research`**.
3. Point to diagrams: [`docs/01-overall-process.drawio`](../../docs/01-overall-process.drawio), [`docs/02-microservices-map.drawio`](../../docs/02-microservices-map.drawio).

## Checklist

```
- [ ] ARCHITECTURE.md read; topology not reinvented
- [ ] Stack interview complete (or .stack.md reused)
- [ ] framework/.stack.md written
- [ ] Monorepo skeleton created
- [ ] User directed to phase-1 skill
```
