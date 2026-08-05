# Stream modes reference

Pass one mode (string) or several (list) to `stream` / `astream`. With `version="v2"`, each yield is a `StreamPart`; `chunk["type"]` matches the mode name.

Upstream: https://docs.langchain.com/oss/python/langgraph/streaming#stream-modes

| Mode | Type | Description |
|------|------|-------------|
| `values` | `ValuesStreamPart` | Full state after each step |
| `updates` | `UpdatesStreamPart` | State updates after each step; multiple updates in one step stream separately |
| `messages` | `MessagesStreamPart` | `(LLM token, metadata)` from LLM calls |
| `custom` | `CustomStreamPart` | Data from `get_stream_writer()` |
| `checkpoints` | `CheckpointStreamPart` | Checkpoint events (same shape as `get_state()`); requires checkpointer |
| `tasks` | `TasksStreamPart` | Task start/finish with results/errors; requires checkpointer |
| `debug` | `DebugStreamPart` | Combines checkpoints + tasks + extra metadata |

Import TypedDicts from `langgraph.types` (`StreamPart` is a disjoint union on `part["type"]`).

## values vs updates

```python
# updates — only what each node returned
for chunk in graph.stream(inputs, stream_mode="updates", version="v2"):
    if chunk["type"] == "updates":
        for node_name, state in chunk["data"].items():
            print(f"Node `{node_name}` updated: {state}")

# values — full state snapshot after each step
for chunk in graph.stream(inputs, stream_mode="values", version="v2"):
    if chunk["type"] == "values":
        print(chunk["data"])
```

## messages

`chunk["data"]` is `(message_chunk, metadata)`. Filter with `metadata["tags"]` or `metadata["langgraph_node"]`. See [../programs/stream-llm-tokens.md](../programs/stream-llm-tokens.md).

## custom

Requires `get_stream_writer()` (or injected `StreamWriter`) inside the graph. See [../programs/emit-custom.md](../programs/emit-custom.md).

## checkpoints / tasks / debug

```python
from langgraph.checkpoint.memory import MemorySaver

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "1"}}

for chunk in graph.stream(inputs, config=config, stream_mode="checkpoints", version="v2"):
    if chunk["type"] == "checkpoints":
        print(chunk["data"])

for chunk in graph.stream(inputs, config=config, stream_mode="tasks", version="v2"):
    if chunk["type"] == "tasks":
        print(chunk["data"])

for chunk in graph.stream(inputs, stream_mode="debug", version="v2"):
    if chunk["type"] == "debug":
        print(chunk["data"])
```

Prefer `checkpoints` or `tasks` alone when you do not need full debug verbosity.

## Multiple modes

```python
for chunk in graph.stream(inputs, stream_mode=["updates", "custom"], version="v2"):
    if chunk["type"] == "updates":
        ...
    elif chunk["type"] == "custom":
        ...
```

Under v1 (default without `version="v2"`), multi-mode yields `(mode, data)` tuples — avoid; migrate to v2.
