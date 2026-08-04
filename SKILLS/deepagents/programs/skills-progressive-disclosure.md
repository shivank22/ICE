# Program: skills-progressive-disclosure

How Deep Agents load skills into the system prompt and when the model reads full instructions.

## Inputs

- Skill source paths on the agent backend
- Whether Path A (`skills=`) or Path B (`SkillsMiddleware`) is used

## Checklist

```
Task Progress:
- [ ] Step 1: Layout skill packages
- [ ] Step 2: Wire sources on the backend
- [ ] Step 3: Confirm index injection
- [ ] Step 4: Confirm on-demand body via read_file
- [ ] Step 5: Subagent inheritance rules
```

### Step 1: Layout skill packages

Each skill is a directory with `SKILL.md` (YAML frontmatter + body):

```text
/skills/project/web-research/
├── SKILL.md
└── helpers/   # optional scripts, refs
```

Frontmatter (Agent Skills style): `name`, `description` (required for the index); optional `license`, `compatibility`, `allowed_tools`, `metadata`.

### Step 2: Wire sources

**Path A:**

```python
create_deep_agent(..., backend=backend, skills=["/skills/user/", "/skills/project/"])
```

**Path B:**

```python
SkillsMiddleware(backend=backend, sources=["/skills/user/", "/skills/project/"])
```

Later sources override earlier ones by skill `name` (last wins). Sources may be `(path, label)` tuples for display labels.

With `StateBackend`, provide skill files via invoke `files={...}` or ensure content is written into state. With `FilesystemBackend` / Composite routes, files must exist under those paths.

### Step 3: Confirm index injection

Lifecycle (see [../references/skills-loading.md](../references/skills-loading.md)):

1. `before_agent` — scan sources, parse **frontmatter only** → `skills_metadata` (private state)
2. Every model call — append `## Skills System` with name, description, path via `append_to_system_message`

The model sees an **index**, not full bodies, at startup.

### Step 4: On-demand body

The skills prompt instructs the model to:

```text
read_file(file_path="<path from list>", limit=1000)
```

Default `read_file` limit (100 lines) is too small for most skills — always use `limit=1000` (or higher). Supporting files use absolute backend paths from the skill directory.

Without filesystem `read_file`, skills are useless (index only).

### Step 5: Subagent inheritance

| Agent | Skills |
|-------|--------|
| Main + auto GP | Same `skills=` sources when factory Path A |
| Declarative custom `SubAgent` | Must set `"skills": [...]` itself — **not** inherited |
| Path B GP | Add `SkillsMiddleware` to GP middleware explicitly |

## Failure modes

| Symptom | Fix |
|---------|-----|
| Empty skills list | Paths missing on backend; check `ls` |
| Model never follows skill | Description not matching task; improve frontmatter |
| Truncated skill body | Pass `limit=1000` on `read_file` |
| Custom subagent ignores skills | Add `"skills"` on that spec |

## See also

- [../references/skills-loading.md](../references/skills-loading.md)
- [../references/prompt-fragments.md](../references/prompt-fragments.md)
