---
name: drawio-diagrams
description: >-
  Create and edit native Draw.io / diagrams.net .drawio XML files for
  general-purpose diagrams (flowcharts, sequences, architecture, ERDs,
  swimlanes, mind maps, and more). Use when the user asks for draw.io,
  diagrams.net, Visio-style editable diagrams, .drawio files, or an
  editable diagram artifact. Not for Mermaid-only output or data-heavy charts.
---

# Draw.io General-Purpose Diagrams

You produce **valid, editable Draw.io / diagrams.net `.drawio` files** (uncompressed `mxfile` XML). Domain is unrestricted: any process, system, data model, or concept the user describes.

You are **not** emitting Mermaid as the primary deliverable, and you are **not** generating Microsoft `.vsdx` binaries.

## When to apply

Apply when the user asks for:

- Draw.io / diagrams.net / `.drawio` files
- Visio-style or Visio-compatible editable diagrams (deliver Draw.io; user can export to Visio from the editor if needed)
- Flowcharts, sequence diagrams, architecture/container diagrams, ERDs, swimlanes, mind maps, org charts, or similar
- An editable diagram artifact in the working tree

Do **not** use this skill for Mermaid-only requests, spreadsheet/chart generation, or image-only mockups with no `.drawio` source.

## Role constraints

- Prefer **one concept per file** (or one page per concept in a multi-page file).
- Prefer **contracts of the XML format** over inventing compressed/Base64 blobs.
- Prefer **readable layout** (grid-aligned, consistent spacing) over decorative clutter.
- Write the `.drawio` file to disk; do not stop at a prose description of the diagram.
- For LangGraph / agentic platform architecture *content*, defer to [`../backend/`](../backend/) when that pack is in scope; still use this skill to emit the Draw.io file.

## Hard rules (always)

1. **Full wrapper required:** `<mxfile>` → `<diagram>` → `<mxGraphModel>` → `<root>`. Bare `mxGraphModel` alone is **not** a valid `.drawio` file.
2. **Uncompressed only:** emit `<mxGraphModel>` as XML children. Never emit deflate/Base64 bodies. Prefer **omitting** the `compressed` attribute (do not set `compressed="true"`).
3. **Structural cells:** always include `id="0"` (root) and `id="1"` (default layer, `parent="0"`). Prefer all shapes/edges at `parent="1"` with absolute coordinates.
4. **Unique ids** for every `mxCell`.
5. **Vertices** use `vertex="1"`; **edges** use `edge="1"` (mutually exclusive). Every edge needs an `<mxGeometry>` child (`relative="1"`).
6. **Escape** `&`, `<`, `>`, `"` (and newlines as `&#xa;`) in labels.
7. **No XML comments** (`<!-- -->`) — they waste tokens and can break parsers.
8. **Avoid fragile attrs:** do not set `background="none"`; do not nest ordinary boxes under group parents—use dashed boundary boxes at `parent="1"` instead.
9. **mxfile metadata:** include `host="app.diagrams.net"`, `agent="drawio-diagrams"`, `version="22.1.0"`, `type="device"`.

Details: [references/xml-format.md](references/xml-format.md).

## Progressive disclosure

Read only what the current request needs:

| Concern | Read |
|---------|------|
| Generation workflow + checklist | [programs/create-diagram.md](programs/create-diagram.md) |
| mxfile / cell / edge rules | [references/xml-format.md](references/xml-format.md) |
| Style presets | [references/styles.md](references/styles.md) |
| Layout by diagram type | [references/diagram-types.md](references/diagram-types.md) |
| Copyable templates | [examples/](examples/) |

## Workflow for agent sessions

Follow [programs/create-diagram.md](programs/create-diagram.md). Short form:

```
Draw.io session:
- [ ] Clarify topic, diagram type, and output path
- [ ] List nodes, edges, and groups
- [ ] Choose layout (see diagram-types.md)
- [ ] Emit uncompressed mxfile XML
- [ ] Write .drawio to disk
- [ ] Run validation checklist
```

## Output convention

1. Path: user-specified path, else `diagrams/<slug>.drawio` under the current working tree.
2. One primary deliverable file per request (add pages only when useful).
3. After writing, briefly state the path and how to open it (draw.io desktop, [app.diagrams.net](https://app.diagrams.net/), or VS Code Draw.io extension).
4. Optional tip only: desktop CLI can export PNG/SVG/PDF with embedded diagram XML — do not require CLI install.

## Anti-patterns

- Saving bare `<mxGraphModel>` as `.drawio` (opens blank)
- Compressed / Base64 diagram bodies
- Self-closing edge cells without `<mxGeometry>`
- Missing cells `0` / `1`
- XML comments in the file
- Dumping Mermaid and calling it the Draw.io deliverable
- Overlapping shapes, random coordinates, or inconsistent box sizes without a grid
