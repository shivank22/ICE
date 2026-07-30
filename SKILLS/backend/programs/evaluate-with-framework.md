# Algorithm — Evaluate With Framework (DeepEval / LangSmith example)

## Purpose

Score a run, episode, or skill version using a bound evaluation framework (DeepEval example; LangSmith/`agentevals` alternative), mapping results into the platform Evaluation contract for gates and episodic scores.

## Binding notes

- **Not built into LangGraph** — requires traces and/or returned outputs/trajectories.
- **DeepEval:** `CallbackHandler(metrics=[...])` on invoke; pytest + `assert_test`; custom metrics + GEval LLM-as-judge; component spans for decomposition.
- **LangSmith:** `evaluate`/`aevaluate` + custom evaluators; `agentevals` for trajectory match/judge.
- Docs: [18 — Evaluation Frameworks](../references/18-evaluation-frameworks.md) · [DeepEval LangGraph](https://deepeval.com/integrations/frameworks/langgraph)

## Inputs

- `subject` (run | episode | skill_version)
- `EvaluationCriteria` (metrics, thresholds, aggregation)
- Signals: outputs, trajectory/messages, trace_id, human ratings
- Framework binding from Stack Binding note

## Outputs

- Platform `Evaluation` record (`scores`, `pass`, `inconclusive`)
- Updated `Episode.scores` when subject is run/episode
- Gate decision for promotion (side effect caller)

## Preconditions

- Criteria loaded for skill/phase.
- For trajectory metrics: messages/tool spans available (from invoke result or Trace Store).
- Skill version pinned when subject is skill_version or regulated run.

## Postconditions

- Framework-native results mapped to Evaluation.scores keys.
- Missing required signal → `inconclusive` or fail per criteria.
- No production skill label changes inside this algorithm.

## Steps

1. Load [evaluation-criteria.json](../references/contracts/evaluation-criteria.json).
2. Collect signals (final output, trajectory, trace attributes, human scores).
3. Run **code/custom** metrics first (schema, policy, latency, cost).
4. Run **trajectory** metrics if tools/multi-node (match mode or judge).
5. Run **LLM-as-judge** metrics (task completion, correctness, soft quality).
6. Aggregate per criteria (`all_required_pass` default).
7. Persist Evaluation; link `trace_id`, `skill_versions`, criteria version, judge model id.
8. Emit `evaluation.completed`.
9. If promotion gate caller: block on fail/inconclusive when `inconclusive_blocks_promote`.

### DeepEval-oriented substeps (example)

1. Attach `CallbackHandler` with selected metrics for live scoring **or**
2. Offline: for each golden, invoke graph with handler; `assert_test` against thresholds.
3. Map DeepEval metric names → criteria `key`s.

### LangSmith-oriented substeps (example)

1. Define target `def target(inputs): return graph.invoke(...)` exposing `output` + `trajectory`.
2. `aevaluate(target, data=dataset, evaluators=[...])`.
3. Map feedback keys → Evaluation.scores.

## Edge Cases

- Custom metric throws → mark that key failed; do not skip required_for_promote keys silently.
- Judge disagreement with code metric → fail closed; note in `comment`.
- Parallel skill pins → evaluate each pinned skill’s criteria or the primary skill per policy.

## Failure Handling

Do not promote on runner crash; leave Evaluation incomplete and alert. Retry idempotent offline experiments with same experiment prefix only when intentional.
