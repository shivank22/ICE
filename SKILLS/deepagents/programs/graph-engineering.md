# Program: graph engineering

Decide when a Deep Agent loop is enough vs an explicit LangGraph workflow, then design nodes / edges / state / gates.

Docs / essay: https://www.analyticsvidhya.com/blog/2026/07/graph-engineering/  
Graph API: https://docs.langchain.com/oss/python/langgraph/use-graph-api

## Inputs

- Task stages, dependencies, validation rules, human touchpoints
- Which steps must be deterministic vs LLM
- Risk of side effects (send, pay, publish)

## Decision

```
Open-ended assistant / soft plan+task?
  → Path A create_deep_agent (this skill's default)

Fixed stages + hard gates (score, policy, HITL, revision cap)?
  → Explicit StateGraph (graph engineering)
  → Optional: deep agent / create_agent as a node; Send for map-reduce workers
```

## Checklist

```
Task Progress:
- [ ] Step 1: List work units, dependencies, failure paths, human gates
- [ ] Step 2: Classify nodes (deterministic vs agent vs interrupt)
- [ ] Step 3: Define typed state + reducers for any parallel fields
- [ ] Step 4: Put hard constraints in route functions (not only prompts)
- [ ] Step 5: Cap loops; wire HITL with checkpointer + same thread_id
- [ ] Step 6: Isolate context per node; add observability hooks
- [ ] Step 7: Choose: standalone graph vs CompiledSubAgent under deep agent
```

### Step 1–2: Topology before agents

Do not start with “how many agents?” Start with stages and control boundaries. Agents fill nodes; engineering lives in **edges**.

### Step 3–4: State and routes

```python
class ResearchState(TypedDict, total=False):
    topic: str
    plan: str
    evidence: str
    draft: str
    feedback: str
    evaluator_approved: bool
    human_approved: bool
    revision_count: int

def route_after_evaluation(state) -> Literal["revise", "human_review"]:
    if state.get("evaluator_approved") or state.get("revision_count", 0) >= 2:
        return "human_review"
    return "revise"
```

### Step 5: HITL node

```python
from langgraph.types import interrupt, Command

def human_review_node(state):
    decision = interrupt({"message": "...", "draft": state["draft"], ...})
    return {"human_approved": decision.get("action") == "approve", ...}

# resume: graph.invoke(Command(resume={...}), config=same_thread)
```

Tool-level HITL inside a deep-agent node: [human-in-the-loop.md](human-in-the-loop.md).

### Step 7: Nesting

| Placement | Use |
|-----------|-----|
| Standalone `StateGraph` | Product workflow is the graph |
| Node = `create_deep_agent` / `create_agent` | Open-ended work inside a stage |
| `CompiledSubAgent` | Map-reduce or custom graph callable via parent `task` — [map-reduce-send.md](map-reduce-send.md) |

## Hard rules

1. Not every node is an LLM
2. Hard constraints in routing code
3. Cap evaluator–optimizer / retry loops
4. Risk-based HITL (not every step)
5. Durable checkpointer in production; idempotent pre-interrupt side effects
6. Prefer Path A when a single harness is enough — avoid graph for graph’s sake

## See also

- [../references/graph-engineering.md](../references/graph-engineering.md)
- [../examples/graph_engineering_research.py](../examples/graph_engineering_research.py)
- [map-reduce-send.md](map-reduce-send.md)
- [human-in-the-loop.md](human-in-the-loop.md)
- [context-engineering.md](context-engineering.md)
