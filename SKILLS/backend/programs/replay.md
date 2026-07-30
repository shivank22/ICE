# Algorithm — Replay

## Purpose

Inspect or re-drive history from a checkpoint for audit/debug using LangGraph **time travel** APIs—not a separate replay engine that mutates production pointers by default.

## LangGraph binding

- Inspect: `graph.get_state_history(config)` → `StateSnapshot` list
- Replay from checkpoint: `invoke` / `stream` with that snapshot’s `config` (includes `checkpoint_id`)
- Fork / branch: `graph.update_state(checkpoint_config, values=...)` then `invoke(None, config=...)` — creates a **new** checkpoint branch; does not delete history
- **Replay re-executes nodes** (LLM/tool calls may differ); final checkpoint with no `next` is effectively a no-op
- Docs: [Time travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel)

## Inputs

- `thread_id`
- Optional `checkpoint_id` / snapshot config
- `mode` (read_only | simulated | reexecute)
- `identity` (debug/audit role)

## Outputs

- Reconstructed view and/or re-execution results
- Audit log entry
- Optional forked thread_id / branch config

## Preconditions

- Identity has debug/audit role.
- Checkpointer history intact.
- For `reexecute` / `simulated`: tool allowlist / stubs defined (platform policy).

## Postconditions

- `read_only`: production current checkpoint unchanged.
- `simulated` / guarded `reexecute`: prefer **fork** (new thread or branched config) so production pointer stays intact unless explicit overwrite requested.
- Side effects follow allowlist.

## Steps

1. Authorize audit role.
2. `snapshots = list(graph.get_state_history({"configurable": {"thread_id": ...}}))`.
3. Select target snapshot.
4. If `read_only`: return snapshot values + optional context digest reconstruction; stop.
5. If `simulated`: fork via `update_state` / new thread_id; run with tool stubs; record hypothetical outcomes.
6. If `reexecute`: fork by default; allow only idempotent/safe tools; block payments/emails unless flagged; invoke with snapshot config.
7. Emit `replay.performed` with mode, actor, source checkpoint id, fork id.

## Edge Cases

- Missing tool stubs → mark node `unreplayable`.
- Schema drift → best-effort projection with warnings.
- Replaying past irreversible effects without guards → **forbidden** by default.

## Failure Handling

Never mutate production `thread_id` current tip on failure. Prefer disposable fork threads for experiments.
