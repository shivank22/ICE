# 19 — Skill Platform Lifecycle

## 1. Executive Summary

Each skill is a folder with **`skill.yaml` (version + metadata)** and **`SKILL.md` (LLM)**. **CI** builds a **Postgres + pgvector Skill Index** from `skill.yaml`.

**Runtime:**

1. **pgvector search** on name + descriptions **plus metadata search/filters** → skill index records.
2. Retrieved **skill records are added to context**.
3. **Skill Resolver Service** (customizable per use case) reads the appropriate full packages from **`lfs`** (code on the container) or **`blob`** (when promoted for singleton API / serverless)—wherever `locator.backend` points.

Pipeline: [../programs/skill-runtime-pipeline.md](../programs/skill-runtime-pipeline.md). See also [06-procedural-memory-skills.md](06-procedural-memory-skills.md).

## 2. Purpose

Separate indexing/search (Postgres), short context (index records), and package load (Skill Resolver Service) so agents never put the full skill corpus into every prompt.

## 3. Scope

Package layout, yaml vs md, CI→index, Discovery, Skill Resolver Service (`lfs` \| `blob`), context assembly of records, execute. Semantic Store and episodic learning remain docs 05/07. Promotion still gated (docs 11–12).

## 4. Architecture Overview

### Package layout

```text
skills/
├── java-migration/
│   ├── SKILL.md          # LLM only
│   ├── skill.yaml        # Version + metadata → drives index
│   ├── prompts/
│   ├── docs/
│   └── scripts/
├── spring-upgrade/
│   ├── SKILL.md
│   ├── skill.yaml
│   └── ...
```

### Runtime pipeline

```text
User goal / conversation
  → Skill Discovery (pgvector on name+description + metadata filters)
       → Top-K skill index records
  → Context Assemble (add those records to context)
  → Skill Resolver Service (customizable)
       → load full packages from locator.backend:
            lfs  = skill/program code on the container
            blob = object store (singleton API / serverless)
  → Execute with resolved SKILL.md (+ package)
```

Algorithms: [../programs/skill-runtime-pipeline.md](../programs/skill-runtime-pipeline.md) · [../programs/skill-discovery.md](../programs/skill-discovery.md) · [../programs/skill-resolve.md](../programs/skill-resolve.md) · [../programs/skill-selection.md](../programs/skill-selection.md) · [../programs/skill-yaml-to-manifest.md](../programs/skill-yaml-to-manifest.md) · [../programs/skill-ci-sync.md](../programs/skill-ci-sync.md)

Diagrams: [../assets/diagrams/19-skill-platform-runtime.mmd](../assets/diagrams/19-skill-platform-runtime.mmd) · [../assets/diagrams/19-skill-ci-sync.mmd](../assets/diagrams/19-skill-ci-sync.mmd)

## 5. Core Concepts

| Artifact | Consumer | Role |
|----------|----------|------|
| **skill.yaml** | CI / index | Version + metadata → Postgres+pgvector cards; never LLM procedural body |
| **SKILL.md** | Executor via Resolver | Full instructions after resolve |
| **Skill Index** | Discovery / Context | Name, description, metadata, locator |
| **Discovery** | Orchestrator | Top-K **index records** |
| **Skill Resolver Service** | Orchestrator | Customizable load from `lfs` or `blob` |
| **lfs** | Container deploy | Skill/program code on the container filesystem |
| **blob** | Serverless / singleton API | Promoted package in object storage |

## 6. Design Decisions

| ID | Decision |
|----|----------|
| SP1 | **`skill.yaml` is required** and is the input to the Skill Index |
| SP2 | Split **SKILL.md** (LLM) vs **skill.yaml** (platform); SkillManifest is a mapped projection |
| SP3 | CI syncs index from `skill.yaml`; does not store full skill bodies as SoR in Postgres |
| SP4 | Index rows need **`index_ready`** before Discovery may return them |
| SP5 | Discovery returns **index records** (name, description, metadata), not full SKILL.md |
| SP6 | Context skill section = those **records** only |
| SP7 | Full packages are loaded only via the **Skill Resolver Service** |
| SP8 | Resolver backends: **`lfs` \| `blob`** only |
| SP9 | Resolver behavior is **customizable per use case** (which records to materialize, cache, authz) |
| SP10 | Assembler never Discovers and never invents a mount-all fallback |

## 7. Decision Rationale

Index records keep planner context small. `lfs` matches container deploys where skill code ships with the service. `blob` covers singleton API / serverless where the package is fetched at resolve time. A dedicated Resolver Service keeps load policy out of the graph and customizable.

## 8. Alternatives Considered

| Alternative | Tradeoff |
|-------------|----------|
| Full SKILL.md only in Postgres | Weak package story; scripts/docs awkward; accidental SoR |
| Put entire corpus in every prompt | Context blowup |
| Ad-hoc file reads outside Resolver | No authz, no backend switch, hard to customize |

## 9. Tradeoffs

Index must stay in sync with published packages (`index_ready`, locator). Blob adds publish/cache credentials; acceptable for serverless. Custom Resolver logic must stay policy-bound (no silent draft/mount-all).

## 10. Component Breakdown

### skill.yaml → index

CI validates yaml/md, embeds searchable text (name, description, tags), upserts [skill-index-record.json](contracts/skill-index-record.json) with description, metadata, `locator` (`lfs` \| `blob`), sets `index_ready`.

### Discovery

pgvector similarity on name + description **and** metadata filters. Returns Top-K records. See [../programs/skill-discovery.md](../programs/skill-discovery.md).

### Skill Resolver Service

Customizable service: given discovered/pinned records, chooses appropriate skills and loads full packages from `lfs` or `blob`. See [../programs/skill-resolve.md](../programs/skill-resolve.md) and [contracts/skill-locator.json](contracts/skill-locator.json).

### Context Assemble / Execute

Records → context; Resolver → full `SKILL.md` for execute.

## 11. Sequence of Operations

### Authoring / promote

1. Edit package under `skills/<id>/` (`SKILL.md` + `skill.yaml`).
2. Approval for production status as required.
3. CI → index sync (`index_ready`); for blob deploys, publish package to object store and set `locator.backend=blob`.
4. For container deploys, ship skill tree with the image/volume (`locator.backend=lfs`).

### Runtime

1. Goal submitted.
2. Discover → Top-K index records (pgvector + metadata).
3. Assemble context with those records.
4. Skill Resolver Service loads appropriate packages from `lfs` or `blob`.
5. Execute; trace pins (id, version, locator).

## 12. State Changes

| `skill.yaml` status | Index | Discovery default |
|---------------------|-------|-------------------|
| draft | optional | excluded |
| staging | indexed | soak flag |
| production | indexed | included |
| deprecated | indexed | pin only |
| archived | flagged/removed | never |

## 13. Mermaid Diagrams

See §4.

## 14. JSON / YAML Contracts

- [contracts/skill-yaml.json](contracts/skill-yaml.json)
- [contracts/skill-index-record.json](contracts/skill-index-record.json) — **runtime records**
- [contracts/skill-locator.json](contracts/skill-locator.json) — `lfs` \| `blob`
- [contracts/skill-pin.json](contracts/skill-pin.json)
- [contracts/skill-reference.json](contracts/skill-reference.json)
- [contracts/skill-manifest.json](contracts/skill-manifest.json)
- [contracts/skill.json](contracts/skill.json)

## 15. Best Practices

- Keep index **description** short and stable (card-sized).
- Full SKILL.md only via Resolver after Discovery.
- Point `locator` at `lfs` for containers; promote to `blob` for serverless/singleton API.
- Rebuild index when name/description/metadata change.

## 16. Anti-patterns

- Injecting full `skill.yaml` or entire corpus into the planner prompt.
- Discovery returning full markdown bodies.
- Editing skill text only in Postgres.
- Bypassing the Skill Resolver Service for package reads.
- Mount-all fallback when Top-K is empty.

## 17. Common Mistakes

- Treating index as full package store.
- Equating SKILL.md with skill.yaml.
- Leaving `index_ready=false` rows visible to Discovery.

## 18. Future Evolution

Multi-tenant overlays; signed blob artifacts; canary status values—same Discovery + Resolver contracts.

## 19. Related Documents

[06-procedural-memory-skills.md](06-procedural-memory-skills.md) · [08-context-construction.md](08-context-construction.md) · [11-human-approval-governance.md](11-human-approval-governance.md) · [14-security.md](14-security.md) · [langgraph-bindings.md](langgraph-bindings.md)
