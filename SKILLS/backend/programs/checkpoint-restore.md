# Algorithm — Checkpoint Restore

## Purpose

Load Thread/Runtime State from a checkpoint.

## Inputs

- `thread_id`
- `checkpoint_id` (or `latest`)
- `identity` (ACL)

## Outputs

- Restored `runtime_state`, `thread_state`

## Preconditions

- Caller authorized for thread.
- Checkpoint exists and is not quarantined.

## Postconditions

- In-memory state matches checkpoint payload.
- Corrupt checkpoints are not partially applied.

## Steps

1. Authorize thread access.
2. Fetch checkpoint row.
3. Validate checksum/schema.
4. Resolve artifact refs as needed.
5. Materialize state in Orchestrator.
6. Emit `checkpoint.restored` (debug/audit).

## Edge Cases

- `latest` on empty thread → empty state.
- Schema newer than runtime → fail with upgrade required.

## Failure Handling

Quarantine checksum failures; restore previous known-good if configured.
