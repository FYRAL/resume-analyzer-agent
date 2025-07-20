# nodes.py
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("Missing OPENAI_API_KEY in environment")

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=openai_key 
)

# Shared state schema
class SharedState(TypedDict):
    resume_text: str
    job_desc: str
    name: str
    email: str
    phone: str
    years_experience: float
    skills: list[str]
    pre_screening_status: Literal["Pass", "Fail"]
    skill_analysis: dict
    final_disposition: Literal["Interview", "Phone Screen", "Rejected"]
    rejection_reason: str



# Node 1: Ingestion & Pre-screening
def pre_screen_node(state: SharedState) -> Command[Literal["tech_analysis","reject"]]:
    prompt = PromptTemplate(
        input_variables=["resume","job"],
        template="""
Extract name, email, phone, total years experience and skill list from resume:
{resume}
Job requirements:
{job}
Return JSON with keys: name, email, phone, years_experience (number), skills (list of strings), knockout_failures (list).
"""
    )
    resp = llm.invoke(prompt.format_prompt(resume=state["resume_text"], job=state["job_desc"]))
    data = resp.content  # parse JSON
    # apply parsing logic here...
    state.update({
        "name": "...", "email": "...", "phone": "...",
        "years_experience": 5.0, "skills": ["Python","SQL"]
    })
    if state["years_experience"] < 3:  # example knockout
        state["pre_screening_status"] = "Fail"
        state["rejection_reason"] = "Insufficient experience"
        return Command(update=state, goto="reject")
    state["pre_screening_status"] = "Pass"
    return Command(update=state, goto="tech_analysis")

# Node 2: Technical Skill Analysis
def tech_analysis_node(state: SharedState) -> Command[Literal["interview","phone_screen","reject"]]:
    required = {"Python", "React", "SQL"}
    have = set(state["skills"])
    matched = list(have & required)
    missing = list(required - have)
    additional = list(have - required)
    score = int(len(matched)/len(required)*100)
    state["skill_analysis"] = {
        "matched": matched,
        "missing": missing,
        "additional": additional,
        "score": score
    }
    if score > 80:
        state["final_disposition"] = "Interview"
        return Command(update=state, goto="interview")
    elif score >= 50:
        state["final_disposition"] = "Phone Screen"
        return Command(update=state, goto="phone_screen")
    state["final_disposition"] = "Rejected"
    state["rejection_reason"] = "Low skill match"
    return Command(update=state, goto="reject")

# Nodes 3-5: Interview, Phone Screening, Rejection
def interview_node(state: SharedState) -> SharedState:
    state["final_disposition"] = "Interview"
    return state

def phone_screen_node(state: SharedState) -> SharedState:
    state["final_disposition"] = "Phone Screen"
    return state

def reject_node(state: SharedState) -> SharedState:
    state["final_disposition"] = "Rejected"
    # ensure rejection_reason exists
    state.setdefault("rejection_reason", "Did not meet requirements")
    return state

# Node 6: Generate ATS payload
def generate_payload_node(state: SharedState) -> SharedState:
    # no modification, only output end state
    return state

# Build graph
def build_agent_graph() -> StateGraph[SharedState]:
    graph = StateGraph(SharedState)
    graph.add_node("pre_screen", pre_screen_node)
    graph.add_node("tech_analysis", tech_analysis_node)
    graph.add_node("interview", interview_node)
    graph.add_node("phone_screen", phone_screen_node)
    graph.add_node("reject", reject_node)
    graph.add_node("generate_payload", generate_payload_node)


    graph.add_edge(START, "pre_screen")
    graph.add_edge("interview", "generate_payload")
    graph.add_edge("phone_screen", "generate_payload")
    graph.add_edge("reject", "generate_payload")
    graph.add_edge("generate_payload", END)

    return graph.compile()

