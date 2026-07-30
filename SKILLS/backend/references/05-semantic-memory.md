# 05 — Semantic Memory

## 1. Executive Summary

Semantic Memory stores durable knowledge about users, organizations, and engagements **across threads**. Preferred LangGraph binding: **`BaseStore` / `PostgresStore`** compiled into the graph (`compile(..., store=store)`), with optional vector **index** for similarity search. Default **namespace** root is the JWT **`user_id`**. Record body is a markdown document conceptually named **`Memory.md`** stored as a field inside the Store item value—not a separate invent-your-own datastore by default.

## 2. Purpose

Give agents stable, namespaced facts that survive threads and are queryable independently of chat history, using LangGraph’s long-term memory primitive.

## 3. Scope

User/org/engagement facts, retrieval, ranking, lifecycle. Not skill procedures (procedural) or run traces (episodic). Not short-term thread state (that is the **checkpointer**).

## 4. Architecture Overview

LangGraph **Store** is the system of record for semantic items. Application code (nodes or a thin Knowledge facade) calls `put` / `get` / `search` with authz-derived namespaces. Context Assembler retrieves; Orchestrator does not write semantic memory unless an explicit governed tool/skill says so.

See [../assets/diagrams/05-semantic-namespace.mmd](../assets/diagrams/05-semantic-namespace.mmd) · [langgraph-bindings.md](langgraph-bindings.md)

### Preferred binding

| Concern | Binding |
|---------|---------|
| API | `langgraph.store` — `BaseStore` |
| Production | `PostgresStore` (+ pgvector via `index=` config) |
| Dev | `InMemoryStore` |
| Namespace | Tuple, e.g. `(user_id, "semantic")` or `(user_id, "semantic", engagement_id)` |
| Key | Stable memory id / slug |
| Value | JSON including `Memory.md`, tags, provenance, revision metadata |

Docs: [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) · [Stores](https://docs.langchain.com/oss/python/langgraph/stores) · [Long-term memory](https://docs.langchain.com/oss/python/langchain/long-term-memory)

## 5. Core Concepts

- **Namespace (tuple):** isolation key; always derive personal scope from JWT `user_id`, never from client-supplied alone.
- **Memory.md:** human-readable markdown fact document **inside** the Store value.
- **Index / embedding:** optional Store `IndexConfig` so `search(..., query=...)` ranks by similarity.
- **Provenance:** who wrote the fact, when, and from which thread/skill (fields on the value or metadata).
- **Knowledge facade (optional):** thin service wrapping Store with RBAC, revision policy, and redaction—not a second persistence model.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| Sem1 | Default implementation = LangGraph Store; do not invent a parallel memory table unless Store cannot meet constraints |
| Sem2 | Namespace root for personal facts = JWT `user_id` (never client-supplied alone) |
| Sem3 | Memory body field named/conceptualized as `Memory.md` inside Store values |
| Sem4 | Updates are versioned (new revision key or superseding put), not silent overwrite without history |
| Sem5 | Retrieval always scoped by authz **before** similarity (`search` only within allowed namespaces) |

## 7. Decision Rationale

LangGraph already separates checkpointer (thread STM) from Store (cross-thread LTM). Reusing Store avoids dual writers and matches official long-term memory guidance. JWT subject prevents namespace spoofing. Markdown keeps facts reviewable. Authz-before-rank prevents cross-tenant leakage.

## 8. Alternatives Considered

| Alternative | Tradeoff |
|-------------|----------|
| Custom Knowledge Service + SQL as source of truth | Only if Store backends cannot satisfy compliance; still mirror the Store namespace/key/value contract |
| Pure vector DB without Store | Weaker integration with `compile(..., store=)`; harder node typing |
| Namespace = email | Emails change; collisions |
| Stuffing facts only into system prompt / checkpoints | No cross-thread lifecycle; bloats STM |

## 9. Tradeoffs

Store + revision history increases storage. Embedding refresh adds cost on update. Acceptable for enterprise correctness. A Knowledge facade adds a hop but centralizes RBAC.

## 10. Component Breakdown

### Semantic Memory via LangGraph Store

- **Purpose:** CRUD + retrieval for semantic records across threads.
- **Responsibilities:** Enforce namespaces, `put`/`get`/`search`, optional index, revision policy, soft-delete/archive conventions.
- **Non-responsibilities:** Graph scheduling; skill index / Discovery / Resolver; checkpoint persistence.
- **Inputs:** Authenticated write/read requests; query text; filters; Store injected into nodes.
- **Outputs:** Store items; ranked hit lists for Context Assembler.
- **Dependencies:** `PostgresStore` (prod) or `InMemoryStore` (dev); embedding function when index enabled.
- **Lifecycle:** create → revise → archive → purge per retention / Store TTL if configured.
- **Failure Modes:** embedding outage, ACL misconfig, Store unavailable.
- **Recovery:** Queue embed retries; fail closed on ACL errors; degrade to lexical filters if policy allows.
- **Security:** Derive namespace from validated JWT; RBAC for org scopes; never trust request-body namespace alone.
- **Scalability:** Namespace partitioning; ANN indexes via Store index config; read replicas as backend allows.

## 11. Sequence of Operations

### Write

1. Validate JWT; extract `user_id`.
2. Authorize target namespace tuple.
3. `store.put(namespace, key, { "Memory.md": ..., provenance..., revision... })` (new key or revise policy).
4. If index configured, Store handles indexing per `IndexConfig` (or enqueue refresh if custom).
5. Emit `memory.updated` event (platform observability).

### Read (retrieval)

1. Authorize candidate namespaces from JWT.
2. `store.search(namespace, query=..., filter=..., limit=top_k)` (or `get` for known keys).
3. Project snippets from `Memory.md` under token budget to Context Assembler.

Algorithm: [../programs/memory-retrieval.md](../programs/memory-retrieval.md) · [../programs/memory-update.md](../programs/memory-update.md)

## 12. State Changes

| Status | Meaning |
|--------|---------|
| active | Retrievable |
| superseded | Older revision (kept for audit) |
| archived | Hidden from default retrieval |
| deleted | Soft-deleted / tombstoned |

Status is an application field on the Store value (or filter convention)—not a separate LangGraph concept.

## 13. Mermaid Diagrams

See §4. Also [../assets/diagrams/05-semantic-write-read.mmd](../assets/diagrams/05-semantic-write-read.mmd)

## 14. JSON Contracts

- [contracts/semantic-memory.json](contracts/semantic-memory.json) — **value shape** for Store items
- [contracts/memory-record.json](contracts/memory-record.json)

## 15. Best Practices

- Pass `store` into `compile` and type nodes with `BaseStore`.
- Separate user vs org namespaces explicitly in tuple design.
- Include `source_thread_id` / `source_skill_id` on writes.
- Redact secrets from `Memory.md` (policies in security doc).
- Prefer Store TTL / retention jobs over unbounded growth.

## 16. Anti-patterns

- Building a second semantic DB while also using Store for the same facts.
- Trusting `namespace` from request body without JWT check.
- One global memory bag for all users.
- Writing semantic facts only into the checkpointer / latest checkpoint.
- Storing procedural instructions in `Memory.md`.

## 17. Common Mistakes

- Using chat summaries as semantic source of truth without curation.
- Forgetting org-admin override paths need audit logs.
- Calling `search` across namespaces the caller is not allowed to read.
- Treating Store as a replacement for the checkpointer (wrong scope).

## 18. Future Evolution

Memory conflict resolution UI; claim-level provenance; automatic decay of stale facts; hierarchical namespaces (user → team → org) still expressed as Store tuples.

## 19. Related Documents

[03-memory-architecture.md](03-memory-architecture.md) · [langgraph-bindings.md](langgraph-bindings.md) · [08-context-construction.md](08-context-construction.md) · [14-security.md](14-security.md)
