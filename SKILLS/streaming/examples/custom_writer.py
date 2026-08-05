"""Emit and consume custom stream events via get_stream_writer()."""

from typing import TypedDict

from langgraph.config import get_stream_writer
from langgraph.graph import START, StateGraph


class State(TypedDict):
    topic: str
    joke: str


def generate_joke(state: State):
    writer = get_stream_writer()
    writer({"status": "thinking of a joke..."})
    return {
        "joke": (
            f"Why did the {state['topic']} go to school? "
            "To get a sundae education!"
        )
    }


graph = (
    StateGraph(State)
    .add_node(generate_joke)
    .add_edge(START, "generate_joke")
    .compile()
)

if __name__ == "__main__":
    for chunk in graph.stream(
        {"topic": "ice cream"},
        stream_mode=["updates", "custom"],
        version="v2",
    ):
        if chunk["type"] == "updates":
            for node_name, state in chunk["data"].items():
                print(f"Node {node_name} updated: {state}")
        elif chunk["type"] == "custom":
            print(f"Status: {chunk['data']['status']}")
