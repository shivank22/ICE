# Prompt fragments

Verbatim / near-verbatim templates from Deep Agents and LangChain sources. Use when rebuilding prompts (Path B) or documenting behavior. Prefer importing middleware over copying when possible — fragments stay in sync with packages.

## Skills (`SkillsMiddleware`)

Source: `deepagents.middleware.skills.SKILLS_SYSTEM_PROMPT`

```text
## Skills System

You have access to a skills library that provides specialized capabilities and domain knowledge.

{skills_locations}{skills_load_warnings}

Sources labeled "Deepagents" are specific to this agent tool; sources labeled "Agents" are shared across all agent tools on this machine.

**Available Skills:**

{skills_list}

**How to Use Skills (Progressive Disclosure):**

Skills follow a **progressive disclosure** pattern - you see their name and description above, but only read full instructions when needed:

1. **Recognize when a skill applies**: Check if the user's task matches a skill's description
2. **Read the skill's full instructions**: Use `read_file` on the path shown in the skill list above.
   Pass `limit=1000` since the default of 100 lines is too small for most skill files.
3. **Follow the skill's instructions**: SKILL.md contains step-by-step workflows, best practices, and examples
4. **Access supporting files**: Skills may include helper scripts, configs, or reference docs - use absolute paths
```

Listing line shape: `- **{name}**: {description} -> Read `{path}` for full instructions`.

## write_todos system (`TodoListMiddleware`)

Source: `langchain.agents.middleware.todo.WRITE_TODOS_SYSTEM_PROMPT` (summary of key mandates):

- Use for complex objectives; break into smaller steps
- Mark completed as soon as a step is done — do not batch
- Skip for simple few-step requests
- Never call `write_todos` multiple times in parallel
- Revise the list as you go
- Final answer in a message **after** the last `write_todos` call

Tool description adds: use for ≥3 steps; mark first `in_progress` immediately; keep ≥1 `in_progress` until done; specific actionable items.

## task tool (`SubAgentMiddleware`)

Source: `TASK_TOOL_DESCRIPTION`

```text
Launch an ephemeral subagent to handle a complex, multi-step task in an isolated context window.

Available agent types and the tools they have access to:
{available_agents}

Specify subagent_type to select the agent. Usage notes:
- Launch multiple agents concurrently when their tasks are independent, using a single message with multiple tool calls.
- Each invocation is stateless: the agent sees only the prompt you give it and returns a single final report. Put full detail in the prompt and state exactly what it should return.
- The agent's report is not shown to the user; relay a summary yourself.
- Tell the agent whether to create content, analyze, or only research, since it cannot see the user's intent.
- If an agent's description says to use it proactively, do so without waiting to be asked.
- When only general-purpose is available, use it for any complex, context-heavy task; it has the same capabilities as the main agent.
```

## General-purpose subagent

`DEFAULT_GENERAL_PURPOSE_DESCRIPTION`:

```text
General-purpose agent for researching complex questions, searching for files and content,
and executing multi-step tasks. When you are searching for a keyword or file and are not
confident that you will find the right match in the first few tries use this agent to
perform the search for you. This agent has access to all tools as the main agent.
```

`DEFAULT_SUBAGENT_PROMPT`:

```text
In order to complete the objective that the user asks of you, you have access to a number of standard tools.

The calling agent only sees your final assistant message, not your intermediate work, tool results, or status tracking. Ensure your final
response contains the complete answer.
```

## Orchestrator planning template

See copyable full prompt: [../examples/orchestrator_planning_prompt.md](../examples/orchestrator_planning_prompt.md).

Pattern: Plan (`write_todos`) → Context → Delegate (`task`) → Verify → Synthesize. Bias to one comprehensive subagent; parallelize only for comparisons / independent aspects.

## Legacy base prompt

`_LEGACY_BASE_AGENT_PROMPT` / deprecated `BASE_AGENT_PROMPT` in `graph.py` taught Understand → Act → Verify. **Not applied by default** anymore — supply your own `system_prompt` / memory / skills.

## See also

- [skills-loading.md](skills-loading.md)
- [planning-and-decomposition.md](planning-and-decomposition.md)
