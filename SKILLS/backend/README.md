# Agentic Backend Architecture — Knowledge Pack

IDE-pluggable Architecture Knowledge Pack for designing enterprise **Agentic Orchestrator** backends.

- Entrypoint for agents: [`SKILL.md`](SKILL.md)
- Handbook index: [`references/00-index.md`](references/00-index.md)
- Algorithms: [`programs/`](programs/)
- Diagrams: [`assets/diagrams/`](assets/diagrams/)
- JSON contracts: [`references/contracts/`](references/contracts/)

## Four memory domains (summary)

| Domain | Store |
|--------|-------|
| Short-term | Messages + checkpointers |
| Semantic | Postgres; namespace = JWT `user_id`; `Memory.md` column |
| Procedural | Skill registry (FS or Blob) |
| Episodic | Traces + episodes; gated promotion to skills |

## Usage

Point Cursor / Claude Code / VS Code agents at this folder (project skill or explicit `@SKILLS/backend`). The agent should elicit stack bindings, then apply the opinionated architecture using progressive disclosure into `references/`.
