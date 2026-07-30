# Algorithm — Human Approval

## Purpose

Record a governed decision that unblocks an interrupt or promotion.

## Inputs

- `target_type` (interrupt | promotion | policy_exception)
- `target_id`
- `decision`
- `identity`
- `comments`

## Outputs

- `approval` record

## Preconditions

- Identity has required role.
- Target is awaiting decision.

## Postconditions

- Decision immutable (append corrections as new records if needed).
- Downstream Resume or Learning Promotion may proceed.

## Steps

1. Authorize role.
2. Load target; verify awaiting state.
3. Validate decision enum for target_type.
4. Persist Approval with timestamp and actor.
5. Emit Event.
6. Invoke Resume or Learning Promotion as applicable.

## Edge Cases

- Delegation: allow designated approvers list.
- Dual control: require two Approvals for high risk.

## Failure Handling

On persistence failure, leave target awaiting; no side effects.
