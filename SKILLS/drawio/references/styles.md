# Style presets

Reuse these `style` strings. Always end with a semicolon. Prefer `html=1;whiteSpace=wrap;` on labeled shapes.

## Shapes

| Kind | Style |
|------|-------|
| Box | `rounded=0;whiteSpace=wrap;html=1;` |
| Rounded | `rounded=1;whiteSpace=wrap;html=1;` |
| Decision (rhombus) | `rhombus;whiteSpace=wrap;html=1;` |
| Ellipse / start-end | `ellipse;whiteSpace=wrap;html=1;` |
| Cylinder / datastore | `shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;` |
| Actor | `shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;` |
| Document | `shape=document;whiteSpace=wrap;html=1;` |
| Process (parallelogram) | `shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;` |

## Containers / boundaries

Prefer **visual** boundaries (all cells `parent="1"`). Avoid `container=1` nesting unless the user needs real swimlanes.

| Kind | Style |
|------|-------|
| Dashed boundary (preferred) | `rounded=1;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=1;fillColor=none;strokeColor=#999999;dashed=1;spacingTop=2;` |
| Filled zone | `rounded=1;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=1;fillColor=#f5f5f5;strokeColor=#666666;spacingTop=2;` |
| Swimlane (only when needed) | `swimlane;whiteSpace=wrap;html=1;startSize=30;` |

## Edges

| Kind | Style |
|------|-------|
| Orthogonal arrow | `edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;` |
| Straight arrow | `endArrow=classic;html=1;rounded=0;` |
| Dashed dependency | `edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=open;dashed=1;` |
| Bidirectional | `edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;startArrow=classic;endArrow=classic;` |

## Color (optional)

Use sparingly. Defaults are fine for most diagrams.

| Role | fillColor | strokeColor | fontColor |
|------|-----------|-------------|-----------|
| Neutral | `#ffffff` | `#666666` | `#333333` |
| Emphasis | `#dae8fc` | `#6c8ebf` | `#333333` |
| Warning / decision | `#fff2cc` | `#d6b656` | `#333333` |
| Store / data | `#e1d5e7` | `#9673a6` | `#333333` |
| External | `#f8cecc` | `#b85450` | `#333333` |

Append as `fillColor=#dae8fc;strokeColor=#6c8ebf;` on the shape style. Prefer one accent family per diagram—avoid rainbow palettes.

## Layout constants

- Snap to multiples of **10** (`gridSize="10"`)
- Default box: **120×60** (or 160×60 for longer labels)
- Horizontal gap: **40–80**; vertical gap: **40–80**
- Page default: landscape A4-ish `pageWidth="1169"` `pageHeight="827"`; grow page or add pages if content overflows
