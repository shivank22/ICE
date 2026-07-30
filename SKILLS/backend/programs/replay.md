# Algorithm — Replay

## Purpose

Inspect or guarded-reexecute history from a checkpoint for audit/debug.

## Inputs

- `thread_id`
- `checkpoint_id`
- `mode` (read_only | simulated | reexecute)
- `identity`

## Outputs

- Reconstructed view and/or simulated results
- Audit log entry

## Preconditions

- Identity has debug/audit role.
- Checkpoint intact.

## Postconditions

- Production thread pointer unchanged unless explicit fork requested.
- Side effects in `reexecute` mode follow allowlist.

## Steps

1. Authorize audit role.
2. Restore checkpoint into isolated replay workspace.
3. If read_only: materialize state + context digest; return.
4. If simulated: run graph with tool stubs; record hypothetical outcomes.
5. If reexecute: allow only idempotent/safe tools; block payments/emails unless flagged.
6. Emit `replay.performed` with mode and actor.

## Edge Cases

- Missing tool stubs → mark node `unreplayable`.
- Schema drift → best-effort projection with warnings.

## Failure Handling

Never mutate production current_checkpoint_id on failure.
