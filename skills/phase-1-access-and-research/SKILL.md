---
name: phase-1-access-and-research
description: >-
  Implements Phase 1 of the Vanilla Agentic Framework: gateway, job-service,
  Engagement entity, guided wizard skeleton, local Docker runner, and Research
  skill end-to-end producing a Research Findings Artifact. Use when scaffolding
  Phase 1, access platform, or Skill 1 Research against this architecture.
disable-model-invocation: true
---

# Phase 1 — Access + Research

Implement **build order Phase 1** from [`ARCHITECTURE.md`](../../ARCHITECTURE.md).

## Prerequisites

1. Read `framework/.stack.md`. If missing, run **agentic-framework-bootstrap** first.
2. Diagrams: [`docs/02-microservices-map`](../../docs/02-microservices-map.md), [`docs/06-discovery-wizard`](../../docs/06-discovery-wizard.md), [`docs/03-system-overview`](../../docs/03-system-overview.md).
3. Contracts: [`reference.md`](reference.md).

## Must not change

- Engagement ID as anchor; routes under `/engagements/{id}/…`
- Clients are thin; business logic only in services behind gateway
- Research produces a **Research Findings Artifact** (versioned); **no MR**
- Runners are ephemeral; Phase 1 uses **local Docker** (or stack-equivalent)

## Must ask (if not in `.stack.md`)

- Gateway + job-service language/framework
- Wizard UI stack
- Auth for local (mock JWT vs real IdP)
- Postgres connection (or approved alternative)
- Docker image base for Research runner
- How SSE is served in their stack

## Scope (done when all true)

| Deliverable | Notes |
|-------------|--------|
| `gateway` | Auth stub, RBAC hooks, REST + SSE pass-through |
| `job-service` | Job lifecycle; owns `job`, `skill_artifact` |
| Engagement entity | Create/get engagement by id |
| `apps/web` wizard skeleton | Steps for Research; SSE progress |
| Local Docker Research runner | Spawned for Skill 1 (provisioner can be minimal) |
| Skill 1 vertical slice | `POST …/research` → confirmed findings artifact |

Optional this phase: stub `sandbox-provisioner` that only starts/stops one Docker container.

## Implementation order

1. **Contracts** — OpenAPI/proto for routes in [`reference.md`](reference.md); artifact JSON schema for Research Findings.
2. **job-service** — Create job, persist artifact metadata, emit status events.
3. **gateway** — Proxy to job-service; SSE from job events.
4. **web wizard** — Four collaboration steps (scope → context → constraints → confirm); see diagram 06.
5. **Runner** — Minimal agent/worker that writes findings payload to job workspace and registers artifact.
6. **Wire** one happy-path demo: open engagement → complete wizard → `GET …/findings` + artifact fetch.

Use the user’s languages from `.stack.md`. Prefer idiomatic project layout for that stack; keep **service names and ownership** from architecture.

## Suggested layout (names fixed; tech flexible)

```
framework/services/gateway/
framework/services/job/
framework/services/sandbox/     # optional thin Docker spawn
framework/apps/web/
framework/runners/research/
```

## Done checklist

```
- [ ] .stack.md respected for languages
- [ ] Engagement CRUD via gateway
- [ ] POST /engagements/{id}/research works
- [ ] GET /engagements/{id}/findings returns confirmed findings
- [ ] skill_artifact row + payload for Research Findings
- [ ] Wizard UI + SSE progress
- [ ] Docker (or equivalent) Research runner used at least once
- [ ] No MR/PR code path introduced
- [ ] User told next skill: phase-2-planning-hitl-skills
```
