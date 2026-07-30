# 14 — Security

## 1. Executive Summary

Security for agentic backends centers on identity propagation, namespace isolation for semantic memory, least-privilege tool credentials, gated promotions, and secret hygiene in traces and Memory.md.

## 2. Purpose

State the security architecture that coding agents must preserve when binding stacks.

## 3. Scope

AuthN/Z, tenancy, data classification, runner isolation principles. Product IdP brand choices are bindings, not topology.

## 4. Architecture Overview

See [../assets/diagrams/14-security-boundaries.mmd](../assets/diagrams/14-security-boundaries.mmd)

## 5. Core Concepts

- **Validated JWT** at gateway; services trust forwarded identity only via secured mesh.
- **Namespace** = JWT `user_id` (Store tuple) for personal semantic memory.
- **Fail closed** on authz errors in Store retrieval and resume.
- **Mount-only skills** — no long-lived secrets in skill packages.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| Sec1 | Never trust client-supplied user_id over token subject |
| Sec2 | Thread ACL on checkpointer access; Store namespace ACL from JWT before search |
| Sec3 | Production skill promote requires Approval role |
| Sec4 | Redact secrets from traces and Memory.md |
| Sec5 | Runners (if used) get short-lived credentials only |
| Sec6 | Resume authz before `Command(resume=...)` |

## 7. Decision Rationale

Agent tools amplify privilege. Explicit identity and short-lived creds limit blast radius. Redaction prevents episodic stores from becoming secret lakes.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Shared service account for all users’ memory | Cross-user leakage |
| Long-lived keys in skill blobs | Credential sprawl |
| Permit on embedding similarity alone | Ignores ACL |

## 9. Tradeoffs

More authz checks add latency; required for multi-tenant safety.

## 10. Component Breakdown

Security is a **cross-cutting control** enforced at Gateway, Knowledge, Orchestrator resume paths, Registry promote, and Trace ingest.

## 11. Sequence of Operations

1. Authenticate at Gateway.
2. Propagate signed identity context.
3. On semantic read/write: authorize namespace.
4. On resume: authorize required_roles.
5. On promote: authorize governance role.
6. On trace ingest: redact.

## 12. State Changes

Security denials do not advance graph state; emit audit Event.

## 13. Mermaid Diagrams

See §4.

## 14. JSON Contracts

- [contracts/user.json](contracts/user.json)
- [contracts/policy.json](contracts/policy.json)
- [contracts/approval.json](contracts/approval.json)

## 15. Best Practices

- Threat-model tool allowlists per skill.
- Rotate embed/LLM keys via secret manager.
- Penetration-test namespace isolation.

## 16. Anti-patterns

- Putting API keys in Memory.md.
- Disabling auth on “internal” orchestrator ports.
- Draft skills executable in production path.

## 17. Common Mistakes

- Email as namespace primary key.
- Logging Authorization headers.
- Broad blob read roles for loader.

## 18. Future Evolution

Confidential computing for runners; attribute-based access on artifacts.

## 19. Related Documents

[05-semantic-memory.md](05-semantic-memory.md) · [11-human-approval-governance.md](11-human-approval-governance.md) · [08-context-construction.md](08-context-construction.md)
