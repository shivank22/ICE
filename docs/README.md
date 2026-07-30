# Agentic Framework Architecture Diagrams

## Design records

| Document | Description |
|----------|-------------|
| [`adr/ADR-001-vanilla-agentic-platform.md`](adr/ADR-001-vanilla-agentic-platform.md) | Architecture Design Record — full component inventory + technology stack (React/Redux, FastAPI, LangGraph Deep Agents, Langfuse, Azure, Postgres, OpenAI) |
| [`../framework/.stack.md`](../framework/.stack.md) | Stack binding for implementation agents |
| [`../skills/README.md`](../skills/README.md) | Fabric coding skills (Connectivity, Context, Orchestrator, Execution, Evaluation, Adaption) for Cursor / GHCP / VS Code agents |

Primary narrative: [`../ARCHITECTURE.md`](../ARCHITECTURE.md)

---

All diagrams are **draw.io** (`.drawio`) with a short markdown companion.

| Diagram | Notes | Description |
|---------|-------|-------------|
| [`01-overall-process.drawio`](01-overall-process.drawio) | [01-overall-process.md](01-overall-process.md) | Overall process (skills → artifacts → Final Deliverable Document) |
| [`02-microservices-map.drawio`](02-microservices-map.drawio) | [02-microservices-map.md](02-microservices-map.md) | All deployable microservices behind gateway. skill-loader is the mount hub to provisioner + runners. |
| [`03-system-overview.drawio`](03-system-overview.drawio) | [03-system-overview.md](03-system-overview.md) | Three platforms, FinOps + Adaption engines, ephemeral runners and external systems. |
| [`04-skill-knowledge-platform.drawio`](04-skill-knowledge-platform.drawio) | [04-skill-knowledge-platform.md](04-skill-knowledge-platform.md) | Four framework skills, three memory types, skill update loop with reviewer HITL. |
| [`05-execution-runners.drawio`](05-execution-runners.drawio) | [05-execution-runners.md](05-execution-runners.md) | skill-loader resolves skills, spawns via sandbox-provisioner, mounts onto runners for agents. |
| [`06-discovery-wizard.drawio`](06-discovery-wizard.drawio) | [06-discovery-wizard.md](06-discovery-wizard.md) | Interactive guided wizard for Skill 1 (Research) — user + agent collaboration. |
| [`07-skill-artifacts.drawio`](07-skill-artifacts.drawio) | [07-skill-artifacts.md](07-skill-artifacts.md) | Artifact per skill; final Final Deliverable Document; no MR. |
| [`08-finops-engine.drawio`](08-finops-engine.drawio) | [08-finops-engine.md](08-finops-engine.md) | Agent cost per run from Langfuse + runner metrics → cost_record. |
| [`09-adaption-engine.drawio`](09-adaption-engine.drawio) | [09-adaption-engine.md](09-adaption-engine.md) | Engagement tracks and emails to stakeholders on lifecycle events. |
| [`10-logical-fabrics.drawio`](10-logical-fabrics.drawio) | [10-logical-fabrics.md](10-logical-fabrics.md) | Five logical layers/frameworks mapped to the framework microservices. |
