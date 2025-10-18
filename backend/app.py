from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import os
import google.generativeai as genai
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Optional clean_text fallback
try:
    from utils import clean_text
except ImportError:
    def clean_text(t): return t.strip()

load_dotenv()

app = Flask(__name__)
CORS(app)

# === Gemini Configuration ===
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("⚠️ WARNING: GEMINI_API_KEY not found in environment variables")
else:
    print("✅ Gemini API key loaded successfully")
    genai.configure(api_key=api_key)


# === Helper: Extract PDF text ===
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return clean_text(text)


# === Helper: Chunking ===
def chunk_text(text, chunk_size=2500, overlap=200):
    """Split text into overlapping chunks for better context preservation."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


# === Helper: Safe Gemini Call with Retry ===
def safe_gemini_generate(model, prompt, retries=1):
    """Safely call Gemini with retry + blocking detection."""
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048,
            )
        )

        if hasattr(response, "candidates") and response.candidates:
            cand = response.candidates[0]
            print(f"Gemini finish_reason: {cand.finish_reason}")
            if hasattr(cand, "content") and cand.content.parts:
                text = cand.content.parts[0].text.strip()
                if text:
                    return text

        if retries > 0:
            print("⚠️ Gemini returned empty/blocked — retrying in 2s...")
            time.sleep(2)
            return safe_gemini_generate(model, prompt, retries - 1)
        else:
            return "[⚠️ Gemini response was blocked or empty after retry.]"

    except Exception as e:
        print(f"⚠️ Gemini generation error: {str(e)}")
        if retries > 0:
            print("Retrying after error...")
            time.sleep(2)
            return safe_gemini_generate(model, prompt, retries - 1)
        return f"⚠️ Gemini generation error: {str(e)}"


# === Helper: Chunk Summarization (used in parallel) ===
def summarize_chunk(i, chunk, mode, model_choice):
    """Summarize an individual text chunk."""
    if mode == "quick":
        prompt = f"""
        Summarize the following section of a legal judgment clearly and concisely.
        Focus on the main facts, issues, and outcome.
        Return only plain text (no JSON, no formatting).

        Section {i}:
        {chunk}
        """
    else:
        prompt = f"""
        You are a professional legal document summarizer.
        Create a detailed summary of this section of an Indian court judgment,
        focusing on facts, issues, arguments, reasoning, and verdict.

        Section {i}:
        {chunk}
        """

    if model_choice == "groq":
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        if not GROQ_API_KEY:
            return f"[Error: Groq API key not found]"

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
            timeout=120
        )

        if groq_response.status_code == 200:
            return groq_response.json()["choices"][0]["message"]["content"]
        return f"[Error: {groq_response.text}]"

    else:
        model = genai.GenerativeModel('gemini-2.5-flash')
        return safe_gemini_generate(model, prompt)


# === Main Route: Summarize PDF ===
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

    # Decide on chunking
    if len(text) < 12000:
        chunks = [text]
    else:
        chunks = chunk_text(text)

    print(f"🧩 Total chunks created: {len(chunks)}")

    # === Process chunks in parallel ===
    summaries = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(summarize_chunk, i, chunk, mode, model_choice)
                   for i, chunk in enumerate(chunks, start=1)]
        for future in as_completed(futures):
            result = future.result()
            print(f"[Chunk done] Length: {len(result)} chars")
            summaries.append(result)

    # Merge all partial summaries
    merged_text = "\n\n".join(summaries)

    # === Final structured summary extraction ===
    if mode == "quick":
        refine_prompt = f"""
        You are a professional legal judgment summarizer.
        Based on the following combined summary of an Indian court judgment,
        extract and return the details strictly in clean JSON format:

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

        Combined summary:
        {merged_text}
        """
    else:
        refine_prompt = f"""
        You are a senior legal analyst.
        Combine and refine the following partial summaries of an Indian court judgment
        into one coherent, structured summary that flows naturally.
        Maintain all important facts, sections, and verdict details.

        {merged_text}
        """

    if model_choice == "groq":
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        groq_response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": refine_prompt}],
                "temperature": 0.6,
                "max_tokens": 2048
            },
            timeout=150
        )
        final_summary = groq_response.json()["choices"][0]["message"]["content"]
        model_used = "Groq (Llama 3.3 70B)"
    else:
        model = genai.GenerativeModel('gemini-2.5-flash')
        final_summary = safe_gemini_generate(model, refine_prompt)
        model_used = "Gemini 2.5 Flash"

    return jsonify({
        "summary": final_summary,
        "model_used": model_used,
        "chunks_processed": len(chunks)
    })


if __name__ == "__main__":
    app.run(debug=True)
