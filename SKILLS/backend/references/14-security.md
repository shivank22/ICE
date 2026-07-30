# 14 — Security

## 1. Executive Summary

Security for agentic backends centers on identity propagation, namespace isolation for semantic memory, least-privilege tool credentials, gated skill promotions, skill pin authz, Resolver backend access, and secret hygiene in traces and Memory.md.

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
- **Resolved skills only** — no long-lived secrets in skill packages; promote gated by Approval + protected change path.
- **Skill pin authz** — clients cannot freely pin draft/staging or cross-org skills.

## 6. Design Decisions

| ID | Decision |
|----|----------|
| Sec1 | Never trust client-supplied user_id over token subject |
| Sec2 | Thread ACL on checkpointer access; Store namespace ACL from JWT before search |
| Sec3 | Production skill promote requires Approval role + protected change path + CI re-index |
| Sec4 | Redact secrets from traces and Memory.md |
| Sec5 | Runners (if used) get short-lived credentials only |
| Sec6 | Resume authz before `Command(resume=...)` |
| Sec7 | Skill pins: require `locator` (`lfs`\|`blob`); status gated (`production` default; non-production needs `skills.pin_non_production` or soak); enforce `org_allowlist` |
| Sec8 | Discovery only returns `index_ready` rows visible to caller org |

## 7. Decision Rationale

Agent tools amplify privilege. Explicit identity and short-lived creds limit blast radius. Redaction prevents episodic stores from becoming secret lakes. Pin authz prevents privilege escalation via client-supplied skill mounts.

## 8. Alternatives Considered

| Alternative | Why not preferred |
|-------------|-------------------|
| Shared service account for all users’ memory | Cross-user leakage |
| Long-lived keys in skill packages | Credential sprawl |
| Permit on embedding similarity alone | Ignores ACL |
| Unrestricted client skill_pins | Mount draft/hostile skills |

## 9. Tradeoffs

More authz checks add latency; required for multi-tenant safety.

## 10. Component Breakdown

Security is a **cross-cutting control** enforced at Gateway, Store facade, Orchestrator resume paths, **skill promote / CI**, skill pin gate, Skill Resolver Service, and Trace ingest.

## 11. Sequence of Operations

1. Authenticate at Gateway.
2. Propagate signed identity context.
3. On semantic read/write: authorize namespace.
4. On CreateThread/StartRun with `skill_pins`: authorize status + org_allowlist + require `locator` (`lfs`\|`blob`).
5. On resume: authorize required_roles.
6. On promote: authorize governance role; CI re-index (+ blob publish when used).
7. On trace ingest: redact.

## 12. State Changes

Security denials do not advance graph state; emit audit Event.

## 13. Mermaid Diagrams

See §4.

## 14. JSON Contracts

- [contracts/user.json](contracts/user.json)
- [contracts/policy.json](contracts/policy.json)
- [contracts/approval.json](contracts/approval.json)
- [contracts/skill-pin.json](contracts/skill-pin.json)

## 15. Best Practices

- Threat-model tool allowlists per skill.
- Rotate embed/LLM keys via secret manager.
- Penetration-test namespace isolation and pin authz.
- Signed commits / required reviews on `skills/**` production status bumps.

## 16. Anti-patterns

- Putting API keys in Memory.md.
- Disabling auth on “internal” orchestrator ports.
- Draft skills executable in production path without pin override role.
- Broad Git credential scopes that allow any service account to push production skill status.
- Serving skill bodies from Postgres when Git SHA verify fails.

## 17. Common Mistakes

- Email as namespace primary key.
- Logging Authorization headers.
- Treating “index row exists” as authorization to mount.

## 18. Future Evolution

Confidential computing for runners; attribute-based access on artifacts; multi-tenant skill overlays with stronger isolation.

## 19. Related Documents

[05-semantic-memory.md](05-semantic-memory.md) · [11-human-approval-governance.md](11-human-approval-governance.md) · [08-context-construction.md](08-context-construction.md) · [19-skill-platform-lifecycle.md](19-skill-platform-lifecycle.md) · [../programs/skill-selection.md](../programs/skill-selection.md)
