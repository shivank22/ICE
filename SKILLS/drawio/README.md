# Draw.io General-Purpose Diagrams

IDE-pluggable skill for producing **native Draw.io / diagrams.net `.drawio` files** for any topic.

- Entrypoint for agents: [`SKILL.md`](SKILL.md)
- Generation workflow: [`programs/create-diagram.md`](programs/create-diagram.md)
- XML rules: [`references/xml-format.md`](references/xml-format.md)
- Style presets: [`references/styles.md`](references/styles.md)
- Layout by type: [`references/diagram-types.md`](references/diagram-types.md)
- Templates: [`examples/`](examples/)

## Usage

Point Cursor / Claude Code / VS Code agents at this folder (project skill or `@SKILLS/drawio`). The agent should clarify the diagram type, emit uncompressed `mxfile` XML, write a `.drawio` file, and validate against the checklist.

Open results in draw.io desktop, [app.diagrams.net](https://app.diagrams.net/), or a Draw.io editor extension. Export to Visio (`.vsdx`) from the Draw.io UI when needed.

## Related

For LangGraph / agentic backend architecture *content*, see [`../backend/`](../backend/). Use this skill when the deliverable should be an editable Draw.io file.
