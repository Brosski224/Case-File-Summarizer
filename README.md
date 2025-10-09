# PDF Summarizer

Small project that provides a backend summarization service and a simple frontend. The repository contains two parts:

- `backend/` - Flask (or plain Python) service that exposes the summarization endpoint(s).
- `frontend/` - Lightweight frontend (Streamlit or simple Python script) that talks to the backend.

## Repository structure

```
D:/IBM/Summerizer/
├─ backend/
│  ├─ app.py
│  ├─ utils.py
│  └─ requirements.txt
├─ frontend/
│  ├─ app_frontend.py
│  └─ requirements.txt
└─ Learning_Report_PDF_Summarizer.md
```

## Prerequisites

- Python 3.8+ (recommend 3.10+)
- pip
- (optional) virtual environment tool: `venv` or `virtualenv`

## Setup

Open a PowerShell terminal and run the following commands from the project root.

Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install backend dependencies:

```powershell
cd backend
pip install -r requirements.txt
cd ..
```

Install frontend dependencies:

```powershell
cd frontend
pip install -r requirements.txt
cd ..
```

## Running

Backend (from `backend/`):

```powershell
cd backend
python app.py
```

The backend should start and expose an HTTP endpoint (see `app.py` for the exact route and port). If the app fails to start, check the traceback printed in the terminal and the `requirements.txt` for missing packages.

Frontend (from `frontend/`):

If the frontend is a Streamlit app:

```powershell
cd frontend
streamlit run app_frontend.py
```

Or, if the frontend is a simple script, run:

```powershell
cd frontend
python app_frontend.py
```

The frontend expects the backend to be running locally. If the backend is on a different host/port, update the endpoint URL in `frontend/app_frontend.py`.

## Usage

- Upload or point the frontend at a PDF file (see the frontend UI).
- The frontend sends the file or text to the backend summarizer endpoint and displays a short summary.

## Troubleshooting

- If you get an import error, make sure you installed the packages from the correct `requirements.txt` and that your virtual env is activated.
- If the backend fails with an exception when starting, examine the `app.py` traceback in the terminal; common issues are missing environment variables or missing model files.
- If the frontend can't connect to the backend, open `frontend/app_frontend.py` and verify the host/port. Also confirm there is no firewall blocking localhost communication.

## Notes & Next steps

- Add exact API documentation (endpoints, request/response JSON examples) to this README after confirming the routes in `backend/app.py`.
- Add unit tests for `backend/utils.py` and a tiny end-to-end test that exercises the backend API.
- Consider pinning dependency versions in `requirements.txt` for reproducible installs.

## License

This repository does not include a license file. Add a LICENSE if you plan to make the project public.

---
