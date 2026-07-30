# Algorithm — Learning Promotion

## Purpose

Promote an approved Reflection Proposal into a new draft skill version and optionally advance labels under governance.

## Inputs

- `proposal_id`
- `approval`
- `target_label_path` (e.g. draft → staging → production)

## Outputs

- New `skill` version ids and label pointers

## Preconditions

- Approval valid for promotion.
- Proposal status open.
- Diff applies cleanly to base skill version.

## Postconditions

- Production unchanged until explicit production Approval.
- Audit trail links proposal → versions → approvals.

## Steps

1. Verify Approval.
2. Apply diff to create **draft** skill version in registry.
3. Run automated validations (manifest schema, eval criteria present).
4. Optionally move to staging after staging Approval.
5. Soak with Evaluation thresholds.
6. Production Approval → move production label.
7. Close proposal as `accepted`.

## Edge Cases

- Base skill changed since proposal → require re-base / new proposal.
- Eval fails in staging → stop; do not promote.

## Failure Handling

Roll back label pointer on failed move; keep draft for inspection.
