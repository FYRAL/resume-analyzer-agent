# streamlit_app.py

import streamlit as st
import requests
from io import BytesIO
from PyPDF2 import PdfReader
import fitz  # PyMuPDF

def extract_text_pymupdf(pdf_bytes: BytesIO) -> str:
    doc = fitz.open(stream=pdf_bytes.read(), filetype="pdf")
    text = "".join(page.get_text("text") for page in doc)
    doc.close()
    return text

st.set_page_config(page_title="Resume + PDF Analyzer", layout="wide")
st.title("📝 PDF-Based Resume Analysis")

# Remove manual resume text input
uploaded_pdf = st.file_uploader("Upload your resume (PDF)", type="pdf")
job_desc = st.text_area("Job Description", height=150)

if uploaded_pdf:
    if st.button("Analyze PDF Resume"):
        with st.spinner("Extracting from PDF and analyzing..."):
            pdf_bytes = BytesIO(uploaded_pdf.read())
            resume_text = extract_text_pymupdf(BytesIO(pdf_bytes.getvalue()))

            try:
                resp = requests.post(
                    "http://localhost:5000/api/analyze",
                    json={"resume_text": resume_text, "job_desc": job_desc},
                    timeout=30
                )
                resp.raise_for_status()
                st.success("Analysis complete!")
                st.json(resp.json())
            except Exception as e:
                st.error(f"API error: {e}")
else:
    st.info("Please upload a PDF resume to begin analysis.")
