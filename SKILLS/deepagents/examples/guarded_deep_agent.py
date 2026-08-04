"""Path A — Deep Agent with permissions, HITL, PII, and tool-call limits.

Requires: pip install deepagents langchain langgraph
Set provider API key before running. HITL resume needs a checkpointer + resume flow.
"""

from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend
from langchain.agents.middleware import (
    PIIMiddleware,
    TodoListMiddleware,
    ToolCallLimitMiddleware,
)
from langgraph.checkpoint.memory import InMemorySaver


backend = CompositeBackend(
    default=StateBackend(),
    routes={},  # scratch-only; add "/workspace/" FilesystemBackend for disk
)

# First-match-wins: specific interrupts/denies before broad allows.
permissions = [
    FilesystemPermission(
        operations=["write"],
        paths=["/secrets/**", "/workspace/.env"],
        mode="interrupt",  # pause for approval (needs checkpointer)
    ),
    FilesystemPermission(
        operations=["read", "write"],
        paths=["/secrets/**"],
        mode="deny",
    ),
    FilesystemPermission(
        operations=["read", "write"],
        paths=["/**"],
        mode="allow",
    ),
]

checkpointer = InMemorySaver()

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    backend=backend,
    permissions=permissions,
    interrupt_on={
        "write_file": True,
        "edit_file": True,
        "delete": True,
    },
    middleware=[
        TodoListMiddleware(),
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
        ToolCallLimitMiddleware(thread_limit=40, run_limit=20),
    ],
    checkpointer=checkpointer,
    system_prompt=(
        "You are a careful assistant. Plan multi-step work with write_todos. "
        "Do not invent secrets or bypass path restrictions."
    ),
)

# Invoke with a stable thread_id so interrupts can resume:
# config = {"configurable": {"thread_id": "demo-1"}, "recursion_limit": 9999}
# result = agent.invoke({"messages": [...]}, config=config)
# On interrupt: inspect state, then Command(resume={"decisions": [...]}) with the same thread_id.
# Full resume example: human_in_the_loop.py
# Docs: https://docs.langchain.com/oss/python/deepagents/human-in-the-loop
