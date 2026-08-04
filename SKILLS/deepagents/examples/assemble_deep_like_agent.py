"""Path B — assemble a deep-agent-equivalent stack with create_agent.

Mirrors create_deep_agent middleware order (skills → FS → subagent → summarization
→ patch → todos). Prefer create_deep_agent for production unless you need a fork.

Requires: pip install deepagents langchain
"""

from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware

from deepagents.backends import StateBackend
from deepagents.middleware import (
    FilesystemMiddleware,
    PatchToolCallsMiddleware,
    SkillsMiddleware,
    SubAgentMiddleware,
)
from deepagents.middleware.subagents import GENERAL_PURPOSE_SUBAGENT
from deepagents.middleware.summarization import create_summarization_middleware

MODEL = "anthropic:claude-sonnet-4-6"
SKILL_SOURCES = ["/skills/"]  # must exist on the backend (or supply via State files=)

backend = StateBackend()

gp_middleware = [
    FilesystemMiddleware(backend=backend),
    create_summarization_middleware(MODEL, backend),
    PatchToolCallsMiddleware(),
    SkillsMiddleware(backend=backend, sources=SKILL_SOURCES),
]

gp = {
    **GENERAL_PURPOSE_SUBAGENT,
    "model": MODEL,
    "tools": [],
    "middleware": gp_middleware,
}

main_middleware = [
    SkillsMiddleware(backend=backend, sources=SKILL_SOURCES),
    FilesystemMiddleware(backend=backend),
    SubAgentMiddleware(backend=backend, subagents=[gp]),
    create_summarization_middleware(MODEL, backend),
    PatchToolCallsMiddleware(),
    TodoListMiddleware(),
]

ORCHESTRATOR = """You are a deep agent orchestrator.

For complex goals (≥3 steps): write_todos, mark the first in_progress, update as you go.
Use task() for heavy or context-isolated work; put full detail in the description.
Bias to one comprehensive subagent unless aspects are clearly independent.
Synthesize a user-facing answer yourself — subagent reports are not shown to the user.
When a skill matches, read_file its path with limit=1000 and follow it.
"""

agent = create_agent(
    MODEL,
    tools=[],
    system_prompt=ORCHESTRATOR,
    middleware=main_middleware,
)

# config = {"configurable": {"thread_id": "path-b-1"}, "recursion_limit": 9999}
# agent.invoke({"messages": [{"role": "user", "content": "..."}]}, config=config)
