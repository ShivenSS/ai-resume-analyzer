# AI Resume Analyzer

Upload a resume PDF and paste a job description. The app uses Claude to return a structured match report: an overall score, matched and missing skills, an experience- lignment summary, and concrete recommendations.

## Why I built it

When I started my internship search, my applications kept getting rejected automatically and I couldn't tell why. I wanted objective feedback on how my resume reads against a specific posting, without just copying other people's resumes, so I built a tool that scores a resume against a job description and tells me what to fix.

## Features

- Extracts text from uploaded PDF resumes, entirely in memory
- Forces Claude to return a fixed JSON schema using tool use, so the output is always parseable
- Filters the "matched skills" list in code, so only skills the job description actually names can appear
- REST API built with FastAPI, with distinct error codes for bad input (400) and upstream failures (502)
- Streamlit frontend with a score display and side-by-side matched/missing skills

## Architecture

```text
Browser
   │
   ▼
Streamlit frontend (frontend/app.py)
   │  HTTP POST /analyze  (PDF + job description)
   ▼
FastAPI backend (backend/main.py)
   ├─ pdf_utils.py : PDF bytes -> plain text
   ├─ scorer.py    : resume text + job description -> Claude API (tool use)
   │                 -> structured JSON -> filter matched skills against the JD
   ▼
JSON response -> Streamlit renders score, skills, recommendations
```

### Design decisions

- **Separate frontend and backend.** The API key lives only in the backend. The UI can be swapped for another client without touching the scoring logic, and a backend failure shows a friendly message in the UI instead of crashing it.
- **Tool use for structured output.** Claude is forced to fill a fixed JSON schema, so the backend never parses free text.
- **A code-level guardrail.** Prompt instructions alone did not stop Claude from listing resume skills the job description never mentioned, so matched skills are verified against the job description text in code.
- **Distinct error codes.** Bad input returns 400, so the user can fix it. A failure in the Claude API returns 502, so the user knows to retry.

## Tech stack

- Python 3.11
- Claude API (Anthropic SDK), using tool use for structured output
- FastAPI and Uvicorn for the backend
- Streamlit for the frontend
- pypdf for PDF text extraction

## Running it locally

You need Python 3.11+ and an Anthropic API key.

```bash
git clone https://github.com/ShivenSS/ai-resume-analyzer.git
cd ai-resume-analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a file named `.env` in the project root containing:

```text
ANTHROPIC_API_KEY=your-key-here
```

The `.env` file is listed in `.gitignore`, so it is never committed.

Start the backend (Terminal 1):

```bash
cd backend
uvicorn main:app --reload
```

Start the frontend (Terminal 2, from the project root):

```bash
source .venv/bin/activate
streamlit run frontend/app.py
```

Open http://localhost:8501, upload a PDF resume, paste a job description, and click Analyze.