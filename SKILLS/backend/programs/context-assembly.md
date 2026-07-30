# Algorithm — Context Assembly

## Purpose

Build a deterministic Context Package for one LangGraph node/step. Runs as a platform helper inside (or immediately before) model-facing nodes—not as a second orchestrator.

**Prerequisite:** skill **index records** already retrieved via [skill-discovery.md](skill-discovery.md) / [skill-runtime-pipeline.md](skill-runtime-pipeline.md). This algorithm does **not** run Discovery or the Skill Resolver Service.

## LangGraph binding

- STM: current graph `state` / `get_state` snapshot values (checkpointer-backed)
- Semantic: `store.search` / `store.get` with JWT-derived namespace tuples
- Procedural: **skill index records** (name, description, metadata)—full SKILL.md via Skill Resolver Service at execute
- Episodic: trace/episode store (platform)
- See [../references/langgraph-bindings.md](../references/langgraph-bindings.md)

## Inputs

- `request` (user message / command)
- `identity` (JWT claims: user_id, roles, org_id)
- `thread_id`, optional `checkpoint_id`
- graph `state` / snapshot values (messages, channels)
- `store` (`BaseStore`) when semantic retrieval is needed
- `skill_records[]` / `skill_pins[]` — index cards: `skill_id`, `version`, **`description`**, metadata, `locator` ([skill-pin.json](../references/contracts/skill-pin.json))
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
- Store available if semantic section required.
- Skill section uses Discovery records (or empty with explicit “no skill” policy). Do not invent a production-default corpus.

## Postconditions

- Package sections ordered per platform standard.
- Skill section cites skill ids + versions; uses **index records**, not full corpus.
- Unauthorized namespaces excluded.
- Draft/staging skills absent unless pin authz allowed them.

## Steps

1. Initialize empty package with `schema_version`.
2. Load **policies** and system guidance; attach as section `policy` (non-droppable under budget except hard fail).
3. Attach **identity** entitlements section.
4. Project **STM slice** from graph state / snapshot (messages window + channel summary)—do not reimplement checkpoint restore.
5. Attach **procedural** section from Discovery / pin **records**:
   - Use **name, description, metadata** from the Skill Index.
   - Do **not** inline every candidate’s full SKILL.md into the planner prompt.
   - Full `SKILL.md` is obtained by the **Skill Resolver Service** (`lfs` \| `blob`) for appropriate skills at execute.
   - Never inject raw `skill.yaml` as LLM instructions.
6. Build semantic query from request + skill retrieval hints; `store.search` within authorized namespace tuples; attach top-k `Memory.md` snippets.
7. Retrieve episodic exemplars under episodic budget; prefer failures matching current skill ids.
8. Attach relevant **artifact** refs and recent tool outputs for this turn.
9. Attach **user request** last among content sections (still below policy in priority).
10. Run **Context Compression** with conflict rules.
11. Hash package → `assembly_digest`; return (optionally attach digest to trace metadata).

## Conflict resolution

Priority: policy > skill constraint > retrieved memory > model preference.  
On conflict: keep higher priority; record override in `metrics.conflicts`.

## Complexity

Dominated by retrieval fan-out; bound with parallel deadlines.

## Edge Cases

- Empty semantic hits → continue with explicit `semantic: []`.
- Missing skill records on a skill-required turn → fail closed (do not Discovery-from-assembler).
- Need full package → Skill Resolver Service, not Assembler.
- Budget overflow → compress per [context-compression.md](context-compression.md).

## Failure Handling

- Authz failure → abort assembly; do not call model.
- Timeout on Store or episode query → degrade that section if marked optional; else abort.
