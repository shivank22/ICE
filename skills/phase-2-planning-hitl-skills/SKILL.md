---
name: phase-2-planning-hitl-skills
description: >-
  Implements Phase 2: Planning skill, HITL approve gate, skill-loader as central
  mount hub, and skill registry (Langfuse or equivalent) integration. Use when
  adding Planning, human approval after plan, or skill mounting to this architecture.
disable-model-invocation: true
---

# Phase 2 — Planning + HITL + Skill Loader

Implement **build order Phase 2** from [`ARCHITECTURE.md`](../../ARCHITECTURE.md).

## Prerequisites

1. Phase 1 vertical slice works; read `framework/.stack.md`.
2. Diagrams: [`docs/04-skill-knowledge-platform`](../../docs/04-skill-knowledge-platform.md), [`docs/05-execution-runners`](../../docs/05-execution-runners.md), [`docs/07-skill-artifacts`](../../docs/07-skill-artifacts.md).

## Must not change

- HITL **after** Plan & Recommendation Artifact, **before** Execution
- Skills are **centralized**; never baked into runner images
- **skill-loader** is the only mount authority (orchestrator does not fetch registry content itself)
- Still **no MR**

## Must ask (if not in `.stack.md`)

- Orchestration library (LangGraph + Deep Agents vs alternative)
- Skill registry product (Langfuse default) and how prompts are labeled (`draft|staging|production`)
- Where skill-loader lives (same deployable as orchestrator vs separate process — architecture allows `services/orchestrator/` bundling)
- Plan scoring dimensions for the first domain (open item — ask user for v1 weights)

## Scope

| Deliverable | Notes |
|-------------|--------|
| Planning skill | Consumes Research Findings → Plan & Recommendation Artifact |
| `POST /engagements/{id}/plan` | Starts planning job/phase |
| `POST /engagements/{id}/approve` | HITL approve / revise |
| `skill-loader` | resolve → ask provisioner → mount bundle onto runner |
| Registry integration | Fetch **production** procedural skill content |
| Seed runtime skills | Minimal `skills/research` + `skills/planning` as SKILL.md / prompts |

## Implementation order

1. **Contracts** — plan artifact schema; approve body (`decision: approve|revise`, optional comments).
2. **Registry client** — pull production prompt/SKILL content by `skill_key`.
3. **skill-loader API** — `prepare_runtime(skill_key, job_id)` returning mount record + runner ref.
4. **Planning path** — orchestrator requests prepare_runtime for `planning`; agents use **mounted** content only.
5. **HITL** — job status `awaiting_approval`; gateway approve route; revise loops back toward research/plan (document path).
6. **Persist** `plan_recommendation` with job-service ownership.

## Mount sequence (must match architecture)

1. Orchestrator → skill-loader: prepare runtime for `skill_key`
2. skill-loader → knowledge/registry: resolve production skills + facts
3. skill-loader → sandbox-provisioner: spawn runner
4. skill-loader: mount skill bundle onto runner
5. Agents execute using mounted skills only
6. Emit skill artifact → job-service

## Done checklist

```
- [ ] Plan & Recommendation Artifact produced from findings
- [ ] HITL approve/revise via gateway
- [ ] skill-loader mounts; no skills baked into images
- [ ] Registry production label used
- [ ] Seed Research + Planning skill content in repo skills/ catalog
- [ ] Next: phase-3-execution-reporting-deliverable
```
