# Algorithm — Skill CI Sync

## Purpose

On promote/merge of skill packages, validate folders and synchronize the **PostgreSQL + pgvector** runtime index from **`skill.yaml`** (name, description, version, metadata, locator). Index is not a full package dump.

## Inputs

- Changed paths under `skills/`
- Embedding model config
- DB connection (pgvector)
- Locator policy for this deploy channel (`lfs` for container images; `blob` uri when publishing to object storage)

## Outputs

- Updated index rows for changed skills
- Pipeline pass/fail
- Optional blob publish artifacts when `locator.backend=blob`

## Preconditions

- Approval satisfied for production status bumps when required.
- Schema for `skill.yaml` and folder conventions published (`SKILL.md` + `skill.yaml` required).

## Postconditions

- Index reflects descriptions/metadata/locator for synced skills (`index_ready`).
- Skill bodies are not rewritten into Postgres as SoR.
- Locator points at `lfs` (container path) or `blob` (object uri) consistently with the deploy channel.

## Steps

1. Validate folder structure (`SKILL.md`, `skill.yaml`, optional prompts/docs/scripts).
2. Validate `SKILL.md` required sections.
3. Validate `skill.yaml` against [skill-yaml.json](../references/contracts/skill-yaml.json).
4. Run unit/integration tests for skill scripts.
5. Secret scan.
6. Dependency validation.
7. Generate embedding from searchable text (name, description, tags, summary).
8. Compute metadata fields + `locator` (`lfs` \| `blob` + uri).
9. If blob channel: publish package artifact; set locator uri/checksum.
10. Upsert [skill-index-record.json](../references/contracts/skill-index-record.json) rows.
11. Set `index_ready=true` only after embed + upsert succeed for that row; leave prior ready row queryable until cutover.
12. Soft-delete / mark archived skills as needed.

## Edge Cases

- Partial monorepo change → sync only changed skill roots.
- Embedding provider outage → fail pipeline or queue retry per policy; keep `index_ready=false` for in-flight rows.
- Status downgrade → update index filters immediately.

## Failure Handling

Leave previous index rows for unchanged skills; do not half-apply a skill row. Alert; block dependent deploys if policy ties release to index health.

## Related

[../references/19-skill-platform-lifecycle.md](../references/19-skill-platform-lifecycle.md)
