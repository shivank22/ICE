"""Path A — HITL with interrupt_on, checkpointer, and Command resume.

Requires: pip install deepagents langchain langgraph
Docs: https://docs.langchain.com/oss/python/deepagents/human-in-the-loop
"""

from langchain.tools import tool
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from deepagents import create_deep_agent


@tool
def remove_file(path: str) -> str:
    """Delete a file from the filesystem."""
    return f"Deleted {path}"


@tool
def notify_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Sent email to {to}"


checkpointer = MemorySaver()

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[remove_file, notify_email],
    interrupt_on={
        "remove_file": True,  # approve | edit | reject | respond
        "notify_email": {"allowed_decisions": ["approve", "reject"]},
    },
    checkpointer=checkpointer,
)

config = {"configurable": {"thread_id": str(uuid7())}, "recursion_limit": 9999}

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Delete temp.txt"}]},
    config=config,
    version="v2",
)

if result.interrupts:
    value = result.interrupts[0].value
    for action in value["action_requests"]:
        print(f"pending: {action['name']} {action['args']}")

    # One decision per action_request, in order
    result = agent.invoke(
        Command(
            resume={
                "decisions": [
                    {
                        "type": "reject",
                        "message": "User rejected deleting temp.txt. Do not retry deletion.",
                    }
                ]
            }
        ),
        config=config,
        version="v2",
    )

print(result.value["messages"][-1].content)
