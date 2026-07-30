# Diagrams

One Mermaid source per concept. Render in any Mermaid-compatible viewer.

| File | Concept |
|------|---------|
| [01-context-layers.mmd](01-context-layers.mmd) | Platform layers |
| [01-container-overview.mmd](01-container-overview.mmd) | Service containers |
| [01-request-sequence.mmd](01-request-sequence.mmd) | Happy-path sequence |
| [02-state-model.mmd](02-state-model.mmd) | StateSnapshot SoR + DTO projections |
| [02-state-transitions.mmd](02-state-transitions.mmd) | Runtime status transitions (DTO) |
| [03-memory-domains.mmd](03-memory-domains.mmd) | Four memory domains (checkpointer/Store/index+resolver/traces) |
| [03-memory-lifecycle.mmd](03-memory-lifecycle.mmd) | Memory lifecycle |
| [04-stm-checkpoint-flow.mmd](04-stm-checkpoint-flow.mmd) | STM + auto checkpointer + interrupt/resume |
| [04-stm-state.mmd](04-stm-state.mmd) | STM states |
| [05-semantic-namespace.mmd](05-semantic-namespace.mmd) | JWT → Store namespace tuples |
| [05-semantic-write-read.mmd](05-semantic-write-read.mmd) | Store put/search |
| [06-skill-registry.mmd](06-skill-registry.mmd) | skill.yaml → CI index → Discovery → Resolver |
| [06-skill-lifecycle.mmd](06-skill-lifecycle.mmd) | Skill labels |
| [19-skill-platform-runtime.mmd](19-skill-platform-runtime.mmd) | Discovery → context records → Resolver (`lfs`\|`blob`) |
| [19-skill-ci-sync.mmd](19-skill-ci-sync.mmd) | CI validate + embed → pgvector (+ optional blob) |
| [07-episodic-to-promotion.mmd](07-episodic-to-promotion.mmd) | Learning promotion path |
| [07-episode-lifecycle.mmd](07-episode-lifecycle.mmd) | Episode states |
| [08-context-assembly.mmd](08-context-assembly.mmd) | Context pipeline order |
| [08-context-priority.mmd](08-context-priority.mmd) | Conflict priority |
| [09-checkpoint-lifecycle.mmd](09-checkpoint-lifecycle.mmd) | Checkpoint lifecycle |
| [09-interrupt-resume.mmd](09-interrupt-resume.mmd) | interrupt() + Command(resume) |
| [10-feedback-loops.mmd](10-feedback-loops.mmd) | Feedback loops |
| [10-rework-sequence.mmd](10-rework-sequence.mmd) | Rework sequence |
| [11-approval-gates.mmd](11-approval-gates.mmd) | Run vs promotion gates |
| [12-reflection-eval.mmd](12-reflection-eval.mmd) | Reflection and eval |
| [13-observability.mmd](13-observability.mmd) | Observability flow |
| [14-security-boundaries.mmd](14-security-boundaries.mmd) | Security boundaries |
| [15-deployment-binding.mmd](15-deployment-binding.mmd) | Contracts vs bindings |
| [16-api-resource-model.mmd](16-api-resource-model.mmd) | Thread/Run/Interrupt API resources |
| [16-api-interrupt-resume-flow.mmd](16-api-interrupt-resume-flow.mmd) | Any-FE interrupt → resume sequence |
| [17-trace-hierarchy.mmd](17-trace-hierarchy.mmd) | Graph + agent/component span tree |
| [17-trace-to-episode.mmd](17-trace-to-episode.mmd) | Traces → Episode → Reflection |
| [18-evaluation-flow.mmd](18-evaluation-flow.mmd) | Custom / LLM-judge / trajectory → gates |
