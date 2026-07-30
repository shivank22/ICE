# Algorithm — Human Approval

## Purpose

Record a governed decision that unblocks a LangGraph interrupt (via resume) or a skill promotion.

## LangGraph binding (run gate)

- Open interrupt comes from `interrupt(payload)` / snapshot interrupts
- After Approval is recorded: invoke Resume algorithm → `Command(resume=decision_value)` with same `thread_id`
- Approval store is platform governance; LangGraph remains durability SoR for the thread
- Docs: [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)

## Inputs

- `target_type` (interrupt | promotion | policy_exception)
- `target_id` / `thread_id` + interrupt id
- `decision`
- `identity`
- `comments`

## Outputs

- `approval` record
- Side effect: Resume invoked (interrupt) or Learning Promotion (skill label)

## Preconditions

- Identity has required role (from interrupt payload `required_roles` or policy).
- Target is awaiting decision (LangGraph open interrupt or promotion pending).

## Postconditions

- Decision immutable (append corrections as new records if needed).
- Downstream Resume (`Command(resume=...)`) or Learning Promotion may proceed.
- No custom clearing of interrupt state outside LangGraph.

## Steps

1. Authorize role.
2. Load target; verify awaiting state (`get_state` interrupts for run gate).
3. Validate decision enum for target_type.
4. Persist Approval with timestamp and actor (append-only).
5. Emit Event.
6. If interrupt: call Resume algorithm with mapped resume value.
7. If promotion: call Learning Promotion algorithm.

## Edge Cases

- Delegation: allow designated approvers list.
- Dual control: require two Approvals for high risk before Resume/Promotion.
- Reject: resume value or graph branch leads to cancelled path per policy.

## Failure Handling

On Approval persistence failure, leave target awaiting; do not call `Command(resume=...)`. On resume failure after Approval recorded, mark Approval with follow-up error event; do not silently invent a parallel “approved” flag that disagrees with LangGraph.
