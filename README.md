#  Resume Analyzer Agent

**Resume Analyzer Agent** is an AI‑powered pipeline that extracts key details from resumes and compares them to a job description. It evaluates technical skills, pre‑screens, and provides a clear recommendation (Interview / Phone Screen / Rejected).

##  Features

- Parses PDF resumes to extract name, email, phone, years of experience, and skills.
- Compares extracted skills against job requirements.
- Scores candidate based on skill match.
- Provides natural-language summary with strengths, weaknesses, and final recommendation.

##  Tech Stack

| Component     | Technology                      |
|---------------|----------------------------------|
| Backend       | Python, Flask, LangGraph, Groq  |
| PDF parsing   | PyPDF2 or pdfminer              |
| LLM           | ChatGroq (Groq's API)          |
| Frontend UI   | React + Vite + Tailwind CSS    |
| state management | LangGraph StateGraph         |



├── backend/ # Flask server
│ ├── server.py # HTTP endpoints
│ ├── agent_graph.py # LangGraph flow
│ └── tools.py # PDF & resume parsing logic
├── frontend/ # React UI for file upload / display
├── streamlit_app.py # (optional) streamlit demo
├── requirements.txt # Python dependencies
├── package.json # Frontend dependencies
└── README.md # Project overview


# Usage
Open the web UI.

Upload a PDF resume.

Paste the job description.

Click "Analyze".

View skill match, disposition, and reasoning.