# Algorithm — Skill Discovery

## Purpose

Find candidate skills matching a task intent.

## Inputs

- `intent` / query
- `label` (default production)
- `filters` (tags, runtime compatibility)

## Outputs

- `candidates[]` of manifests with scores

## Preconditions

- Registry reachable.

## Postconditions

- Only skills with requested label (unless pin override).

## Steps

1. Parse intent into keywords / embedding.
2. Query registry metadata (tags, purpose, examples).
3. Filter by compatibility with runtime version.
4. Rank by relevance + quality scores.
5. Return top candidates (not yet selected).

## Edge Cases

- No production match → return empty; do not silently return draft.
- Deprecated skills excluded unless pinned.

## Failure Handling

Fail closed if registry unavailable for required discovery.
