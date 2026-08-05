# Program: Stream LLM tokens

Use `stream_mode="messages"` for token-by-token LLM output from nodes, tools, subgraphs, or tasks.

Upstream: https://docs.langchain.com/oss/python/langgraph/streaming#llm-tokens

## Preconditions

- LangChain chat model (or use [emit-custom.md](emit-custom.md) for non-LC clients)
- Consumer ready to handle `(message_chunk, metadata)` tuples in `chunk["data"]`

## Steps

1. **Stream with messages mode** (LLM need not call `.stream` — `.invoke` still emits message events):

```python
for chunk in graph.stream(
    {"topic": "ice cream"},
    stream_mode="messages",
    version="v2",
):
    if chunk["type"] == "messages":
        message_chunk, metadata = chunk["data"]
        if message_chunk.content:
            print(message_chunk.content, end="", flush=True)
```

2. **Filter by LLM invocation tags** when multiple models run:

```python
model_joke = init_chat_model(model="...", tags=["joke"])
model_poem = init_chat_model(model="...", tags=["poem"])

# in consumer:
if chunk["type"] == "messages":
    msg, metadata = chunk["data"]
    if metadata.get("tags") == ["joke"]:
        print(msg.content, end="", flush=True)
```

3. **Filter by node** via `metadata["langgraph_node"]`:

```python
if msg.content and metadata["langgraph_node"] == "write_poem":
    print(msg.content, end="", flush=True)
```

4. **Omit tokens with `nostream`** — model still runs; tokens are not emitted in `messages` mode:

```python
internal = ChatAnthropic(...).with_config({"tags": ["nostream"]})
```

Use when structured output is internal-only, or the same content is already pushed via `custom`.

5. **Nested agent as a node** — set `subgraphs=True` or parent `messages` streams miss inner tokens. See [stream-subgraphs.md](stream-subgraphs.md).

6. **Disable streaming on a model** that cannot stream: `streaming=False` or `disable_streaming=True` at init.

## Checklist

```
- [ ] stream_mode includes "messages"
- [ ] version="v2"; unpack chunk["data"] as (msg, metadata)
- [ ] Filter tags / langgraph_node if multiple LLMs or nodes
- [ ] nostream on internal models
- [ ] subgraphs=True for nested create_agent / create_deep_agent
- [ ] Python < 3.11 async: pass config into ainvoke (see async-python.md)
```

## Related

- Consume loop: [stream-graph.md](stream-graph.md)
- Example: [../examples/messages_tokens.py](../examples/messages_tokens.py)
