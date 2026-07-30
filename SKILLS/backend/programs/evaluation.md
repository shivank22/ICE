# Algorithm — Evaluation

## Purpose

Score a run, episode, or skill version against criteria.

## Inputs

- `subject` (run_id | episode_id | skill_version)
- `criteria[]`
- `signals` (trace metrics, human ratings, tests)

## Outputs

- `evaluation` record with scores and pass/fail

## Preconditions

- Criteria defined for subject type.
- Signals available or marked missing.

## Postconditions

- Evaluation linked to subject.
- Gate decisions can read pass/fail.

## Steps

1. Load criteria for skill/phase.
2. Collect signals (auto + human).
3. Compute per-criterion scores.
4. Aggregate with weights; determine pass/fail vs thresholds.
5. Persist Evaluation; attach to Episode.
6. Emit `evaluation.completed`.

## Edge Cases

- Missing mandatory signal → fail or `inconclusive` per policy.
- Human rating conflicts → escalate.

## Failure Handling

Do not promote on inconclusive when policy requires hard pass.

## Related

Framework runners: [evaluate-with-framework.md](evaluate-with-framework.md) · [../references/18-evaluation-frameworks.md](../references/18-evaluation-frameworks.md) · criteria [../references/contracts/evaluation-criteria.json](../references/contracts/evaluation-criteria.json)
