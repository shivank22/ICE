# Draw.io XML format

Uncompressed native `.drawio` structure for AI generation.

## Minimal valid file

```xml
<mxfile host="app.diagrams.net" compressed="false">
  <diagram id="page-1" name="Page-1">
    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0" background="none">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="n1" value="Start" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="80" y="80" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="n2" value="End" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="280" y="80" width="120" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="e1" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;" edge="1" parent="1" source="n1" target="n2">
          <mxGeometry relative="1" as="geometry"/>
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
            └── mxCell…             (shapes / edges / groups)
```

## Vertex

```xml
<mxCell id="box1" value="Label" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="60" as="geometry"/>
</mxCell>
```

- Require `vertex="1"` and `mxGeometry` with `x`, `y`, `width`, `height`
- `parent` is `"1"` or a group cell id

## Edge

```xml
<mxCell id="edge1" value="label" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;" edge="1" parent="1" source="box1" target="box2">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

- Require `edge="1"` and a **non-self-closing** `<mxGeometry>` child
- Prefer `source` and `target` cell ids
- Unconnected edges need `mxPoint` source/target points inside geometry

## Groups / containers

A group is a vertex whose children set `parent` to the group id. Swimlanes use `swimlane` shape styles (see [styles.md](styles.md)).

## Multi-page

Add sibling `<diagram id="…" name="…">` elements under `mxfile`. Each page has its own `mxGraphModel` and `0`/`1` cells (ids are scoped per diagram page in practice; still keep them unique within a page).

## Escaping

| Character | Escape |
|-----------|--------|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |

Never include `<!-- XML comments -->`.

## Compression

Always `compressed="false"`. Do not emit Base64/deflate bodies inside `diagram`. Uncompressed XML is smaller for models, readable, and validatable.

## Validation checklist

1. `mxfile` root with `compressed="false"`
2. At least one `diagram` → `mxGraphModel` → `root`
3. Cells `0` and `1` present
4. Unique ids within the page
5. Vertices: `vertex="1"` + absolute geometry
6. Edges: `edge="1"` + `<mxGeometry>` child
7. Labels escaped; no comments
8. Prefer `background="none"`
