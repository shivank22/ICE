# Algorithm — Resume

## Purpose

Continue a thread from an interrupt with Approval or revision input.

## Inputs

- `thread_id`
- `interrupt_id`
- `decision` (approve | revise | reject)
- `comments` / structured input
- `identity`

## Outputs

- Runtime status `running` (or terminal if reject policy says so)
- New checkpoint

## Preconditions

- Interrupt is open.
- Identity satisfies required_roles.
- Checkpoint for interrupt exists.

## Postconditions

- Interrupt closed with decision.
- Revision comments recorded in Thread State.
- Graph continues from gated node semantics.

## Steps

1. Authorize identity vs interrupt.required_roles.
2. Checkpoint Restore at interrupt checkpoint.
3. Validate interrupt still open.
4. Record Approval object.
5. If approve: clear interrupt; schedule next node.
6. If revise: inject revision message; re-enter node or prior planning node per graph policy.
7. If reject: transition to cancelled/failed per policy.
8. Checkpoint Save; emit Event.

## Edge Cases

- Stale interrupt id → reject resume.
- Concurrent resumes → single winner via conditional update.

## Failure Handling

Leave interrupt open on failure; surface retryable error.
