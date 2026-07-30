# JSON Contracts

Canonical structural schemas for architectural objects. These document **shape** for APIs and design docs.

**LangGraph note:** `runtime-state`, `thread-state`, `checkpoint`, `interrupt-payload`, and `run-result` are **projections/DTOs** over LangGraph `StateSnapshot` / interrupt values / invoke outcomes—not a license to invent a second durability layer. `run-create` vs `resume-request` encode StartRun (`input`) vs ResumeRun (`command.resume`). `semantic-memory` is the **Store value shape**. See [../langgraph-bindings.md](../langgraph-bindings.md) and [../16-api-surface-interrupt-resume.md](../16-api-surface-interrupt-resume.md).

| Contract | Object |
|----------|--------|
| [runtime-state.json](runtime-state.json) | Runtime State (DTO) |
| [thread-state.json](thread-state.json) | Thread State (DTO) |
| [thread-create.json](thread-create.json) | CreateThread request |
| [run-create.json](run-create.json) | StartRun request (`input`) |
| [resume-request.json](resume-request.json) | ResumeRun request (`command.resume`) |
| [run-result.json](run-result.json) | Start/Resume response |
| [session.json](session.json) | Session |
| [user.json](user.json) | User |
| [checkpoint.json](checkpoint.json) | Checkpoint (projection) |
| [interrupt-payload.json](interrupt-payload.json) | Interrupt (projection) |
| [memory-record.json](memory-record.json) | Memory Record base |
| [semantic-memory.json](semantic-memory.json) | Semantic Memory Store value (`Memory.md`) |
| [procedural-memory.json](procedural-memory.json) | Procedural Memory |
| [episodic-memory.json](episodic-memory.json) | Episodic Memory |
| [context.json](context.json) | Context Package |
| [skill.json](skill.json) | Skill package view |
| [skill-manifest.json](skill-manifest.json) | Skill Manifest (API projection of skill.yaml) |
| [skill-yaml.json](skill-yaml.json) | On-disk platform manifest (`skill.yaml`) |
| [skill-pin.json](skill-pin.json) | Run/thread skill pin (description + locator) |
| [skill-locator.json](skill-locator.json) | Package origin (`lfs` \| `blob`) |
| [skill-reference.json](skill-reference.json) | Resolver handle after load |
| [skill-index-record.json](skill-index-record.json) | pgvector index row (runtime **cards**) |
| [artifact.json](artifact.json) | Artifact |
| [tool-invocation.json](tool-invocation.json) | Tool Invocation |
| [trace.json](trace.json) | Trace |
| [reflection.json](reflection.json) | Reflection Proposal |
| [evaluation.json](evaluation.json) | Evaluation |
| [evaluation-criteria.json](evaluation-criteria.json) | Skill/run metric definitions & thresholds |
| [approval.json](approval.json) | Approval |
| [policy.json](policy.json) | Policy |
| [event.json](event.json) | Event |

**Skill contracts rule:** prose and programs must match these schemas. **Runtime model** = CI builds index from `skill.yaml` → Discovery puts **index records** in context → **Skill Resolver Service** loads full packages from `lfs` or `blob`. Map `skill.yaml` → SkillManifest via [../../programs/skill-yaml-to-manifest.md](../../programs/skill-yaml-to-manifest.md).
