# 11 — Human Approval & Governance

## 1. Executive Summary

Governance makes irreversible actions and skill evolution safe. Approvals are first-class records that unblock interrupts or promotions. Policies declare what requires approval; humans (or dual-control roles) decide.

## 2. Purpose

Define approval targets, roles, audit requirements, and separation between run-time HITL and skill-promotion governance.

## 3. Scope

Approval service behavior, policy gates, dual control. Reflection content generation is in doc 12.

## 4. Architecture Overview

See [../assets/diagrams/11-approval-gates.mmd](../assets/diagrams/11-approval-gates.mmd)

Two primary gates:

1. **Run gate** — LangGraph `interrupt()` before irreversible execution; Approval authorizes `Command(resume=...)` via the ResumeRun / ApproveAndResume API ([16-api-surface-interrupt-resume.md](16-api-surface-interrupt-resume.md)).
2. **Promotion gate** — label moves on procedural skills (platform; not a LangGraph primitive).

Prefer **dynamic** `interrupt()` for production HITL. Use static `interrupt_before` / `interrupt_after` for debugging, not as the primary approval mechanism ([Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)).

## 5. Core Concepts

- **Approval:** immutable decision record.
- **Policy:** rules with allow/deny/require_approval effects.
- **Dual control:** two independent Approvals for high risk.
- **Delegation:** named approver sets per engagement/org.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| G1 | Run approval ≠ skill promotion approval |
| G2 | Approvals are append-only |
| G3 | High-risk tools always require_approval via `interrupt()` before side effects |
| G4 | Policy priority participates in context assembly |
| G5 | Approval service wraps LangGraph resume—it does not replace checkpointer/interrupt |

## 7. Decision Rationale

Separating gates prevents “approved the plan” from silently changing agent procedures forever. Append-only decisions support compliance.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Soft prompts “please be careful” | Not enforceable |
| Single admin backdoor without audit | Non-compliant |
| Auto-approve below cost threshold only | Misses safety/regulatory risk |

## 9. Tradeoffs

Slower cycle time vs lower blast radius. Mitigate with clear SLAs and notification channels.

## 10. Component Breakdown

### Approval / Policy Gate

- **Purpose:** Enforce and record decisions.
- **Responsibilities:** Role checks, dual control, emit events, invoke Resume/Promotion.
- **Non-responsibilities:** Generating reflection diffs; running tools.
- **Inputs:** interrupt/promotion targets; actor identity; decision.
- **Outputs:** Approval records; unblock signals.
- **Dependencies:** Identity provider roles; Orchestrator; Skill Registry.
- **Lifecycle:** request → pending → decided.
- **Failure Modes:** approver unavailable; conflicting dual decisions.
- **Recovery:** escalate; timeout policies; keep target awaiting.
- **Security:** break-glass with extra audit.
- **Scalability:** queue per org; async notifications.

## 11. Sequence of Operations

Algorithm: [../programs/human-approval.md](../programs/human-approval.md)

## 12. State Changes

| Target | Pending | Terminal |
|--------|---------|----------|
| interrupt | awaiting_approval | running / cancelled |
| promotion | awaiting_promotion | draft/staging/production advanced or rejected |

## 13. Mermaid Diagrams

See §4.

## 14. JSON Contracts

- [contracts/approval.json](contracts/approval.json)
- [contracts/policy.json](contracts/policy.json)
- [contracts/event.json](contracts/event.json)

## 15. Best Practices

- Show artifact diffs in approval UI.
- Encode required_roles on interrupt payload.
- Retain approvals beyond thread TTL.

## 16. Anti-patterns

- Overwriting Approval rows.
- Using the same button for plan approve and prompt promote.
- Policy stored only in prose inside skills.

## 17. Common Mistakes

- Missing timeout on awaiting_approval.
- Approver is the same service account as orchestrator.
- No link from Approval to checkpoint id.

## 18. Future Evolution

Policy-as-code engines; risk scoring to select dual control dynamically.

## 19. Related Documents

[09-checkpoints-interrupt-resume.md](09-checkpoints-interrupt-resume.md) · [10-feedback-loops-rework.md](10-feedback-loops-rework.md) · [12-reflection-evaluation.md](12-reflection-evaluation.md) · [14-security.md](14-security.md)
