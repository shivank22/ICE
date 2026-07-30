# Algorithm — Memory Retrieval

## Purpose

Retrieve ranked semantic and/or episodic memories for context assembly. Semantic hits use LangGraph **Store** (`search` / `get`); episodic hits use the platform episode/trace store.

## LangGraph binding

- Semantic: `store.search(namespace, query=..., filter=..., limit=top_k)` or `store.get(namespace, key)`
- Namespace tuples derived from JWT (e.g. `(user_id, "semantic")`)
- Optional vector ranking when Store was created with `index=` / `IndexConfig`
- Docs: [Stores](https://docs.langchain.com/oss/python/langgraph/stores) · [Long-term memory](https://docs.langchain.com/oss/python/langchain/long-term-memory)

## Inputs

- `query_text`
- `identity`
- `domains` (semantic | episodic | both)
- `namespace_scope` (tuples or prefixes)
- `top_k`, `min_score`
- `filters` (skill_id, time range, tags, status)
- `store` (LangGraph `BaseStore` for semantic)

## Outputs

- `hits[]` with id, score, snippet, provenance, domain

## Preconditions

- Caller authorized for namespaces.
- Store available for semantic domain (or keyword/filter fallback enabled).
- Embedding path available if similarity search required and index configured.

## Postconditions

- Hits only from authorized namespaces.
- Scores comparable within a domain.
- No cross-tenant Store prefix leakage.

## Steps

1. Derive allowed namespace tuples/prefixes from JWT (`user_id`, org roles).
2. Intersect with requested `namespace_scope`.
3. **Semantic:** for each allowed namespace, call `store.search(...)` (or filter + client-side rank if no index). ACL filter is the namespace itself—do not search unauthorized prefixes.
4. **Episodic:** query episode store under same authz and budget (not LangGraph Store unless you chose to mirror episodes there).
5. Apply filters (`status=active`, tags, time); cut to `top_k`.
6. Project snippets from `Memory.md` / episode summaries (not full traces).
7. Return hits with provenance to Context Assembler.

## Edge Cases

- No embedding / no index → filter + lexical fallback with lower confidence flag.
- Cross-org request without role → empty set (not error).
- Store prefix match too broad → tighten tuple design; never pass bare `()`.

## Failure Handling

On Store error: return partial with `degraded=true` if policy allows; else abort assembly. Fail closed on authz errors.
