# Agentic Backend Architecture — Knowledge Pack

IDE-pluggable Architecture Knowledge Pack for designing enterprise **Agentic Orchestrator** backends **on LangGraph**.

- Entrypoint for agents: [`SKILL.md`](SKILL.md)
- LangGraph bindings: [`references/langgraph-bindings.md`](references/langgraph-bindings.md)
- Handbook index: [`references/00-index.md`](references/00-index.md)
- **Thread/Run API (HITL any FE):** [`references/16-api-surface-interrupt-resume.md`](references/16-api-surface-interrupt-resume.md)
- **LangGraph observability:** [`references/17-langgraph-observability.md`](references/17-langgraph-observability.md)
- **Evaluation frameworks (DeepEval example):** [`references/18-evaluation-frameworks.md`](references/18-evaluation-frameworks.md)
- Algorithms: [`programs/`](programs/)
- Diagrams: [`assets/diagrams/`](assets/diagrams/)
- JSON contracts: [`references/contracts/`](references/contracts/)

## Four memory domains (summary)

| Domain | Binding |
|--------|---------|
| Short-term | Graph state + LangGraph **checkpointer** (`PostgresSaver`) |
| Semantic | LangGraph **Store** (`PostgresStore`); namespace = JWT `user_id`; `Memory.md` in values |
| Procedural | Skill registry (FS or Blob) — platform on top |
| Episodic | Traces + episodes; gated promotion to skills — platform on top |

## Usage

Point Cursor / Claude Code / VS Code agents at this folder (project skill or explicit `@SKILLS/backend`). The agent should elicit stack bindings (LangGraph defaults), then apply the opinionated architecture using progressive disclosure into `references/`.
