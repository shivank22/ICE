# Agentic Backend Architecture — Knowledge Pack

IDE-pluggable Architecture Knowledge Pack for designing enterprise **Agentic Orchestrator** backends **on LangGraph**.

- Entrypoint for agents: [`SKILL.md`](SKILL.md)
- LangGraph bindings: [`references/langgraph-bindings.md`](references/langgraph-bindings.md)
- Handbook index: [`references/00-index.md`](references/00-index.md)
- **Thread/Run API (HITL any FE):** [`references/16-api-surface-interrupt-resume.md`](references/16-api-surface-interrupt-resume.md)
- **Skill platform:** [`references/19-skill-platform-lifecycle.md`](references/19-skill-platform-lifecycle.md)
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
| Procedural | **`SKILL.md` + `skill.yaml`** → CI → Postgres/pgvector; runtime search → records in context; **Skill Resolver Service** loads packages from **`lfs`** (container) or **`blob`** (serverless/singleton API) — doc 19 |
| Episodic | Traces + episodes; gated promotion to skills — platform on top |

**Contracts rule:** skill locator `backend` is `lfs` \| `blob`. Index holds cards (name, description, metadata); Resolver loads full packages. See [`references/contracts/`](references/contracts/).

## Usage

Point Cursor / Claude Code / VS Code agents at this folder (project skill or explicit `@SKILLS/backend`). The agent should elicit stack bindings (LangGraph defaults), then apply the opinionated architecture using progressive disclosure into `references/`.
