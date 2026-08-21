from google import genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google.genai import types
from typing import List, Optional
import time, requests
import json, io
# pyrefly: ignore [missing-import]
from pypdf import PdfReader

from extensions import ai_client as client
class WorkExperience(BaseModel):
    job_title: str = Field(description="Role or job title held by the candidate")
    company: str = Field(description="Company or organization name")
    duration: str = Field(description="Dates or duration of employment")
    responsibilities: List[str] = Field(description="Key achievements and duties")

class Education(BaseModel):
    degree: str = Field(description="Degree, diploma, or certificate title")
    institution: str = Field(description="School, college, or university name")
    year: Optional[str] = Field(None, description="Graduation year or date range")

class Project(BaseModel):
    title: str = Field(description="Project name")
    description: str = Field(description="Brief summary of the project and technologies used")

# Main schema for the complete review
class CandidateApplicationReview(BaseModel):
    professional_summary: str = Field(
        description="Extracted overview of professional background from the CV"
    )
    work_experience: List[WorkExperience] = Field(
        description="List of prior employment entries"
    )
    skills: List[str] = Field(
        description="List of technical, domain, and soft skills identified"
    )
    education: List[Education] = Field(
        description="Academic background and educational history"
    )
    certification: List[str] = Field(
        description="Professional certifications, licenses, or accreditations"
    )
    projects: List[Project] = Field(
        description="Notable projects or portfolio work mentioned"
    )
    cover_letter: Optional[str] = Field(
        None, description="Extracted content or analysis of the candidate's cover letter"
    )
    personal_summary: str = Field(
        description="AI-generated qualitative assessment of candidate strengths, fit, and potential red flags"
    )
    candidate_summary: str = Field(
        description="High-level executive summary summarizing overall suitability for the target role"
    )

def pdf_url_to_text(url):
    # 1. Download the PDF file stream
    response = requests.get(url)
    response.raise_for_status()  # Check for download errors
    
    # 2. Convert the byte content into an in-memory file stream
    pdf_file = io.BytesIO(response.content)
    
    # 3. Initialize the PDF reader
    reader = PdfReader(pdf_file)
    
    # 4. Loop through pages and extract text
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
        
    return text

print("Models created")
def agent_resume_coverLetter_parser(resumeURL, cover_letter):
    pdfText = pdf_url_to_text(resumeURL)
    prompt = f"""
        You are an expert HR recruiter. Analyze the candidate's CV and application materials.
        Extract all requested resume details into their respective structured fields, and synthesize
        a comprehensive 'personal_summary' and 'candidate_summary' evaluating their fit.

        Candidate Resume:
        {pdfText}

        Cover Letter:
        {cover_letter}
    """
    print("prompt created")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CandidateApplicationReview,
            temperature=0.2,
        ),
    )
    print("response started")

    # Convert Gemini's JSON response into a Python dictionary
    result = json.loads(response.text)
    print("converted")

    return result


