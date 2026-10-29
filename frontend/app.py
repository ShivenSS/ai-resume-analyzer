import os
import requests
import streamlit as st


def get_api_url() -> str:
    try:
        return st.secrets["API_URL"]
    except Exception:
        return os.environ.get("API_URL", "http://127.0.0.1:8000/analyze")


API_URL = get_api_url()

st.title("AI Resume Analyzer")
st.write("Upload your resume and paste a job description to see how well they match.")

resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
job_description = st.text_area("Paste the job description", height=200)

if st.button("Analyze"):
    if resume_file is None:
        st.warning("Please upload a resume PDF.")
    elif not job_description.strip():
        st.warning("Please paste a job description.")
    else:
        with st.spinner("Analyzing... the first request after a quiet period can take up to a minute while the server wakes up."):
            try:
                response = requests.post(
                    API_URL,
                    files={"resume": (resume_file.name, resume_file.getvalue(), "application/pdf")},
                    data={"job_description": job_description},
                    timeout=120,
                )
            except requests.exceptions.RequestException:
                st.error("Could not reach the scoring service. Is the backend running?")
                st.stop()

        if response.status_code == 200:
            result = response.json()

            st.metric("Match score", f"{result['overall_score']}/100")
            st.progress(result["overall_score"])

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Skills matched")
                for skill in result["skills_matched"]:
                    st.write(f"✅ {skill}")
            with col2:
                st.subheader("Skills missing")
                for skill in result["skills_missing"]:
                    st.write(f"❌ {skill}")

            st.subheader("Experience alignment")
            st.write(result["experience_alignment"])

            st.subheader("Top recommendations")
            for rec in result["top_recommendations"]:
                st.write(f"- {rec}")
        else:
            st.error(response.json().get("detail", "Something went wrong."))