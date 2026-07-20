# Vanilla Agentic Framework — Architecture

## Architecture (Microservices)

> **Scope of this document:** Architecture only. No application code yet.  
> Core patterns: Deep Agents, LangGraph, a centralized skill registry, and ephemeral runners with skill mounting. The framework is domain-agnostic — the example skills used throughout are illustrative and pluggable.

---

## Goal

The **Vanilla Agentic Framework** is an interactive enterprise platform for running **agentic workflows with best practices built in**: durable orchestration, centralized skills, ephemeral execution, human-in-the-loop gates, cost accounting, and stakeholder engagement.

Users open an **engagement** (a unit of work identified by an Engagement ID) and work through a guided flow of skills. The reference pipeline uses four neutral example skills:

1. **Research** — gather and confirm context through a guided wizard → **Research Findings Artifact**
2. **Planning** — analyze findings and propose a plan → **Plan & Recommendation Artifact**
3. **Execution** — carry out the approved plan → **Execution Report Artifact**
4. **Reporting** — summarize outcomes and learnings → **Summary Artifact**
5. Compose the final **Final Deliverable Document** from those artifacts

**There is no Merge Request (MR) in this process.** Deliverables are skill artifacts and the Final Deliverable Document.

### Platforms (physical)

| Platform | Role |
|----------|------|
| **Access Platform** | Interactive UI (guided wizard), MCP, CLI + API Gateway |
| **Skill & Knowledge Platform** | Skills, org memory, skill registry (Langfuse), governance |
| **Execution Platform** | LangGraph + Deep Agents control plane + ephemeral runners |

### Logical layers / frameworks

| Layer / Framework | Concern |
|-------------------|---------|
| **Connectivity Layer** | Clients + Gateway + SSE |
| **Context Layer** | Skills, prompts, semantic + episodic memory |
| **Orchestrator Framework** | Jobs, LangGraph, Deep Agents, Skill Loader |
| **Execution Framework** | Ephemeral runners, provisioner, phase work |
| **Evaluation Framework** | Tracing + **FinOps Engine** (agent cost per run) |

**Cross-cut:** **Adaption Engine** — engagement tracks + emails to stakeholders.

---

## System Overview

### Architecture diagrams (draw.io)

| # | Diagram | Notes |
|---|---------|-------|
| 01 | [`docs/01-overall-process.drawio`](docs/01-overall-process.drawio) / [`ICE.drawio`](ICE.drawio) | Full layered architecture — skills → artifacts → Final Deliverable Document, no MR ([notes](docs/01-overall-process.md)) |
| 02 | [`docs/02-microservices-map.drawio`](docs/02-microservices-map.drawio) | All microservices + gateway ([notes](docs/02-microservices-map.md)) |
| 03 | [`docs/03-system-overview.drawio`](docs/03-system-overview.drawio) | Platforms, engines, runners ([notes](docs/03-system-overview.md)) |
| 04 | [`docs/04-skill-knowledge-platform.drawio`](docs/04-skill-knowledge-platform.drawio) | Skills, memory, update loop ([notes](docs/04-skill-knowledge-platform.md)) |
| 05 | [`docs/05-execution-runners.drawio`](docs/05-execution-runners.drawio) | skill-loader → provisioner → mount → agents ([notes](docs/05-execution-runners.md)) |
| 06 | [`docs/06-discovery-wizard.drawio`](docs/06-discovery-wizard.drawio) | Interactive guided wizard ([notes](docs/06-discovery-wizard.md)) |
| 07 | [`docs/07-skill-artifacts.drawio`](docs/07-skill-artifacts.drawio) | Artifacts → Final Deliverable Document ([notes](docs/07-skill-artifacts.md)) |
| 08 | [`docs/08-finops-engine.drawio`](docs/08-finops-engine.drawio) | Agent cost per run ([notes](docs/08-finops-engine.md)) |
| 09 | [`docs/09-adaption-engine.drawio`](docs/09-adaption-engine.drawio) | Tracks + email stakeholders ([notes](docs/09-adaption-engine.md)) |
| 10 | [`docs/10-logical-fabrics.drawio`](docs/10-logical-fabrics.drawio) | Five layers/frameworks ([notes](docs/10-logical-fabrics.md)) |

Index: [`docs/README.md`](docs/README.md)

```mermaid
flowchart TD
    subgraph access [Access Platform]
        UI["Web UI - guided wizard"]
        MCP["MCP"]
        CLI["CLI"]
    end

    GW["API Gateway"]

    subgraph knowledge [Skill and Knowledge Platform]
        KS["knowledge-service"]
        PG[("Postgres + pgvector")]
        LF[("Langfuse - Skill Registry + Tracing")]
    end

    subgraph execution [Execution Platform]
        Job["job-service"]
        Orch["agent-orchestrator\nLangGraph + Deep Agents"]
        Loader["skill-loader"]
        Prov["sandbox-provisioner"]
    end

    subgraph engines [Engines]
        FinOps["finops-engine"]
        Adapt["adaption-engine"]
    end

    UI --> GW
    MCP --> GW
    CLI --> GW
    GW --> Job
    GW --> KS
    GW --> FinOps
    GW --> Adapt

    Job --> Orch
    Orch --> Loader
    Loader --> KS
    KS --> PG
    KS --> LF
    Loader --> Prov

    subgraph runners [Ephemeral Runners]
        R["Research"]
        E["Execution"]
        Rep["Reporting"]
        C["Optional Custom"]
    end

    Prov -->|"spawn"| runners
    Loader -->|"mount centralized skills"| runners
    Orch -->|"agents use mounted skills"| runners
    runners --> Ext["Enterprise systems / APIs / data sources"]
    runners -.-> LF
    Orch -->|"episodes"| KS
    LF --> FinOps
    Job --> FinOps
    Job -->|"lifecycle events"| Adapt
    Adapt -->|"email"| Owners["Stakeholders"]
```
---

## Microservice Map

The framework is a **microservice architecture**. Each service below is an independently deployable unit with a clear API and ownership boundary. Clients never call execution services directly — only via **gateway**.

```mermaid
flowchart TB
    subgraph clients [Clients]
        Web[web]
        Mcp[mcp]
        Cli[cli]
    end

    Gw[gateway]

    subgraph ms [Deployable Microservices]
        Job[job-service]
        Orch[agent-orchestrator]
        Loader[skill-loader]
        Know[knowledge-service]
        Prov[sandbox-provisioner]
        FinOps[finops-engine]
        Adapt[adaption-engine]
    end

    Shared[(Postgres + pgvector)]
    LF[(Langfuse)]
    Bus[(Message bus)]
    Runners[ephemeral runners]

    clients --> Gw
    Gw --> Job
    Gw --> Know
    Gw --> FinOps
    Gw --> Adapt

    Job --> Orch
    Job --> Bus
    Orch --> Loader
    Loader --> Know
    Know --> Shared
    Know --> LF
    Loader --> Prov
    Loader -->|"mount centralized skills"| Runners
    Prov --> Runners
    Orch -->|"agents use mounted skills"| Runners
    Bus --> Adapt
    Orch -.-> FinOps
    LF --> FinOps
```

**skill-loader** is the mount hub: it resolves skills from the central registry (via knowledge-service / Langfuse), asks **sandbox-provisioner** to spawn runners, and **mounts** those skills onto **ephemeral runners** so agents can use them. Orchestrator does not inject skills into runners directly.
### Service catalogue

| Microservice | Platform | Responsibilities | Primary data |
|--------------|----------|------------------|--------------|
| **gateway** | Access | Auth (e.g. Entra ID), RBAC, REST + SSE routing, rate limits | Session / auth only |
| **web** | Access | Interactive guided wizard UI | None (API client) |
| **mcp** | Access | MCP tools → Gateway parity | None |
| **cli** | Access | Scriptable / CI client | None |
| **knowledge-service** | Skill & Knowledge | Engagement records, skills metadata, semantic + episodic memory, change-request review | Postgres + Langfuse pointers |
| **job-service** | Execution | Engagement job lifecycle, hybrid phase skip/re-run, HITL state, event publish | Job + plan state |
| **agent-orchestrator** | Execution | LangGraph state machine, Deep Agents; agents **consume** skills already mounted on runners | LangGraph checkpoints |
| **skill-loader** | Execution | **Central mount authority** — resolve production skills/facts/episodes; talk to sandbox-provisioner; mount skill bundles onto ephemeral runners for agents | Transient bundles + mount records |
| **sandbox-provisioner** | Execution | Create/destroy ephemeral runners; apply mount instructions from skill-loader | Runner refs / TTL |
| **finops-engine** | Evaluation | Agent + runner cost per run; rollups by engagement/skill/day | `cost_record` |
| **adaption-engine** | Engagement | Engagement tracks; email stakeholders on lifecycle events | `engagement_track`, `email_event` |

### Shared infrastructure

- **Postgres + pgvector** — structured domain data + embeddings
- **Langfuse** — procedural skill prompts (`draft` / `staging` / `production`) + tracing
- **Message bus** — durable job/event fan-out (e.g. Azure Service Bus)
- **Runner workspace store** — per-job share for skill artifacts (e.g. Azure Files / PVC)

### Design seams

- **SandboxBackendProtocol** — local Docker first; swap to managed K8s runners without changing agent code
- **Skill mount contract** — centralized skills are never baked into images. **skill-loader** resolves them and mounts them onto ephemeral runners (via sandbox-provisioner). Agents only use skills that skill-loader has mounted for that run.
- **Gateway as single edge** — UI / MCP / CLI stay thin and at parity

---

## Logical Architecture — Layer Mapping

| Layer / Framework | Microservices |
|-------------------|---------------|
| Connectivity | gateway, web, mcp, cli, adaption-engine (outbound email) |
| Context | knowledge-service, Langfuse prompts, Postgres memory |
| Orchestrator | job-service, agent-orchestrator |
| Execution | sandbox-provisioner, ephemeral runners, **skill-loader** (mount into runners) |
| Evaluation | Langfuse traces, finops-engine, optional validation hooks |

---

## Core Domain Model

Everything is anchored on an **Engagement ID** — a generic unit of work, not a git repo.

| Entity | Description |
|--------|-------------|
| **Engagement** | id, name, stakeholder contacts, priority, objective |
| **Guided Session** | Wizard state: user inputs + agent findings + confidence |
| **Skill Artifact** | Versioned output of each skill run (findings, plan, execution report, summary) |
| **Plan & Recommendation** | Scored options → recommended course of action |
| **Final Deliverable Document** | **Final deliverable** — composed from skill artifacts (no MR) |
| **Episode** | Past run outcomes for learning / few-shot retrieval |
| **Cost Record** | Per job/phase/agent: tokens, model $, runner $, totals |
| **Engagement Track** | Per engagement: stage, stakeholders, SLA clocks, next nudge |
| **Email Event** | Audit of Adaption Engine sends |

### Logical data ownership

| Service | Tables / stores (logical) |
|---------|---------------------------|
| knowledge-service | `engagement`, `guided_session`, `skill_meta`, `org_asset`, `episode`, `change_request` |
| job-service | `job`, `skill_artifact`, `plan_recommendation`, `final_deliverable_document` |
| finops-engine | `cost_record` |
| adaption-engine | `engagement_track`, `email_event` |
| agent-orchestrator | LangGraph checkpoints (separate store) |

---

# PART A — Access Platform

Thin clients over **gateway**. No business logic in clients.

```mermaid
flowchart LR
    subgraph clients [Clients]
        UI["web - guided wizard\n- open engagement\n- research collaboration\n- approve plan\n- FinOps + engagement views"]
        MCP["mcp - tools map 1:1 to Gateway"]
        CLI["cli - scriptable parity"]
    end
    clients --> GW["gateway"]
```

### Starter Gateway routes (engagement-centric)

- `POST /engagements/{id}/research` — start / continue the guided Research wizard
- `GET /engagements/{id}/findings` — confirmed research findings
- `POST /engagements/{id}/plan` — run Planning
- `POST /engagements/{id}/approve` — HITL gate on the plan
- `POST /engagements/{id}/execute` — Execution
- `POST /engagements/{id}/report` — Reporting → Summary Artifact
- `GET /engagements/{id}/jobs/{job_id}/artifacts` — list skill artifacts
- `GET /engagements/{id}/jobs/{job_id}/artifacts/{artifact_id}` — fetch artifact
- `GET /engagements/{id}/jobs/{job_id}/final-deliverable` — final composed document
- `GET /engagements/{id}/jobs/{job_id}` — status
- `GET /engagements/{id}/jobs/{job_id}/events` — SSE progress
- `GET /engagements/{id}/costs` — FinOps rollup for the engagement
- `GET /engagements/{id}/track` — Adaption track status

RBAC roles (illustrative): `viewer`, `operator`, `skill-author`, `skill-reviewer`, `admin`, `finops-viewer`.

---

# PART B — Skill & Knowledge Platform

Procedural skill content lives in **Langfuse Prompt Management**. Metadata, org facts, episodes, and governance live in **Postgres + pgvector** behind **knowledge-service**.

```mermaid
flowchart TD
    Agents["agent-orchestrator / runners"]
    API["knowledge-service"]
    PG[("Postgres + pgvector")]
    LF[("Langfuse production skills")]

    Agents -->|"retrieve skills + facts + episodes"| API
    Agents -->|"write episode"| API
    API --> PG
    API -->|"fetch prod prompts"| LF
    PG --> Reflect["Reflection"]
    Reflect -->|"change_request"| Review["Human reviewer HITL"]
    Review -->|"approve skill"| LF
    Review -->|"approve fact"| PG
```

## B1. Four example skills (procedural)

| Skill | Purpose | Artifact produced | Mounted into |
|-------|---------|-------------------|--------------|
| **1. Research** | Guided gathering and confirmation of context for the engagement | Research Findings Artifact | Research runner |
| **2. Planning** | Analyze findings, score options, recommend a course of action | Plan & Recommendation Artifact | Orchestrator / planning path |
| **3. Execution** | Carry out the approved plan against enterprise systems | Execution Report Artifact | Execution runner |
| **4. Reporting** | Summarize outcomes, metrics, and learnings | Summary Artifact | Reporting runner |

**Final composition (not a skill mount):** Final Deliverable Document — assembled from the four skill artifacts after the pipeline (or after the last executed skill in a hybrid path).

Optional secondary skills can be added per domain (e.g. a code-change skill emitting its own artifact). Still **no MR**.

## B2. Three memory types

| Memory | What | Store |
|--------|------|-------|
| **Procedural** | How to research / plan / execute / report | Langfuse (`production` label) |
| **Semantic** | Org facts: standards, catalogs, policies, reference data | Postgres + embeddings |
| **Episodic** | Past runs: scores, outcomes, failures | Postgres + embeddings |

## B3. Skill update loop

Completed jobs write **episodes** → reflection opens **change_request** → skill-reviewer HITL → publish to Langfuse or update semantic facts. Rollback = re-point Langfuse `production` label.

---

# PART C — Execution Platform

## C1. Job lifecycle (hybrid)

Default pipeline: **Research → Planning → HITL → Execution → Reporting**. Skills may be **re-run** or **skipped** when prior outputs remain valid.

```mermaid
flowchart TD
    Start([User opens an engagement]) --> Wizard["Guided Wizard - Skill 1: Research"]
    Wizard --> A1["Artifact: Research Findings"]
    A1 --> Plan["Planning - Skill 2"]
    Plan --> A2["Artifact: Plan and Recommendation"]
    A2 --> HITL{"HITL approve plan artifact?"}
    HITL -->|"revise"| Wizard
    HITL -->|"approve"| Exec["Execution - Skill 3"]
    Exec --> A3["Artifact: Execution Report"]
    A3 --> Report["Reporting - Skill 4"]
    Report --> A4["Artifact: Summary"]
    A4 --> Compose["Compose Final Deliverable Document"]
    A1 --> Compose
    A2 --> Compose
    A3 --> Compose
    Compose --> FDD["Final deliverable: Final Deliverable Document"]
    FDD --> Done([Complete])
    Done --> Episode["Write episode"]
    Done --> Cost["FinOps cost_record"]
    Done --> Track["Adaption Engine update track"]
```

Primary human gate: **after Planning**, before irreversible execution.

**Outputs (no MR):** each completed skill persists a **skill artifact**. After Reporting (or when the approved path completes), the platform **composes the Final Deliverable Document** from all skill artifacts. There is **no Merge Request / PR** in this process.

## C2. Guided wizard (interactive)

Research is a **guided collaboration**, not a silent batch pull:

1. User opens an engagement on the platform
2. Agent and user walk through the relevant context step by step
3. Agent may enrich with live checks / APIs when available
4. User confirms the findings → persisted as **Research Findings Artifact** → input to Planning

Wizard progress is checkpointed in LangGraph; UI receives SSE updates.

## C2b. Skill artifacts & Final Deliverable Document

| Skill / step | Artifact |
|--------------|----------|
| Research | Research Findings Artifact |
| Planning | Plan & Recommendation Artifact |
| Execution | Execution Report Artifact |
| Reporting | Summary Artifact |
| **Final composition** | **Final Deliverable Document** |

```mermaid
flowchart LR
    S1["Skill 1"] --> A1["Findings"]
    S2["Skill 2"] --> A2["Plan"]
    S3["Skill 3"] --> A3["Execution Report"]
    S4["Skill 4"] --> A4["Summary"]
    A1 --> FDD["Final Deliverable Document"]
    A2 --> FDD
    A3 --> FDD
    A4 --> FDD
```

Artifact metadata lives with job-service / knowledge-service; payload in workspace/object store. The Final Deliverable Document is a first-class downloadable/viewable deliverable in the UI — **not** a git merge.

## C3. Ephemeral runners + skill mounting

**Control plane (always-on):** gateway edge → job-service, agent-orchestrator, **skill-loader**, sandbox-provisioner, credentials. Never runs untrusted commands itself.

**Data plane (ephemeral):** runners per phase; **centralized skills mounted by skill-loader** at start; torn down after TTL/completion.

**skill-loader** talks to:
- **knowledge-service / Langfuse** — resolve production skill content + facts + episodes  
- **sandbox-provisioner** — spawn / prepare the ephemeral runner for this phase  
- **ephemeral runners** — mount the skill bundle so agents on that runner can use it  

```mermaid
sequenceDiagram
    participant Job as job-service
    participant Orch as agent-orchestrator
    participant Loader as skill-loader
    participant KS as knowledge-service
    participant LF as Langfuse
    participant Prov as sandbox-provisioner
    participant Runner as ephemeral runner

    Job->>Orch: run phase
    Orch->>Loader: prepare runtime for skill_key
    Loader->>KS: skill_meta + facts + episodes
    KS->>LF: production prompt
    Loader->>Prov: spawn ephemeral runner
    Prov-->>Loader: runner_id ready
    Loader->>Runner: mount centralized skill bundle
    Loader-->>Orch: runner_id + skills mounted
    Orch->>Runner: agents execute using mounted skills
    Runner-->>Orch: phase results
    Orch-->>Job: checkpoint + skill artifact
```

Agents produced for a phase **use** the skills skill-loader mounted; they do not pull registry content themselves.
Runner types (same or phase-specific images):

| Runner | Used by |
|--------|---------|
| Research | Skill 1 — data gathering, enrichment, findings writes |
| Execution | Skill 3 — enterprise system APIs, action execution |
| Reporting | Skill 4 — aggregation, document generation |
| Custom | Optional domain skills — isolated workspace |

## C4. Orchestration notes

- LangGraph provides durable state, retries, HITL pause/resume
- Deep Agents orchestrator may fan out sub-agents inside a phase and consolidate
- One runner workspace per job; no cross-job leakage
- Idle TTL + sweeper for orphaned runners

---

# PART D — FinOps Engine

**Purpose:** answer “what did this agent run cost?” per job, engagement, skill, and day.

```mermaid
flowchart LR
    Orch["agent-orchestrator"] -->|"traces"| LF["Langfuse"]
    Job["job-service"] -->|"runner lifetime"| FinOps["finops-engine"]
    LF -->|"tokens + model cost"| FinOps
    FinOps --> CR[("cost_record")]
    FinOps --> APIs["Gateway cost APIs / UI"]
```

### Responsibilities

- Ingest Langfuse spans (tokens, model, latency) keyed by `job_id` / phase / skill / agent
- Attribute ephemeral runner compute when metered (pod lifetime × rate)
- Persist `cost_record`; expose rollups
- Optional soft budgets / alerts

### Example `cost_record` fields

`id`, `job_id`, `engagement_id`, `skill_key`, `phase`, `agent_id`, `token_input`, `token_output`, `model_cost`, `runner_cost`, `total_cost`, `currency`, `recorded_at`

### Deployment (as a microservice)

- Independently deployable service behind **gateway** (`GET /engagements/{id}/costs`, program-level rollup APIs)
- Owns its data: `cost_record` (no other service writes it)
- Ingest paths: pull/webhook from Langfuse (spans) + events from job-service (runner lifetime); both async — FinOps downtime never blocks a job
- Scales independently (ingest volume, not job volume); stateless workers + its own schema/DB

---

# PART E — Adaption Engine

**Purpose:** keep **tracks** of each engagement’s journey and **email stakeholders** so work continues (HITL, stalls, deadlines, stage transitions).

> Naming: **Adaption Engine** = stakeholder engagement. Optional domain skills that change systems are different.

```mermaid
flowchart LR
    Job["job-service events"] --> Adapt["adaption-engine"]
    Adapt --> Tracks[("engagement_track")]
    Adapt -->|"email"| Owners["Stakeholders"]
    Adapt --> Hist[("email_event")]
    Adapt --> UI["Gateway / UI status"]
```

### Example triggers

| Event | Email intent |
|-------|----------------|
| Plan ready | Ask stakeholder to review / approve the plan |
| HITL idle > N days | Reminder |
| Guided wizard abandoned | Nudge to resume |
| Execution complete | Summary + next validation steps |
| Deadline approaching | Urgency / program outreach |

### Engagement track fields (logical)

`engagement_id`, `stage`, `stakeholder_emails`, `last_contact_at`, `next_action`, `sla_due_at`, `status`

### Deployment (as a microservice)

- Independently deployable service behind **gateway** (`GET /engagements/{id}/track`)
- Owns its data: `engagement_track`, `email_event` (audit)
- Consumes job-service lifecycle events from the message bus (decoupled — the job pipeline never waits on email)
- Pluggable mail transport (Graph / SMTP / SES) behind one interface; respects quiet hours / unsubscribe
- Scheduler component for SLA/idle timers (e.g. periodic sweep) — separate from the event consumer

---

# Design Principles

| Principle | Application in this framework |
|-----------|-------------------------------|
| **Modular** | Microservices + clear APIs; swap Docker ↔ K8s runners behind one protocol |
| **Scalable** | Gateway replicas; workers on queue depth; runners on demand |
| **Portable** | Agent logic cloud-agnostic; infra bindings pluggable |
| **Open** | REST + MCP + CLI; skills as `SKILL.md` / prompts, not binaries |
| **HITL** | Plan approval; skill-review for knowledge updates |
| **Agent / sub-agent** | Orchestrator in control plane; work in runners; credentials stay central |
| **Parallelism** | Fan-out within phases; many jobs across workers |
| **Handoffs** | FIFO pipeline + circular revise loops + fan-out/consolidate + handoff-to-human |
| **State layers** | Job DB, LangGraph checkpoints, runner workspace, knowledge, traces, cost, engagement |

---

# Cross-cutting

## Observability

- Langfuse: LLM/agent traces (`job_id` root span)
- FinOps: cost truth per run
- Infra metrics: runner OOM, queue depth, TTLs (e.g. App Insights)

## Proposed monorepo layout (for later implementation — not created yet)

```
framework/
├── apps/
│   ├── web/
│   ├── cli/
│   └── mcp/
├── services/
│   ├── gateway/
│   ├── knowledge/
│   ├── job/
│   ├── orchestrator/      # agent-orchestrator + skill-loader
│   ├── sandbox/           # sandbox-provisioner
│   ├── finops/
│   └── adaption/
├── runners/               # runner images / exec bridge
├── infra/
├── docs/                  # architecture diagrams (.drawio)
└── skills/                # seed SKILL.md content
```

## Key decisions

- The framework is **domain-agnostic** and engagement-centric (Engagement ID)
- Four example skills; each emits a **skill artifact**; pipeline ends with the **Final Deliverable Document**
- **No Merge Request / PR** in the process
- Interactive guided wizard first-class
- HITL after the Plan & Recommendation artifact
- Microservices behind gateway; **skill-loader** mounts centralized skills onto ephemeral runners (via sandbox-provisioner) for agents
- FinOps Engine for agent cost per run
- Adaption Engine for tracks + stakeholder email

## Build order

**This phase (docs only — done):** microservice map, this architecture document, draw.io diagrams in `docs/`.

Implementation phases (post architecture sign-off, no code yet):

| Phase | Scope |
|-------|-------|
| **1** | gateway + job-service + Engagement entity + guided wizard skeleton + local Docker runner + Skill 1 end-to-end (Research Findings Artifact) |
| **2** | Planning skill + HITL gate + skill-loader + Langfuse skill registry integration |
| **3** | Execution + Reporting runners (Skills 3–4) + managed K8s ephemeral runner backend + Final Deliverable Document composition |
| **4** | knowledge-service memory (episodes, reflection, skill-review HITL) + MCP/CLI parity |
| **5** | finops-engine (cost_record from Langfuse + runner metrics) + adaption-engine (tracks + email) + dashboards |

## Architecture status & next steps

| Done in this phase | Explicitly not done |
|--------------------|---------------------|
| This architecture doc | Application / service source code |
| Microservice boundaries | Deployable stubs / scaffolds |
| draw.io diagrams in `docs/*.drawio` | Production infra/Terraform |

**Next:** review this architecture → then scaffold microservices per the build order above.

## Open items (TBD)

- Domain skill catalog for the first concrete use case
- Live enrichment mechanisms per data source
- Plan scoring dimensions and weights
- Cloud provider bindings
- Adaption email transport (Graph / SMTP / SES)
- FinOps v1: model $ only vs include runner compute $
