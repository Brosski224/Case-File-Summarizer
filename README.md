# Case-File-Summarizer

Case-File-Summarizer is a lightweight, privacy-conscious toolkit for converting case-file PDFs (legal, medical, incident reports, etc.) into concise, actionable summaries. It contains a small Flask backend that extracts and preprocesses PDF text and a minimal frontend (Streamlit or script) for uploading files, previewing extracted text, viewing or exporting summaries, and comparing multiple cases.

## Key features

- PDF text extraction using `pdfplumber` with optional preprocessing (see `backend/utils.py`)
- HTTP summarization endpoint (`/summarize`) served by a small Flask app (`backend/app.py`)
- Frontend UI for upload, preview, and JSON export (Streamlit or a simple script in `frontend/app_frontend.py`)

- Selectable model backend: Google Gemini (`gemini-2.5-flash`) or Groq (Llama 3.x via Groq API)
- Built-in chunking strategy for long documents (overlapping chunks, default chunk size 2500 chars with 200 char overlap)
- Concurrent processing of chunks using a ThreadPoolExecutor for faster summarization of large PDFs
- Intended for local use to protect sensitive data; external APIs are only used if configured with keys

Activity Completed
------------------
Extraction of key details from case-file PDFs and generation of structured summaries from judgment documents. The system can also compare summaries to highlight similarities and differences across cases.

Project summary
---------------
Case-File-PDF Summarizer is a Python-based system built with Flask (backend) and an optional Streamlit frontend. It extracts text from judgment PDFs, cleans and chunks the text, summarizes chunks using configurable remote LLMs (Google Gemini or Groq/Llama), and returns a clean, structured JSON summary. A comparison utility can identify overlaps and key differences between two or more case summaries.

Key features
------------
- Reliable PDF text extraction using `pdfplumber` with a small preprocessing helper (`backend/utils.py`).
- Chunking and overlap strategy to preserve context in long documents (default: 2500-char chunks, 200-char overlap).
- Concurrent summarization of chunks using `ThreadPoolExecutor` for faster processing.
- Two summarization backends: Google Gemini (`gemini-2.5-flash`) and Groq (Llama 3.x via Groq API).
- Two summary modes: `quick` (structured JSON) and `detailed` (narrative).
- Exportable, machine-readable JSON summaries containing the most relevant legal fields.
- Basic capability to compare two or more case summaries to surface similarities/differences.

Extracted fields (structured JSON)
----------------------------------
- case_title
- petitioner
- respondent
- judges
- court_name
- date_of_judgment
- sections_or_acts_mentioned
- final_verdict_or_order
- case_summary (short 2–3 sentence description)

Tools & technologies
--------------------
- Language: Python (3.8+, 3.10+ recommended)
- Backend: Flask, flask-cors
- PDF parsing: pdfplumber
- Frontend (optional): Streamlit
- HTTP & requests: requests
- Environment: python-dotenv
- LLM clients: google-generativeai (Gemini) and direct Groq REST calls
- Concurrency: concurrent.futures (ThreadPoolExecutor)

Models / APIs
------------
- Google Gemini: `gemini-2.5-flash` (via `google.generativeai` client)
- Groq (Llama 3.x): Llama 3.3 70B Versatile (accessed via Groq API)

High-level process
------------------
1. PDF Extraction: `pdfplumber` reads pages and extracts text.
2. Text cleaning: minimal cleanup via `backend/utils.py` (strip whitespace/artifacts).
3. Chunking: split text into overlapping chunks to maintain context for long documents.
4. Parallel summarization: summarize chunks concurrently using the selected model backend.
5. Merge & refine: combine partial summaries and (optionally) call the model again to produce a clean structured summary or narrative.
6. Comparison (optional): compare multiple structured summaries to find overlapping facts, statutes cited, and differing outcomes.

API endpoint
------------
- POST /summarize
  - form-data: `file` (PDF), `mode` (`quick` or `detailed`, default `quick`), `model_choice` (`gemini` or `groq`, default `gemini`)
  - response JSON: { "summary": string, "model_used": string, "chunks_processed": int }

Environment variables
---------------------
- `GEMINI_API_KEY` — required to use the Gemini backend (optional; if absent, Gemini calls will not be configured).
- `GROQ_API_KEY` — required to use Groq/Llama via the Groq API.

Quick start (PowerShell)
------------------------
Create & activate a venv, then install dependencies for backend and frontend (from project root):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

cd backend; pip install -r requirements.txt; cd ..
cd frontend; pip install -r requirements.txt; cd ..
```

Run the backend:

```powershell
cd backend
python app.py
```

Run the optional Streamlit frontend:

```powershell
cd frontend
streamlit run app_frontend.py
```

Notes & assumptions
-------------------
- The backend can run without API keys but will return error messages if a model backend is selected and its key is not configured.
- Scanned PDFs without embedded text will not be parsed by `pdfplumber` (OCR needed).
- The default chunk size and overlap were chosen for reasonable model-context usage; tune `chunk_text` in `backend/app.py` if required.

Role
----
Developer / NLP Engineer (place-holder — replace with your role or team name)

Repository
----------
GitHub: https://github.com/Brosski224/Case-File-Summarizer

Conclusion
----------
Implemented a compact system to extract structured information from court judgments and produce human- and machine-readable summaries. The project supports two LLM backends, concurrent chunk processing, and a simple comparison utility to analyze multiple cases.
