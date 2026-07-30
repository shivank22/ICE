# Algorithm — Skill Runtime Pipeline

## Purpose

Order procedural skill work so Discovery (index) feeds **records** into context, and the **Skill Resolver Service** loads full packages from **`lfs`** or **`blob`**.

## Runtime model

1. Each skill folder has **`SKILL.md`** + **`skill.yaml`** (version + metadata).
2. CI: `skill.yaml` → **Postgres + pgvector** Skill Index.
3. Discovery: pgvector on name + descriptions **+ metadata search** → Top-K **index records**.
4. Those records are **added to context**.
5. **Skill Resolver Service** (customizable) loads appropriate full packages from `locator.backend` ∈ {`lfs`, `blob`}.

## Graph phases

| Phase | Owns | Output |
|-------|------|--------|
| **1. Discover** | Skill Discovery | Top-K index records (name, description, metadata, locator) |
| **2. Assemble** | Context Assembler | Context Package with skill **records** (not full corpus) |
| **3. Resolve** | Skill Resolver Service | SkillReference[] with readable `SKILL.md` from `lfs` or `blob` |
| **4. Execute** | LangGraph nodes / tools | Tool/artifact events using resolved packages |

## Rules

1. **Context gets index records**, not full SKILL.md for every candidate.
2. **Full packages only via Skill Resolver Service** — no ad-hoc reads.
3. **Assembler does not discover** and does not resolve.
4. **Empty Discovery** → interrupt or fail closed; never mount-all; never silent drafts.
5. **Resolver is customizable** (which records to materialize, cache, authz) per use case.
6. **Backends:** `lfs` = code on the container; `blob` = object store for singleton API / serverless.

## Sequence

```text
StartRun(input)
  → Discover (Postgres/pgvector + metadata) → Top-K skill records
  → Context Assemble (include those records)
  → Skill Resolver Service → load from lfs | blob
  → Execute
```

## Related

[skill-discovery.md](skill-discovery.md) · [skill-resolve.md](skill-resolve.md) · [skill-selection.md](skill-selection.md) · [context-assembly.md](context-assembly.md) · [../references/19-skill-platform-lifecycle.md](../references/19-skill-platform-lifecycle.md)
