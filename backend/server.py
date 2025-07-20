from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
from backend.agent_graph import compiled_graph   # or compiled_graph usage

app = Flask(__name__)
CORS(app)  # Enables cross-origin requests

@app.route('/api/analyze', methods=['POST'])
def analyze():
    print("➡️ /api/analyze was called!")  # Debug log
    resume_pdf = request.files.get("resume_pdf")
    job_desc = request.form.get("job_desc")
    if not resume_pdf or not job_desc:
        print("❌ Missing file or job_desc", resume_pdf, job_desc)
        return jsonify({"error": "Missing inputs"}), 400

    pdf_text = "\n".join(page.extract_text() for page in PdfReader(resume_pdf).pages)
    print("📄 Extracted PDF text length:", len(pdf_text))
    result = compiled_graph.invoke({
    "resume_text": pdf_text,
    "job_desc": job_desc
})
    print("🧾 Pipeline result:", result)
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
