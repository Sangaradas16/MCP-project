# Local MCP Expense Tracking Assistant

A fully local expense tracking and intelligent analysis app built with FastAPI, SQLite, and a simple frontend.

## Features
- Add, update, delete expenses locally
- Category-based analytics and charts
- Monthly trend tracking
- Expense forecasting with local trend modeling
- Weekly anomaly detection
- Natural language chat interface powered by a local or optional OpenAI LLM
- Modular MCP design with tools, context routing, and agent orchestration

## Project Structure
- `backend/`
  - `main.py` — FastAPI application and startup logic
  - `router.py` — API endpoints
  - `database.py` — SQLAlchemy setup
  - `models.py` — expense data model
  - `schemas.py` — request/response schemas
  - `tools/` — database, analysis, prediction tool modules
  - `agent/` — context router and MCP agent
  - `assistant.py` — assistant wrapper for local/OpenAI responses
  - `sample_data.py` — seed sample expenses
- `frontend/`
  - `index.html` — dashboard UI
  - `styles.css` — UI styling
  - `app.js` — frontend logic and charts
- `requirements.txt` — Python dependencies

## Setup
1. Open a terminal in the workspace folder.
2. Create a virtual environment (recommended):

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

> Note: If you encounter build errors on Windows, the core packages (FastAPI, SQLAlchemy, OpenAI) should install successfully. The app uses pure Python implementations for analysis and forecasting to avoid heavy dependencies.

4. Optional: set a local LLM model path for richer assistant responses.

```bash
set LOCAL_LLM_MODEL_PATH=C:\path\to\your\model.bin
```

If you want to use OpenAI instead, set:

```bash
set OPENAI_API_KEY=your_api_key
```

```bash
set LOCAL_LLM_MODEL_PATH=C:\path\to\your\model.bin
```

If you want to use OpenAI instead, set:

```bash
set OPENAI_API_KEY=your_api_key
```
> Note: Installing `llama-cpp-python` on Windows may require a local build environment. The core app works without it, and the assistant will still provide grounded responses from tool outputs.
## Run Locally

From the workspace root run:

```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open your browser to `http://localhost:8000`.

## Notes
- The app stores data in `backend/expenses.db`.
- Sample expenses are seeded on first startup.
- Chat intent classification routes queries into `database`, `analysis`, and `prediction` flows.
- The frontend is served from the FastAPI static files mount.

## Troubleshooting
- If `llama-cpp-python` fails on Windows, remove the environment variable and the assistant will fall back to a simpler local response or OpenAI if configured.
- If charts do not appear, reload the page after the backend is started.
