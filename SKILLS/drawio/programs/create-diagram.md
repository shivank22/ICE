# Program: create-diagram

Step-by-step workflow for emitting a valid `.drawio` file.

## Inputs

- Topic / content to diagram (any domain)
- Diagram type (flowchart, sequence, architecture, ERD, swimlane, mind map, other)
- Optional: output path, page size, branding colors, existing `.drawio` to edit

## Checklist

```
Task Progress:
- [ ] Step 1: Clarify intent
- [ ] Step 2: Inventory elements
- [ ] Step 3: Choose layout
- [ ] Step 4: Emit mxfile XML
- [ ] Step 5: Write .drawio
- [ ] Step 6: Validate
```

### Step 1: Clarify intent

Confirm:

1. Diagram type (default: flowchart if ambiguous process; architecture if systems/components)
2. Audience (engineer vs exec) — affects label density
3. Output path (default: `diagrams/<slug>.drawio`)
4. Whether to edit an existing `.drawio` (if so, read it first and preserve ids where possible)

### Step 2: Inventory elements

List before writing XML:

- **Nodes:** id, label, shape kind (box, rounded, cylinder, actor, decision, …)
- **Edges:** source id, target id, optional label, directed or not
- **Groups / swimlanes:** containers and membership

Keep labels short. Prefer nouns for components, verb phrases for process steps.

### Step 3: Choose layout

Use [../references/diagram-types.md](../references/diagram-types.md):

| Type | Default flow | Grid |
|------|--------------|------|
| Flowchart | top → bottom or left → right | 20px snap |
| Sequence | participants across top; time down | 40px lane gap |
| Architecture | left → right or layered top → bottom | 20px snap |
| ERD | entities as boxes; relationships as edges | 20px snap |
| Swimlane | lanes as containers; steps inside | 20px snap |
| Mind map | center → radial/branches | 20px snap |

Align to multiples of 10. Consistent box sizes within a layer (e.g. 120×60).

### Step 4: Emit mxfile XML

Follow [../references/xml-format.md](../references/xml-format.md) and styles from [../references/styles.md](../references/styles.md).

Skeleton:

```xml
<mxfile host="app.diagrams.net" compressed="false">
  <diagram id="page-1" name="Page-1">
    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0" background="none">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

Copy patterns from [../examples/](../examples/) when helpful.

### Step 5: Write `.drawio`

Write the full XML to the chosen path. Create parent directories if needed. Do not wrap the file in a markdown code fence on disk.

### Step 6: Validate

Before finishing:

- [ ] Root is `<mxfile … compressed="false">`
- [ ] Cells `0` and `1` present
- [ ] All ids unique
- [ ] Vertices have `vertex="1"` + geometry `x,y,width,height`
- [ ] Edges have `edge="1"`, `source`/`target` (or points), and a `<mxGeometry>` child
- [ ] Labels escaped; no XML comments
- [ ] `background="none"` unless requested otherwise
- [ ] File opens conceptually as one clear composition

Report the file path to the user. Optional: mention open in [app.diagrams.net](https://app.diagrams.net/) or export to Visio from Draw.io UI.

## Editing an existing diagram

1. Read the current `.drawio`
2. Preserve structural cells and existing ids for unchanged shapes
3. Add new cells with new unique ids
4. Re-run the validation checklist
5. Overwrite the same path unless the user asks for a new file

## Failure modes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Blank in Draw.io | Missing `mxfile` wrapper | Use full wrapper |
| Missing arrows | Self-closing edge / no geometry | Expand `<mxGeometry>` |
| Broken open | XML comments or bad escapes | Remove comments; escape `& < > "` |
| Messy layout | Random coordinates | Snap to grid; consistent sizes |
