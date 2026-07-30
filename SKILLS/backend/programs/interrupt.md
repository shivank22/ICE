# Algorithm — Interrupt

## Purpose

Pause a running graph for external input (typically human approval).

## Inputs

- `thread_id`
- `interrupt_type` (approval | input | policy_hold)
- `payload` (summary, artifacts, options)
- `required_roles`

## Outputs

- Updated runtime status `awaiting_approval`
- `interrupt` record
- Checkpoint saved

## Preconditions

- Thread status is `running`.
- Side effects for this node are either not yet executed or are reversible per policy.

## Postconditions

- Scheduling stopped.
- Interrupt id open and unique.
- Notification event emitted.

## Steps

1. Validate gate node allows interrupt.
2. Build interrupt payload (human-readable).
3. Set runtime.status = awaiting_approval; attach interrupt id.
4. Checkpoint Save.
5. Emit `job.awaiting_approval` (or equivalent Event).
6. Stop further node scheduling.

## Edge Cases

- Duplicate interrupt on same node → idempotent return existing open interrupt.
- Missing required_roles → default to engagement owner / admin policy.

## Failure Handling

If checkpoint save fails, do not advertise interrupt to users; retry or fail thread safely.
