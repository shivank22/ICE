---
name: phase-4-knowledge-and-clients
description: >-
  Implements Phase 4: knowledge-service semantic and episodic memory, reflection
  and skill-review HITL, plus MCP and CLI clients at parity with the gateway.
  Use when adding memory, skill governance, or non-UI clients for this architecture.
disable-model-invocation: true
---

# Phase 4 — Knowledge Memory + MCP/CLI Parity

Implement **build order Phase 4** from [`ARCHITECTURE.md`](../../ARCHITECTURE.md).

## Prerequisites

1. Phases 1–3 core pipeline works; read `framework/.stack.md`.
2. Diagrams: [`docs/04-skill-knowledge-platform`](../../docs/04-skill-knowledge-platform.md), [`docs/02-microservices-map`](../../docs/02-microservices-map.md).

## Must not change

- Three memory types: **procedural** (registry), **semantic**, **episodic** (DB + embeddings)
- Skill updates go through **change_request → human skill-reviewer** — no silent overwrite of production skills
- MCP and CLI map **1:1** to gateway routes (no special-case business logic in clients)
- knowledge-service owns: `engagement`, `guided_session`, `skill_meta`, `org_asset`, `episode`, `change_request` (as applicable)

## Must ask (if not in `.stack.md`)

- Embedding model / dimension for pgvector (or alternative)
- Where engagement entity lives if Phase 1 stubbed it on job-service (migrate ownership if needed)
- MCP SDK language preference
- CLI packaging (pip, npm, cargo, go install, …)

## Scope

| Deliverable | Notes |
|-------------|--------|
| `knowledge-service` | CRUD + retrieval for facts/episodes; registry pointers |
| Episodic writes | Completed jobs write episodes |
| Reflection stub | Opens `change_request` from episodes (can be batch job) |
| Skill-review HITL | Approve → publish production skill / update semantic fact |
| `apps/mcp` | Tools mirror gateway routes |
| `apps/cli` | Scriptable parity for the same routes |

## Implementation order

1. **Schema** — semantic docs + episode records + embeddings; `change_request` states (`open|approved|rejected`).
2. **APIs** — retrieve skills/facts/episodes for loader/orchestrator; write episode on job success.
3. **Governance UI or admin routes** — list change requests; approve/reject (role `skill-reviewer`).
4. **MCP server** — one tool per gateway route used by operators.
5. **CLI** — same operations; share API client library with MCP if practical.
6. **Move engagement ownership** to knowledge-service if it was temporary on job-service.

## Memory map (fixed)

| Memory | Store |
|--------|--------|
| Procedural | Langfuse (or chosen registry) `production` label |
| Semantic | Postgres + embeddings |
| Episodic | Postgres + embeddings |

## Done checklist

```
- [ ] Episodes written after successful jobs
- [ ] change_request + skill-reviewer path works
- [ ] Semantic retrieve usable by skill-loader
- [ ] MCP tools 1:1 with gateway
- [ ] CLI parity for core operator flows
- [ ] Next: phase-5-finops-and-adaption
```
