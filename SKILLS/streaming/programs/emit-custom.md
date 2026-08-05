# Program: Emit custom stream data

Send user-defined events from nodes or tools with `get_stream_writer()`, consumed via `stream_mode="custom"`.

Upstream: https://docs.langchain.com/oss/python/langgraph/streaming#custom-data

## Preconditions

- At least one of the requested modes is `"custom"` (alone or in a list)
- Python ≥ 3.11 for `get_stream_writer()` in async; otherwise inject `writer` ([../references/async-python.md](../references/async-python.md))

## Steps

1. **In a node**, get the writer and emit dicts (or any serializable payload):

```python
from langgraph.config import get_stream_writer

def node(state):
    writer = get_stream_writer()
    writer({"status": "thinking of a joke..."})
    return {"joke": "..."}
```

2. **In a tool**, same pattern:

```python
from langchain.tools import tool
from langgraph.config import get_stream_writer

@tool
def query_database(query: str) -> str:
    """Query the database."""
    writer = get_stream_writer()
    writer({"data": "Retrieved 0/100 records", "type": "progress"})
    # ... work ...
    writer({"data": "Retrieved 100/100 records", "type": "progress"})
    return "some-answer"
```

3. **Consume** with `custom` (optionally combined with other modes):

```python
for chunk in graph.stream(inputs, stream_mode=["updates", "custom"], version="v2"):
    if chunk["type"] == "custom":
        print(chunk["data"])
```

4. **Arbitrary / non-LangChain LLMs** — stream client chunks through the writer:

```python
def call_arbitrary_model(state):
    writer = get_stream_writer()
    for piece in your_custom_streaming_client(state["topic"]):
        writer({"custom_llm_chunk": piece})
    return {"result": "completed"}
```

## Checklist

```
- [ ] stream_mode includes "custom"
- [ ] version="v2"
- [ ] Writer used inside node/tool (not outside graph execution)
- [ ] Python < 3.11 async: writer: StreamWriter param instead of get_stream_writer()
```

## Related

- Consume loop: [stream-graph.md](stream-graph.md)
- Example: [../examples/custom_writer.py](../examples/custom_writer.py)
