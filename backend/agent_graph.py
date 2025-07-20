# agent_graph.py
import os
import json
from typing_extensions import TypedDict, Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from backend.tools import ExtractedEntities, extract_resume_entities
from langchain_groq.chat_models import ChatGroq
from pydantic import BaseModel
from typing import Optional, Dict, Any

#  Pydantic model for clean reasoning input
class AnalysisInput(BaseModel):
    name: str
    pre_screening_status: str
    skill_analysis: Dict[str, Any]
    final_disposition: str
    rejection_reason: Optional[str] = None

# Shared candidate state
class SharedState(TypedDict, total=False):
    resume_text: str
    job_desc: str
    name: str
    email: str
    phone: str
    years_experience: float
    skills: list[str]
    knockout_failures: list[str]
    pre_screening_status: Literal["Pass", "Fail"]
    skill_analysis: dict
    final_disposition: Literal["Interview", "Phone Screen", "Rejected"]
    rejection_reason: str
    analysis_reasoning: str  # new field to hold natural-language reasoning

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=os.getenv("GROQ_API_KEY"))
llm_structured = llm.with_structured_output(ExtractedEntities, method="json_mode", include_raw=False)

def pre_screen_node(state: SharedState) -> Command:
    response = llm_structured.invoke([
        {"role": "system", "content": (
            "Respond in valid JSON exactly matching schema. "
            "`skills` list must include everything from resume."
        )},
        {"role": "user", "content": state["resume_text"]},
        {"role": "user", "content": state["job_desc"]}
    ])
    entities: dict = response
    if "skills" not in entities or not isinstance(entities["skills"], list):
        entities["skills"] = [
            skill for skill in ["Python", "SQL", "React", "Docker", "AWS"]
            if skill.lower() in state["resume_text"].lower()
        ]
    state.update(entities)
    if state.get("knockout_failures"):
        state["pre_screening_status"] = "Fail"
        state["rejection_reason"] = ", ".join(state["knockout_failures"])
        return Command(update=state, goto="reject")
    state["pre_screening_status"] = "Pass"
    return Command(update=state, goto="tech_analysis")

def tech_analysis_node(state: SharedState) -> Command:
    skills = state.get("skills", []) or []
    required = {"Python", "SQL", "React"}
    have = set(skills)
    matched = [s for s in skills if s in required]
    missing = list(required - have)
    additional = [s for s in skills if s not in required]
    score = int(len(matched) / len(required) * 100) if required else 0
    state["skill_analysis"] = {"matched": matched, "missing": missing, "additional": additional, "score": score}
    if score > 80:
        state["final_disposition"] = "Interview"
        return Command(update=state, goto="interview")
    if score >= 50:
        state["final_disposition"] = "Phone Screen"
        return Command(update=state, goto="phone_screen")
    state["final_disposition"] = "Rejected"
    state["rejection_reason"] = "Low skill match"
    return Command(update=state, goto="reject")

def interview_node(state: SharedState) -> SharedState:
    state["final_disposition"] = "Interview"
    return state

def phone_screen_node(state: SharedState) -> SharedState:
    state["final_disposition"] = "Phone Screen"
    return state

def reject_node(state: SharedState) -> SharedState:
    state["final_disposition"] = "Rejected"
    state.setdefault("rejection_reason", "Did not meet requirements")
    return state

def payload_node(state: SharedState) -> SharedState:
    print("\n Payload JSON:")
    print(json.dumps(state, indent=2))
    return state

# Reasoning node: adds natural-language explanation
def reasoning_node(state: SharedState) -> SharedState:
    # Extract values from the pipeline result
    name = state.get("name", "The candidate")
    final = state["final_disposition"]
    strengths = state["skill_analysis"]["matched"]
    missing = state["skill_analysis"]["missing"]

    # Build a clear English summary
    reasoning = f"""
{name} shows strengths in: {', '.join(strengths) or 'none detected'}.
However, they're missing: {', '.join(missing) or 'none'}.
💡 **Recommendation:** {final}.
"""

    if final == "Rejected" and state.get("rejection_reason"):
        reasoning += f" 🔍 **Reason:** {state['rejection_reason']}."

    state["analysis_reasoning"] = reasoning.strip()
    return state




# Build the graph
graph = StateGraph(SharedState)
graph.add_node("pre_screen", pre_screen_node)
graph.add_node("tech_analysis", tech_analysis_node)
graph.add_node("interview", interview_node)
graph.add_node("phone_screen", phone_screen_node)
graph.add_node("reject", reject_node)
graph.add_node("payload", payload_node)
graph.add_node("reasoning", reasoning_node)

graph.add_edge(START, "pre_screen")
graph.add_edge("pre_screen", "tech_analysis")
graph.add_conditional_edges(
    "tech_analysis",
    lambda state: (
        "interview" if state["skill_analysis"]["score"] > 80 else
        "phone_screen" if state["skill_analysis"]["score"] >= 50 else
        "reject"
    ),
    {"interview": "interview", "phone_screen": "phone_screen", "reject": "reject"}
)
graph.add_edge("interview", "payload")
graph.add_edge("phone_screen", "payload")
graph.add_edge("reject", "payload")
graph.add_edge("payload", "reasoning")
graph.add_edge("reasoning", END)

compiled_graph = graph.compile()
