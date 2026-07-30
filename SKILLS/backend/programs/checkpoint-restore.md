# Algorithm — Checkpoint Restore

## Purpose

Load thread graph state for continue, inspect, or time travel. **LangGraph restores automatically** when you invoke/stream with an existing `thread_id` (latest) or a historical checkpoint config.

## LangGraph binding

- Latest: `graph.invoke(..., config={"configurable": {"thread_id": ...}})` or `graph.get_state(config)`
- History: `list(graph.get_state_history(config))`
- Specific checkpoint: pass that snapshot’s `config` (includes `checkpoint_id`) into invoke / get_state
- Docs: [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) · [Time travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel)

## Inputs

- Compiled graph with same checkpointer backend
- `thread_id`
- Optional `checkpoint_id` / snapshot `config` (omit for latest)
- `identity` (ACL before exposing state)

## Outputs

- `StateSnapshot` (values, next, config, interrupts, metadata, parent_config)
- Optional API projection: `RuntimeState` / `ThreadState` DTOs derived from snapshot—not a second store

## Preconditions

- Caller authorized for thread.
- Checkpointer reachable; thread exists or empty state accepted for new threads.

## Postconditions

- Caller observes consistent snapshot; no partial custom deserialize into a parallel state DB.
- Production “current” pointer unchanged by read-only `get_state` / history listing.

## Steps

1. Authorize thread access (platform ACL).
2. If inspect only: `graph.get_state(config)` or iterate `get_state_history`.
3. If continue from latest: invoke/stream with same `thread_id` and appropriate input (`None` / `Command(resume=...)` / new messages)—**do not** re-pass full prior state as a new run input unless intentionally starting fresh.
4. If time travel: select historical snapshot config; invoke with that config (understand replay re-executes nodes).
5. Map snapshot → `RuntimeState` DTO for clients if needed.

## Edge Cases

- Empty thread → empty/default state.
- Passing `checkpoint_id` unintentionally → time travel instead of resume-from-latest; omit unless intended.
- Schema drift in channel values → project with warnings; prefer versioned state schemas.

## Failure Handling

Surface checkpointer errors; do not fabricate state. Quarantine corrupt checkpoint rows via ops; restore from prior history entry if available.
