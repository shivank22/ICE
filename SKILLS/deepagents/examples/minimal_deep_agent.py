"""Path A — minimal Deep Agent with create_deep_agent.

Requires: pip install deepagents langchain
Set provider API key (e.g. ANTHROPIC_API_KEY) before running.
"""

from deepagents import create_deep_agent


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[get_weather],
    system_prompt="You are a helpful assistant. Prefer tools over guessing.",
)

if __name__ == "__main__":
    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "What is the weather in San Francisco?"}
            ]
        }
    )
    print(result["messages"][-1].content)
