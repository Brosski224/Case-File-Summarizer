from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv

# Optional: fallback clean_text
try:
    from utils import clean_text
except ImportError:
    def clean_text(t): return t.strip()

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found in environment variables")
else:
    print("Gemini API key loaded successfully")
    genai.configure(api_key=api_key)

# Extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return clean_text(text)


@app.route("/list-models", methods=["GET"])
def list_models():
    try:
        models = genai.list_models()
        model_names = [model.name for model in models]
        return jsonify({"available_models": model_names})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/test-gemini", methods=["GET"])
def test_gemini():
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Say hello in a friendly way")
        return jsonify({"status": "success", "response": response.text})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/summarize", methods=["POST"])
def summarize_pdf():
    file = request.files.get("file")
    mode = request.form.get("mode", "quick")
    model_choice = request.form.get("model_choice", "gemini").lower()

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    text = extract_text_from_pdf(file)
    if len(text.strip()) == 0:
        return jsonify({"error": "Empty or unreadable PDF"}), 400

    if len(text) > 15000:
        text = text[:15000]

    if mode == "quick":
        prompt = f"""
        You are a professional legal judgment summarizer.
        Extract and return the following details from the given Indian court judgment **in clean JSON format**.

        Return output STRICTLY in this JSON structure (no extra text or explanations):

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

    else:
        prompt = f"""
        You are a professional legal document summarizer.
        Create a **detailed summary** of this Indian court judgment in structured paragraphs,
        focusing on facts, issues, arguments, reasoning, and verdict.
        {text}
        """

    try:
        if model_choice == "groq":
            GROQ_API_KEY = os.getenv("GROQ_API_KEY")
            if not GROQ_API_KEY:
                return jsonify({"error": "Groq API key not found"}), 500

            groq_response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 2048
                },
                timeout=150
            )

            if groq_response.status_code == 200:
                summary = groq_response.json()["choices"][0]["message"]["content"]
                return jsonify({"summary": summary, "model_used": "Groq (Llama 3.1 70B)"})
            else:
                return jsonify({"error": f"Groq API error: {groq_response.text}"}), 500

        else:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                )
            )

            if response.candidates and response.candidates[0].content:
                summary = response.text
                return jsonify({"summary": summary, "model_used": "Gemini 2.5 Flash"})
            else:
                return jsonify({"error": "Response was blocked or empty"}), 500

    except Exception as e:
        print(f"Model Error: {str(e)}")
        return jsonify({"error": f"Model Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
