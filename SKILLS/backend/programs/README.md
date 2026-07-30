# Programs (Algorithms)

Structured algorithms for the Architecture Knowledge Pack. Steps use plain language—not programming language syntax.

Where a LangGraph primitive exists, algorithms **bind to it** (checkpointer, Store, `interrupt`, `Command(resume=...)`, `get_state_history`). See [../references/langgraph-bindings.md](../references/langgraph-bindings.md).

| Algorithm | File | Layer |
|-----------|------|-------|
| Context Assembly | [context-assembly.md](context-assembly.md) | Platform |
| Context Compression | [context-compression.md](context-compression.md) | Platform |
| Memory Retrieval | [memory-retrieval.md](memory-retrieval.md) | Store + episodes |
| Memory Update | [memory-update.md](memory-update.md) | Store |
| Checkpoint Save | [checkpoint-save.md](checkpoint-save.md) | LangGraph checkpointer |
| Checkpoint Restore | [checkpoint-restore.md](checkpoint-restore.md) | LangGraph checkpointer |
| Interrupt | [interrupt.md](interrupt.md) | LangGraph `interrupt()` |
| Resume | [resume.md](resume.md) | LangGraph `Command(resume=...)` |
| API Run Lifecycle | [api-run-lifecycle.md](api-run-lifecycle.md) | Thread/Start/Resume HTTP scaffold |
| Replay | [replay.md](replay.md) | LangGraph time travel |
| Skill Discovery | [skill-discovery.md](skill-discovery.md) | pgvector + metadata → index records |
| Skill Resolve | [skill-resolve.md](skill-resolve.md) | Skill Resolver Service (`lfs` \| `blob`) |
| Skill CI Sync | [skill-ci-sync.md](skill-ci-sync.md) | Validate + embed + index from `skill.yaml` |
| Skill Selection | [skill-selection.md](skill-selection.md) | Resolver policy hooks + pin authz |
| Skill Runtime Pipeline | [skill-runtime-pipeline.md](skill-runtime-pipeline.md) | Discover → context records → Resolve → Execute |
| skill.yaml → Manifest | [skill-yaml-to-manifest.md](skill-yaml-to-manifest.md) | Deterministic projection |
| Skill Composition | [skill-composition.md](skill-composition.md) | Platform |
| Reflection | [reflection.md](reflection.md) | Platform |
| Learning Promotion | [learning-promotion.md](learning-promotion.md) | Platform |
| Evaluation | [evaluation.md](evaluation.md) | Platform |
| Evaluate With Framework | [evaluate-with-framework.md](evaluate-with-framework.md) | DeepEval / LangSmith binding |
| Trace Emit | [trace-emit.md](trace-emit.md) | Graph + agent spans → Trace Store |
| Human Approval | [human-approval.md](human-approval.md) | Platform wraps resume |
| Artifact Generation | [artifact-generation.md](artifact-generation.md) | Platform |
