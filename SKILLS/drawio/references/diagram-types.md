# Diagram types and layout recipes

Opinionated defaults. Adapt when the user specifies otherwise.

## Flowchart

- **Flow:** top → bottom (default) or left → right for short pipelines
- **Shapes:** ellipse start/end; rounded process; rhombus decision
- **Edges:** orthogonal with `endArrow=classic`; label Yes/No on decision branches
- **Heuristic:** one decision per branch point; avoid crossing edges when possible
- **Template:** [../examples/flowchart.drawio](../examples/flowchart.drawio)

## Sequence

- **Layout:** participants in a row at the top; time flows downward
- **Shapes:** rectangles for lifelines/participants; optional actor for humans
- **Edges:** straight or orthogonal messages downward; return messages dashed
- **Heuristic:** keep participant spacing ≥ 160px; message y-increments of 40–60
- **Template:** [../examples/sequence.drawio](../examples/sequence.drawio)

## Architecture / containers

- **Flow:** left → right (request path) or top → bottom (layers)
- **Shapes:** rounded boxes for services; cylinders for stores; group containers for boundaries
- **Edges:** solid for runtime calls; dashed for dependencies
- **Heuristic:** one layer or one trust boundary per horizontal/vertical band; label edges only when direction is ambiguous
- **Template:** [../examples/architecture.drawio](../examples/architecture.drawio)

## ERD

- **Layout:** entities as boxes in a loose grid; related entities nearby
- **Shapes:** rectangle (or table-like stacked labels); crow’s-foot optional via edge labels (`1`, `N`, `0..1`)
- **Edges:** undirected or with end markers; put cardinality in `value`
- **Heuristic:** entity name alone on first pass; add attributes only if the user asks

## Swimlane

- **Layout:** horizontal or vertical `swimlane` containers for roles/systems
- **Shapes:** process steps inside the owning lane
- **Edges:** may cross lanes; keep handoffs explicit with edge labels
- **Heuristic:** max 4–6 lanes; put the primary actor in the first lane

## Mind map

- **Layout:** central topic; branches left/right or radial
- **Shapes:** rounded central node; smaller children
- **Edges:** simple connectors without heavy orthogonal routing
- **Heuristic:** depth ≤ 3 unless the user needs a full breakdown

## Choosing a type

| User cue | Prefer |
|----------|--------|
| steps, process, decision, workflow | Flowchart |
| request/response over time, API calls | Sequence |
| services, components, stores, layers | Architecture |
| tables, entities, relationships | ERD |
| who does what / RACI-like | Swimlane |
| brainstorm, topics, hierarchy of ideas | Mind map |

If unclear, ask one clarifying question; otherwise default to **flowchart** for processes and **architecture** for systems.
