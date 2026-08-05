# StreamPart v2 format

Requires LangGraph ≥ 1.1. Always pass `version="v2"` in this skill's recipes.

Upstream: https://docs.langchain.com/oss/python/langgraph/streaming#stream-output-format-v2

## Shape

Every streamed chunk:

```python
{
    "type": "values" | "updates" | "messages" | "custom" | "checkpoints" | "tasks" | "debug",
    "ns": (),           # namespace; populated for subgraph events when subgraphs=True
    "data": ...,        # payload varies by type
}
```

Types: `ValuesStreamPart`, `UpdatesStreamPart`, `MessagesStreamPart`, `CustomStreamPart`, `CheckpointStreamPart`, `TasksStreamPart`, `DebugStreamPart`, union `StreamPart` — from `langgraph.types`. Narrow by `part["type"]`.

## v1 vs v2

| Scenario | v1 (default) | v2 (`version="v2"`) |
|----------|--------------|---------------------|
| Single mode | Raw data | `StreamPart` |
| Multiple modes | `(mode, data)` | Same `StreamPart`, filter `type` |
| Subgraphs | `(namespace, data)` | Same `StreamPart`, check `ns` |
| Modes + subgraphs | `(namespace, mode, data)` | Same `StreamPart` |
| `invoke()` return | Plain dict | `GraphOutput` with `.value` / `.interrupts` |
| Interrupt in stream | `__interrupt__` in state | `interrupts` on `values` parts |
| Interrupt in invoke | `__interrupt__` key | `.interrupts` on `GraphOutput` |
| Pydantic/dataclass state | Plain dict in values | Coerced to model/dataclass instance |

## Consume with narrowing

```python
for part in graph.stream(
    inputs,
    stream_mode=["values", "updates", "messages", "custom"],
    version="v2",
):
    if part["type"] == "values":
        print(part["data"])
    elif part["type"] == "updates":
        for node_name, state in part["data"].items():
            print(node_name, state)
    elif part["type"] == "messages":
        msg, metadata = part["data"]
        print(msg.content, end="", flush=True)
    elif part["type"] == "custom":
        print(part["data"])
```

## GraphOutput (invoke)

```python
from langgraph.types import GraphOutput

result = graph.invoke(inputs, version="v2")
assert isinstance(result, GraphOutput)
result.value       # state / model instance
result.interrupts  # tuple[Interrupt, ...]; empty if none
```

Dict-style access on `GraphOutput` is deprecated. Prefer `.value` / `.interrupts`.

```python
if result.interrupts:
    print(result.interrupts[0].value)
    graph.invoke(Command(resume=True), config=config, version="v2")
```

With a non-default `stream_mode` on `invoke(..., version="v2")`, the return is `list[StreamPart]` instead of mode-dependent tuples.
