"""Stream LLM tokens with stream_mode=messages and version=v2.

Requires a configured chat-model provider (e.g. OPENAI_API_KEY).
"""

from dataclasses import dataclass

from langchain.chat_models import init_chat_model
from langgraph.graph import START, StateGraph


@dataclass
class MyState:
    topic: str
    joke: str = ""


model = init_chat_model(model="gpt-4.1-mini")


def call_model(state: MyState):
    # Message events emit even when using .invoke (not only .stream)
    model_response = model.invoke(
        [{"role": "user", "content": f"Generate a joke about {state.topic}"}]
    )
    return {"joke": model_response.content}


graph = (
    StateGraph(MyState)
    .add_node(call_model)
    .add_edge(START, "call_model")
    .compile()
)

if __name__ == "__main__":
    for chunk in graph.stream(
        {"topic": "ice cream"},
        stream_mode="messages",
        version="v2",
    ):
        if chunk["type"] == "messages":
            message_chunk, metadata = chunk["data"]
            if message_chunk.content:
                print(message_chunk.content, end="|", flush=True)
    print()
