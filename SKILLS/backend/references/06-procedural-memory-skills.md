# 06 — Procedural Memory & Skills

## 1. Executive Summary

Procedural Memory is a **governed skill platform** on top of LangGraph. Each skill is a folder with **`skill.yaml` (version + metadata)** and **`SKILL.md` (LLM)**. **CI** builds a **Postgres + pgvector** index from `skill.yaml`. At runtime, Discovery searches the index; **skill records go into context**; the **Skill Resolver Service** loads full packages from **`lfs`** (container) or **`blob`** (serverless / singleton API).

Full lifecycle: **[19-skill-platform-lifecycle.md](19-skill-platform-lifecycle.md)**. Pipeline: [../programs/skill-runtime-pipeline.md](../programs/skill-runtime-pipeline.md).

## 2. Purpose

Make “how the agent should work” explicit, reviewable, searchable, and promotable without silent drift or putting full skill bodies into every prompt.

## 3. Scope

Package layout, yaml vs md roles, CI index sync, Discovery, Skill Resolver Service, governance. Semantic facts and episodic learning are out of scope (docs 05, 07).

## 4. Architecture Overview

See [../assets/diagrams/06-skill-registry.mmd](../assets/diagrams/06-skill-registry.mmd) · [../assets/diagrams/06-skill-lifecycle.mmd](../assets/diagrams/06-skill-lifecycle.mmd) · [../assets/diagrams/19-skill-platform-runtime.mmd](../assets/diagrams/19-skill-platform-runtime.mmd)

```text
skills/<skill-id>/
├── SKILL.md       # LLM only
├── skill.yaml     # Version + metadata (platform)
├── prompts/
├── docs/
└── scripts/
```

## 5. Core Concepts

- **SKILL.md / skill.yaml split:** model instructions vs platform metadata.
- **Runtime index:** Postgres + pgvector; rebuildable from `skill.yaml`.
- **Discovery:** pgvector on name + descriptions + metadata filters → index records for context.
- **Skill Resolver Service:** customizable load of full packages from `lfs` or `blob`.
- **Status:** draft | staging | production | deprecated | archived (in `skill.yaml`, synced to index).

## 6. Design Decisions

| ID | Decision |
|----|----------|
| P1 | Skills are packages with `SKILL.md` + `skill.yaml`, not prompt-only strings |
| P2 | CI builds the Skill Index from **`skill.yaml` only** (cards/metadata); not full bodies as SoR |
| P3 | Production status changes require Approval → promote → CI re-index (and blob publish when used) |
| P4 | Full packages are read only through the **Skill Resolver Service** (`lfs` \| `blob`) |
| P5 | Episodic reflection may only propose changes; never write production skill text silently |
| P6 | Discovery returns **index records**; Resolver loads appropriate full packages |

## 7. Decision Rationale

Splitting yaml/md keeps ops metadata out of the model. A disposable index enables fast semantic + metadata search. Resolver isolation lets teams customize load policy (container vs serverless) without changing Discovery or context contracts.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| DB-held skill bodies as SoR | Weak review; hard package story |
| Entire corpus in every prompt | Context blowup |
| Ad-hoc filesystem reads outside Resolver | No consistent authz or backend switch |

## 9. Tradeoffs

CI/index correctness vs latency; blob publish complexity for serverless vs simpler `lfs` on containers.

## 10. Component Breakdown

### Skill packages

- **Purpose:** SoR for skill content (`SKILL.md` + assets) with platform metadata in `skill.yaml`.
- **Non-responsibilities:** Serving vector search.

### CI / Skill Lifecycle

- Validate structure, md, yaml, tests, secrets, deps → embed → sync pgvector.
- See [../programs/skill-ci-sync.md](../programs/skill-ci-sync.md).

### Skill index (Postgres + pgvector)

- Searchable name, description, metadata, locator, embeddings.
- Rebuildable from `skill.yaml`.

### Skill Discovery

- Top-K index records from goal/conversation. [../programs/skill-discovery.md](../programs/skill-discovery.md)

### Skill Resolver Service

- Customizable: records → load from `lfs` or `blob` → SkillReference. [../programs/skill-resolve.md](../programs/skill-resolve.md)

### Context / Execute

- Index records in context; full SKILL.md after resolve.

## 11. Sequence of Operations

1. Author package under `skills/<id>/`.
2. Approval for production status as required; promote.
3. CI validates + syncs index (`index_ready`); set locator to `lfs` or publish `blob`.
4. Runtime: Discover → context (records) → Skill Resolver Service → Execute.
5. Reflection → proposal only.

Also: [../programs/skill-selection.md](../programs/skill-selection.md) · [../programs/skill-composition.md](../programs/skill-composition.md) · [../programs/learning-promotion.md](../programs/learning-promotion.md)

## 12. State Changes

| Status | Meaning |
|--------|---------|
| draft | Editable; not for default Discovery |
| staging | Soak/eval candidate |
| production | Default Discovery target |
| deprecated | Pin only |
| archived | Not resolvable |

## 13. Mermaid Diagrams

Linked in §4 and doc 19.

## 14. JSON Contracts

- [contracts/skill-yaml.json](contracts/skill-yaml.json)
- [contracts/skill-manifest.json](contracts/skill-manifest.json) — mapped via [../programs/skill-yaml-to-manifest.md](../programs/skill-yaml-to-manifest.md)
- [contracts/skill-pin.json](contracts/skill-pin.json)
- [contracts/skill-reference.json](contracts/skill-reference.json)
- [contracts/skill-index-record.json](contracts/skill-index-record.json)
- [contracts/skill-locator.json](contracts/skill-locator.json)
- [contracts/skill.json](contracts/skill.json)
- [contracts/procedural-memory.json](contracts/procedural-memory.json)

## 15. Best Practices

- Require evaluation criteria before staging (doc 18).
- Pin `skill_id` + `version` + `locator` on regulated runs.
- Keep Discovery cards tiny; full SKILL.md via Resolver only.

## 16. Anti-patterns

- Editing skill text in Postgres or the trace store.
- Injecting `skill.yaml` into the LLM as instructions.
- Resolver/Assembler falling back to draft on miss or mount-all.
- Discovery returning full markdown.

## 17. Common Mistakes

- Equating SKILL.md with the platform manifest.
- Treating the index as the package store.
- Circular skill dependencies without composition checks.

## 18. Future Evolution

Federated skill feeds with the same Discovery + Resolver contracts; signed blob artifacts; canary status values.

## 19. Related Documents

[19-skill-platform-lifecycle.md](19-skill-platform-lifecycle.md) · [03-memory-architecture.md](03-memory-architecture.md) · [08-context-construction.md](08-context-construction.md) · [07-episodic-memory.md](07-episodic-memory.md) · [11-human-approval-governance.md](11-human-approval-governance.md) · [12-reflection-evaluation.md](12-reflection-evaluation.md)
