# 18 — Evaluation Frameworks (Custom Metrics, LLM-as-Judge, DeepEval)

## 1. Executive Summary

Evaluation is a **platform layer on top of traces**, not a LangGraph built-in. Score **agent/graph responses** (final output), **trajectories** (tool use / decomposition), and **skill versions** (aggregated, pinned suites). Prefer **custom code metrics + LLM-as-judge**; bind a framework in Stack Binding—**DeepEval** is the documented example; **LangSmith experiments / `agentevals`** are first-class alternatives. Results become [Evaluation](contracts/evaluation.json) records attached to episodes and used as promotion gates—never silent production skill mutation.

## 2. Purpose

Tell teams how to score runs and skills with interchangeable frameworks while keeping contracts and governance stable.

## 3. Scope

Evaluator types, metric catalog, DeepEval/LangSmith bindings, offline vs online, trajectory/tool/decomposition scoring, skill-version gates. Trace emission is doc 17. Reflection/promotion is doc 12.

## 4. Architecture Overview

```text
Traces (Langfuse/LangSmith) + Dataset goldens
        ↓
 Evaluation runner (DeepEval | LangSmith | custom)
   ├─ Code / custom metrics
   ├─ LLM-as-judge metrics
   └─ Trajectory / tool metrics
        ↓
 Evaluation record → Episode.scores
        ↓
 Staging soak / promotion gate / online monitors
```

See [../assets/diagrams/18-evaluation-flow.mmd](../assets/diagrams/18-evaluation-flow.mmd)

## 5. Core Concepts

- **Metric:** named scorer → `{ key, score|value, comment? }`.
- **Custom metric:** team-defined code or rubric (schema, policy, business rules).
- **LLM-as-judge:** model grades output/trajectory against a rubric (reference-free or reference-based).
- **Trajectory eval:** tool-call / message sequence quality (decomposition, tool choice).
- **Offline:** dataset experiments pre-deploy.
- **Online:** sample live traces without gold answers.
- **Criteria package:** versioned with the skill (`evaluation_criteria_ref` on manifest).

## 6. Design Decisions

| ID | Decision |
|----|----------|
| Ev1 | Frameworks are **bindings**; Evaluation JSON is the platform contract |
| Ev2 | Support **custom metrics** and **LLM-as-judge** by default |
| Ev3 | Example binding: **DeepEval** (`CallbackHandler` + metrics / pytest) |
| Ev4 | Alt binding: **LangSmith** `evaluate`/`aevaluate` + **`agentevals`** for trajectories |
| Ev5 | Score final answer **and** trajectory when tools/HITL matter |
| Ev6 | Pin `skill_id@version` + `graph_id` + `assembly_digest` on every Evaluation |
| Ev7 | Inconclusive / fail blocks staging→production when policy requires hard pass |
| Ev8 | Human ratings remain first-class alongside automated metrics |

## 7. Decision Rationale

Locking to one vendor in the core topology fights multi-cloud ICE constraints. Contracts + bindings let teams use DeepEval today and LangSmith tomorrow without rewriting promotion gates.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Only final-string BLEU/ROUGE | Misses tool misuse and bad plans |
| Only LLM-as-judge, no code checks | Expensive, flaky for schema/policy |
| Auto-promote on high judge score | Silent prod mutation |
| Framework-specific IDs as SoR | Breaks when swapping DeepEval ↔ LangSmith |

## 9. Tradeoffs

LLM-as-judge cost/latency vs nuance. Mitigate with cheap code gates first, judge on failures or sampled set.

## 10. Component Breakdown

### Metric catalog (opinionated starter)

| Key | Type | Use |
|-----|------|-----|
| `task_completion` | LLM-as-judge or DeepEval TaskCompletion | End-to-end goal met |
| `answer_correctness` | Reference-based judge / code | Vs golden |
| `tool_correctness` | Trajectory match / judge | Right tools + args |
| `trajectory_efficiency` | Judge or heuristic | No redundant loops |
| `policy_compliance` | Code + judge | Forbidden tools, PII, tone |
| `json_schema_valid` | Code | Structured outputs |
| `latency_p95_ms` | Code | Perf gate |
| `cost_usd` | Code from traces | FinOps gate |
| `hitl_appropriateness` | Judge | Interrupted when required |

Teams **must** be able to add custom keys beyond this list.

### DeepEval binding (example)

Docs: [DeepEval × LangGraph](https://deepeval.com/integrations/frameworks/langgraph)

**Runtime / online-style:**

```text
config.callbacks += CallbackHandler(metrics=[TaskCompletionMetric(), <CustomMetric>, <GEval rubric>...])
graph.invoke(input, config)
```

**CI / offline:**

```text
dataset goldens → pytest parametrize → invoke graph with CallbackHandler
→ assert_test / metric thresholds → fail build
```

**Component-level:** stage metrics on agent/LLM spans (`next_agent_span` / equivalent) to score planner vs executor separately (task decomposition).

**Confident AI:** optional hosted online evals via `metric_collection` on the handler.

### LangSmith / agentevals binding (alternative)

- Dataset + `evaluate`/`aevaluate` target wrapping `graph.ainvoke`
- Custom evaluator callables (code or LLM-as-judge)
- `agentevals` trajectory match: `strict` | `unordered` | `subset` | `superset` + trajectory LLM judge
- Docs: [Evaluate graph](https://docs.langchain.com/langsmith/evaluate-graph) · [Trajectory evals](https://docs.langchain.com/langsmith/trajectory-evals)

### Skill-version evaluation

1. Static gates (manifest, criteria present)  
2. Offline suite pinned to skill version (goldens)  
3. Staging soak: online/sample metrics vs thresholds  
4. Promotion Approval only if Evaluation pass (doc 06 / 12)

## 11. Sequence of Operations

### Offline (pre-promote)

1. Load criteria for skill version ([evaluation-criteria.json](contracts/evaluation-criteria.json)).
2. Run dataset through graph (traces emitted per doc 17).
3. Apply custom + LLM-as-judge + trajectory metrics (DeepEval or LangSmith).
4. Persist Evaluation; attach to experiment id + skill version.
5. Gate: fail → block staging/production label move.

### Online (production sample)

1. Sample traces from Langfuse/LangSmith (prefer failures + random %).
2. Reference-free metrics (toxicity, policy, task_completion without gold).
3. Write Evaluation; update Episode.scores; alert on regression.
4. Feed bad episodes into reflection cohorts (doc 12)—**proposals only**.

Algorithm: [../programs/evaluate-with-framework.md](../programs/evaluate-with-framework.md) · [../programs/evaluation.md](../programs/evaluation.md)

## 12. State Changes

| Subject | On eval complete |
|---------|------------------|
| run / episode | `scores` populated; may trigger alerts |
| skill_version staging | pass → eligible for prod Approval; fail → hold |
| skill_version production | never auto-changed by eval alone |

## 13. Mermaid Diagrams

See §4 diagram.

## 14. JSON Contracts

- [contracts/evaluation.json](contracts/evaluation.json)
- [contracts/evaluation-criteria.json](contracts/evaluation-criteria.json)
- [contracts/episodic-memory.json](contracts/episodic-memory.json)
- [contracts/reflection.json](contracts/reflection.json)

## 15. Best Practices

- Code metrics for hard constraints; LLM-as-judge for soft quality.
- Version rubrics with skills; pin judge model id in Evaluation metadata.
- Always evaluate trajectory when tools or multi-node plans exist.
- Keep a tiny golden set (10–20) before scaling synthetic data.
- Map framework-native scores → platform Evaluation.scores keys 1:1.

## 16. Anti-patterns

- Framework lock-in inside Orchestrator core
- Promoting skills on a single judge score without Approval
- Evaluating without skill version pins
- Ignoring tool trajectory when only checking final text

## 17. Common Mistakes

- Expecting LangGraph to “score itself”
- No traces → weak trajectory metrics
- Flaky judges without few-shot rubrics
- Treating DeepEval UI prompt edits as production procedural memory

## 18. Future Evolution

Canary skill labels driven by online metric SLOs; pairwise evals for prompt diffs.

## 19. Related Documents

[12-reflection-evaluation.md](12-reflection-evaluation.md) · [17-langgraph-observability.md](17-langgraph-observability.md) · [07-episodic-memory.md](07-episodic-memory.md) · [06-procedural-memory-skills.md](06-procedural-memory-skills.md) · [13-observability.md](13-observability.md)
