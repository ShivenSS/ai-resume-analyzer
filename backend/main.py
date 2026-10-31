from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from scorer import score_resume
from pdf_utils import extract_text_from_pdf
import time
from collections import deque

app = FastAPI(title="AI Resume Analyzer")

RATE_LIMIT = 10        # requests allowed...
RATE_WINDOW = 3600    # ...per this many seconds, across all visitors
_recent_requests = deque()


def check_rate_limit():
    now = time.time()
    while _recent_requests and now - _recent_requests[0] > RATE_WINDOW:
        _recent_requests.popleft()
    if len(_recent_requests) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="The demo has reached its hourly limit. Please try again later.",
        )
    _recent_requests.append(time.time())


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    check_rate_limit()
    try:
        pdf_bytes = await resume.read()
        resume_text = extract_text_from_pdf(pdf_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        result = score_resume(resume_text, job_description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result