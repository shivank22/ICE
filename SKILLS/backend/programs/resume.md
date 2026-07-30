# Algorithm — Resume

## Purpose

Continue a thread after an interrupt by re-invoking the graph with LangGraph **`Command(resume=...)`** and the **same `thread_id`**.

## LangGraph binding

- `graph.invoke(Command(resume=decision_value), config={"configurable": {"thread_id": same_id}})`
- Resume value becomes the return value of `interrupt()` inside the node
- **Do not** re-pass the original graph input/state to “continue”—that starts a new run from the entrypoint
- **Do not** set `checkpoint_id` unless intentionally time-traveling
- Docs: [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)

## Inputs

- `thread_id` (same as interrupt)
- Resume value / Approval decision (approve | revise | reject + comments)
- `identity` (must satisfy required_roles from interrupt payload)
- Compiled graph + checkpointer

## Outputs

- Graph continues; node completes past `interrupt()`
- New checkpoints written by LangGraph
- Approval audit record (platform)

## Preconditions

- Interrupt is open (visible on `get_state(config).tasks` / interrupts).
- Identity authorized.
- Node logic remains idempotent for re-entry before `interrupt()`.

## Postconditions

- Interrupt consumed for this resume.
- Revision comments applied via resume value and/or state update per graph design.
- Reject path follows graph branches (return resume value that routes to cancel, or `update_state` + conditional edges as designed).

## Steps

1. Authorize identity vs interrupt `required_roles` (platform Approval gate).
2. Record append-only Approval object (platform governance—not LangGraph).
3. Map decision → resume payload (boolean, structured object, or revision text).
4. `graph.invoke(Command(resume=payload), config)` with **same** `thread_id`, **no** accidental `checkpoint_id`.
5. On revise: resume value should instruct the node to replan; or use `update_state` then continue—document which pattern the graph uses.
6. On reject: resume value or subsequent edge leads to cancelled/failed terminal per policy.
7. Project new `StateSnapshot` to clients; emit Event.

## Edge Cases

- Stale / already-resumed interrupt → reject with clear error.
- Concurrent resumes → single winner; others fail authz or state conflict.
- Need multiple what-if resumes from same interrupt → fork with `update_state` duplication pattern; do not blindly re-resume the same config repeatedly without branching.

## Failure Handling

Leave graph interrupted on failure; surface retryable error. Do not clear interrupt in a side database that disagrees with LangGraph state.

## Related

API scaffolding for any frontend: [api-run-lifecycle.md](api-run-lifecycle.md) · [../references/16-api-surface-interrupt-resume.md](../references/16-api-surface-interrupt-resume.md) · contract [../references/contracts/resume-request.json](../references/contracts/resume-request.json)
