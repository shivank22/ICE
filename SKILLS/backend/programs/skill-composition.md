# Algorithm — Skill Composition

## Purpose

Order and constrain multiple selected skills into an executable plan.

## Inputs

- `skill_pins[]` — each with `skill_id`, `version`, `description`, `locator`
- `manifests[]` — SkillManifest projections (from skill.yaml map) with dependencies and constraints
- `phase_graph` template

## Outputs

- `composition_plan` (ordered nodes, shared artifacts contracts)

## Preconditions

- All manifests resolved for pinned `skill_id` + `version` via Skill Resolver Service.
- Dependency graph is acyclic.
- Pin authz already passed.

## Postconditions

- Deterministic order.
- Shared artifact schemas agreed.

## Steps

1. Load dependency edges from manifests.
2. Topologically sort; detect cycles → fail.
3. Merge constraints (intersection of prohibitions; union of required checks).
4. Map skills onto phase graph slots.
5. Define artifact handoff contracts between skills.
6. Return composition_plan for Orchestrator.

## Edge Cases

- Optional skills skipped when inputs already satisfied.
- Conflicting constraints → fail or interrupt for human.

## Failure Handling

Reject composition rather than arbitrary override.
