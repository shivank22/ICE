# Algorithm — Learning Promotion

## Purpose

Promote an approved Reflection Proposal into a **draft skill change**, then advance `skill.yaml` status under governance. Never write skill bodies to Postgres as SoR; CI re-indexes cards after promote. For blob channels, publish the package artifact when status warrants it.

## Inputs

- `proposal_id`
- `approval`
- `target_status_path` (e.g. draft → staging → production)

## Outputs

- Updated `SKILL.md` / package files and `skill.yaml` version/status (via reviewed change)
- CI sync updates pgvector index after promote
- Optional blob publish when `locator.backend=blob`

## Preconditions

- Approval valid for promotion.
- Proposal status open.
- Diff applies cleanly to base skill version.

## Postconditions

- Production packages unchanged until production Approval + promote.
- Audit trail links proposal → change → version → approvals → index row.

## Steps

1. Verify Approval.
2. Apply diff as **draft** (`skill.yaml` status draft or staging per policy).
3. CI: validate structure, yaml, tests, secrets (skill-ci-sync stages).
4. Staging Approval → set status staging; promote as policy dictates.
5. Soak with Evaluation thresholds (doc 18).
6. Production Approval → set `status: production` in `skill.yaml`.
7. CI sync upserts index (`index_ready`); publish blob artifact when that channel is used.
8. Close proposal as `accepted`.

## Edge Cases

- Base skill changed since proposal → re-base / new proposal.
- Eval fails in staging → stop; do not promote production status.

## Failure Handling

Revert/close the change on failed move; keep draft for inspection. Never “fix” by editing the index alone.

## Related

[../references/12-reflection-evaluation.md](../references/12-reflection-evaluation.md) · [skill-ci-sync.md](skill-ci-sync.md)
