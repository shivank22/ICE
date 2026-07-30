# Algorithm — Checkpoint Save

## Purpose

Persist a durable snapshot of Thread/Runtime State.

## Inputs

- `thread_id`
- `runtime_state`
- `thread_state`
- `parent_checkpoint_id` (optional)
- `metadata`

## Outputs

- `checkpoint`

## Preconditions

- Caller is Orchestrator (single writer).
- State serializable under current schema_version.

## Postconditions

- New checkpoint id is current for thread.
- Parent lineage linked.

## Steps

1. Validate schema_version.
2. Serialize state (replace large blobs with refs).
3. Atomic write with parent pointer.
4. Update thread current_checkpoint_id.
5. Emit `checkpoint.saved`.

## Edge Cases

- Serialization exceeds size limit → offload channels to object store refs, retry.
- Parent missing → reject (except first checkpoint).

## Failure Handling

On write failure, keep previous current pointer; surface retryable error.
