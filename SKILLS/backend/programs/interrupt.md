# Algorithm — Interrupt

## Purpose

Pause a running graph for external input (typically human approval) using LangGraph’s **`interrupt()`** primitive—not a custom “stop the scheduler” service.

## LangGraph binding

- Inside a node: `value = interrupt(payload)` where `payload` is JSON-serializable
- Requires a **checkpointer**; state is persisted automatically when the interrupt fires
- Prefer **dynamic** `interrupt()` for HITL; use `interrupt_before` / `interrupt_after` for **debug/static breakpoints**, not production approval gates
- Surface to clients via stream interrupts / `__interrupt__` on invoke result; map to `InterruptPayload` DTO
- Docs: [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)

## Inputs

- Graph node execution context
- `payload` (summary, artifacts, options, required_roles, type)
- Checkpointer-backed compiled graph + `thread_id` in config

## Outputs

- Graph paused; interrupt value returned to caller
- Checkpoint saved by LangGraph
- Platform notification event (optional) with `thread_id` + interrupt id/value

## Preconditions

- Checkpointer enabled.
- **Node is idempotent through the `interrupt()` call:** on resume, LangGraph **re-executes the node from the beginning**. Any side effects before `interrupt()` run again.
- Irreversible tools/effects occur **only after** a successful resume path past `interrupt()`.

## Postconditions

- Execution waiting for `Command(resume=...)`.
- Interrupt payload available to Approval UI.
- No second custom checkpoint writer invoked.

## Steps

1. In the gate node, build JSON-serializable interrupt payload (human-readable summary, artifact ids, options, required_roles).
2. Ensure no irreversible side effect has run yet in this node invocation.
3. Call `interrupt(payload)` — LangGraph raises/suspends and persists checkpoint.
4. API layer maps returned interrupt to `InterruptPayload` / `awaiting_approval` **projection** for clients (status is derived from snapshot interrupts, not a separately authored FSM store).
5. Emit `job.awaiting_approval` for notifications.

## Edge Cases

- Multiple interrupts in one node → order matters; LangGraph matches resume values by order—keep one HITL interrupt per node when possible, or document multi-interrupt resume carefully.
- Missing required_roles → default to engagement owner / admin policy in payload.

## Failure Handling

If checkpointer cannot persist, interrupt will not be safely resumable—fail the run; do not advertise approval to users until persistence succeeds.
