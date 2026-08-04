"""Dynamic subagents via CodeInterpreterMiddleware (beta).

Requires:
  pip install deepagents "langchain-quickjs>=0.2.0"
  Python >= 3.11

Phrase the user ask as a "workflow" to bias toward interpreter orchestration.
"""

from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    subagents=[
        {
            "name": "reviewer",
            "description": (
                "Reviews code for security and correctness issues, "
                "citing file paths, line numbers, and severity."
            ),
            "system_prompt": (
                "You are a security-focused code reviewer. "
                "Report concrete issues with severity (high/medium/low)."
            ),
        },
    ],
    # ptc=["glob"] lets interpreter JS call glob before fan-out
    middleware=[CodeInterpreterMiddleware(ptc=["glob", "ls"])],
)

# Example trigger — "workflow" opts into code-orchestrated task() fan-out:
# agent.invoke({
#     "messages": [{
#         "role": "user",
#         "content": (
#             "Run a workflow that reviews every Python file under /workspace/src "
#             "and summarizes the top risks."
#         ),
#     }]
# })

# Notes:
# - Interpreter task() bypasses parent interrupt_on per dispatch — gate `eval` for HITL.
# - Disable dynamic subagents only: CodeInterpreterMiddleware(subagents=False)
# - For a single delegation, skip "workflow" and use the normal task tool path.
