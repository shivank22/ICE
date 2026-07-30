# Algorithm — Memory Update (Semantic)

## Purpose

Create a new semantic memory revision for an authorized namespace.

## Inputs

- `identity`
- `namespace`
- `memory_md` (markdown body)
- `metadata` (tags, source_thread_id, source_skill_id)
- `mode` (create | revise)

## Outputs

- `memory_record` (new revision id)

## Preconditions

- JWT validated; namespace authorized.
- Body passes secret/PII policy scan.

## Postconditions

- Prior active revision marked superseded (if revise).
- Embed job enqueued.
- Audit event emitted.

## Steps

1. Authorize namespace vs identity.
2. Validate markdown size and policy.
3. Insert new row/revision with status `active`.
4. Mark previous revision `superseded`.
5. Enqueue embedding.
6. Emit `memory.updated`.

## Edge Cases

- Concurrent revises → use optimistic version or append-only conflict resolution.
- Empty body → reject.

## Failure Handling

Transaction rollback on insert failure; do not leave two actives.
