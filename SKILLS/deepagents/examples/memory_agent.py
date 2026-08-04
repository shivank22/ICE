"""Long-term memory via StoreBackend + memory= AGENTS.md path.

Requires: pip install deepagents langgraph
In production use a durable Store (e.g. PostgresStore) and real user identity namespaces.
"""

from langchain_core.utils.uuid import uuid7

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Seed user-scoped memory
store.put(
    ("demo-user",),
    "/memories/AGENTS.md",
    create_file_data(
        """## Preferences
- Prefer concise answers
- Use Python examples when showing code
"""
    ),
)

backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/memories/": StoreBackend(
            namespace=lambda _rt: ("demo-user",),
        ),
    },
)

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    memory=["/memories/AGENTS.md"],
    backend=backend,
    store=store,
    system_prompt=(
        "Respect preferences in memory. When the user asks you to remember "
        "something lasting, update /memories/AGENTS.md with edit_file."
    ),
)

# Thread 1 — learn
# agent.invoke(
#     {"messages": [{"role": "user", "content": "Remember that I prefer TypeScript examples."}]},
#     config={"configurable": {"thread_id": str(uuid7())}},
# )
# Thread 2 — recall (new thread_id, same Store namespace)
# agent.invoke(
#     {"messages": [{"role": "user", "content": "Show a hello-world snippet."}]},
#     config={"configurable": {"thread_id": str(uuid7())}},
# )
