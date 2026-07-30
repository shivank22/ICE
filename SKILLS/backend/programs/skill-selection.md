# Algorithm — Skill Selection

## Purpose

Choose which skills to pin for a run/phase.

## Inputs

- `candidates[]`
- `policies`
- `user_or_plan_preferences`
- `risk_class`

## Outputs

- `skill_pins[]` (id + version)

## Preconditions

- Candidates discovered or explicitly requested.

## Postconditions

- Pins immutable for the run unless rework policy allows change.
- Required skills present.

## Steps

1. Apply policy allow/deny lists.
2. Prefer explicit user/plan skill requests when allowed.
3. Else pick highest ranked compatible candidate per capability slot.
4. Resolve version: pin production digest/version.
5. Validate dependency closure (composition prerequisites).
6. Persist pins on Runtime State.

## Edge Cases

- Ambiguous top scores → interrupt for human skill choice on high risk_class.
- Missing dependency → fail selection.

## Failure Handling

Do not start execution phase without required pins.
