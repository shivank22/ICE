# Phase 1 — Contracts reference

Source: [`ARCHITECTURE.md`](../../ARCHITECTURE.md) Part A + domain model.

## Gateway routes (Phase 1 minimum)

| Method | Path | Owner behind gateway |
|--------|------|----------------------|
| `POST` | `/engagements` | knowledge-service **or** job-service stub (document choice in `.stack.md`) |
| `GET` | `/engagements/{id}` | same |
| `POST` | `/engagements/{id}/research` | job-service → orchestrator/runner path |
| `GET` | `/engagements/{id}/findings` | job-service / knowledge |
| `GET` | `/engagements/{id}/jobs/{job_id}` | job-service |
| `GET` | `/engagements/{id}/jobs/{job_id}/events` | job-service (SSE) |
| `GET` | `/engagements/{id}/jobs/{job_id}/artifacts` | job-service |
| `GET` | `/engagements/{id}/jobs/{job_id}/artifacts/{artifact_id}` | job-service |

Defer until later phases: `/plan`, `/approve`, `/execute`, `/report`, `/final-deliverable`, `/costs`, `/track`.

## Logical entities (Phase 1)

### `engagement`

`id`, `title`, `status`, `stakeholder_emails[]`, `created_at`, `updated_at`

### `job`

`id`, `engagement_id`, `phase` (`research`), `status` (`pending|running|awaiting_user|succeeded|failed`), `created_at`, `updated_at`

### `skill_artifact`

`id`, `job_id`, `engagement_id`, `skill_key` (`research`), `version`, `content_type`, `storage_uri`, `checksum`, `created_at`

### Research Findings Artifact (payload sketch)

```json
{
  "engagement_id": "…",
  "confirmed": true,
  "scope": { "summary": "…" },
  "stakeholders": [{ "email": "…", "role": "…" }],
  "context": {},
  "constraints": {},
  "notes": "…",
  "confirmed_at": "ISO-8601"
}
```

## Wizard steps (Skill 1)

1. Confirm scope & stakeholders  
2. Gather context & dependencies  
3. Review inputs & constraints  
4. User confirms findings → persist artifact  

Progress via LangGraph checkpoints **or** equivalent state machine in the chosen language; UI gets SSE updates.

## Events (minimal)

Publish (bus or in-process): `job.created`, `job.phase_started`, `job.phase_succeeded`, `artifact.created`, `wizard.abandoned` (stub OK).

## RBAC roles (illustrative)

`viewer`, `operator`, `admin` — wire at least operator for research + confirm.
