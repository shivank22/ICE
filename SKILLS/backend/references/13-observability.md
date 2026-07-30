# 13 — Observability

## 1. Executive Summary

Observability for agent platforms covers traces, quality signals, infrastructure health, and cost. Traces feed episodic memory; they are not a substitute for checkpoints or skill registries.

**Opinionated LangGraph practices** (graph-level + agent-level emission, Langfuse/LangSmith bindings, attribute vocabulary, sampling, PII) live in **[17-langgraph-observability.md](17-langgraph-observability.md)**. Evaluation framework bindings (DeepEval, custom metrics, LLM-as-judge) live in **[18-evaluation-frameworks.md](18-evaluation-frameworks.md)**.

## 2. Purpose

Define what must be observable for operation, eval, and learning—without conflating telemetry with control-plane state.

## 3. Scope

Tracing overview, metrics, logging correlation, FinOps signals. Detailed LangGraph emission checklist in doc 17; episode curation in doc 07.

## 4. Architecture Overview

See [../assets/diagrams/13-observability.mmd](../assets/diagrams/13-observability.mmd)

## 5. Core Concepts

- **Trace / span:** execution timeline.
- **Correlation ids:** thread_id, run_id, checkpoint_id, assembly_digest.
- **Quality signals:** eval scores, user feedback.
- **Cost record:** tokens, model $, runner time.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| O1 | Every model/tool span carries thread and skill version |
| O2 | Context assembly_digest stored on Trace |
| O3 | FinOps consumes traces + runner metrics; does not own orchestration |
| O4 | PII redaction at ingest for long-term stores |

## 7. Decision Rationale

Correlation enables replay of “what the model saw.” Separating FinOps keeps cost accounting independent of graph correctness.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Logs only | Weak structure for eval |
| Traces as checkpoint store | Wrong durability semantics |
| Cost in orchestrator DB only | Incomplete runner picture |

## 9. Tradeoffs

Telemetry volume vs retention cost. Use sampling for high-frequency spans; keep full fidelity on failures.

## 10. Component Breakdown

### Trace Store

- **Purpose:** Ingest and query spans.
- **Responsibilities:** Retention, redaction, tenant isolation.
- **Non-responsibilities:** Approving skills; mutating STM.
- **Inputs:** Orchestrator/runner exporters.
- **Outputs:** Trace queries; export to Episode curation.
- **Failure Modes:** ingest backlog.
- **Recovery:** buffer; degrade non-critical spans.
- **Security:** RBAC on trace read.
- **Scalability:** time partitioning.

## 11. Sequence of Operations

1. Start trace on thread start.
2. Child spans per node/tool/LLM.
3. Attach assembly_digest each model call.
4. On terminal: finalize trace; curate Episode.
5. FinOps aggregates cost_record.

## 12. State Changes

Telemetry is append-mostly; episodes may move through reflection states independently.

## 13. Mermaid Diagrams

See §4.

## 14. JSON Contracts

- [contracts/trace.json](contracts/trace.json)
- [contracts/event.json](contracts/event.json)
- [contracts/evaluation.json](contracts/evaluation.json)

## 15. Best Practices

- Standard attribute vocabulary across services.
- Alert on interrupt aging SLA.
- Track skill version error rates.

## 16. Anti-patterns

- Logging full prompts with secrets.
- Missing skill version on spans.
- Using App Insights alone without agent-native traces.

## 17. Common Mistakes

- Different ids in gateway vs orchestrator.
- No link from cost_record to thread.
- Over-sampling away all failures.

## 18. Future Evolution

OpenTelemetry semantic conventions for agents; anomaly detection on tool error clusters.

## 19. Related Documents

[07-episodic-memory.md](07-episodic-memory.md) · [12-reflection-evaluation.md](12-reflection-evaluation.md) · [15-deployment-evolution.md](15-deployment-evolution.md) · [17-langgraph-observability.md](17-langgraph-observability.md) · [18-evaluation-frameworks.md](18-evaluation-frameworks.md)
