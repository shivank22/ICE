# Algorithm — Artifact Generation

## Purpose

Produce a versioned durable artifact from a skill phase.

## Inputs

- `skill_pin`
- `thread_id`
- `content` / locator
- `artifact_type`
- `schema_id`

## Outputs

- `artifact` record

## Preconditions

- Skill phase succeeded or explicitly partial-allowed.
- Schema validation available for type.

## Postconditions

- Artifact immutable version stored.
- Prior artifact of same slot may be marked superseded on rework.

## Steps

1. Validate content against schema.
2. Store blob/object; compute checksum.
3. Write artifact metadata (skill version, thread, checkpoint id).
4. Link to Runtime State / job record.
5. Emit `artifact.created`.

## Edge Cases

- Schema evolution → write with schema_version; readers tolerate N-1.
- Empty content → reject.

## Failure Handling

Orphan blob GC if metadata write fails; do not reference missing checksums.
