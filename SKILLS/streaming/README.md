# LangGraph Streaming

IDE-pluggable skill for **streaming LangGraph graphs and agents** with the stream-mode API (`stream` / `astream`, `stream_mode`, `version="v2"`).

- Entrypoint for agents: [`SKILL.md`](SKILL.md)
- Core consume loop: [`programs/stream-graph.md`](programs/stream-graph.md)
- LLM tokens: [`programs/stream-llm-tokens.md`](programs/stream-llm-tokens.md)
- Custom writer: [`programs/emit-custom.md`](programs/emit-custom.md)
- Subgraphs / nested agents: [`programs/stream-subgraphs.md`](programs/stream-subgraphs.md)
- References: [`references/`](references/)
- Examples: [`examples/`](examples/)

## Usage

Point Cursor / Claude Code / VS Code agents at this folder (project skill or `@SKILLS/streaming`). Prefer `version="v2"`, branch on `chunk["type"]`, and set `subgraphs=True` when nested agents must emit tokens to the parent stream.

## Related

- Deep Agents / `create_agent` harness: [`../deepagents/`](../deepagents/)
- ICE Thread/Run APIs and SSE/WS: [`../backend/`](../backend/)
- Upstream: [LangGraph Streaming](https://docs.langchain.com/oss/python/langgraph/streaming)
