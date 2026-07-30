# Glossary

Shared terminology for this Architecture Knowledge Pack. Use these terms consistently across documents and generated client artifacts.

## Core runtime

| Term | Definition |
|------|------------|
| **Agentic Orchestrator** | Control-plane service that runs durable agent workflows as LangGraph graphs (explicit state machines). |
| **StateSnapshot** | LangGraph object from `get_state` / `get_state_history` (`values`, `next`, `config`, interrupts, metadata). System of record for thread execution. |
| **Runtime State** | API **projection (DTO)** of an in-flight or paused graph—derived from `StateSnapshot` + platform metadata, not a second checkpoint store. |
| **Thread** | Durable API resource identified by `thread_id`; cursor into checkpointer-backed STM. Frontend-agnostic. |
| **Run** | One API invocation that mutates a thread—either StartRun (`input`) or ResumeRun (`command.resume`). |
| **Thread State** | Projection of conversation-scoped working memory for one durable thread (messages + channel values from `snapshot.values`). |
| **RunResult** | API response DTO for Start/Resume (status, interrupts, optional output/messages preview). |
| **Session** | Authenticated interaction window that may span one or more threads. |
| **API Operation** | Language-agnostic capability (CreateThread, StartRun, ResumeRun, GetThreadState, …) bound to HTTP/MCP paths per environment. |
| **Checkpointer** | LangGraph persistence backend for thread-scoped STM (e.g. `PostgresSaver`). |
| **Store** | LangGraph long-term memory backend for cross-thread data (e.g. `PostgresStore`). |
| **Checkpoint** | Durable serialization of graph state at a versioned step, owned by the checkpointer. |
| **Interrupt** | Controlled pause via LangGraph `interrupt(value)`, awaiting external input (usually human approval). |
| **Resume** | Continuation with `Command(resume=...)` and the same `thread_id`. |
| **Replay** | Inspection or re-execution from history via `get_state_history` / time travel; prefer forks for side effects. |
| **Context Package** | Ordered, budgeted bundle of guidance, memory, skills, and request content sent to the model. |
| **Artifact** | Versioned durable output of a skill or phase. |

## Memory domains

| Term | Definition |
|------|------------|
| **Short-Term Memory (STM)** | Thread-scoped conversation and execution state managed via graph messages/channels and **checkpointers**. |
| **Semantic Memory** | Cross-thread facts about users, orgs, or engagements in **Store**, retrieved by namespace/similarity. |
| **Procedural Memory** | Governed how-to knowledge packaged as Skills in a registry—not bare prompt strings (platform layer). |
| **Episodic Memory** | Records of what happened: traces, outcomes, failures, scores (platform / observability). |
| **Memory.md** | Markdown document field inside a Store semantic value (not a reason to invent a parallel DB). |
| **Namespace** | Store isolation key (tuple of strings); preferred user scope is JWT `user_id`. |

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
| **Evaluation** | Scored judgment of run or skill quality against criteria (platform contract). |
| **Evaluation Criteria** | Versioned metric definitions (code, LLM-as-judge, trajectory) referenced by skill manifests. |
| **LLM-as-judge** | Evaluator that uses a model + rubric to score outputs or trajectories. |
| **Trajectory eval** | Scoring of tool-call / message sequences (decomposition and tool use). |
| **Engagement** | Optional product-level unit of work (ICE example); not required by this pack. |

## Identity

| Term | Definition |
|------|------------|
| **User** | Authenticated principal represented by JWT claims. |
| **user_id** | Stable subject identifier from the token used as the default semantic namespace. |
