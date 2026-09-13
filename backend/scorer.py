import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-5"

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SCORE_TOOL = {
    "name": "submit_resume_analysis",
    "description": "Submit a structured analysis of how well a resume matches a job description.",
    "input_schema": {
        "type": "object",
        "properties": {
            "overall_score": {
                "type": "integer",
                "description": "Overall match score from 0-100",
            },
            "skills_matched": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Skills/keywords from the JD that appear in the resume",
            },
            "skills_missing": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Important skills/keywords from the JD that are absent from the resume",
            },
            "experience_alignment": {
                "type": "string",
                "description": "1-2 sentence assessment of how well the candidate's experience level/domain matches the role",
            },
            "top_recommendations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "2-4 concrete, actionable suggestions to improve the resume for this specific JD",
            },
        },
        "required": [
            "overall_score",
            "skills_matched",
            "skills_missing",
            "experience_alignment",
            "top_recommendations",
        ],
    },
}

SYSTEM_PROMPT = """You are an expert technical recruiter and resume reviewer.
You give honest, specific, and actionable feedback. You do not inflate scores
to make the candidate feel good — a generic or weak resume against a
demanding JD should score low. Be precise about which skills are present
vs. missing; do not hallucinate skills that are not actually in the resume text."""


def score_resume(resume_text: str, job_description: str) -> dict:
    if not resume_text.strip():
        raise ValueError("Resume text is empty.")
    if not job_description.strip():
        raise ValueError("Job description text is empty.")

    user_message = f"""Analyze this resume against this job description.

RESUME:
{resume_text[:8000]}

JOB DESCRIPTION:
{job_description[:4000]}

Call submit_resume_analysis with your structured analysis."""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            tools=[SCORE_TOOL],
            tool_choice={"type": "tool", "name": "submit_resume_analysis"},
            messages=[{"role": "user", "content": user_message}],
        )
    except Exception as e:
        raise RuntimeError(f"Claude API call failed: {e}")

    for block in response.content:
        if block.type == "tool_use" and block.name == "submit_resume_analysis":
            return block.input

    raise RuntimeError("Claude did not return the expected tool call.")

if __name__ == "__main__":
    sample_resume = """
    Shiven - First-year CS student, University of Toronto Mississauga.
    Coursework: Data Structures (CSC148), Discrete Math (MAT102), Calculus.
    Skills: Python, basic algorithms, recursion, tree/graph traversal.
    """
    sample_jd = """
    Software Engineering Intern - looking for students with experience in
    Python or Java, familiarity with REST APIs, Git, and a CS fundamentals
    background (data structures, algorithms). Bonus: any deployed project
    or open-source contribution.
    """
    result = score_resume(sample_resume, sample_jd)
    print(json.dumps(result, indent=2))