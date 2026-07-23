---
name: phase-5-finops-and-adaption
description: >-
  Implements Phase 5: finops-engine (cost_record from traces and runner metrics),
  adaption-engine (engagement tracks and stakeholder email), and cost/engagement
  dashboards. Use when adding FinOps, Adaption, cost APIs, or stakeholder outreach.
disable-model-invocation: true
---

# Phase 5 — FinOps + Adaption

Implement **build order Phase 5** from [`ARCHITECTURE.md`](../../ARCHITECTURE.md).

## Prerequisites

1. Pipeline through Phase 4 (or at least jobs + events exist); read `framework/.stack.md`.
2. Diagrams: [`docs/08-finops-engine`](../../docs/08-finops-engine.md), [`docs/09-adaption-engine`](../../docs/09-adaption-engine.md).
3. Field lists: [`reference.md`](reference.md).

## Must not change

- **finops-engine** exclusively owns `cost_record` (no other service writes it)
- FinOps ingest is **async** — downtime must not block jobs
- **adaption-engine** consumes lifecycle events from the bus; pipeline never waits on email
- Gateway routes: `GET /engagements/{id}/costs`, `GET /engagements/{id}/track`
- Adaption emails **stakeholders**, not “application owners”

## Must ask (if not in `.stack.md`)

- FinOps v1: model cost only vs include runner compute
- Trace source (Langfuse pull/webhook vs OTel)
- Email transport: Graph / SMTP / SES / ACS / other
- Quiet hours / unsubscribe policy
- Dashboard: embed in `apps/web` vs separate BI tool

## Scope

| Deliverable | Notes |
|-------------|--------|
| `finops-engine` | Ingest traces + runner lifetime → `cost_record` + rollups |
| Cost APIs | Engagement + program rollups via gateway |
| `adaption-engine` | `engagement_track`, `email_event`, triggers |
| Mail transport interface | Pluggable behind one interface |
| Scheduler | SLA / idle sweeps separate from event consumer |
| Dashboards | Cost per run; engagement track status |

## Implementation order

1. **Schemas** — see [`reference.md`](reference.md).
2. **finops ingest workers** — map spans → cost_record; optional runner cost from job-service events.
3. **Gateway cost routes** + web cost view (`finops-viewer` role).
4. **adaption event consumer** — on plan ready, HITL idle, wizard abandoned, execution complete, deadline approaching.
5. **Email sender** + audit `email_event`.
6. **Scheduler** for idle/SLA.
7. **UI** track status + recent emails (metadata only).

## Example Adaption triggers (fixed intents)

| Event | Email intent |
|-------|----------------|
| Plan ready | Approve link |
| HITL idle > N days | Reminder |
| Wizard abandoned | Nudge to resume |
| Execution complete | Summary + next steps |
| Deadline approaching | Urgency |

## Done checklist

```
- [ ] cost_record written only by finops-engine
- [ ] GET /engagements/{id}/costs works
- [ ] engagement_track + email_event working
- [ ] GET /engagements/{id}/track works
- [ ] Email transport pluggable; pipeline not blocked by email
- [ ] Basic cost + engagement dashboards
- [ ] Architecture Phase 1–5 scaffold complete for this stack
```
