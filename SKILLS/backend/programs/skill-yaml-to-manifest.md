# Algorithm — skill.yaml → SkillManifest

## Purpose

Produce a deterministic **SkillManifest** API projection from on-disk **`skill.yaml`** (+ optional SKILL.md summary). One mapping; no divergent hand-authored manifests.

## Inputs

- Parsed `skill.yaml` (validated against [skill-yaml.json](../references/contracts/skill-yaml.json))
- Optional: `locator` (`lfs` \| `blob`), SKILL.md front-matter/summary
- Optional: package-relative `examples_ref`

## Outputs

- [skill-manifest.json](../references/contracts/skill-manifest.json)

## Field map

| SkillManifest | Source |
|---------------|--------|
| `skill_id` | `skill.yaml.name` |
| `name` | `skill.yaml.name` (display override not supported unless added later) |
| `version` | `skill.yaml.version` |
| `status` | `skill.yaml.status` |
| `purpose` | `skill.yaml.purpose` if set; else `skill.yaml.description`; else first paragraph of SKILL.md |
| `scope` | `skill.yaml.scope` |
| `tags` | `skill.yaml.tags` |
| `owner` | `skill.yaml.owner` |
| `compatibility` | `skill.yaml.compatibility` |
| `evaluation_criteria_ref` | `skill.yaml.evaluation_criteria_ref` |
| `dependencies[].skill_id` | `skill.yaml.dependencies[].name` |
| `dependencies[].version_range` | `skill.yaml.dependencies[].version_range` |
| `org_allowlist` | `skill.yaml.org_allowlist` |
| `locator` | Index / Resolver locator (`lfs` \| `blob`) when known |
| `examples_ref` | optional package path |
| `inputs` / `outputs` / `constraints` / `policies` | optional; omit unless declared in package extensions (not in base yaml) |

## Preconditions

- `skill.yaml` schema validation passed.
- Folder name equals `skill.yaml.name`.

## Postconditions

- Manifest `skill_id` === yaml `name` === folder name.
- Manifest `status` === yaml `status` (never invent a separate `label` field).

## Steps

1. Validate yaml.
2. Assert folder/`name` match.
3. Apply field map above.
4. Attach `locator` when projecting from index/Resolver output.
5. Emit SkillManifest; use in Context Package cards / APIs — **do not** inject full yaml into the LLM.

## Edge Cases

- Missing `purpose` and `description` → use truncated SKILL.md summary; fail CI if both empty for production status.
- Unknown yaml keys → **reject** (`additionalProperties: false`).

## Related

[../references/19-skill-platform-lifecycle.md](../references/19-skill-platform-lifecycle.md) · [skill-resolve.md](skill-resolve.md)
