# 05 — Semantic Memory

## 1. Executive Summary

Semantic Memory stores durable knowledge about users, organizations, and engagements. Preferred implementation: **Postgres** (with embeddings for retrieval). Default **namespace** is the JWT **`user_id`**. Record body lives in a **`Memory.md`** column (markdown memory document).

## 2. Purpose

Give agents stable, namespaced facts that survive threads and are queryable independently of chat history.

## 3. Scope

User/org/engagement facts, retrieval, ranking, lifecycle. Not skill procedures (procedural) or run traces (episodic).

## 4. Architecture Overview

Knowledge service owns the table and APIs. Context Assembler retrieves; Orchestrator does not write semantic memory unless an explicit governed tool/skill says so.

See [../assets/diagrams/05-semantic-namespace.mmd](../assets/diagrams/05-semantic-namespace.mmd)

## 5. Core Concepts

- **Namespace:** `user:<user_id>`, optionally `org:<org_id>`, `engagement:<id>`.
- **Memory.md:** human-readable markdown fact document.
- **Embedding:** vector derived from Memory.md (and optional metadata) for similarity search.
- **Provenance:** who wrote the fact, when, and from which thread/skill.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| Sem1 | Namespace root for personal facts = JWT `user_id` (never client-supplied alone) |
| Sem2 | Memory body column named/conceptualized as `Memory.md` |
| Sem3 | Updates are versioned (new revision), not silent overwrite without history |
| Sem4 | Retrieval always scoped by authz before similarity |

## 7. Decision Rationale

JWT subject prevents namespace spoofing. Markdown keeps facts reviewable by humans. Versioning supports audit and rollback. Authz-before-rank prevents cross-tenant vector leakage.

## 8. Alternatives Considered

| Alternative | Tradeoff |
|-------------|----------|
| Pure vector DB without SQL | Weaker transactions and ACL joins |
| Namespace = email | Emails change; collisions |
| Stuffing facts only into system prompt | No retrieval lifecycle |

## 9. Tradeoffs

Versioned rows increase storage. Embedding refresh adds cost on update. Acceptable for enterprise correctness.

## 10. Component Breakdown

### Knowledge / Semantic Memory Service

- **Purpose:** CRUD + retrieval for semantic records.
- **Responsibilities:** Enforce namespaces, embed, rank, version, soft-delete.
- **Non-responsibilities:** Graph scheduling; skill registry.
- **Inputs:** Authenticated write/read requests; query text; filters.
- **Outputs:** Memory records; ranked hit lists.
- **Dependencies:** Postgres + vector extension; embedding model.
- **Lifecycle:** create → revise → archive → purge per retention.
- **Failure Modes:** embedding outage, unique constraint, ACL misconfig.
- **Recovery:** Queue embed retries; fail closed on ACL errors.
- **Security:** Derive namespace from validated JWT; RBAC for org scopes.
- **Scalability:** Partition by namespace hash; ANN indexes; read replicas.

## 11. Sequence of Operations

### Write

1. Validate JWT; extract `user_id`.
2. Authorize target namespace.
3. Insert new revision of Memory.md + metadata.
4. Compute embedding asynchronously if needed.
5. Emit memory.updated event.

### Read (retrieval)

1. Authorize candidate namespaces.
2. Embed query (or use hybrid keyword + vector).
3. Rank within allowed set.
4. Return top-k under budget to Context Assembler.

Algorithm: [../programs/memory-retrieval.md](../programs/memory-retrieval.md) · [../programs/memory-update.md](../programs/memory-update.md)

## 12. State Changes

| Status | Meaning |
|--------|---------|
| active | Retrievable |
| superseded | Older revision |
| archived | Hidden from default retrieval |
| deleted | Soft-deleted / tombstoned |

## 13. Mermaid Diagrams

See §4. Also [../assets/diagrams/05-semantic-write-read.mmd](../assets/diagrams/05-semantic-write-read.mmd)

## 14. JSON Contracts

- [contracts/semantic-memory.json](contracts/semantic-memory.json)
- [contracts/memory-record.json](contracts/memory-record.json)

## 15. Best Practices

- Separate user vs org namespaces explicitly in queries.
- Include `source_thread_id` / `source_skill_id` on writes.
- Redact secrets from Memory.md (policies in security doc).

## 16. Anti-patterns

- Trusting `namespace` from request body without JWT check.
- One global memory bag for all users.
- Updating embeddings in the request path without timeout budgets.

## 17. Common Mistakes

- Storing procedural instructions in Memory.md.
- Using chat summaries as semantic source of truth without curation.
- Forgetting org-admin override paths need audit logs.

## 18. Future Evolution

Memory conflict resolution UI; claim-level provenance; automatic decay of stale facts.

## 19. Related Documents

[03-memory-architecture.md](03-memory-architecture.md) · [08-context-construction.md](08-context-construction.md) · [14-security.md](14-security.md)
