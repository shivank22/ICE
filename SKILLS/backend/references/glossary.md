# Glossary

Shared terminology for this Architecture Knowledge Pack. Use these terms consistently across documents and generated client artifacts.

## Core runtime

| Term | Definition |
|------|------------|
| **Agentic Orchestrator** | Control-plane service that runs durable agent workflows as explicit state machines. |
| **Runtime State** | Canonical machine-readable snapshot of an in-flight or paused graph execution. |
| **Thread State** | Conversation-scoped working memory for one durable thread (messages + channel values). |
| **Session** | Authenticated interaction window that may span one or more threads. |
| **Checkpoint** | Durable serialization of graph state at a versioned step, enabling resume/replay. |
| **Interrupt** | Controlled pause of the graph awaiting external input (usually human approval). |
| **Resume** | Continuation from a checkpoint with new external input. |
| **Replay** | Re-execution or inspection from a historical checkpoint for debug or audit. |
| **Context Package** | Ordered, budgeted bundle of guidance, memory, skills, and request content sent to the model. |
| **Artifact** | Versioned durable output of a skill or phase. |

## Memory domains

| Term | Definition |
|------|------------|
| **Short-Term Memory (STM)** | Ephemeral-to-durable conversation and execution state managed via messages and checkpointers. |
| **Semantic Memory** | Persistent facts about users, orgs, or engagements, retrieved by similarity/namespace. |
| **Procedural Memory** | Governed how-to knowledge packaged as Skills in a registry—not bare prompt strings. |
| **Episodic Memory** | Records of what happened: traces, outcomes, failures, scores. |
| **Memory.md** | Markdown document stored in the semantic memory record’s Memory column. |
| **Namespace** | Isolation key for memory records; preferred user scope is JWT `user_id`. |

## Skills and learning

| Term | Definition |
|------|------------|
| **Skill** | Architectural package: purpose, manifest, constraints, references, examples, evaluation criteria. |
| **Skill Manifest** | Machine-readable metadata for discovery, versioning, compatibility, and mount. |
| **Skill Registry** | System of record for procedural memory versions and labels (draft/staging/production). |
| **Skill Loader** | Authority that resolves and mounts production skills into the execution environment. |
| **Reflection Proposal** | Suggested skill/prompt improvement derived from episodes; never auto-applied. |
| **Promotion** | Governed move of a skill version into a higher label (e.g. staging → production). |

## Governance and observation

| Term | Definition |
|------|------------|
| **Policy** | Explicit rule constraining agent, tool, memory, or promotion behavior. |
| **Approval** | Recorded human or policy decision that unblocks an interrupt or promotion. |
| **Trace** | Structured record of spans/events for a run. |
| **Evaluation** | Scored judgment of run or skill quality against criteria. |
| **Engagement** | Optional product-level unit of work (ICE example); not required by this pack. |

## Identity

| Term | Definition |
|------|------------|
| **User** | Authenticated principal represented by JWT claims. |
| **user_id** | Stable subject identifier from the token used as the default semantic namespace. |
