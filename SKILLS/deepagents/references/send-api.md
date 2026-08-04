# Map-reduce and the Send API

LangGraph control primitive for **runtime fan-out**: invoke the **same node N times** with **different payloads**, then fan in with a reducer.

Docs: https://docs.langchain.com/oss/python/langgraph/use-graph-api#map-reduce-and-the-send-api

## When this belongs in a Deep Agents session

| Need | Prefer |
|------|--------|
| Ship Path A deep agent | `task` / parallel tool calls / [dynamic subagents](dynamic-subagents.md) |
| Custom graph shape (orchestrator → N workers → reduce) | **`Send`** inside `StateGraph` |
| That graph as a child of a deep agent | Wrap as `CompiledSubAgent` |

`create_deep_agent` / `create_agent` do **not** expose `Send` on the ReAct harness. Use Send when you leave the agent loop for an explicit map-reduce graph.

## `Send` shape

```python
from langgraph.types import Send

Send(node_name: str, arg: dict)  # arg = state (or partial) for that worker invoke
```

Return a **list of `Send`** from a conditional-edge function:

```python
def continue_to_jokes(state: OverallState):
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]
```

Wire:

```python
builder.add_conditional_edges("generate_topics", continue_to_jokes, ["generate_joke"])
```

The third argument lists **allowed destinations** so the graph can validate Send targets.

## Map-reduce pattern

```text
map_setup → [Send × N] → worker (parallel, same node) → reduce → END
```

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing_extensions import TypedDict, Annotated
import operator

class OverallState(TypedDict):
    topic: str
    subjects: list[str]
    jokes: Annotated[list[str], operator.add]  # reducer for fan-in
    best_selected_joke: str

def generate_topics(state: OverallState):
    return {"subjects": ["lions", "elephants", "penguins"]}

def generate_joke(state: OverallState):
    # Worker sees Send payload (e.g. subject), returns OverallState updates
    joke_map = {...}
    return {"jokes": [joke_map[state["subject"]]]}

def continue_to_jokes(state: OverallState):
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]

def best_joke(state: OverallState):
    return {"best_selected_joke": "penguins"}

builder = StateGraph(OverallState)
builder.add_node("generate_topics", generate_topics)
builder.add_node("generate_joke", generate_joke)
builder.add_node("best_joke", best_joke)
builder.add_edge(START, "generate_topics")
builder.add_conditional_edges("generate_topics", continue_to_jokes, ["generate_joke"])
builder.add_edge("generate_joke", "best_joke")
builder.add_edge("best_joke", END)
graph = builder.compile()
```

All `generate_joke` Sends run in **one superstep** (parallel); then `best_joke` runs once after they complete.

## Send vs other branching

| Mechanism | Fan-out size | Worker input |
|-----------|--------------|--------------|
| Fixed edges / conditional → `["b","c"]` | Fixed at design time | Shared graph state |
| **`Send`** | **Runtime** (from state) | **Per-Send payload** |
| Deep Agents parallel `task` tools | Model chooses N tool calls | Each `description` string |
| Dynamic subagents `task()` in JS | Code loops / `Promise.all` | Interpreter orchestration |

### Reducers are mandatory for fan-in

Without `Annotated[..., operator.add]` (or similar), parallel workers overwrite the same key. Messages: prefer `add_messages`.

### Uneven branch lengths

If some paths have extra nodes before the join, use **deferred** nodes (`defer=True` on `add_node`) so the join waits for all pending work — common beside map-reduce (see same Graph API guide: deferring node execution).

## As a Deep Agents subagent

```python
from deepagents.middleware.subagents import CompiledSubAgent

map_reduce_graph = builder.compile()  # StateGraph with Send

create_deep_agent(
    ...,
    subagents=[
        CompiledSubAgent(
            name="joke-batch",
            description="Map-reduce joke generator over subjects",
            runnable=map_reduce_graph,
        )
    ],
)
```

Parent still delegates via `task`; the child graph owns the Send fan-out. `CompiledSubAgent` does **not** inherit parent `interrupt_on` — configure HITL inside the child if needed.

## Hard rules

1. Conditional edge must **return `list[Send]`**, not only node-name strings, for dynamic map
2. Each Send carries the worker’s input — do not assume full `OverallState` is copied unless you put it in the payload
3. Fan-in fields need reducers
4. Do not reach for Send inside Path A middleware stacks — use `task` / dynamic subagents unless building a custom graph

## See also

- [../programs/map-reduce-send.md](../programs/map-reduce-send.md)
- [../examples/map_reduce_send.py](../examples/map_reduce_send.py)
- [graph-engineering.md](graph-engineering.md) — when an explicit graph beats a single agent loop
- [planning-and-decomposition.md](planning-and-decomposition.md)
- [dynamic-subagents.md](dynamic-subagents.md)
- https://docs.langchain.com/oss/python/langgraph/use-graph-api#map-reduce-and-the-send-api
- https://docs.langchain.com/oss/python/langgraph/graph-api
