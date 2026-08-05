# Program: Stream subgraphs and nested agents

Include subgraph (and nested agent) events in the parent stream with `subgraphs=True`.

Upstream: https://docs.langchain.com/oss/python/langgraph/streaming#subgraph-outputs

## Preconditions

- Parent graph that invokes a compiled subgraph or agent as a node
- Consumer that can interpret `chunk["ns"]`

## Why it matters for agents

`create_agent` / `create_deep_agent` return a **compiled graph**. Adding one as a node makes it a subgraph. Without `subgraphs=True`, parent `stream_mode="messages"` does **not** emit tokens from the inner agent's LLM calls. Calling `agent.stream(...)` directly still works — the gap appears only after wrapping.

## Steps

1. **Enable subgraph streaming**:

```python
for chunk in graph.stream(
    inputs,
    stream_mode="updates",  # or "messages", etc.
    subgraphs=True,
    version="v2",
):
    print(chunk["type"])  # e.g. "updates"
    print(chunk["ns"])    # () root; ("node_name:<task_id>",) subgraph
    print(chunk["data"])
```

2. **Branch on namespace**:

```python
if chunk["type"] == "updates":
    if chunk["ns"]:
        print(f"Subgraph {chunk['ns']}: {chunk['data']}")
    else:
        print(f"Root: {chunk['data']}")
```

3. **Nested agent tokens**:

```python
from langchain.agents import create_agent
from langgraph.graph import END, START, StateGraph

graph = (
    StateGraph(State)
    .add_node("agent", create_agent(model, tools, state_schema=State))
    .add_edge(START, "agent")
    .add_edge("agent", END)
    .compile()
)

for chunk in graph.stream(
    {"messages": [{"role": "user", "content": "..."}]},
    stream_mode="messages",
    subgraphs=True,
    version="v2",
):
    if chunk["type"] == "messages":
        msg, metadata = chunk["data"]
        if msg.content:
            print(msg.content, end="", flush=True)
```

## Checklist

```
- [ ] subgraphs=True on parent stream/astream
- [ ] version="v2" — use ns, not v1 (namespace, data) tuples
- [ ] Nested create_agent / create_deep_agent → expect non-empty ns for inner events
```

## Related

- Tokens: [stream-llm-tokens.md](stream-llm-tokens.md)
- Example: [../examples/subgraph_agent_messages.py](../examples/subgraph_agent_messages.py)
- Deep Agents: [`../../deepagents/`](../../deepagents/)
