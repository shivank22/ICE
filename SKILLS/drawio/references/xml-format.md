# Draw.io XML format

Uncompressed native `.drawio` structure for AI generation. Matches the format already used successfully in this repo’s blueprint generator.

## Minimal valid file

```xml
<mxfile host="app.diagrams.net" agent="drawio-diagrams" version="22.1.0" type="device">
  <diagram id="page-1" name="Page-1">
    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="n1" value="Start" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="80" y="80" width="120" height="60" as="geometry" />
        </mxCell>
        <mxCell id="n2" value="End" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="280" y="80" width="120" height="60" as="geometry" />
        </mxCell>
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;" edge="1" parent="1" source="n1" target="n2">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Hierarchy

```
mxfile
└── diagram (+ optional more pages)
    └── mxGraphModel
        └── root
            ├── mxCell id=0          (root)
            ├── mxCell id=1 parent=0 (default layer)
            └── mxCell…             (shapes / edges; prefer parent="1")
```

## Vertex

```xml
<mxCell id="box1" value="Label" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="60" as="geometry" />
</mxCell>
```

- Require `vertex="1"` and `mxGeometry` with `x`, `y`, `width`, `height`, `as="geometry"`
- Prefer `parent="1"` for all shapes (absolute page coordinates)

## Edge

```xml
<mxCell id="edge1" value="label" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;" edge="1" parent="1" source="box1" target="box2">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

- Require `edge="1"` and a **non-self-closing** `<mxGeometry>` child when it contains waypoints; otherwise `<mxGeometry … />` is fine
- Prefer `source` and `target` cell ids
- Unconnected edges need `mxPoint` with `as="sourcePoint"` / `as="targetPoint"`

## Boundaries (prefer flat, not nested)

For visual “containers”, draw a dashed background box with `parent="1"`, and keep **all** child shapes also at `parent="1"` with absolute coordinates. Do **not** nest shapes with `parent="<groupId>"` unless the user explicitly needs true swimlane/container nesting.

```xml
<mxCell id="boundary" value="Zone" style="rounded=1;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=1;fillColor=none;strokeColor=#999999;dashed=1;spacingTop=2;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="400" height="200" as="geometry" />
</mxCell>
```

## Multi-page

Add sibling `<diagram id="…" name="…">` elements under `mxfile`. Keep ids unique within each page.

## Escaping

| Character | Escape |
|-----------|--------|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| newline in labels | `&#xa;` |

Never include `<!-- XML comments -->`.

## Compression

Emit **uncompressed** XML: put `<mxGraphModel>` as a child of `<diagram>`. Do **not** set `compressed="true"`. Prefer omitting `compressed` entirely (do not rely on `compressed="false"`).

## Attributes to avoid (compatibility)

| Avoid | Why |
|-------|-----|
| `compressed="false"` on `mxfile` | Some editors mis-handle the attribute; omit instead |
| `background="none"` on `mxGraphModel` | Omit; default is fine |
| Nested `parent="<group>"` for ordinary boxes | Prefer flat `parent="1"` + dashed boundary boxes |

## Validation checklist

1. `mxfile` root with `host`, optional `agent` / `version` / `type="device"`
2. At least one `diagram` → `mxGraphModel` → `root`
3. Cells `0` and `1` present (`<mxCell id="0" />`, `<mxCell id="1" parent="0" />`)
4. Unique ids within the page
5. Vertices: `vertex="1"` + absolute geometry; prefer `parent="1"`
6. Edges: `edge="1"` + `<mxGeometry …>` child
7. Labels escaped; no comments
8. No `compressed="true"`; prefer no `compressed` attribute at all

## Troubleshooting load errors

If Cursor’s Draw.io extension shows a blank editor or an attribute/parse error:

1. Confirm the file is full `mxfile` → `diagram` → `mxGraphModel` (not bare `mxGraphModel`)
2. Remove `compressed` and `background` attributes
3. Flatten nested parents to `parent="1"`
4. Open with Draw.io desktop (`open file.drawio`) or [app.diagrams.net](https://app.diagrams.net/) as a check
5. Ensure `"hediet.vscode-drawio.offline": true` in Cursor settings if the online viewer fails to boot
