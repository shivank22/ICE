# Async streaming on Python &lt; 3.11

Before 3.11, asyncio tasks lack the `context` parameter, so LangGraph cannot always propagate context automatically.

Upstream: https://docs.langchain.com/oss/python/langgraph/streaming#async

## Impacts

1. **LLM streaming** — pass `RunnableConfig` explicitly into async model calls (`ainvoke`), or callbacks/streaming context may not propagate.
2. **Custom streaming** — `get_stream_writer()` does **not** work in async nodes/tools; inject `writer: StreamWriter` instead.

Prefer upgrading to Python ≥ 3.11 when possible.

## Pass config into async LLM calls

```python
async def call_model(state, config):
    topic = state["topic"]
    joke_response = await model.ainvoke(
        [{"role": "user", "content": f"Write a joke about {topic}"}],
        config,  # required for proper streaming on Python < 3.11
    )
    return {"joke": joke_response.content}

async for chunk in graph.astream(
    {"topic": "ice cream"},
    stream_mode="messages",
    version="v2",
):
    if chunk["type"] == "messages":
        message_chunk, metadata = chunk["data"]
        if message_chunk.content:
            print(message_chunk.content, end="", flush=True)
```

## Inject StreamWriter for custom data

```python
from langgraph.types import StreamWriter

async def generate_joke(state: State, writer: StreamWriter):
    writer({"custom_key": "Streaming custom data while generating a joke"})
    return {"joke": f"This is a joke about {state['topic']}"}

async for chunk in graph.astream(
    {"topic": "ice cream"},
    stream_mode="custom",
    version="v2",
):
    if chunk["type"] == "custom":
        print(chunk["data"])
```

LangGraph injects `writer` when it appears in the node/tool signature.
