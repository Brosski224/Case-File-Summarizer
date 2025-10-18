# Case-File-Summarizer

Case-File-Summarizer is a lightweight, privacy-conscious toolkit for converting case-file PDFs (legal, medical, incident reports, etc.) into concise, actionable summaries. It combines a small Python backend that extracts and preprocesses PDF text with a minimal frontend for uploading files, previewing extracted text, viewing or exporting summaries, and comparing multiple cases.

## Key features

* PDF text extraction and basic preprocessing
* HTTP summarization endpoint(s) exposed by the backend
* Simple frontend for upload, preview, summary display, and JSON export (Streamlit or script)
* Configurable summary length/detail and optional redaction hints
* Selectable model for summarization: **Gemini** or **Groq**
* Case comparison: upload two or more PDFs and get a detailed analysis of **similarities and differences** between cases
* Intended for local use to protect sensitive data

## Repository structure

```
Summerizer/
├─ backend/
│  ├─ app.py            # backend service (API endpoints for summarization & comparison)
│  ├─ utils.py          # helper functions (parsing, summarization helpers)
│  └─ requirements.txt
├─ frontend/
│  ├─ app_frontend.py   # frontend UI (Streamlit or simple script)
│  └─ requirements.txt
└─ Learning_Report_PDF_Summarizer.md
```

## Prerequisites

* Python 3.8+ (3.10+ recommended)
* pip
* Optional: virtual environment tool (`venv` or `virtualenv`)

## Quick setup (PowerShell)

From the project root, create and activate a virtual environment and install dependencies for both backend and frontend:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

cd backend
pip install -r requirements.txt
cd ..

cd frontend
pip install -r requirements.txt
cd ..
```

If you prefer to install only the backend or frontend dependencies, run the corresponding `pip install -r` command inside that folder.

## Running the project

**Backend (example):**

```powershell
cd backend
python app.py
```

The backend will start and listen on the host/port defined in `app.py` (default: `http://127.0.0.1:5000/`).

**Frontend (Streamlit example):**

```powershell
cd frontend
streamlit run app_frontend.py
```

Or run the frontend script directly (if it's a CLI/UI script):

```powershell
cd frontend
python app_frontend.py
```

By default, the frontend expects the backend to be reachable at localhost; update the endpoint URL in `frontend/app_frontend.py` if needed.

## Usage

* Open the frontend UI in your browser (Streamlit will open one automatically).
* Upload a case-file PDF. The frontend will send the file to the backend for extraction and summarization.
* Select the **model** (Gemini or Groq) before summarization.
* Review the extracted text and generated summary. Export or copy results as needed.
* **Case Comparison:** navigate to the "Case Comparison" page via the sidebar, upload two or more PDFs, and view a structured breakdown of **similarities and differences** for each pair of cases.

## Security & privacy notes

* This project may process sensitive information. Run it in a secure environment and follow your organization's data-handling policies.
* No external APIs are called by default (unless configured). If you add cloud-based models or APIs, consider where data is sent and obtain required approvals.
* Summaries and comparisons are automatically generated; always verify critical facts against source documents.

## Troubleshooting

* Import errors: ensure your virtual environment is activated and that you installed dependencies from the correct `requirements.txt`.
* Backend startup errors: check the full traceback in the terminal and confirm any expected environment variables or model files exist.
* Frontend cannot reach backend: verify host/port in `frontend/app_frontend.py` and ensure no firewall blocks localhost connections.
* Case comparison outputs invalid JSON: ensure you are uploading at least two PDFs and that your selected model API keys are valid.

## Next steps (suggested)

* Add concrete API documentation (endpoint routes, request/response examples) by inspecting `backend/app.py`.
* Add tests for `backend/utils.py` and end-to-end tests posting sample PDFs.
* Provide a simple PowerShell script (`setup.ps1`) to automate venv creation and dependency installation.
* Add a LICENSE file and CONTRIBUTING guide if the project will be public.

## Contributing

Contributions are welcome. If you plan to add features that change data handling or add external services, document them clearly and include configuration instructions.

