# Algorithm — Skill Discovery

## Purpose

Find **Top-K skills** matching a task via the **Postgres + pgvector** index: similarity search on **name + descriptions**, combined with **metadata filters/search**. Returns **index records** for context. Does not load full `SKILL.md`. Does not call the LLM. Does not read `lfs` / `blob`.

## Inputs

- `intent` / user goal / conversation slice
- `status` filter (default `production`)
- `filters` (tags, owner, runtime compatibility, other metadata)
- `org_id` from JWT (for `org_allowlist`)

## Outputs

- Ranked list of skill index records: `{ skill_id, name, description, version, status, tags?, locator, ... }`
- Telemetry scores optional

## Preconditions

- Skill index reachable; rows built from `skill.yaml` by CI.
- Embedding model available (or lexical fallback if policy allows).

## Postconditions

- Only `index_ready=true` rows; status/org/metadata filters applied.
- **Records come from the index** — this is what context assembly uses.
- No full skill bodies in the response.

## Steps

1. Build query text from goal + relevant conversation turns.
2. Embed query; **pgvector** similarity search over name + description embeddings.
3. Apply **metadata search/filters**: `index_ready`, status, tags, compatibility, org_allowlist, other indexed fields.
4. Rank; take Top-K.
5. Return index records → Context Assembler.
6. Hand off selected/appropriate ids to the **Skill Resolver Service** for package load.

## Edge Cases

- No production match → empty list; do not return all skills; do not return drafts.
- Deprecated excluded unless pinned.
- K too large → cap per context budget.

## Failure Handling

Fail closed if index unavailable when discovery is required. Do not scan container trees or blob buckets as Discovery fallback.

## Related

[skill-resolve.md](skill-resolve.md) · [skill-runtime-pipeline.md](skill-runtime-pipeline.md) · [../references/19-skill-platform-lifecycle.md](../references/19-skill-platform-lifecycle.md)
