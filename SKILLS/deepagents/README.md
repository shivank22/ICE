# LangChain Deep Agents

IDE-pluggable skill for **writing Deep Agents** with `create_deep_agent`, or for **reconstructing** the same harness from internals with `create_agent`.

- Entrypoint for agents: [`SKILL.md`](SKILL.md)
- Path A (factory): [`programs/create-deep-agent.md`](programs/create-deep-agent.md)
- Internals map: [`programs/under-the-hood.md`](programs/under-the-hood.md)
- Path B (assemble): [`programs/assemble-deep-like-agent.md`](programs/assemble-deep-like-agent.md)
- Memory: [`programs/configure-memory.md`](programs/configure-memory.md)
- Context engineering: [`programs/context-engineering.md`](programs/context-engineering.md)
- Human-in-the-loop: [`programs/human-in-the-loop.md`](programs/human-in-the-loop.md)
- Dynamic subagents: [`programs/dynamic-subagents.md`](programs/dynamic-subagents.md)
- References: [`references/`](references/)
- Examples: [`examples/`](examples/)

## Agenda

| Path | When | Outcome |
|------|------|---------|
| **A — Factory** | Ship quickly | Correct `create_deep_agent(...)` app |
| **B — Internals** | Teach, fork, or debug | Equivalent `create_agent` + middleware stack |

Both produce a LangGraph `CompiledStateGraph` on the same ReAct tool-calling loop.

## Usage

Point Cursor / Claude Code / VS Code agents at this folder (project skill or `@SKILLS/deepagents`). Prefer Path A unless the stack must be customized or explained layer by layer.

## Related

For ICE agentic platform architecture (skill CI/index/resolver, Thread/Run APIs, Store ownership), see [`../backend/`](../backend/). Use **this** skill for Deep Agents harness mechanics.
