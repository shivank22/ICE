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
| **Procedural Memory** | Governed how-to knowledge packaged as Skills (`SKILL.md` + `skill.yaml`) with a rebuildable Skill Index and Resolver (`lfs` \| `blob`)—not bare prompt strings. |
| **Episodic Memory** | Records of what happened: traces, outcomes, failures, scores (platform / observability). |
| **Memory.md** | Markdown document field inside a Store semantic value (not a reason to invent a parallel DB). |
| **Namespace** | Store isolation key (tuple of strings); preferred user scope is JWT `user_id`. |

## Skills and learning

| Term | Definition |
|------|------------|
| **Skill** | Folder under `skills/<name>/` with `SKILL.md` (LLM) + `skill.yaml` (version + metadata). |
| **SKILL.md** | LLM-facing instructions and references; not platform deploy metadata. |
| **skill.yaml** | Platform-only manifest (version, status, owner, tags, description); never injected as LLM procedural body. CI syncs it into the Skill Index. |
| **Skill Index** | Rebuildable Postgres + pgvector rows from `skill.yaml` (name, description, metadata, locator). Primary runtime input for Discovery. |
| **Skill Discovery** | pgvector search on name + descriptions **plus metadata filters**; returns Top-K **index records** (no full SKILL.md). |
| **Skill Resolver Service** | Customizable service that loads full skill packages for appropriate skills from `locator.backend`: **`lfs`** (code on the container) or **`blob`** (object store for singleton API / serverless). |
| **Skill Manifest** | API projection of `skill.yaml` via [../programs/skill-yaml-to-manifest.md](../programs/skill-yaml-to-manifest.md). |
| **Skill Pin** | Run record: `skill_id` + `version` + description + `locator` (`lfs` \| `blob`). |
| **Skill Locator** | Package origin: `lfs` \| `blob` ([contracts/skill-locator.json](contracts/skill-locator.json)). |
| **lfs** | Container-local skill/program tree the Resolver reads at runtime. |
| **blob** | Object-storage backend when skills are promoted for singleton API or serverless execution. |
| **Reflection Proposal** | Suggested skill/prompt improvement derived from episodes; never auto-applied. |
| **Promotion** | Governed move of a skill version into a higher status (`draft`→`staging`→`production`), with index re-sync and optional blob publish. |

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
