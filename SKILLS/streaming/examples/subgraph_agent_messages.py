"""Stream messages from a nested create_agent node (requires subgraphs=True).

Requires a configured chat-model provider. Illustrates the nested-agent gotcha:
without subgraphs=True, parent messages streams miss inner LLM tokens.
"""

from typing import Annotated, TypedDict

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]


model = init_chat_model(model="gpt-4.1-mini")
agent = create_agent(model, tools=[], state_schema=State)

graph = (
    StateGraph(State)
    .add_node("agent", agent)
    .add_edge(START, "agent")
    .add_edge("agent", END)
    .compile()
)

if __name__ == "__main__":
    for chunk in graph.stream(
        {"messages": [{"role": "user", "content": "Say hello in one short sentence."}]},
        stream_mode="messages",
        subgraphs=True,
        version="v2",
    ):
        if chunk["type"] == "messages":
            msg, metadata = chunk["data"]
            if msg.content:
                # ns is () for root; non-empty for the nested agent subgraph
                print(f"[{chunk['ns']}] {msg.content}", end="", flush=True)
    print()
