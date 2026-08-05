---
name: streaming
description: >-
  Stream LangGraph graphs and agents with stream()/astream(), stream_mode
  (values, updates, messages, custom, checkpoints, tasks, debug), StreamPart
  v2 format, get_stream_writer custom events, subgraph token streaming, and
  nostream filtering. Use when implementing or debugging LangGraph streaming,
  LLM token streams, progress events, or nested-agent stream visibility.
---

# LangGraph Streaming

Teach agents how to **stream LangGraph graph execution** via the stream-mode API: `stream` / `astream`, one or more `stream_mode`s, and the unified `StreamPart` shape (`version="v2"`).

For greenfield apps, upstream also offers [event streaming](https://docs.langchain.com/oss/python/langgraph/event-streaming) (typed projections, LangGraph ≥ 1.2). This skill focuses on the stream-mode API.

Defer ICE Thread/Run SSE/WS mapping to [`../backend/`](../backend/). Defer Deep Agent / `create_agent` construction to [`../deepagents/`](../deepagents/).

## Mental model

```text
Compiled graph
  → stream / astream(inputs, stream_mode=..., version="v2", subgraphs=?)
  → iterator of StreamPart { type, ns, data }
  → consumer branches on type (messages | updates | custom | ...)
```

Modes select **what** is emitted. `version="v2"` makes **every** chunk the same shape regardless of single/multi mode or subgraphs.

## When to apply

- Wire `graph.stream` / `graph.astream` for UIs or services
- Stream LLM tokens (`messages`), state deltas (`updates`/`values`), or progress (`custom`)
- Nested agents as nodes and tokens never appear (need `subgraphs=True`)
- Migrate v1 tuple/`__interrupt__` consumers to v2 `StreamPart` / `GraphOutput`

Do **not** use this skill for platform HTTP/SSE contract design (backend) or building the agent harness (deepagents).

## Mode cheat sheet

| Mode | Payload | Typical use |
|------|---------|-------------|
| `updates` | `{node: partial_state}` | Node deltas for UIs |
| `values` | Full state after each step | Snapshots / debugging |
| `messages` | `(token, metadata)` | Token-by-token LLM output |
| `custom` | Anything from `get_stream_writer()` | Progress, non-LC LLMs |
| `checkpoints` | Checkpoint like `get_state()` | Persistence introspection (needs checkpointer) |
| `tasks` | Task start/finish | Per-node lifecycle (needs checkpointer) |
| `debug` | checkpoints + tasks + extras | Max verbosity |

Details: [references/stream-modes.md](references/stream-modes.md).

## Hard rules (always)

1. **Pass `version="v2"`** — unified `StreamPart`; avoid v1 format branching.
2. **Branch on `chunk["type"]`** — never assume raw dicts or `(mode, data)` tuples under v2.
3. **Agent UIs default** to `stream_mode=["messages", "updates"]`; add `"custom"` when emitting progress.
4. **`subgraphs=True` for nested agents** — `create_agent` / `create_deep_agent` as a node is a subgraph; without this, parent `messages` streams miss inner tokens.
5. **Prefer `astream` in async services**; `stream` for sync scripts/CLIs.
6. **Tag internal models `nostream`** when tokens must not hit the client (structured output, duplicate channels).
7. **Python &lt; 3.11 async** — pass `config` into `ainvoke`; inject `writer: StreamWriter` instead of `get_stream_writer()` ([references/async-python.md](references/async-python.md)).
8. **`checkpoints` / `tasks` need a checkpointer** and usually a `thread_id` config.

## Progressive disclosure

Read only what the current request needs:

| Concern | Read |
|---------|------|
| Choose modes + consume StreamParts | [programs/stream-graph.md](programs/stream-graph.md) |
| LLM tokens, tags, nostream, node filter | [programs/stream-llm-tokens.md](programs/stream-llm-tokens.md) |
| Custom progress / arbitrary LLM APIs | [programs/emit-custom.md](programs/emit-custom.md) |
| Nested graphs / agents | [programs/stream-subgraphs.md](programs/stream-subgraphs.md) |
| Mode reference | [references/stream-modes.md](references/stream-modes.md) |
| StreamPart + v1→v2 + GraphOutput | [references/stream-part-v2.md](references/stream-part-v2.md) |
| Python &lt; 3.11 async pitfalls | [references/async-python.md](references/async-python.md) |
| Copyable scripts | [examples/](examples/) |

## Workflow for agent sessions

```
Streaming session:
- [ ] Sync stream vs async astream?
- [ ] Modes: messages / updates / custom / ... (list if multiple)
- [ ] version="v2" on every call
- [ ] Nested agent/subgraph? → subgraphs=True
- [ ] Internal LLM? → tags=["nostream"] if needed
- [ ] Consume via chunk["type"] / chunk["ns"] / chunk["data"]
- [ ] Python < 3.11? → config + StreamWriter injection
```

## Upstream

- [Streaming (stream-mode API)](https://docs.langchain.com/oss/python/langgraph/streaming)
- [Event streaming](https://docs.langchain.com/oss/python/langgraph/event-streaming)
- [Subgraphs](https://docs.langchain.com/oss/python/langgraph/use-subgraphs)
- [Persistence / checkpointers](https://docs.langchain.com/oss/python/langgraph/persistence)
