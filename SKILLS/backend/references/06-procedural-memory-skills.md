# 06 — Procedural Memory & Skills

## 1. Executive Summary

Procedural Memory is a **governed Skill Registry**. A Skill is an architectural package—not a free-floating prompt. Skills are versioned, labeled (draft/staging/production), stored in **local filesystem (e.g. LangGraph backend)** or **object/Blob storage**, and resolved into runtime only through a **Skill Loader**.

## 2. Purpose

Make “how the agent should work” explicit, reviewable, compatible, and promotable without silent drift.

## 3. Scope

Skill package structure, manifest, lifecycle, discovery, selection, composition, storage backends, governance. Runtime STM and semantic facts are out of scope.

## 4. Architecture Overview

See [../assets/diagrams/06-skill-registry.mmd](../assets/diagrams/06-skill-registry.mmd) and [../assets/diagrams/06-skill-lifecycle.mmd](../assets/diagrams/06-skill-lifecycle.mmd)

```
Skill Package
├── Manifest (metadata, version, compatibility)
├── Purpose / Scope
├── Constraints & Policies
├── References & Algorithms
├── Examples
├── Evaluation Criteria
└── Optional assets
```

## 5. Core Concepts

- **Manifest:** discovery and mount contract.
- **Label:** draft | staging | production (or equivalent).
- **Compatibility:** runtime/graph/API version constraints.
- **Loader:** sole authority to resolve production skills into the execution environment.
- **Composition:** orchestrated use of multiple skills with explicit dependency order.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| P1 | Skills are packages with manifests, not prompt-only strings |
| P2 | Storage backend may be FS or Blob; registry metadata is mandatory either way |
| P3 | Production label changes require Approval |
| P4 | Runners/images never bake skill bodies; mount/resolve at execution |
| P5 | Episodic reflection may only create draft proposals |

## 7. Decision Rationale

Packages enable evaluation criteria, dependencies, and versioning. Separating storage from registry metadata keeps Blob/FS swappable. Mount-at-runtime prevents stale images. Gated labels protect production behavior.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Prompt files in git only | Weak runtime resolution and label model |
| Skills baked into container images | Slow iteration; environment drift |
| Unversioned shared prompt store | No rollback or compatibility |

## 9. Tradeoffs

Registry + loader adds a hop before execution. Benefit: governance and environment parity.

## 10. Component Breakdown

### Skill Registry

- **Purpose:** System of record for skill versions and labels.
- **Responsibilities:** Versioning, metadata, dependency graph, deprecation.
- **Non-responsibilities:** Executing skills; storing semantic user facts.
- **Inputs:** Publish requests, label changes, queries.
- **Outputs:** Manifests, package locators, audit events.
- **Dependencies:** Object store or FS; Approval service for promotions.
- **Lifecycle:** draft → staging → production → deprecated → archived.
- **Failure Modes:** broken dependencies, invalid manifest, conflicting labels.
- **Recovery:** Reject publish; keep previous production pointer.
- **Security:** Role-gated publish/promote; signed artifacts optional.
- **Scalability:** Content-addressed blobs; CDN/cache for hot production skills.

### Skill Loader

- **Purpose:** Resolve and mount skills for a run.
- **Responsibilities:** Fetch production (or pinned) versions; verify checksums; expose to runtime.
- **Non-responsibilities:** Authoring content; approving promotions.
- **Inputs:** skill ids, label/pin, run identity.
- **Outputs:** Mounted skill tree / in-memory package set.
- **Failure Modes:** missing blob, checksum mismatch.
- **Recovery:** Fail the run phase; do not fall back to arbitrary draft silently.
- **Security:** Least privilege credentials for blob/FS read.
- **Scalability:** Cache by content hash per node.

## 11. Sequence of Operations

1. Author creates draft Skill Package + Manifest.
2. Validation (schema, deps, eval criteria present).
3. Optional staging soak with Evaluation.
4. Approval promotes to production.
5. At run: Loader resolves ids → mounts → Orchestrator uses constraints in context.
6. Deprecation: label move; dependents warned.

Algorithms: [../programs/skill-discovery.md](../programs/skill-discovery.md) · [../programs/skill-selection.md](../programs/skill-selection.md) · [../programs/skill-composition.md](../programs/skill-composition.md) · [../programs/learning-promotion.md](../programs/learning-promotion.md)

## 12. State Changes

| Label | Meaning |
|-------|---------|
| draft | Editable, not for prod runs |
| staging | Candidate for soak/eval |
| production | Default resolve target |
| deprecated | Resolvable only if pinned |
| archived | Not resolvable |

## 13. Mermaid Diagrams

Linked in §4.

## 14. JSON Contracts

- [contracts/skill.json](contracts/skill.json)
- [contracts/skill-manifest.json](contracts/skill-manifest.json)
- [contracts/procedural-memory.json](contracts/procedural-memory.json)

## 15. Best Practices

- Require evaluation criteria before staging.
- Pin skill versions on regulated runs.
- Keep examples inside the package for agent grounding.

## 16. Anti-patterns

- “Just update the prompt in Langfuse/prod” without version diff.
- Procedural instructions living only in semantic Memory.md.
- Loader falling back to latest draft on miss.

## 17. Common Mistakes

- Equating SKILL.md entrypoint with the entire skill package.
- Missing compatibility ranges.
- Circular skill dependencies.

## 18. Future Evolution

Signed skill provenance, multi-tenant registries, automatic canary labels.

## 19. Related Documents

[03-memory-architecture.md](03-memory-architecture.md) · [07-episodic-memory.md](07-episodic-memory.md) · [11-human-approval-governance.md](11-human-approval-governance.md) · [12-reflection-evaluation.md](12-reflection-evaluation.md)
