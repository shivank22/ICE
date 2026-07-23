# Phase 5 — Contracts reference

Source: [`ARCHITECTURE.md`](../../ARCHITECTURE.md) Parts D–E.

## `cost_record` fields

`id`, `job_id`, `engagement_id`, `skill_key`, `phase`, `agent_id`, `token_input`, `token_output`, `model_cost`, `runner_cost`, `total_cost`, `currency`, `recorded_at`

**Ownership:** finops-engine only.

**Ingest (async):**
- Trace spans (tokens, model, latency) keyed by job / phase / skill / agent
- Runner lifetime events from job-service (when metering runner $)

**APIs (via gateway):**
- `GET /engagements/{id}/costs` — rollup for engagement
- Optional program-level rollups by skill / day

## `engagement_track` fields

`engagement_id`, `stage`, `stakeholder_emails`, `last_contact_at`, `next_action`, `sla_due_at`, `status`

## `email_event` fields (audit)

`id`, `engagement_id`, `trigger`, `to[]`, `subject`, `provider_message_id`, `sent_at`, `status`

## Gateway routes (Phase 5)

| Method | Path | Service |
|--------|------|---------|
| `GET` | `/engagements/{id}/costs` | finops-engine |
| `GET` | `/engagements/{id}/track` | adaption-engine |

## Deployment notes

- Both engines independently deployable behind gateway
- Message bus decoupling required for adaption and recommended for finops ingest
- Mail transport behind one interface (Graph / SMTP / SES / ACS / …)
- Scheduler component for SLA/idle timers ≠ event consumer process
