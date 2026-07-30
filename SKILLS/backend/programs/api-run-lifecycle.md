# Algorithm — API Run Lifecycle (Thread / Start / Interrupt / Resume)

## Purpose

Drive a frontend-agnostic HTTP (or MCP) lifecycle over LangGraph: create a thread, start a run, surface interrupts, and resume with `Command(resume=...)` without the client holding messages, context, or completed work.

## LangGraph binding

| API step | Primitive |
|----------|-----------|
| CreateThread | Allocate `thread_id` (platform); checkpointer empty until first run |
| StartRun | `graph.ainvoke(input, config)` or `stream_events(..., version="v3")` with `configurable.thread_id` |
| Detect interrupt | `result["__interrupt__"]` or `stream.interrupted` / `stream.interrupts` |
| GetThreadState | `graph.get_state(config)` → RuntimeState DTO |
| ResumeRun | `graph.ainvoke(Command(resume=value), same config)` — **no** original `input` |
| Parallel interrupts | `Command(resume={interrupt_id: value, ...})` |

Docs: [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) · [HITL Server API](https://docs.langchain.com/langsmith/add-human-in-the-loop) · [16 — API Surface](../references/16-api-surface-interrupt-resume.md)

## Inputs

- Authenticated identity (JWT)
- Optional `ThreadCreate`
- `RunCreate` **or** `ResumeRequest`
- Optional `Approval` when governance requires it

## Outputs

- `RunResult` (status, interrupts, optional messages_preview)
- Events: `thread.interrupted`, `thread.resumed`, `run.failed`
- Checkpoints written solely by LangGraph

## Preconditions

- Checkpointer configured (durable in production).
- Caller authorized for thread (ACL by user/org).
- For Resume: open interrupt on snapshot; roles satisfy `required_roles` when present.
- Resume body must contain `command.resume`, not a replay of initial `input`.

## Postconditions

- Client never required to resubmit STM/messages for continue.
- On interrupt: RunResult carries InterruptPayload DTOs; thread remains durable.
- On resume: node may re-execute pre-`interrupt()` code (idempotent); side effects only after return.

## Steps

### A. CreateThread

1. Validate JWT; derive `user_id`.
2. Create `thread_id` (or accept client UUID with uniqueness check).
3. Persist thread metadata (platform); do not write fake checkpoint rows.
4. Return `{ thread_id }`.

### B. StartRun

1. Authorize thread access.
2. Validate [run-create.json](../references/contracts/run-create.json): require `input`; reject if body looks like a resume (`command.resume` present → route to Resume).
3. Apply `multitask_strategy` if a run is already active.
4. Invoke graph with `config.configurable.thread_id = thread_id`.
5. If streaming: emit message/values events; on disconnect honor `on_disconnect`.
6. If interrupted: map each interrupt to InterruptPayload; set status `awaiting_approval` or `awaiting_input`; emit `thread.interrupted`; optionally fire webhook.
7. If completed: status `succeeded`; project output.
8. Return [run-result.json](../references/contracts/run-result.json).

### C. GetThreadState (any client, any time)

1. Authorize.
2. `get_state` → project [runtime-state.json](../references/contracts/runtime-state.json).
3. Include open interrupts; optional messages channel projection for UI.
4. Never treat this response as writable SoR.

### D. ResumeRun (frontend-agnostic)

1. Authorize; load snapshot; verify open interrupt(s).
2. If Approval required: ensure Approval recorded (or run ApproveAndResume as one transaction: persist Approval then resume).
3. Validate [resume-request.json](../references/contracts/resume-request.json).
4. Reject if `input` present instead of `command.resume`.
5. Reject if `checkpoint_id` set unless explicit time-travel API.
6. Map decision → resume value (single or id→value map).
7. `ainvoke(Command(resume=...), same thread_id)`.
8. Emit `thread.resumed`; return new RunResult (may interrupt again).

### E. ApproveAndResume (optional composite)

1. Validate role vs interrupt `required_roles`.
2. Persist append-only Approval.
3. Map `decision` → resume payload.
4. Execute ResumeRun steps 7–8.
5. On resume failure after Approval: emit error Event; leave graph state authoritative.

## Edge Cases

- **Stale interrupt** (already resumed): `409` or `410`; do not invoke Command.
- **Concurrent resumes:** one succeeds; others conflict.
- **Long human wait:** prefer async run + webhook/GetThreadState over multi-hour HTTP wait.
- **Revise loop:** resume with comments; graph returns to planning; may interrupt again.
- **Reject:** resume value routes to cancel branch; status `cancelled` or succeeded-with-cancel per graph design.

## Failure Handling

- Checkpointer failure on interrupt → do not advertise awaiting to clients.
- Authz failure → leave interrupted; no resume.
- Partial Approval persist + resume fail → compensating Event; operator retries Resume with `approval_id` only (no duplicate Approval) if policy allows.

## Related

[interrupt.md](interrupt.md) · [resume.md](resume.md) · [human-approval.md](human-approval.md) · [../references/16-api-surface-interrupt-resume.md](../references/16-api-surface-interrupt-resume.md)
