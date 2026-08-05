# Program: Stream a graph

Choose modes, call `stream` / `astream` with `version="v2"`, consume `StreamPart`s.

Upstream: https://docs.langchain.com/oss/python/langgraph/streaming

## Preconditions

- Compiled `StateGraph` (or agent that returns one)
- Decision on sync vs async and which modes to emit

## Steps

1. **Pick modes** (see [../references/stream-modes.md](../references/stream-modes.md)):
   - Agent UI → `["messages", "updates"]`
   - Progress bars / tool status → add `"custom"`
   - Full snapshots → `"values"` instead of or with `"updates"`
   - Persistence debug → `"checkpoints"` / `"tasks"` (checkpointer required)

2. **Call the API**:

```python
for chunk in graph.stream(
    inputs,
    stream_mode=["messages", "updates"],  # list or single string
    version="v2",
    # subgraphs=True,  # if nested agents/subgraphs must appear
):
    ...
```

Async:

```python
async for chunk in graph.astream(
    inputs,
    stream_mode=["messages", "updates"],
    version="v2",
):
    ...
```

3. **Branch on `chunk["type"]`** — every chunk is `{type, ns, data}`:

```python
for chunk in graph.stream(inputs, stream_mode=["updates", "custom"], version="v2"):
    if chunk["type"] == "updates":
        for node_name, state in chunk["data"].items():
            print(f"Node {node_name} updated: {state}")
    elif chunk["type"] == "custom":
        print(f"Status: {chunk['data']}")
```

4. **Inspect `chunk["ns"]`** when `subgraphs=True` — `()` is root; non-empty tuples identify subgraph path. See [stream-subgraphs.md](stream-subgraphs.md).

## Checklist

```
- [ ] version="v2"
- [ ] stream_mode matches consumer needs
- [ ] Consumer switches on chunk["type"]
- [ ] subgraphs=True if nested agents need visibility
- [ ] astream in async services
```

## Related

- Tokens: [stream-llm-tokens.md](stream-llm-tokens.md)
- Custom emit: [emit-custom.md](emit-custom.md)
- Format details: [../references/stream-part-v2.md](../references/stream-part-v2.md)
- Example: [../examples/basic_updates.py](../examples/basic_updates.py)
