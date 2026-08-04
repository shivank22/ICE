# Graph engineering

Practice of designing agentic apps as **executable graphs** — nodes, edges, typed state, routes/guards, checkpoints, interrupts — instead of hiding all control flow inside one autonomous loop.

Broader than LangGraph (one implementation), GraphRAG, or knowledge graphs.

Sources:
- https://www.analyticsvidhya.com/blog/2026/07/graph-engineering/
- https://docs.langchain.com/oss/python/langgraph/use-graph-api
- Related skill sections: [send-api.md](send-api.md), [human-in-the-loop.md](human-in-the-loop.md), [context-engineering.md](context-engineering.md), [planning-and-decomposition.md](planning-and-decomposition.md)

## Relation to Deep Agents

| Layer | Controls | Deep Agents skill mapping |
|-------|----------|---------------------------|
| Prompt engineering | Single model call | `system_prompt=`, prompt fragments |
| Context engineering | What each model sees | [context-engineering.md](context-engineering.md), memory, skills |
| Loop / harness engineering | How one agent reasons + tools | Path A/B ReAct (`create_agent`) |
| **Graph engineering** | How agents, functions, validators, humans coordinate | Custom `StateGraph`, `CompiledSubAgent`, patterns below |

```text
Prompts → Context → Agent loops (Deep Agent) → Graph (edges between loops/nodes)
```

Deep Agents = opinionated **single (or supervisor) ReAct harness**. Graph engineering = when **permitted transitions** must be explicit (validate → revise → HITL → finalize), not left to the model.

| Prefer Deep Agent (Path A) | Prefer explicit graph |
|----------------------------|------------------------|
| Open-ended tool use, research, coding assistant | Fixed stages with verifiable gates |
| Soft planning via todos + `task` | Hard routes in code (`if score < 0.8: revise`) |
| Few consequential side effects | Risk-based human gates before send/publish/pay |
| One context window + subagent isolation | Strict per-node context + typed state contracts |

Often combine: outer **graph** for stages; inner nodes that are `create_agent` / deep agents / deterministic functions.

## Core components

### Nodes

Bounded execution units — not all are LLM agents:

- LLM call, full tool-using agent, Python function
- Retrieval / DB / API, policy check, test suite
- Human approval, **subgraph**

Keep known business rules **deterministic**. Use LLMs for semantic interpretation, generation, planning, ambiguity.

### Edges

Direct, conditional, parallel, looping, error, human-controlled, event-triggered. An edge is a **dependency or control rule**, not a suggestion to the model.

### State + reducers

Typed shared record (`TypedDict` / Pydantic). Nodes return **field updates**, not mutated shared blobs.

Parallel writers on the same key need a **reducer** (`operator.add`, `add_messages`, merge, latest-wins). See [send-api.md](send-api.md).

### Routes and guards

```python
def route_after_review(state):
    if state["grounding_score"] < 0.8:
        return "research_again"
    if state["risk_level"] == "high":
        return "human_review"
    return "finalize"
```

Hard constraints belong in routing code, not only in prompts. Evaluator nodes **update state**; route functions **choose allowed edges**. Cap revision loops (`revision_count >= 2 → escalate`).

### Checkpoints vs store

| | Checkpointer | Store |
|--|--------------|-------|
| Scope | One thread / run | Cross-thread app data |
| Use | Resume, HITL, replay, crash recovery | Long-term memory / `/memories/` |

### Interrupts

Pause for approval / edit / missing info; resume same `thread_id`. Side effects **before** an interrupt should be **idempotent**. Deep Agents tool HITL: [human-in-the-loop.md](human-in-the-loop.md). Graph-level `interrupt()` in a custom node is the same LangGraph primitive with a custom payload.

## Recurring patterns

| Pattern | Idea | Skill / LangGraph hook |
|---------|------|------------------------|
| Prompt chaining | Fixed verifiable stages | Sequential `add_edge` |
| Routing | Specialized branches | Conditional edges; det. vs LLM classifier |
| Parallelization | Independent work concurrently | Fan-out edges; [Send](send-api.md) for runtime N |
| Orchestrator–worker | Decompose → delegate → integrate | Deep Agents `task` / dynamic subagents; or Send workers |
| Evaluator–optimizer | Generate ↔ evaluate loop | Conditional revise edges + revision cap |
| Human-in-the-loop | Risk-based review | `interrupt` / `interrupt_on` |

Orchestrator should **plan, assign, integrate** — if it does every tool call, it collapses to a monolith.

## Production checklist (beyond the diagram)

1. **Node contracts** — required I/O, tools, timeout, retry, side effects, failure categories, ownership
2. **Idempotency** — keys / dedupe for payments, emails, writes on retry
3. **Error classification** — retry vs validate vs escalate vs stop (not one generic retry)
4. **Context isolation** — give each node only the fields it needs
5. **Observability** — node timing, route chosen, state deltas, tools, tokens, human decisions
6. **Durable checkpointer** in prod (not `InMemorySaver` alone)

## Limitations

More infra, state complexity, testing, join latency, cost if over-agented. A graph helps when it makes the system safer, clearer, or easier to evaluate — not because it has more boxes.

**Start from work:** dependencies, decision boundaries, parallel opportunities, validation, failure paths, human responsibilities — then place agents in nodes.

## Minimal research-graph skeleton

```text
START → planner → researcher → writer → evaluator
                    ↑               │
                    └── revise ←────┤ (if not approved & under cap)
                                    ↓
                              human_review → finalize → END
                                    │
                                    └── revise (if rejected)
```

Full walkthrough: Analytics Vidhya article hands-on section. Example sketch: [../examples/graph_engineering_research.py](../examples/graph_engineering_research.py).

## See also

- [../programs/graph-engineering.md](../programs/graph-engineering.md)
- [send-api.md](send-api.md)
- [human-in-the-loop.md](human-in-the-loop.md)
- [assemble-deep-like-agent.md](../programs/assemble-deep-like-agent.md)
- https://www.analyticsvidhya.com/blog/2026/07/graph-engineering/
