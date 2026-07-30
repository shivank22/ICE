# Algorithm — Memory Update (Semantic)

## Purpose

Create or revise a semantic memory item in LangGraph **Store** for an authorized namespace.

## LangGraph binding

- `store.put(namespace, key, value)` where `value` includes `Memory.md` and provenance
- Production: `PostgresStore`; Dev: `InMemoryStore`
- Do **not** invent a parallel write path for the same facts
- Docs: [Stores](https://docs.langchain.com/oss/python/langgraph/stores)

## Inputs

- `identity`
- `namespace` (tuple; must be authorized)
- `key` (stable memory id)
- `memory_md` (markdown body)
- `metadata` (tags, source_thread_id, source_skill_id, revision)
- `mode` (create | revise)
- `store` (`BaseStore`)

## Outputs

- Store item locator (`namespace`, `key`) + revision id in value

## Preconditions

- JWT validated; namespace authorized from token claims.
- Body passes secret/PII policy scan.
- Graph/runtime has Store configured when writes happen inside nodes.

## Postconditions

- New or revised item visible via `get`/`search` within namespace.
- Prior revision retained per policy (superseded key/value or history field)—not silent lossy overwrite without audit.
- Audit event emitted.

## Steps

1. Authorize namespace vs identity (JWT `user_id` / org roles).
2. Validate markdown size and policy.
3. Build value: `{ "Memory.md": memory_md, "status": "active", "revision": ..., provenance... }`.
4. If `revise`: load current via `store.get`; mark previous revision `superseded` in history field or write new revision key per policy.
5. `store.put(namespace, key, value)`.
6. Emit `memory.updated` (platform event; Store itself is the durability).

## Edge Cases

- Concurrent revises → append-only revision ids or optimistic `revision` check before put.
- Empty body → reject.
- Client-supplied namespace that does not match JWT → reject.

## Failure Handling

Do not leave two conflicting “active” heads without policy; retry put; surface error to caller. Never fall back to writing semantic facts into the checkpointer.
