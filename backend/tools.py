# tools.py
import os
import json
from dotenv import load_dotenv
from typing import TypedDict
from langchain_groq.chat_models import ChatGroq




class ExtractedEntities(TypedDict):
    name: str
    email: str
    phone: str
    years_experience: float
    skills: list[str]
    knockout_failures: list[str]

def extract_resume_entities(resume: str, job: str) -> ExtractedEntities:
    """
    Use OpenAI function-calling API to parse resume + job description
    and output structured entity JSON.
    """
    response = ChatGroq.ChatCompletion.create(
         model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a resume-parsing assistant."},
            {"role": "user", "content": f"Extract name, email, phone, years_experience (as number), skills (list), "
                                       f"and list any knockout failures (missing minimum requirements) from this resume:\n\n{resume}\n\nJob description:\n{job}"}
        ],
        functions=[
            {
                "name": "extract_resume_entities",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "years_experience": {"type": "number"},
                        "skills": {"type": "array", "items": {"type": "string"}},
                        "knockout_failures": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["name", "email", "years_experience", "skills", "knockout_failures"]
                }
            }
        ],
        function_call={"name": "extract_resume_entities"}
    )
    call_args = response.choices[0].message["function_call"]["arguments"]
    data = json.loads(call_args)
    return ExtractedEntities(
        name=data["name"],
        email=data["email"],
        phone=data["phone"],
        years_experience=data["years_experience"],
        skills=data["skills"],
        knockout_failures=data["knockout_failures"]
    )
