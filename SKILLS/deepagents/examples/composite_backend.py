"""Composite backend: State scratch + /workspace disk + /memories Store.

Requires: pip install deepagents langgraph
Replace root_dir with an absolute project path. Provide a real Store in production
(e.g. PostgresStore) instead of InMemoryStore.
"""

from deepagents import create_deep_agent
from deepagents.backends import (
    CompositeBackend,
    FilesystemBackend,
    StateBackend,
    StoreBackend,
)
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

backend = CompositeBackend(
    default=StateBackend(),
    routes={
        # Project files on disk (virtual_mode sandboxes paths under root_dir)
        "/workspace/": FilesystemBackend(
            root_dir="/absolute/path/to/project",
            virtual_mode=True,
        ),
        # Cross-thread memory — always set a namespace factory for multi-user
        "/memories/": StoreBackend(
            namespace=lambda rt: (
                # Prefer rt.server_info.user.identity in deployed LangGraph apps
                "demo-user",
            ),
        ),
    },
)

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    backend=backend,
    store=store,
    system_prompt=(
        "Scratch and large tool results stay in state. "
        "Project files live under /workspace/. "
        "Persist lasting preferences under /memories/."
    ),
)

# Internals (/large_tool_results/, /conversation_history/) stay on StateBackend
# and do not pollute the project tree — unlike bare FilesystemBackend.
