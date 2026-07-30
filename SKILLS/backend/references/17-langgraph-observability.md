# 17 — LangGraph Observability (Opinionated)

## 1. Executive Summary

Observability for LangGraph platforms is **contract-first, binding-second**. Emit structured traces at **graph level** (whole invoke/thread run) and **agent/component level** (nodes, tools, LLM calls, custom logic). Preferred bindings: **Langfuse** (ICE example) or **LangSmith**; both use LangChain callbacks / OpenTelemetry-style nesting. Traces feed [episodic memory](07-episodic-memory.md) and [evaluation](18-evaluation-frameworks.md)—they never replace the checkpointer or skill registry.

Official refs: [LangGraph Observability](https://docs.langchain.com/oss/python/langgraph/observability) · [Trace with LangGraph](https://docs.langchain.com/langsmith/trace-with-langgraph) · [Langfuse × LangGraph](https://langfuse.com/guides/cookbook/integration_langgraph)

## 2. Purpose

Give architects and coding agents a single opinionated checklist so every agent service emits correlatable, redacted, eval-ready traces at the right granularity.

## 3. Scope

Trace hierarchy, required attributes, emission points, sampling, PII, bindings (Langfuse / LangSmith), link to episodes. Eval scoring frameworks are in doc 18. Checkpoint durability remains doc 09.

## 4. Architecture Overview

### Two emission levels (required)

| Level | Unit | What it captures |
|-------|------|------------------|
| **Graph / run** | One `invoke` / `ainvoke` / stream session on a `thread_id` | Root span: input summary, final status, interrupt payloads, duration, cost rollup |
| **Agent / component** | Node, subgraph, tool, LLM, custom helper | Nested spans: state deltas (safe), tool args/results (redacted), model I/O (redacted), skill version |

```text
AgentService entry (optional @observe / @traceable root)
 └── Graph run span          ← GRAPH LEVEL
      ├── node:planner
      ├── node:skill_x       ← AGENT / NODE LEVEL
      │    ├── llm
      │    └── tool:jira
      ├── interrupt (event)
      └── node:finalize
```

See [../assets/diagrams/17-trace-hierarchy.mmd](../assets/diagrams/17-trace-hierarchy.mmd)

### Dual store reminder

Langfuse/LangSmith = **Trace Store**. Episode rows = curated episodic memory. See [07-episodic-memory.md](07-episodic-memory.md).

## 5. Core Concepts

- **Trace:** end-to-end timeline for one graph run (maps to Langfuse trace / LangSmith root run).
- **Span / run:** nested step (node, tool, LLM).
- **Correlation ids:** `thread_id`, `run_id`, `checkpoint_id`, `user_id`, `org_id`, `assembly_digest`, `skill_id@version`, `graph_id`.
- **Selective tracing:** `tracing_context` / env sampling — never “off in prod” as the only cost control.
- **Anonymizers:** mask PII/secrets before export.

## 6. Design Decisions (opinionated defaults)

| ID | Decision |
|----|----------|
| Obs1 | **Always** attach a callback handler (or equivalent) on graph invoke—not only in local debug |
| Obs2 | Emit **both** graph-level and node/tool/LLM spans; wrap custom Python in `@traceable` / `@observe` |
| Obs3 | Required metadata on every root trace (see §10 attribute vocabulary) |
| Obs4 | Prefer **Langfuse** when ICE Azure stack is chosen; **LangSmith** when LC-native eval UX is primary—document in Stack Binding |
| Obs5 | Sample high-volume happy paths; **100%** of failures, interrupts, and regulated threads |
| Obs6 | Redact before export; never log raw secrets, full Authorization headers, or unredacted Memory.md |
| Obs7 | On run terminal → curate Episode with `trace_id` link |
| Obs8 | Serverless: flush traces before process exit (`LANGCHAIN_CALLBACKS_BACKGROUND=false` or vendor equivalent) |
| Obs9 | Multi-agent: one root per user-facing turn; child agent graphs nest under it |
| Obs10 | Interrupt/resume: same `thread_id` / session id across pauses so Langfuse session groups HITL |

## 7. Decision Rationale

Graph-only traces hide tool/LLM failures. Node-only traces without a root break session/HITL correlation. Sampling-by-off loses incidents. Episode curation without `trace_id` breaks learning evidence.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Logs only | No nested agent timeline |
| Langfuse as checkpointer | Wrong durability semantics |
| Trace every token in prod at 100% forever | Cost explosion |
| Per-node new CallbackHandler instances | Broken nesting / orphan spans |

## 9. Tradeoffs

Full fidelity vs cost: use attribute-based keep rules (errors, interrupts, tagged `debug=true`) plus sampling rate for the rest.

## 10. Component Breakdown

### Attribute vocabulary (required on root; propagate to children)

| Attribute | Source |
|-----------|--------|
| `thread_id` | LangGraph configurable |
| `run_id` | Platform run id |
| `user_id` / `org_id` | JWT (never client-spoofed) |
| `graph_id` / `assistant_id` | Deployed graph |
| `skill_pins` | Manifest versions mounted for the run |
| `assembly_digest` | Context Package hash |
| `checkpoint_id` | When known (post-step) |
| `status` | running / awaiting_* / succeeded / failed |
| `interrupt_ids` | When paused |
| `env` | dev / staging / prod |

### Graph-level emission

**When:** every StartRun / ResumeRun / StreamRun.

**How (bindings):**

- **Langfuse:** `CallbackHandler` in `config={"callbacks": [...]}`; optionally `graph.with_config({"callbacks": [...]})` for Agent Server; wrap entry with `@observe` / `propagate_attributes(session_id=thread_id, user_id=..., tags=[...])`.
- **LangSmith:** env `LANGSMITH_TRACING=true` (+ API key, project); tags/metadata on config; `@traceable` on service entry.

**Capture:** input shape (redacted), output/interrupt summary, duration, token/cost rollup, error.

### Agent / component-level emission

| Component | Practice |
|-----------|----------|
| LangGraph nodes | Auto via callbacks when LLM/tools are LangChain runnables |
| Custom Python in nodes | `@traceable` (LangSmith) or `@observe` / manual span (Langfuse) |
| Tools | Ensure tool invokes go through instrumented clients; tag `tool_name` |
| Subgraphs | Enable nested tracing; preserve parent span |
| Context assembler | Span with `assembly_digest` + skill pin list (not full package dump) |
| Approval / resume | Event or span linking `approval_id` → `interrupt_id` |

### Trace Store service responsibilities

Ingest, retain, RBAC, redaction, export-to-episode. Non-responsibilities: promoting skills; owning STM.

## 11. Sequence of Operations

1. Gateway creates/continues `thread_id`; starts platform `run_id`.
2. Orchestrator opens **graph-level** trace with required attributes.
3. Graph executes; **agent-level** spans nest (nodes → LLM/tools).
4. On `interrupt()`: mark root status awaiting_*; record interrupt payload summary; keep session open.
5. On ResumeRun: continue same session/`thread_id`; new run span under same session.
6. On terminal: finalize root; compute cost; **curate Episode** (`trace_id`, outcome, skill_versions, scores placeholder).
7. Evaluation framework (doc 18) scores offline suite or online sample → write Evaluation → attach to Episode.
8. FinOps aggregates from traces independently.

Algorithm: [../programs/trace-emit.md](../programs/trace-emit.md)

## 12. State Changes

| Trace lifecycle | Episode link |
|-----------------|--------------|
| open (running) | episode optional / open |
| interrupted | episode open; status awaiting |
| finalized success/fail | episode complete + `trace_id` |
| retained / purged | episode may outlive raw spans per retention policy |

## 13. Mermaid Diagrams

- [../assets/diagrams/17-trace-hierarchy.mmd](../assets/diagrams/17-trace-hierarchy.mmd)
- [../assets/diagrams/17-trace-to-episode.mmd](../assets/diagrams/17-trace-to-episode.mmd)
- Related: [../assets/diagrams/13-observability.mmd](../assets/diagrams/13-observability.mmd)

## 14. JSON Contracts

- [contracts/trace.json](contracts/trace.json)
- [contracts/episodic-memory.json](contracts/episodic-memory.json)
- [contracts/event.json](contracts/event.json)

## 15. Best Practices (LangGraph-aligned checklist)

- [ ] Callbacks (or auto-trace env) on **every** production invoke
- [ ] Graph root + nested node/tool/LLM spans
- [ ] Custom logic wrapped for nesting
- [ ] Tags: `env`, `graph_id`, `hitl`, `skill:<id>`
- [ ] Metadata: correlation ids in §10
- [ ] PII anonymizers / allowlists on inputs/outputs
- [ ] Sampling rate for volume; keep errors & interrupts
- [ ] Separate Langfuse/LangSmith **projects** per environment
- [ ] Serverless flush before exit
- [ ] Episode curation on terminal with `trace_id`
- [ ] Health/readiness exposes “tracing configured” in non-prod
- [ ] Never use traces as the resume SoR

## 16. Anti-patterns

- Tracing disabled in production to “save money”
- New `CallbackHandler()` inside every node (orphan trees)
- Dumping full Context Package or secrets into span attributes
- Treating Langfuse prompt playground edits as production skill updates
- Missing `thread_id` so HITL resume cannot be found in the UI

## 17. Common Mistakes

- Assuming LangGraph “includes” eval—tracing ≠ scoring
- No link from cost to `thread_id`
- Over-sampling away all failures
- Different ids in gateway vs orchestrator vs trace metadata

## 18. Future Evolution

OpenTelemetry agent semantic conventions; mandating `assembly_digest` in online eval filters; cross-region trace residency.

## 19. Related Documents

[13-observability.md](13-observability.md) · [07-episodic-memory.md](07-episodic-memory.md) · [18-evaluation-frameworks.md](18-evaluation-frameworks.md) · [16-api-surface-interrupt-resume.md](16-api-surface-interrupt-resume.md) · [langgraph-bindings.md](langgraph-bindings.md)
