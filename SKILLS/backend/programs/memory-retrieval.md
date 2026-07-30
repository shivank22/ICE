# Algorithm — Memory Retrieval

## Purpose

Retrieve ranked semantic and/or episodic memories for context assembly.

## Inputs

- `query_text`
- `identity`
- `domains` (semantic | episodic | both)
- `namespace_scope`
- `top_k`, `min_score`
- `filters` (skill_id, time range, tags)

## Outputs

- `hits[]` with id, score, snippet, provenance

## Preconditions

- Caller authorized for namespaces.
- Embedding service available (or keyword fallback enabled).

## Postconditions

- Hits only from authorized namespaces.
- Scores comparable within a domain.

## Steps

1. Derive allowed namespaces from JWT (`user_id`, org roles).
2. Intersect with requested `namespace_scope`.
3. Embed `query_text` (or build lexical query).
4. Query store(s) with ACL filter **before** ranking.
5. Apply filters; rank; cut to `top_k`.
6. Project snippets (not necessarily full Memory.md).
7. Return hits.

## Edge Cases

- No embedding → lexical fallback with lower confidence flag.
- Cross-org request without role → empty set (not error).

## Failure Handling

On store error: return partial with `degraded=true` if policy allows; else abort assembly.
