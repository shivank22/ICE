# 16 — API Surface: Threads, Runs, Interrupt & Resume

## 1. Executive Summary

Frontends are **not** the source of truth for agent work. Any client (web, mobile, Slack, CLI, MCP) talks to a **frontend-agnostic HTTP/API surface** that wraps LangGraph: create a **Thread**, start a **Run**, surface **Interrupt** payloads when the graph pauses, and **Resume** with `Command(resume=...)` on the same `thread_id`. Messages, context inputs already applied, and completed graph work live in the **checkpointer**; clients only exchange DTOs and decisions.

This document defines the **API scaffold** (resources + operations), **flows**, **contracts**, and bindings to LangGraph / Agent Server. It does not prescribe a single web framework.

Docs: [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) · [HITL via Server API](https://docs.langchain.com/langsmith/add-human-in-the-loop) · [Agent Server API](https://docs.langchain.com/langsmith/server-api-ref)

## 2. Purpose

Close the gap between LangGraph primitives (`interrupt`, `Command(resume)`, `get_state`) and what platform teams must expose so any UI can pause and resume safely without owning STM or inventing a second interrupt store.

## 3. Scope

**In scope:** language-agnostic API resources, operations, request/response contracts, interrupt→resume sequence, authz at the edge, status projection, Agent Server binding table.

**Out of scope:** concrete OpenAPI for one cloud, UI wireframes, IaC, non-HITL CRUD for skills (see doc 06).

## 4. Architecture Overview

### Resource model (scaffold)

| Resource | Meaning | Durability |
|----------|---------|------------|
| **Thread** | Durable conversation / job cursor (`thread_id`) | Checkpointer-backed |
| **Run** | One invocation that mutates a thread (start **or** resume) | Ephemeral execution; result written to checkpoints |
| **Assistant / Graph** | Configured graph to execute (`graph_id` / assistant_id) | Deployed artifact |
| **Interrupt** | Open pause surfaced from `interrupt(value)` | Part of `StateSnapshot` tasks/interrupts |
| **Approval** | Platform audit record that authorizes a resume (optional gate) | Platform store (append-only) |
| **RuntimeState** | Client DTO projected from `get_state` | Not a second SoR |

See diagrams: [../assets/diagrams/16-api-resource-model.mmd](../assets/diagrams/16-api-resource-model.mmd) · [../assets/diagrams/16-api-interrupt-resume-flow.mmd](../assets/diagrams/16-api-interrupt-resume-flow.mmd)

### Operation catalog (implement these)

Paths below are **canonical scaffold names**. Bind to Agent Server paths *or* your Gateway equivalents; keep operation semantics identical.

| Operation | Method + path (scaffold) | Body | Success result |
|-----------|--------------------------|------|----------------|
| **CreateThread** | `POST /v1/threads` | [thread-create.json](contracts/thread-create.json) | `{ thread_id, ... }` |
| **GetThread** | `GET /v1/threads/{thread_id}` | — | Thread metadata |
| **GetThreadState** | `GET /v1/threads/{thread_id}/state` | — | [runtime-state.json](contracts/runtime-state.json) (+ messages projection) |
| **StartRun** | `POST /v1/threads/{thread_id}/runs` | [run-create.json](contracts/run-create.json) with `input` | [run-result.json](contracts/run-result.json) |
| **ResumeRun** | `POST /v1/threads/{thread_id}/runs` | [resume-request.json](contracts/resume-request.json) → maps to `command.resume` | [run-result.json](contracts/run-result.json) |
| **StreamRun** | `POST /v1/threads/{thread_id}/runs/stream` | Same as Start/Resume | SSE/WS events until complete or interrupt |
| **ApproveAndResume** | `POST /v1/threads/{thread_id}/approvals` | [approval.json](contracts/approval.json) + resume mapping | Approval + RunResult |
| **ListInterrupts** | (derived) via GetThreadState | — | Open `interrupt` / `interrupts[]` on RuntimeState |

**Rule:** Start and Resume are both “create a Run on a Thread.” The discriminator is `input` vs `command.resume` — never reuse initial `input` to continue after an interrupt.

### Agent Server binding (reference, not required)

| Scaffold operation | Agent Server |
|--------------------|--------------|
| CreateThread | `POST /threads` |
| StartRun (wait) | `POST /threads/{thread_id}/runs/wait` + `input` |
| ResumeRun (wait) | `POST /threads/{thread_id}/runs/wait` + `command.resume` |
| StartRun (async) | `POST /threads/{thread_id}/runs` |
| StreamRun | `POST /threads/{thread_id}/runs/stream` |
| GetThreadState | `GET /threads/{thread_id}/state` |
| UpdateState (fork/edit) | `POST /threads/{thread_id}/state` — **not** normal chat continue |

Self-hosted binding: Gateway handlers call `graph.ainvoke` / `stream_events` with the same semantics.

## 5. Core Concepts

- **Frontend-agnostic:** any client may call Resume; only JWT identity + authz matter.
- **Thread is the cursor:** same `thread_id` restores messages, channels, and completed nodes from the checkpointer.
- **Interrupt payload:** JSON-serializable value from `interrupt()`; projected as [interrupt-payload.json](contracts/interrupt-payload.json).
- **Resume value:** becomes the return value of `interrupt()` inside the node.
- **Node re-entry:** on resume, the interrupted **node restarts from the beginning**; code before `interrupt()` must be idempotent; irreversible effects only **after** resume returns.
- **Context Package:** rebuilt inside graph nodes on each run step from Store + skills + snapshot — clients do not POST a full Context Package to resume.
- **Multitask strategy:** if a second Run arrives while one is active on a thread — `reject` | `enqueue` | `interrupt` | `rollback` (document environment default; prefer `enqueue` or `reject` in enterprise).

## 6. Design Decisions

| ID | Decision |
|----|----------|
| A1 | Expose Thread + Run resources; do not expose “session blob replace” as the continue API |
| A2 | Resume uses `command.resume` only; re-passing initial `input` is forbidden for HITL continue |
| A3 | RuntimeState / RunResult are projections of LangGraph state + `__interrupt__` |
| A4 | Approval is optional platform gate wrapping Resume — not a replacement for checkpointer interrupts |
| A5 | Do not set `checkpoint_id` on normal Resume (avoids accidental time travel) |
| A6 | Parallel interrupts resume with a map `{ interrupt_id: value }` |
| A7 | Streaming clients use `on_disconnect: continue` by default so leaves don’t cancel long HITL waits |
| A8 | Version platform API (`/v1`) separately from skill package versions |

## 7. Decision Rationale

Separating Thread (durable) from Run (invocation) matches LangGraph and Agent Server, keeps FE disposable, and prevents “chat history in the browser” from becoming SoR. Forbidding input-replay-as-resume stops the most common production bug.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Single `POST /chat` that always sends full message history | Duplicates STM; breaks interrupt semantics |
| FE stores checkpoint and posts it back | Security and consistency risk |
| Custom `awaiting_approval` DB as SoR | Diverges from `StateSnapshot` interrupts |
| Static `interrupt_before` for prod HITL | Wrong tool; use dynamic `interrupt()` |

## 9. Tradeoffs

Richer API surface vs one chat endpoint: more ops to implement; gain is correct resume, multi-client HITL, and clear authz. Waiting runs (`/runs/wait`) simplify sync UIs but need timeouts/webhooks for long approvals — prefer async run + GetThreadState or webhook for human-scale waits.

## 10. Component Breakdown

### Gateway / API layer

- **Purpose:** Authenticate, authorize, validate contracts, map HTTP ↔ LangGraph.
- **Responsibilities:** JWT validation; thread ACL; Start/Resume discrimination; project RuntimeState/RunResult; optional Approval write-before-resume.
- **Non-responsibilities:** Reimplementing checkpointer; assembling Context Package (graph nodes).
- **Inputs:** HTTP/SSE/MCP with bearer token.
- **Outputs:** Thread, RunResult, RuntimeState, Events.
- **Failure Modes:** stale interrupt, concurrent resume, unauthorized role.
- **Recovery:** Fail closed; leave graph interrupted; return conflict/410 for consumed interrupts.
- **Security:** Never trust client `user_id` over token; enforce `required_roles` from interrupt payload.
- **Scalability:** Stateless API replicas; sticky optional; durability in Postgres checkpointer.

### Orchestrator binding

- StartRun → `ainvoke(input, config={thread_id})` or Agent Server wait/stream.
- ResumeRun → `ainvoke(Command(resume=...), same config)`.
- GetThreadState → `get_state(config)` → RuntimeState DTO.

## 11. Sequence of Operations

### 11.1 Happy path — start until interrupt, then resume (any frontend)

```
1. Client: CreateThread
2. Client: StartRun(input)  [or StreamRun]
3. Graph runs; checkpointer saves steps; Context Assembler runs in nodes
4. Node calls interrupt(payload) → checkpointer persists; run returns awaiting
5. API returns RunResult { status: awaiting_input|awaiting_approval, interrupts: [...] }
6. (Optional) Notify approver via Event / webhook
7. Same or different client: GetThreadState → messages + interrupt summary (DTO)
8. Client: ResumeRun(command.resume) OR ApproveAndResume(decision → resume value)
9. Orchestrator: Command(resume=value), same thread_id
10. Node re-enters; interrupt() returns value; work after interrupt proceeds
11. RunResult status succeeded | awaiting_* | failed
```

Algorithm detail: [../programs/api-run-lifecycle.md](../programs/api-run-lifecycle.md) · [../programs/interrupt.md](../programs/interrupt.md) · [../programs/resume.md](../programs/resume.md) · [../programs/human-approval.md](../programs/human-approval.md)

### 11.2 What is preserved across the pause (no FE required)

| Data | Preserved by | Client must send on resume? |
|------|--------------|----------------------------|
| Messages / STM channels | Checkpointer | No |
| Completed nodes’ results | Checkpointer | No |
| Open interrupt id + payload | Snapshot interrupts | No (API re-reads); client sends **decision/resume value** only |
| Semantic facts | Store | No |
| Skill pins on thread | Thread metadata / state | Only if changing pins (rare) |
| Context Package | Rebuilt in nodes | No |

### 11.3 Multi-interrupt (parallel branches)

When `RunResult.interrupts.length > 1`, Resume with:

```json
{ "command": { "resume": { "<interrupt_id>": <value>, "...": "..." } } }
```

Index/order matching applies inside a single node with multiple `interrupt()` calls — prefer one HITL interrupt per node when possible.

### 11.4 Reject / revise

| Decision | Resume value pattern | Graph expectation |
|----------|----------------------|-------------------|
| approve | `true` / `{ "decision": "approve" }` | Continue past gate; side effects allowed after return |
| revise | `{ "decision": "revise", "comments": "..." }` | Node replans / loops |
| reject | `{ "decision": "reject" }` | Branch to cancelled / safe exit |

Record [approval.json](contracts/approval.json) **before** calling LangGraph resume when governance requires audit.

## 12. State Changes

| API event | LangGraph effect | Client-visible status |
|-----------|------------------|------------------------|
| StartRun | New checkpoints; may hit interrupt | `running` → `awaiting_*` or `succeeded` |
| Interrupt fired | Snapshot has interrupt; thread idle | `awaiting_approval` or `awaiting_input` |
| ResumeRun | Node re-entry; interrupt consumed | `running` → terminal or next await |
| GetThreadState | Read-only | Projection only |
| Concurrent Resume | One winner | `409` conflict for loser |

Status is **derived** from snapshot (`next`, interrupts, errors)—not written to a separate FSM table that can disagree with LangGraph.

## 13. Mermaid Diagrams

- [../assets/diagrams/16-api-resource-model.mmd](../assets/diagrams/16-api-resource-model.mmd)
- [../assets/diagrams/16-api-interrupt-resume-flow.mmd](../assets/diagrams/16-api-interrupt-resume-flow.mmd)
- Related: [../assets/diagrams/09-interrupt-resume.mmd](../assets/diagrams/09-interrupt-resume.mmd)

## 14. JSON Contracts

| Contract | Role |
|----------|------|
| [thread-create.json](contracts/thread-create.json) | CreateThread body |
| [run-create.json](contracts/run-create.json) | StartRun body (`input`, durability, stream options) |
| [resume-request.json](contracts/resume-request.json) | ResumeRun body (`command.resume`) |
| [run-result.json](contracts/run-result.json) | Unified Start/Resume response |
| [interrupt-payload.json](contracts/interrupt-payload.json) | Interrupt DTO |
| [runtime-state.json](contracts/runtime-state.json) | GetThreadState projection |
| [approval.json](contracts/approval.json) | Governance record before resume |
| [event.json](contracts/event.json) | `thread.interrupted`, `thread.resumed`, etc. |

### Example — Start until interrupt (Agent Server-shaped)

```http
POST /v1/threads/{thread_id}/runs
Content-Type: application/json
Authorization: Bearer <jwt>

{
  "graph_id": "agent",
  "input": { "messages": [{ "role": "user", "content": "Book the flight" }] },
  "durability": "async"
}
```

```json
{
  "thread_id": "t-123",
  "run_id": "r-456",
  "status": "awaiting_approval",
  "interrupts": [
    {
      "interrupt_id": "45fda847...",
      "type": "approval",
      "summary": "Confirm $840 purchase",
      "required_roles": ["approver"],
      "raw": { "action": "purchase", "amount": 840 }
    }
  ],
  "runtime_state_ref": "t-123"
}
```

### Example — Resume from any frontend

```http
POST /v1/threads/{thread_id}/runs
Content-Type: application/json
Authorization: Bearer <jwt>

{
  "graph_id": "agent",
  "command": {
    "resume": { "decision": "approve" }
  }
}
```

**Wrong (anti-pattern):**

```json
{ "input": { "messages": [ ... entire history ... ] } }
```

## 15. Best Practices

- Document one **resume value schema** per interrupt `type` (approval vs free-text input).
- Return human-readable `summary` in every interrupt payload for non-technical UIs.
- Use webhooks or notification Events for human-scale waits; don’t hold HTTP for hours.
- Pin `graph_id` / assistant version on the thread for regulated resume.
- Chaos-test: kill API mid-run; confirm GetThreadState still shows interrupt; Resume still works.
- For streaming UIs: loop Start/Resume until `interrupted == false` (see LangGraph event streaming).

## 16. Anti-patterns

- Re-posting initial graph `input` to “continue” after interrupt.
- Storing FE-only copy of messages as SoR.
- Clearing interrupts in a side table without LangGraph resume.
- Passing `checkpoint_id` on every Resume.
- Allowing Resume without checking `required_roles`.
- Putting irreversible tool calls before `interrupt()` without idempotency.

## 17. Common Mistakes

- Treating Agent Server path names as mandatory while changing resume semantics.
- Confusing static breakpoints (`interrupt_before`) with production HITL.
- Assuming Context Package is POSTed by the client on resume.
- Multiple API writers calling checkpointer bypassing the compiled graph.

## 18. Future Evolution

- Joinable resumable streams (`stream_resumable`) across FE reconnects.
- A2A / MCP tool exposure of the same Thread/Run operations.
- Signed interrupt payloads for cross-trust-boundary approvers.

## 19. Related Documents

[09-checkpoints-interrupt-resume.md](09-checkpoints-interrupt-resume.md) · [11-human-approval-governance.md](11-human-approval-governance.md) · [02-runtime-state-model.md](02-runtime-state-model.md) · [14-security.md](14-security.md) · [langgraph-bindings.md](langgraph-bindings.md) · [00-index.md](00-index.md) · [../SKILL.md](../SKILL.md)
