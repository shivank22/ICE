# 12 — Reflection & Evaluation

## 1. Executive Summary

Evaluation scores runs and skill versions against criteria. Reflection analyzes episodic cohorts and emits **proposals**. Together they support learning without automatic mutation of production procedural memory.

## 2. Purpose

Specify how quality signals become governed change—and what must never happen automatically.

## 3. Scope

Evaluation records, reflection proposals, learning promotion inputs. Trace infrastructure detail is in observability.

## 4. Architecture Overview

See [../assets/diagrams/12-reflection-eval.mmd](../assets/diagrams/12-reflection-eval.mmd)

## 5. Core Concepts

- **Criteria:** versioned expectations per skill/phase.
- **Evaluation:** scored pass/fail/inconclusive.
- **Reflection Proposal:** evidenced suggested diff.
- **Soak:** staging period with eval gates before production.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| RE1 | Reflection never writes production labels |
| RE2 | Every proposal cites episode/trace evidence |
| RE3 | Inconclusive eval blocks promotion when policy requires hard pass |
| RE4 | Human ratings are first-class signals |

## 7. Decision Rationale

Evidence-backed proposals enable review. Hard pass policies protect regulated environments.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Continuous fine-tuning from all logs | Opaque, costly, hard to reverse |
| Auto-merge high-confidence diffs | Still silent prod mutation |
| Metrics-only without traces | Weak diagnosis |

## 9. Tradeoffs

Human review latency vs safety. Use staging soak to reduce production risk.

## 10. Component Breakdown

### Reflection / Learning Promoter

- **Purpose:** Turn episodes into proposals and apply **approved** draft versions.
- **Responsibilities:** Cohort selection, proposal generation, invoke Learning Promotion after Approval.
- **Non-responsibilities:** Final production label moves without Approval; context assembly.
- **Inputs:** Episodes, criteria, base skill versions.
- **Outputs:** Reflection Proposals; draft skill versions.
- **Dependencies:** Episodic store; Skill Registry; Approval.
- **Lifecycle:** schedule → analyze → propose → await → apply draft → close.
- **Failure Modes:** weak evidence; rebase conflicts.
- **Recovery:** defer proposal; require new reflection.
- **Security:** redact PII before model analysis where required.
- **Scalability:** batch cohorts; rate-limit LLM analysis.

### Evaluation Service (logical)

- **Purpose:** Score subjects.
- See algorithm [../programs/evaluation.md](../programs/evaluation.md).

## 11. Sequence of Operations

1. Attach Evaluation to completed Episode.
2. Select underperforming cohorts.
3. Reflection → Proposal.
4. Approval → Learning Promotion (draft).
5. Staging Evaluation → Production Approval.

Algorithms: [../programs/reflection.md](../programs/reflection.md) · [../programs/learning-promotion.md](../programs/learning-promotion.md)

## 12. State Changes

Proposal: open → accepted | rejected | deferred.  
Skill labels advance only via Learning Promotion + Approvals.

## 13. Mermaid Diagrams

See §4.

## 14. JSON Contracts

- [contracts/reflection.json](contracts/reflection.json)
- [contracts/evaluation.json](contracts/evaluation.json)
- [contracts/episodic-memory.json](contracts/episodic-memory.json)

## 15. Best Practices

- Version evaluation criteria with skills.
- Require minimum episode count before reflection.
- Publish dashboards of proposal accept rates.

## 16. Anti-patterns

- Applying proposal text directly to production prompts.
- Evaluating without skill version pins.
- Cherry-picking only successful episodes.

## 17. Common Mistakes

- No confidence field on proposals.
- Ignoring cost regressions in scores.
- Closing proposals without audit comments.

## 18. Future Evolution

Automated canary skill labels; causal attribution across tool failures.

## 19. Related Documents

[07-episodic-memory.md](07-episodic-memory.md) · [06-procedural-memory-skills.md](06-procedural-memory-skills.md) · [11-human-approval-governance.md](11-human-approval-governance.md) · [13-observability.md](13-observability.md)
