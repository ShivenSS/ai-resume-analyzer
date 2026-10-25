from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from scorer import score_resume
from pdf_utils import extract_text_from_pdf

app = FastAPI(title="AI Resume Analyzer")


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
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