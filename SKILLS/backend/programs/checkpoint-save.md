# Algorithm — Checkpoint Save

## Purpose

Ensure thread graph state is durably snapshotted. **LangGraph’s checkpointer performs saves automatically** when the graph is compiled with a checkpointer—application code does not implement a custom checkpoint writer for normal steps.

## LangGraph binding

- `graph = builder.compile(checkpointer=PostgresSaver | SqliteSaver | InMemorySaver)`
- Config: `{"configurable": {"thread_id": ...}}` (optional `checkpoint_ns` for subgraphs)
- Production: durable checkpointer (e.g. `PostgresSaver`); never `InMemorySaver` alone in prod
- Docs: [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) · [Checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers)

## Inputs

- Compiled graph with checkpointer
- `thread_id` (and optional namespace) in invoke/stream config
- Graph state updates produced by nodes (messages, channels)

## Outputs

- New checkpoint in the checkpointer store (LangGraph-managed id / parent lineage)
- Observable via `graph.get_state(config)` / `get_state_history`

## Preconditions

- Single writer path: the compiled graph + checkpointer (no second service writing the same thread’s checkpoints).
- State channels serializable; large blobs stored by reference in state.
- `thread_id` length within backend limits (e.g. PostgresSaver column limits).

## Postconditions

- Latest checkpoint for `thread_id` reflects completed step.
- Parent lineage preserved for time travel.

## Steps

1. Compile graph once with production checkpointer; call `setup()` if required by backend.
2. Invoke/stream with stable `thread_id` in config—**do not** hand-roll INSERT into checkpoint tables.
3. After step, optionally read `graph.get_state(config)` for API projection (`RuntimeState` DTO).
4. Emit platform `checkpoint.saved` telemetry if needed (correlate `thread_id` + checkpoint id from snapshot).
5. Apply retention/TTL/prune jobs on the checkpointer backend (ops)—do not skip durability to save space.

## Edge Cases

- Unbounded history → prune old checkpoints per policy ([persistence troubleshooting](https://docs.langchain.com/oss/python/langgraph/persistence)).
- Subgraphs → configure subgraph checkpointing (`checkpointer=True` / namespace) so nested state is saved correctly.

## Failure Handling

On checkpointer write failure, LangGraph surfaces the error; do not advance external side effects that assumed durability. Retry idempotent invokes; quarantine corrupt backends via ops playbooks.


