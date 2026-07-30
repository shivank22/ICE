# Algorithm — Skill Selection (Resolver policy hooks)

## Purpose

Decide which Discovery hits (or client pins) the **Skill Resolver Service** should materialize. Selection is part of Resolver customization—not a separate package loader. Index **records** stay in context regardless; only **appropriate** skills get full packages from `lfs` / `blob`.

## Inputs

- Discovery records: ids + descriptions + metadata + locator
- Explicit user / client pin requests
- `policies`, risk class, caller identity (`roles`, `org_id`)

## Outputs

- Ordered set of records / pins for the Skill Resolver Service
- Each pin: [skill-pin.json](../references/contracts/skill-pin.json) — `skill_id`, `version`, `description`, `locator`

## Preconditions

- Candidates from Discovery or explicit request.
- Client-supplied pins passed pin-gate authz.

## Postconditions

- Pins immutable for the run unless rework policy allows change.
- Only appropriate skills resolved—not the full corpus.
- Context continues to use **index descriptions**, not full packages.

## Pin authz

| Requested status | Allowed when |
|------------------|--------------|
| `production` | Authenticated; `org_allowlist` empty or contains `org_id` |
| `deprecated` | Explicit pin + policy allow |
| `staging` | Role `skills.pin_non_production` or soak flag |
| `draft` / `archived` | Override role / break-glass only |

## Steps

1. Apply policy allow/deny + pin authz.
2. Prefer explicit user/plan requests when allowed.
3. Else apply use-case Resolver policy over Top-K records (ranked cut, LLM select, rules—customizable).
4. Attach index **description** + `locator` onto each pin.
5. Hand pins to Skill Resolver Service (`lfs` \| `blob`).

## Edge Cases

- Ambiguous scores → interrupt for human choice on high risk.
- Empty shortlist → fail or ask user; **never** resolve all production skills.
- Resolve failure for required skill → fail selection/run.

## Failure Handling

Do not start execution without required resolved packages.

## Related

[skill-discovery.md](skill-discovery.md) · [skill-resolve.md](skill-resolve.md) · [skill-runtime-pipeline.md](skill-runtime-pipeline.md) · [../references/14-security.md](../references/14-security.md)
