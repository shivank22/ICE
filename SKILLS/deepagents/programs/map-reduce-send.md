# Program: map-reduce with Send

Build a LangGraph map-reduce fan-out with `Send`, optionally as a `CompiledSubAgent` under a deep agent.

Docs: https://docs.langchain.com/oss/python/langgraph/use-graph-api#map-reduce-and-the-send-api

## Inputs

- List of work items whose count is known only at runtime
- Worker node that accepts a **per-item** payload
- Reduce step that needs a **reducer** on collected results

## Decision first

```
Need runtime N× same worker with different inputs?
  ├─ Inside deep-agent ReAct only → parallel task / dynamic subagents
  └─ Explicit StateGraph map-reduce → Send (this program)
```

## Checklist

```
Task Progress:
- [ ] Step 1: Define OverallState + Annotated reducers for fan-in fields
- [ ] Step 2: Write map setup node (produces the list)
- [ ] Step 3: Write worker node (reads Send payload keys)
- [ ] Step 4: Conditional edge returns list[Send(worker, payload)]
- [ ] Step 5: Edge worker → reduce → END; compile
- [ ] Step 6: Optional — wrap as CompiledSubAgent for create_deep_agent
```

### Steps 1–5 (minimal)

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing_extensions import TypedDict, Annotated
import operator

class OverallState(TypedDict):
    subjects: list[str]
    jokes: Annotated[list[str], operator.add]

def generate_topics(state: OverallState):
    return {"subjects": ["lions", "elephants", "penguins"]}

def generate_joke(state: OverallState):
    return {"jokes": [f"joke about {state['subject']}"]}

def continue_to_jokes(state: OverallState):
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]

def best_joke(state: OverallState):
    return {}  # or pick from state["jokes"]

builder = (
    StateGraph(OverallState)
    .add_node("generate_topics", generate_topics)
    .add_node("generate_joke", generate_joke)
    .add_node("best_joke", best_joke)
    .add_edge(START, "generate_topics")
    .add_conditional_edges("generate_topics", continue_to_jokes, ["generate_joke"])
    .add_edge("generate_joke", "best_joke")
    .add_edge("best_joke", END)
)
graph = builder.compile()
```

### Step 6: Under a deep agent

```python
from deepagents import create_deep_agent
from deepagents.middleware.subagents import CompiledSubAgent

agent = create_deep_agent(
    model=...,
    subagents=[
        CompiledSubAgent(
            name="batch-worker",
            description="Runs map-reduce over a list of subjects",
            runnable=graph,
        )
    ],
)
```

## Prefer Path A when …

A single deep agent with soft todos/`task` is enough. Prefer an **explicit graph** when stages, validators, and human gates must be enforceable in routing code — [graph-engineering.md](graph-engineering.md).

## Hard rules

1. Fan-in keys need reducers (`operator.add`, `add_messages`, …)
2. List allowed destinations in `add_conditional_edges(..., ["worker_node"])`
3. Uneven branches before join → consider `defer=True` on the join node
4. Prefer Path A `task` / dynamic subagents unless you need a custom graph topology

## See also

- [../references/send-api.md](../references/send-api.md)
- [../examples/map_reduce_send.py](../examples/map_reduce_send.py)
- [plan-and-decompose.md](plan-and-decompose.md)
- [dynamic-subagents.md](dynamic-subagents.md)
- [graph-engineering.md](graph-engineering.md)
