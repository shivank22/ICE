# 15 — Deployment & Evolution

## 1. Executive Summary

Deploy the architecture as replaceable services behind stable contracts. Bind cloud and frameworks after elicitation. Evolve memory, skills, and graphs independently. This pack stays vendor-neutral; ICE Azure bindings are one example.

## 2. Purpose

Guide rollout phasing and evolution without rewriting topology for each vendor.

## 3. Scope

Deployment shapes, binding examples, evolution principles. Not IaC templates.

## 4. Architecture Overview

See [../assets/diagrams/15-deployment-binding.mmd](../assets/diagrams/15-deployment-binding.mmd)

### Preferred production bindings (defaults)

| Concern | Preferred |
|---------|-----------|
| Orchestration | LangGraph durable graphs |
| Checkpoints | Postgres |
| Semantic memory | Postgres + vector |
| Procedural | Registry + FS or Blob |
| Traces | Agent-native trace platform (e.g. Langfuse) |
| Auth | OIDC/JWT |

### Example binding (ICE / Azure)

Documented in repo ADR-001: Entra ID, Azure Postgres, Service Bus, Langfuse, Azure OpenAI, Container Apps/AKS. Treat as **example**, not requirement of this skill.

## 5. Core Concepts

- **Contract first, binding second.**
- **Colocation allowed early** (orchestrator + loader) if API boundaries remain.
- **Phase delivery:** STM/checkpoints → skills HITL → semantic/episodic learning.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| Dpl1 | Do not hard-code cloud into reference docs |
| Dpl2 | Single writer for checkpoints preserved under scale-out |
| Dpl3 | Skill bodies not baked into images |
| Dpl4 | Evolve eval/reflection after durable runs exist |

## 7. Decision Rationale

Vendor lock in docs causes copy-paste architectures that fight the client’s constraints. Phasing matches dependency order: without checkpoints, HITL and learning lack foundations.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Big-bang all services | High integration risk |
| Serverless-only graph without durable store | Breaks interrupt |
| Multi-cloud identical deploy day one | Premature complexity |

## 9. Tradeoffs

Phased value vs temporary colocation debt—track debt explicitly.

## 10. Component Breakdown

Deployment units map to services in [01-architecture-overview.md](01-architecture-overview.md). Scale orchestrator horizontally by thread affinity; scale knowledge reads with replicas; keep registry promote path protected.

## 11. Sequence of Operations (suggested build order)

1. Gateway + identity + empty Orchestrator thread API  
2. Checkpoint store + STM interrupt/resume  
3. Skill registry/loader + one production skill  
4. Context assembler with policies + STM  
5. Semantic memory namespaced by user_id  
6. Traces + episodes  
7. Approval UX  
8. Reflection proposals + promotion  
9. FinOps / advanced eval  

## 12. State Changes

Platform maturity: prototype → durable HITL → multi-skill → learning loop → multi-tenant hardened.

## 13. Mermaid Diagrams

See §4.

## 14. JSON Contracts

All contracts under [contracts/](contracts/) remain stable across bindings; only locators/URIs change.

## 15. Best Practices

- Keep a Stack Binding markdown per environment.
- Version platform APIs separately from skill packages.
- Chaos-test checkpoint restore and approval resume.

## 16. Anti-patterns

- Rewriting memory model per cloud migration.
- Shipping learning loop before authz on namespaces.
- Environment-specific skill ids without manifests.

## 17. Common Mistakes

- Assuming LangGraph is the only possible orchestrator (it is the reference, not a religion).
- Skipping retention policies until storage incident.
- Treating blueprint PDF as the runtime contract.

## 18. Future Evolution

Multi-region active/active checkpoints; federated skill registries; policy-as-code continuous verification.

## 19. Related Documents

[01-architecture-overview.md](01-architecture-overview.md) · [00-index.md](00-index.md) · [SKILL.md](../SKILL.md) · ICE `docs/adr/ADR-001-vanilla-agentic-platform.md` (example binding)
