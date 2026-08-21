from google.genai import types
from pydantic import BaseModel, Field
from extensions import ai_client
from routes.upload_rank import extract_pdf_text

"""
class CandidateEvaluation(BaseModel):
    candidate_name: str
    match_score: int = Field(description="Score between 0 and 100 based on job fit")
    key_strengths: list[str]
    missing_skills: list[str]
    summary_verdict: str
"""

def evaluate_cv_content(cv_text: str, job_description: str) -> dict:
    prompt = f"""
    Evaluate the following candidate CV against the job requirements.
    
    JOB DESCRIPTION:
    {job_description}
    
    CANDIDATE CV:
    {cv_text}
    """

    response = ai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CandidateEvaluation,
            temperature=0.2,
        ),
    )
    return response.parsed.model_dump()