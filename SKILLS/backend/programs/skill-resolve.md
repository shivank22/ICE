# Algorithm — Skill Resolve (Skill Resolver Service)

## Purpose

**Skill Resolver Service:** load full skill packages (`SKILL.md` + package tree) for the skills that should run. Backend is wherever the locator points:

| Backend | When |
|---------|------|
| **`lfs`** | Skill/program code on the **container** (default for containerized agents) |
| **`blob`** | Package promoted to **object storage** for singleton API or **serverless** execution |

This service is **customizable per use case** (selection policy among Discovery hits, cache, authz, materialization). No semantic search. No LLM required.

## Inputs

- Discovered or pinned skill records (ids, versions, locators)
- Use-case policy hooks (which records are “appropriate” to materialize)
- Credentials for blob when needed

## Outputs

- `SkillReference[]` with `description` (from index), `locator`, `resolved_from` (`lfs` \| `blob`), `skill_md_path`

## Preconditions

- Authz already passed for the skill status/org.
- Index (or pin) supplies a valid `locator` with `backend` ∈ {`lfs`, `blob`}.

## Postconditions

- `SKILL.md` readable at `skill_md_path` for execute.
- Description remains the index card (do not replace context cards with full markdown dumps).

## Steps

1. For each candidate record, apply **use-case policy** (must-resolve vs optional; pin overrides; risk gates).
2. Read `locator.backend` / `uri` / `version` / optional `checksum`.
3. Dispatch:
   - **`lfs`** — open container path at `uri`; fail if absent.
   - **`blob`** — download/materialize package by uri/checksum into a cache dir; verify checksum when present.
4. Verify `skill.yaml` name/version match the pin/record when required.
5. Return SkillReference; do not inject full SKILL.md into Discovery/shortlist context.

## Edge Cases

- Cache hit for same blob uri+version/checksum → reuse.
- Checksum mismatch → fail closed; do not run.
- Index locator stale vs package → fail or re-index; do not invent alternate backends.

## Failure Handling

Default: fail the run (or the required skill) if a needed package cannot be resolved. No silent substitute skills. Customization may skip **optional** skills when policy allows.

## Related

[skill-discovery.md](skill-discovery.md) · [skill-selection.md](skill-selection.md) · [skill-runtime-pipeline.md](skill-runtime-pipeline.md) · [../references/contracts/skill-locator.json](../references/contracts/skill-locator.json)
