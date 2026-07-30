# Algorithm — Reflection

## Purpose

Analyze episodic cohorts and emit a Reflection Proposal (never a production write).

## Inputs

- `episode_ids[]` or query cohort
- `target_skill_id` (optional)
- `evaluation_criteria`

## Outputs

- `reflection_proposal`

## Preconditions

- Episodes complete and linked to skill versions.
- Critieria available.

## Postconditions

- Proposal stored with evidence links.
- No production skill label changed.

## Steps

1. Load episodes, traces summaries, scores, failure taxonomies.
2. Cluster patterns (failures, regressions, cost spikes).
3. Generate proposed skill/policy diff with rationale.
4. Attach evidence (episode ids, example spans).
5. Score confidence; mark needs_human_review.
6. Persist proposal status `open`.

## Edge Cases

- Insufficient episodes → proposal `deferred`.
- Conflicting patterns → multiple alternative proposals.

## Failure Handling

On model failure, leave cohort unmarked or `under_reflection` for retry; never partial-apply diffs.
