# Algorithm — Context Assembly

## Purpose

Build a deterministic Context Package for one graph step.

## Inputs

- `request` (user message / command)
- `identity` (JWT claims: user_id, roles, org_id)
- `thread_id`, `checkpoint_id`
- `skill_pins[]`
- `budgets` (per-section token limits)
- `policies[]`

## Outputs

- `context_package`
- `assembly_digest`
- `metrics` (tokens per section, drops)

## Preconditions

- Identity validated.
- Thread ACL allows caller.
- Budgets configured.

## Postconditions

- Package sections ordered per platform standard.
- Every injected memory/skill cites source ids.
- Unauthorized namespaces excluded.

## Steps

1. Initialize empty package with `schema_version`.
2. Load **policies** and system guidance; attach as section `policy` (non-droppable under budget except hard fail).
3. Attach **identity** entitlements section.
4. Restore **STM slice** from checkpoint (messages window + channel summary).
5. Resolve **procedural skills** via Skill Loader for `skill_pins` or production defaults; attach manifests + constraints.
6. Build semantic query from request + skill retrieval hints; retrieve within authorized namespaces; attach top-k.
7. Retrieve episodic exemplars under episodic budget; prefer failures matching current skill ids.
8. Attach relevant **artifact** refs and recent tool outputs for this turn.
9. Attach **user request** last among content sections (still below policy in priority).
10. Run **Context Compression** with conflict rules.
11. Hash package → `assembly_digest`; return.

## Conflict resolution

Priority: policy > skill constraint > retrieved memory > model preference.  
On conflict: keep higher priority; record override in `metrics.conflicts`.

## Complexity

Dominated by retrieval fan-out; bound with parallel deadlines.

## Edge Cases

- Empty semantic hits → continue with explicit `semantic: []`.
- Skill resolve failure → fail closed for required skills; warn for optional.
- Budget overflow → compress per [context-compression.md](context-compression.md).

## Failure Handling

- Authz failure → abort assembly; do not call model.
- Timeout on one store → degrade that section if marked optional; else abort.
