from flask import Flask, request, jsonify
import pdfplumber
import os
import google.generativeai as genai
from dotenv import load_dotenv
from utils import clean_text

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ✅ Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("⚠️ WARNING: GEMINI_API_KEY not found in environment variables")
else:
    print("✅ Gemini API key loaded successfully")
    genai.configure(api_key=api_key)


# 🧾 Extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return clean_text(text)


# 🧠 Main Summarization Route
@app.route("/summarize", methods=["POST"])
def summarize_pdf():
    """
    Accepts a PDF file, extracts text, and generates a structured summary
    using the Gemini API. Returns JSON output.
    """
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    text = extract_text_from_pdf(file)
    if len(text.strip()) == 0:
        return jsonify({"error": "Empty or unreadable PDF"}), 400

    # Truncate if too long
    if len(text) > 15000:
        text = text[:15000]

    # Combined summary prompt (quick + full merged)
    prompt = f"""
    You are a professional legal document summarizer.
    Analyze the following Indian court judgment and return the following details
    in clean JSON format — no extra text, code blocks, or explanations.

    {{
        "case_title": "...",
        "petitioner": "...",
        "respondent": "...",
        "judges": "...",
        "court_name": "...",
        "date_of_judgment": "...",
        "sections_or_acts_mentioned": "...",
        "final_verdict_or_order": "...",
        "case_summary": "A short 2–3 sentence summary describing what the case is about."
    }}

    Text of the judgment:
    {text}
    """

    # ✅ Send prompt to Gemini
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.5,
                max_output_tokens=2048,
            )
        )

        if response and response.candidates and response.candidates[0].content:
            summary = response.text.strip()
            return jsonify({"summary": summary})
        else:
            return jsonify({"error": "Model returned an empty or blocked response"}), 500

    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return jsonify({"error": f"Gemini API Error: {str(e)}"}), 500


# 🚀 Run app
if __name__ == "__main__":
    app.run(debug=True)
