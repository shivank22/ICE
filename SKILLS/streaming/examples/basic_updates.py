"""Stream state updates with version=v2 StreamPart format."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    topic: str
    joke: str


def refine_topic(state: State):
    return {"topic": state["topic"] + " and cats"}


def generate_joke(state: State):
    return {"joke": f"This is a joke about {state['topic']}"}


graph = (
    StateGraph(State)
    .add_node(refine_topic)
    .add_node(generate_joke)
    .add_edge(START, "refine_topic")
    .add_edge("refine_topic", "generate_joke")
    .add_edge("generate_joke", END)
    .compile()
)

if __name__ == "__main__":
    for chunk in graph.stream(
        {"topic": "ice cream"},
        stream_mode="updates",
        version="v2",
    ):
        if chunk["type"] == "updates":
            for node_name, state in chunk["data"].items():
                print(f"Node `{node_name}` updated: {state}")
