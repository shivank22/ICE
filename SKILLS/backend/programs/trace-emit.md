# Algorithm — Trace Emit (Graph + Agent Level)

## Purpose

Emit correlatable traces for every LangGraph run at **graph level** and **agent/component level**, then link terminal runs to episodic memory.

## LangGraph / binding notes

- LangGraph does not replace a Trace Store; use callbacks / auto-trace.
- **Langfuse:** `CallbackHandler` on `config.callbacks`; optional `@observe` / `propagate_attributes` for session (`thread_id`) and user.
- **LangSmith:** tracing env + `@traceable` for custom spans; metadata/tags on config.
- Docs: [Observability](https://docs.langchain.com/oss/python/langgraph/observability) · [Langfuse LangGraph](https://langfuse.com/guides/cookbook/integration_langgraph) · [17 — LangGraph Observability](../references/17-langgraph-observability.md)

## Inputs

- `thread_id`, `run_id`, identity claims
- `graph_id`, skill pins, `assembly_digest` (when known)
- Compiled graph invoke/stream call
- Trace backend client/handler

## Outputs

- Nested spans in Trace Store
- `trace_id` (vendor id)
- On terminal: Episode draft with `trace_id`

## Preconditions

- Trace backend configured for environment (or explicit no-op with warning in non-prod only).
- PII anonymizers registered where required.

## Postconditions

- Root graph span exists for the run.
- Node/tool/LLM work nested when instrumented.
- Failures and interrupts retained even if happy-path sampling is low.

## Steps

1. Create/attach CallbackHandler (or ensure auto-trace env) **once** at request/graph scope—not inside each node.
2. Open graph-level context: set metadata (`thread_id`, `run_id`, `user_id`, `org_id`, `graph_id`, `env`, skill pins).
3. Invoke `ainvoke` / `stream_events` with `config={"callbacks": [...], "configurable": {"thread_id": ...}, "metadata": {...}, "tags": [...]}`.
4. For custom Python in nodes: wrap with `@traceable` / `@observe` so spans nest.
5. On interrupt: record status + interrupt summary attributes; do not close session identity.
6. On resume: reuse `thread_id` / session id; new run_id allowed; link parent session.
7. On terminal: finalize root; capture cost/latency rollup.
8. Curate Episode: outcome, skill_versions, artifact_ids, `trace_id`; emit `episode.completed`.
9. Hand off to evaluation runner when offline suite or online sample policy applies.

## Edge Cases

- Serverless: force flush before freeze/exit.
- Parallel nodes: ensure handler supports concurrent spans; avoid per-task new global clients that break nesting.
- Sampling: force keep if error, interrupt, or `tags` contains `debug` / `regulated`.

## Failure Handling

If export fails, buffer or mark run `trace_incomplete`; still persist checkpoint. Do not fail the user-visible run solely on telemetry loss unless policy requires.
