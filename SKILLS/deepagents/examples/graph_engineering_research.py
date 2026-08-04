"""Graph-engineered research workflow skeleton (LangGraph).

Requires: pip install langgraph langchain
Essay: https://www.analyticsvidhya.com/blog/2026/07/graph-engineering/
Wire real models / structured review before production use.
"""

from typing import Literal

from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class ResearchState(TypedDict, total=False):
    topic: str
    plan: str
    evidence: str
    draft: str
    feedback: str
    evaluator_approved: bool
    human_approved: bool
    revision_count: int


def planner_node(state: ResearchState) -> ResearchState:
    return {"plan": f"Plan for: {state['topic']}", "revision_count": 0}


def researcher_node(state: ResearchState) -> ResearchState:
    return {"evidence": f"Evidence brief under plan: {state.get('plan', '')}"}


def writer_node(state: ResearchState) -> ResearchState:
    return {"draft": f"Draft from evidence: {state.get('evidence', '')}"}


def evaluator_node(state: ResearchState) -> ResearchState:
    # Replace with structured LLM review in real systems
    approved = state.get("revision_count", 0) >= 1
    return {
        "evaluator_approved": approved,
        "feedback": "" if approved else "Add limitations section.",
    }


def revision_node(state: ResearchState) -> ResearchState:
    return {
        "draft": state.get("draft", "") + "\n[revised]",
        "revision_count": state.get("revision_count", 0) + 1,
    }


def human_review_node(state: ResearchState) -> ResearchState:
    decision = interrupt(
        {
            "message": "Review this article before finalization.",
            "draft": state.get("draft", ""),
            "allowed_actions": ["approve", "reject"],
        }
    )
    return {
        "human_approved": decision.get("action") == "approve",
        "feedback": decision.get("feedback", state.get("feedback", "")),
    }


def finalize_node(state: ResearchState) -> ResearchState:
    return {"human_approved": True}


def route_after_evaluation(
    state: ResearchState,
) -> Literal["revise", "human_review"]:
    if state.get("evaluator_approved") or state.get("revision_count", 0) >= 2:
        return "human_review"
    return "revise"


def route_after_human_review(
    state: ResearchState,
) -> Literal["finalize", "revise"]:
    if state.get("human_approved"):
        return "finalize"
    return "revise"


builder = StateGraph(ResearchState)
builder.add_node("planner", planner_node)
builder.add_node("researcher", researcher_node)
builder.add_node("writer", writer_node)
builder.add_node("evaluator", evaluator_node)
builder.add_node("revise", revision_node)
builder.add_node("human_review", human_review_node)
builder.add_node("finalize", finalize_node)

builder.add_edge(START, "planner")
builder.add_edge("planner", "researcher")
builder.add_edge("researcher", "writer")
builder.add_edge("writer", "evaluator")
builder.add_conditional_edges(
    "evaluator",
    route_after_evaluation,
    {"revise": "revise", "human_review": "human_review"},
)
builder.add_edge("revise", "evaluator")
builder.add_conditional_edges(
    "human_review",
    route_after_human_review,
    {"finalize": "finalize", "revise": "revise"},
)
builder.add_edge("finalize", END)

graph = builder.compile(checkpointer=InMemorySaver())

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "graph-engineering-demo"}}
    result = graph.invoke({"topic": "Graph engineering for agents"}, config=config)
    # On interrupt: resume with same thread_id
    # from langgraph.types import Command
    # graph.invoke(Command(resume={"action": "approve", "feedback": "OK"}), config=config)
    print(result)
