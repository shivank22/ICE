---
name: phase-3-execution-reporting-deliverable
description: >-
  Implements Phase 3: Execution and Reporting skills/runners, managed ephemeral
  runner backend (K8s or equivalent), and Final Deliverable Document composition
  with no merge request. Use when adding Skills 3–4 or composing the final document.
disable-model-invocation: true
---

# Phase 3 — Execution + Reporting + Final Deliverable

Implement **build order Phase 3** from [`ARCHITECTURE.md`](../../ARCHITECTURE.md).

## Prerequisites

1. Phase 2 HITL + skill-loader working; read `framework/.stack.md`.
2. Diagrams: [`docs/05-execution-runners`](../../docs/05-execution-runners.md), [`docs/07-skill-artifacts`](../../docs/07-skill-artifacts.md), [`docs/01-overall-process`](../../docs/01-overall-process.md).

## Must not change

- Execution runs **only after** approve
- Each skill emits its own artifact; final doc is a **composition**, not a git MR
- Credentials stay on the control plane; runners are ephemeral + TTL-swept
- Hybrid skip/re-run of skills is allowed; document how job-service records it

## Must ask (if not in `.stack.md`)

- Phase 3 runner backend: AKS/K8s pods, ACI, Nomad, etc.
- Which enterprise APIs Execution may call (stubs OK for first slice)
- Final Deliverable format: Markdown, PDF, DOCX, HTML
- Object store / volume for artifact payloads (Azure Files, S3, PVC, …)

## Scope

| Deliverable | Notes |
|-------------|--------|
| `POST /engagements/{id}/execute` | Execution Report Artifact |
| `POST /engagements/{id}/report` | Summary Artifact |
| Execution + Reporting runners | Via skill-loader + provisioner |
| Managed runner backend | Protocol seam: Docker (Phase 1) → K8s/other without rewriting agents |
| Final Deliverable Document | `GET …/final-deliverable`; compose from all artifacts |
| Seed skills | `skills/execution`, `skills/reporting` |

## Implementation order

1. **Contracts** — execution report + summary artifact schemas; `final_deliverable_document` metadata.
2. **Provisioner protocol** — abstract `create_runner` / `destroy_runner` / `apply_mount`; implement K8s (or chosen) adapter beside Docker.
3. **Execution skill path** — mount → call stubbed enterprise APIs → Execution Report Artifact.
4. **Reporting skill path** — aggregate prior artifacts → Summary Artifact.
5. **Composer** — after reporting (or last skill in hybrid path), build Final Deliverable Document; store URI on job-service.
6. **UI** — download/view final deliverable; show artifact list.

## Artifact chain (fixed names)

| Skill / step | Artifact |
|--------------|----------|
| Research | Research Findings Artifact |
| Planning | Plan & Recommendation Artifact |
| Execution | Execution Report Artifact |
| Reporting | Summary Artifact |
| Composition | **Final Deliverable Document** |

## Done checklist

```
- [ ] Execute + report routes work after approve
- [ ] Execution Report + Summary artifacts persisted
- [ ] Managed runner backend used (or explicitly deferred with issue filed)
- [ ] Final Deliverable Document composable and fetchable
- [ ] No MR/PR in pipeline
- [ ] Next: phase-4-knowledge-and-clients
```
