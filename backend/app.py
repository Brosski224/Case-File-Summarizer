from flask import Flask, request, jsonify
import pdfplumber
import os
import google.generativeai as genai
from dotenv import load_dotenv
from utils import clean_text

load_dotenv()

app = Flask(__name__)

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
    """List available Gemini models"""
    try:
        models = genai.list_models()
        model_names = [model.name for model in models]
        return jsonify({"available_models": model_names})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/test-gemini", methods=["GET"])
def test_gemini():
    """Test route to verify Gemini API is working"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Say hello in a friendly way")
        return jsonify({"status": "success", "response": response.text})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/summarize", methods=["POST"])
def summarize_pdf():
    file = request.files.get("file")
    mode = request.form.get("mode", "quick")  # 'quick' or 'full'

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    text = extract_text_from_pdf(file)
    if len(text.strip()) == 0:
        return jsonify({"error": "Empty or unreadable PDF"}), 400

    if len(text) > 15000:
        text = text[:15000]  # prevent model overload

        # Different prompts for quick / full summary
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
                    "final_verdict_or_order": "..."
                    "case_summary": "A short 2–3 sentence summary describing what the case is about."

                }}

                Text of the judgment:
                {text}
                """

        
    # Send to Gemini
    try:
        # Use gemini-2.5-flash which has better rate limits for free tier
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generate content with safety settings
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048,
            )
        )
        
        # Check if response was blocked
        if response.candidates and response.candidates[0].content:
            summary = response.text
            return jsonify({"summary": summary})
        else:
            return jsonify({"error": "Response was blocked or empty"}), 500
            
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")  # For debugging
        return jsonify({"error": f"Gemini API Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
